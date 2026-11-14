from store.models import Category
from cart.models import CartItem, WishlistItem
from accounts.models import Address


def cart_and_categories(request):
    categories = Category.objects.filter(parent__isnull=True).prefetch_related('subcategories')
    cart_count = 0
    cart_total = 0
    wishlist_count = 0
    user_address = None

    if request.user.is_authenticated:
        cart_items = CartItem.objects.filter(user=request.user)
        cart_count = sum(item.quantity for item in cart_items)
        cart_total = sum(item.subtotal for item in cart_items)
        wishlist_count = WishlistItem.objects.filter(user=request.user).count()
        user_address = Address.objects.filter(user=request.user).first()
    else:
        if request.session.session_key:
            cart_items = CartItem.objects.filter(session_key=request.session.session_key)
            cart_count = sum(item.quantity for item in cart_items)
            cart_total = sum(item.subtotal for item in cart_items)

    return {
        'nav_categories': categories,
        'cart_count': cart_count,
        'cart_total': cart_total,
        'wishlist_count': wishlist_count,
        'user_address': user_address,
    }
