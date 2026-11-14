from django.shortcuts import render, get_object_or_404, redirect
from django.core.paginator import Paginator
from django.db.models import Q, Count, Avg, Min, Max
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from .models import Category, Product, Review
from .forms import ReviewForm
import datetime


def product_list(request):
    products = Product.objects.filter(is_available=True)

    # 1. Search Query
    q = request.GET.get('q', '').strip()
    if q:
        products = products.filter(
            Q(title__icontains=q) |
            Q(brand__icontains=q) |
            Q(description__icontains=q) |
            Q(category__name__icontains=q)
        )

    # 2. Category Filter (Supports parent category matching children)
    category_slug = request.GET.get('category', '').strip()
    current_category = None
    if category_slug:
        cat_matches = Category.objects.filter(Q(slug=category_slug) | Q(name__iexact=category_slug))
        if cat_matches.exists():
            current_category = cat_matches.first()
            category_ids = [current_category.id] + list(current_category.subcategories.values_list('id', flat=True))
            products = products.filter(category_id__in=category_ids)

    # 3. Brand Filter
    selected_brands = request.GET.getlist('brand')
    if selected_brands:
        products = products.filter(brand__in=selected_brands)

    # 4. Price Filter
    min_price = request.GET.get('min_price')
    max_price = request.GET.get('max_price')
    if min_price and min_price.isdigit():
        products = products.filter(selling_price__gte=int(min_price))
    if max_price and max_price.isdigit():
        products = products.filter(selling_price__lte=int(max_price))

    # 5. Rating Filter
    min_rating = request.GET.get('rating')
    if min_rating and min_rating.isdigit():
        products = products.filter(rating__gte=float(min_rating))

    # 6. In Stock Filter
    in_stock = request.GET.get('in_stock')
    if in_stock == '1':
        products = products.filter(stock__gt=0)

    # 7. Discount Filter
    discount_filter = request.GET.get('discount')
    if discount_filter and discount_filter.isdigit():
        disc_val = int(discount_filter)
        # Filter products whose discount is >= disc_val
        valid_ids = [p.id for p in products if p.discount_percentage >= disc_val]
        products = products.filter(id__in=valid_ids)

    # 8. Sorting
    sort = request.GET.get('sort', 'featured')
    if sort == 'price_low':
        products = products.order_by('selling_price')
    elif sort == 'price_high':
        products = products.order_by('-selling_price')
    elif sort == 'rating':
        products = products.order_by('-rating', '-num_reviews')
    elif sort == 'newest':
        products = products.order_by('-created_at')
    else:  # featured / default
        products = products.order_by('-is_featured', '-is_deal_of_day', '-is_bestseller', '-rating')

    # Available Brands for Sidebar
    all_brands = Product.objects.filter(is_available=True).values_list('brand', flat=True).distinct().order_by('brand')

    # Pagination
    paginator = Paginator(products, 9)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    # Get query params string without page for pagination links
    params = request.GET.copy()
    if 'page' in params:
        del params['page']
    query_params_str = params.urlencode()

    context = {
        'page_obj': page_obj,
        'total_count': products.count(),
        'all_brands': all_brands,
        'selected_brands': selected_brands,
        'current_category': current_category,
        'search_query': q,
        'current_sort': sort,
        'min_price': min_price or '',
        'max_price': max_price or '',
        'selected_rating': min_rating or '',
        'selected_discount': discount_filter or '',
        'in_stock': in_stock or '',
        'query_params': query_params_str,
    }
    return render(request, 'store/product_list.html', context)


def product_detail(request, slug):
    product = get_object_or_404(Product, slug=slug)
    gallery_images = product.gallery_images.all()
    reviews = product.reviews.select_related('user').order_by('-created_at')

    # Rating distribution breakdown
    total_reviews = reviews.count()
    rating_breakdown = {}
    for star in [5, 4, 3, 2, 1]:
        count = reviews.filter(rating=star).count()
        pct = round((count / total_reviews * 100)) if total_reviews > 0 else 0
        rating_breakdown[star] = {'count': count, 'percent': pct}

    related_products = Product.objects.filter(category=product.category).exclude(id=product.id)[:4]

    # Check if user already reviewed
    user_has_reviewed = False
    if request.user.is_authenticated:
        user_has_reviewed = reviews.filter(user=request.user).exists()

    review_form = ReviewForm()

    context = {
        'product': product,
        'gallery_images': gallery_images,
        'reviews': reviews,
        'total_reviews': total_reviews,
        'rating_breakdown': rating_breakdown,
        'related_products': related_products,
        'user_has_reviewed': user_has_reviewed,
        'review_form': review_form,
    }
    return render(request, 'store/product_detail.html', context)


def category_detail(request, slug):
    return redirect(f"/store/?category={slug}")


@login_required
def add_review(request, product_id):
    product = get_object_or_404(Product, id=product_id)

    if request.method == 'POST':
        # Check if already reviewed
        existing_review = Review.objects.filter(product=product, user=request.user).first()
        form = ReviewForm(request.POST, instance=existing_review)
        if form.is_valid():
            rev = form.save(commit=False)
            rev.product = product
            rev.user = request.user
            rev.is_verified_purchase = True
            rev.save()
            messages.success(request, "Thank you! Your verified review has been submitted.")
        else:
            messages.error(request, "Failed to submit review. Please ensure all fields are filled.")

    return redirect('store:product_detail', slug=product.slug)


def check_pincode(request):
    pincode = request.GET.get('pincode', '').strip()
    if len(pincode) == 6 and pincode.isdigit():
        delivery_date = datetime.date.today() + datetime.timedelta(days=2)
        formatted_date = delivery_date.strftime("%A, %b %d")
        return JsonResponse({
            'status': 'success',
            'delivery_date': formatted_date,
            'message': f"FREE Delivery by {formatted_date}. Cash on Delivery also available."
        })
    return JsonResponse({
        'status': 'error',
        'message': 'Please enter a valid 6-digit Indian PIN code.'
    })
