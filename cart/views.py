from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from decimal import Decimal
from store.models import Product
from .models import CartItem, WishlistItem, Coupon


def _get_cart_items(request):
    if request.user.is_authenticated:
        return CartItem.objects.filter(user=request.user).select_related('product')
    else:
        if not request.session.session_key:
            request.session.create()
        return CartItem.objects.filter(session_key=request.session.session_key).select_related('product')


def cart_view(request):
    cart_items = _get_cart_items(request)

    total_mrp = sum(item.mrp_subtotal for item in cart_items)
    subtotal = sum(item.subtotal for item in cart_items)
    product_discount = total_mrp - subtotal

    # Delivery charge rule: Free delivery above ₹499, else ₹40
    delivery_charge = Decimal('0.00') if subtotal >= 499 or subtotal == 0 else Decimal('40.00')

    # Coupon handling
    applied_coupon_code = request.session.get('coupon_code')
    coupon_discount = Decimal('0.00')
    active_coupon = None

    if applied_coupon_code:
        try:
            active_coupon = Coupon.objects.get(code=applied_coupon_code, is_active=True)
            if subtotal >= active_coupon.min_purchase:
                coupon_discount = active_coupon.calculate_discount(subtotal)
            else:
                # Minimum not met
                del request.session['coupon_code']
                messages.warning(request, f"Coupon {applied_coupon_code} removed. Minimum purchase of ₹{active_coupon.min_purchase} required.")
                active_coupon = None
        except Coupon.DoesNotExist:
            if 'coupon_code' in request.session:
                del request.session['coupon_code']

    final_total = max(Decimal('0.00'), subtotal - coupon_discount + delivery_charge)

    # Available coupons for banner
    available_coupons = Coupon.objects.filter(is_active=True)[:3]

    context = {
        'cart_items': cart_items,
        'total_mrp': total_mrp,
        'subtotal': subtotal,
        'product_discount': product_discount,
        'delivery_charge': delivery_charge,
        'coupon_discount': coupon_discount,
        'active_coupon': active_coupon,
        'final_total': final_total,
        'available_coupons': available_coupons,
    }
    return render(request, 'cart/cart.html', context)


def add_to_cart(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    quantity = int(request.POST.get('quantity', 1))

    if not product.in_stock:
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            return JsonResponse({'status': 'error', 'message': 'This product is out of stock.'}, status=400)
        messages.error(request, f"{product.title} is currently out of stock.")
        return redirect('store:product_detail', slug=product.slug)

    # Cart item resolution
    if request.user.is_authenticated:
        cart_item, created = CartItem.objects.get_or_create(
            user=request.user,
            product=product,
            defaults={'quantity': quantity}
        )
        if not created:
            cart_item.quantity += quantity
            cart_item.save()
    else:
        if not request.session.session_key:
            request.session.create()
        cart_item, created = CartItem.objects.get_or_create(
            session_key=request.session.session_key,
            product=product,
            defaults={'quantity': quantity}
        )
        if not created:
            cart_item.quantity += quantity
            cart_item.save()

    # If action is 'buy_now', redirect straight to checkout
    if request.POST.get('action') == 'buy_now':
        return redirect('orders:checkout')

    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        cart_items = _get_cart_items(request)
        cart_count = sum(item.quantity for item in cart_items)
        return JsonResponse({
            'status': 'success',
            'message': f"Added '{product.title}' to your cart!",
            'cart_count': cart_count,
        })

    messages.success(request, f"Added '{product.title}' to your cart!")
    return redirect(request.META.get('HTTP_REFERER', 'cart:cart_view'))


def update_cart_item(request, item_id):
    cart_item = get_object_or_404(CartItem, id=item_id)
    # Check permissions
    if (cart_item.user and cart_item.user != request.user) or \
       (cart_item.session_key and cart_item.session_key != request.session.session_key):
        return redirect('cart:cart_view')

    action = request.POST.get('action')
    if action == 'increase':
        if cart_item.quantity < cart_item.product.stock:
            cart_item.quantity += 1
            cart_item.save()
        else:
            messages.warning(request, f"Maximum available stock for {cart_item.product.title} is {cart_item.product.stock}.")
    elif action == 'decrease':
        if cart_item.quantity > 1:
            cart_item.quantity -= 1
            cart_item.save()
        else:
            cart_item.delete()
            messages.info(request, "Item removed from cart.")
            return redirect('cart:cart_view')

    return redirect('cart:cart_view')


def remove_from_cart(request, item_id):
    cart_item = get_object_or_404(CartItem, id=item_id)
    if (cart_item.user and cart_item.user == request.user) or \
       (cart_item.session_key and cart_item.session_key == request.session.session_key):
        title = cart_item.product.title
        cart_item.delete()
        messages.success(request, f"Removed '{title}' from your cart.")
    return redirect('cart:cart_view')


def apply_coupon(request):
    if request.method == 'POST':
        code = request.POST.get('code', '').strip().upper()
        try:
            coupon = Coupon.objects.get(code=code, is_active=True)
            cart_items = _get_cart_items(request)
            subtotal = sum(item.subtotal for item in cart_items)

            if subtotal >= coupon.min_purchase:
                request.session['coupon_code'] = coupon.code
                messages.success(request, f"Coupon '{coupon.code}' applied successfully!")
            else:
                messages.error(request, f"Coupon requires a minimum order amount of ₹{coupon.min_purchase}.")
        except Coupon.DoesNotExist:
            messages.error(request, "Invalid or expired promo code.")

    return redirect('cart:cart_view')


def remove_coupon(request):
    if 'coupon_code' in request.session:
        del request.session['coupon_code']
        messages.info(request, "Coupon removed.")
    return redirect('cart:cart_view')


@login_required
def wishlist_view(request):
    wishlist_items = WishlistItem.objects.filter(user=request.user).select_related('product')
    return render(request, 'cart/wishlist.html', {'wishlist_items': wishlist_items})


@login_required
def toggle_wishlist(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    item, created = WishlistItem.objects.get_or_create(user=request.user, product=product)

    if not created:
        item.delete()
        action = 'removed'
        msg = f"Removed '{product.title}' from your Wishlist."
    else:
        action = 'added'
        msg = f"Saved '{product.title}' to your Wishlist!"

    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        count = WishlistItem.objects.filter(user=request.user).count()
        return JsonResponse({
            'status': 'success',
            'action': action,
            'message': msg,
            'wishlist_count': count
        })

    messages.success(request, msg)
    return redirect(request.META.get('HTTP_REFERER', 'store:product_detail', slug=product.slug))


@login_required
def move_to_cart(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    # Remove from wishlist
    WishlistItem.objects.filter(user=request.user, product=product).delete()

    # Add to cart
    cart_item, created = CartItem.objects.get_or_create(
        user=request.user,
        product=product,
        defaults={'quantity': 1}
    )
    if not created:
        cart_item.quantity += 1
        cart_item.save()

    messages.success(request, f"Moved '{product.title}' to your Cart!")
    return redirect('cart:cart_view')
