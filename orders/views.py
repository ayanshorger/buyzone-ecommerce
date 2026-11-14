from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from decimal import Decimal
import datetime
import uuid

from cart.models import CartItem, Coupon
from accounts.models import Address
from .models import Order, OrderItem
from .forms import CheckoutForm


@login_required
def checkout(request):
    cart_items = CartItem.objects.filter(user=request.user).select_related('product')
    if not cart_items.exists():
        messages.warning(request, "Your cart is empty. Add products before proceeding to checkout.")
        return redirect('store:product_list')

    # Calculations
    total_mrp = sum(item.mrp_subtotal for item in cart_items)
    subtotal = sum(item.subtotal for item in cart_items)
    product_discount = total_mrp - subtotal
    delivery_charge = Decimal('0.00') if subtotal >= 499 else Decimal('40.00')

    coupon_code = request.session.get('coupon_code', '')
    coupon_discount = Decimal('0.00')
    if coupon_code:
        try:
            c = Coupon.objects.get(code=coupon_code, is_active=True)
            if subtotal >= c.min_purchase:
                coupon_discount = c.calculate_discount(subtotal)
        except Coupon.DoesNotExist:
            coupon_code = ''

    final_total = max(Decimal('0.00'), subtotal - coupon_discount + delivery_charge)
    user_addresses = Address.objects.filter(user=request.user)

    if request.method == 'POST':
        form = CheckoutForm(request.POST)
        if form.is_valid():
            # 1. Determine Shipping Address
            address_id = form.cleaned_data.get('selected_address_id')
            selected_address = None

            if address_id:
                try:
                    selected_address = Address.objects.get(id=address_id, user=request.user)
                except Address.DoesNotExist:
                    pass

            if not selected_address:
                # Check if new address was submitted
                full_name = form.cleaned_data.get('full_name')
                phone = form.cleaned_data.get('phone')
                street = form.cleaned_data.get('street_address')
                city = form.cleaned_data.get('city')
                state = form.cleaned_data.get('state')
                postal_code = form.cleaned_data.get('postal_code')
                addr_type = form.cleaned_data.get('address_type') or 'HOME'

                if full_name and phone and street and city and postal_code:
                    selected_address = Address.objects.create(
                        user=request.user,
                        full_name=full_name,
                        phone=phone,
                        street_address=street,
                        landmark=form.cleaned_data.get('landmark', ''),
                        city=city,
                        state=state,
                        postal_code=postal_code,
                        address_type=addr_type,
                        is_default=(not user_addresses.exists())
                    )
                elif user_addresses.exists():
                    selected_address = user_addresses.filter(is_default=True).first() or user_addresses.first()
                else:
                    messages.error(request, "Please provide a valid delivery address.")
                    return redirect('orders:checkout')

            # 2. Payment details
            payment_method = form.cleaned_data.get('payment_method')
            payment_status = 'PAID' if payment_method in ['UPI', 'CARD', 'NETBANKING'] else 'PENDING'
            txn_id = f"TXN-{uuid.uuid4().hex[:12].upper()}" if payment_status == 'PAID' else ''

            # Address snapshot
            address_snapshot = (
                f"{selected_address.full_name}\n"
                f"{selected_address.street_address}"
                f"{', ' + selected_address.landmark if selected_address.landmark else ''}\n"
                f"{selected_address.city}, {selected_address.state} - {selected_address.postal_code}\n"
                f"Phone: {selected_address.phone} ({selected_address.get_address_type_display()})"
            )

            # Estimated delivery (3 days from order date)
            estimated_del = datetime.date.today() + datetime.timedelta(days=3)

            # 3. Create Order
            order = Order.objects.create(
                user=request.user,
                shipping_address=selected_address,
                shipping_address_snapshot=address_snapshot,
                total_mrp=total_mrp,
                product_discount=product_discount,
                coupon_code=coupon_code,
                coupon_discount=coupon_discount,
                delivery_charge=delivery_charge,
                final_total=final_total,
                payment_method=payment_method,
                payment_status=payment_status,
                transaction_id=txn_id,
                order_status='CONFIRMED',
                estimated_delivery=estimated_del,
                tracking_notes=[
                    {
                        'status': 'Ordered',
                        'timestamp': datetime.datetime.now().strftime("%d %b %Y, %I:%M %p"),
                        'detail': 'Your order has been placed successfully.'
                    },
                    {
                        'status': 'Confirmed',
                        'timestamp': datetime.datetime.now().strftime("%d %b %Y, %I:%M %p"),
                        'detail': 'Order verified and seller is preparing the package.'
                    }
                ]
            )

            # 4. Create OrderItems & Deduct Stock
            for item in cart_items:
                OrderItem.objects.create(
                    order=order,
                    product=item.product,
                    product_title=item.product.title,
                    product_sku=item.product.sku,
                    product_image_url=item.product.get_image(),
                    price=item.product.selling_price,
                    quantity=item.quantity,
                    total_price=item.subtotal
                )
                # Deduct inventory
                if item.product.stock >= item.quantity:
                    item.product.stock -= item.quantity
                    item.product.save(update_fields=['stock'])

            # 5. Clear Cart & Session Coupon
            cart_items.delete()
            if 'coupon_code' in request.session:
                del request.session['coupon_code']

            messages.success(request, f"Order #{order.order_number} confirmed! Thank you for shopping with Buyzone.")
            return redirect('orders:order_success', order_number=order.order_number)
        else:
            messages.error(request, "Please check the form inputs and select your payment method.")
    else:
        form = CheckoutForm()

    context = {
        'form': form,
        'cart_items': cart_items,
        'user_addresses': user_addresses,
        'total_mrp': total_mrp,
        'subtotal': subtotal,
        'product_discount': product_discount,
        'coupon_code': coupon_code,
        'coupon_discount': coupon_discount,
        'delivery_charge': delivery_charge,
        'final_total': final_total,
    }
    return render(request, 'orders/checkout.html', context)


@login_required
def order_success(request, order_number):
    order = get_object_or_404(Order, order_number=order_number, user=request.user)
    return render(request, 'orders/order_success.html', {'order': order})


@login_required
def order_history(request):
    orders = Order.objects.filter(user=request.user).prefetch_related('items').order_by('-created_at')
    return render(request, 'orders/order_history.html', {'orders': orders})


@login_required
def order_detail(request, order_number):
    order = get_object_or_404(Order, order_number=order_number, user=request.user)
    return render(request, 'orders/order_detail.html', {'order': order})


@login_required
def cancel_order(request, order_number):
    order = get_object_or_404(Order, order_number=order_number, user=request.user)
    if order.can_cancel:
        order.order_status = 'CANCELLED'
        # Restock products
        for item in order.items.all():
            if item.product:
                item.product.stock += item.quantity
                item.product.save(update_fields=['stock'])
        
        notes = order.tracking_notes or []
        notes.append({
            'status': 'Cancelled',
            'timestamp': datetime.datetime.now().strftime("%d %b %Y, %I:%M %p"),
            'detail': 'Order was cancelled by the customer.'
        })
        order.tracking_notes = notes
        order.save()
        messages.success(request, f"Order #{order.order_number} has been cancelled successfully.")
    else:
        messages.error(request, "This order cannot be cancelled because it is already shipped or delivered.")

    return redirect('orders:order_detail', order_number=order.order_number)


@login_required
def order_invoice(request, order_number):
    order = get_object_or_404(Order, order_number=order_number, user=request.user)
    return render(request, 'orders/invoice.html', {'order': order})
