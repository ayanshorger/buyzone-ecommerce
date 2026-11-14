from django.shortcuts import render, redirect
from django.urls import reverse
from store.models import Category, Product
from django.contrib import messages


def home(request):
    hero_slides = [
        {
            'badge': 'MEGA FESTIVAL SALE',
            'title': 'Next-Gen Smartphones & Audio',
            'subtitle': 'Up to 45% OFF on Apple, Samsung, Sony & OnePlus with No-Cost EMI',
            'btn_text': 'Shop Flagships',
            'btn_link': '/store/?category=Flagship+Smartphones',
            'image': 'https://images.unsplash.com/photo-1511707171634-5f897ff02aa9?w=1600&auto=format&fit=crop&q=80',
            'theme': 'dark'
        },
        {
            'badge': 'PREMIUM WORKSPACE',
            'title': 'Elevate Your Productivity',
            'subtitle': 'M3 MacBooks, Ultra-Wide Displays, and Ergonomic Chairs',
            'btn_text': 'Explore Tech',
            'btn_link': '/store/?category=Laptops+%26+PCs',
            'image': 'https://images.unsplash.com/photo-1517336714731-489689fd1ca8?w=1600&auto=format&fit=crop&q=80',
            'theme': 'dark'
        },
        {
            'badge': 'TRENDING FASHION',
            'title': 'Iconic Kicks & Designer Styles',
            'subtitle': 'Fresh drops from Nike, Zara, and Levi’s starting at ₹5,499',
            'btn_text': 'Discover Styles',
            'btn_link': '/store/?category=Sneakers+%26+Shoes',
            'image': 'https://images.unsplash.com/photo-1445205170230-053b83016050?w=1600&auto=format&fit=crop&q=80',
            'theme': 'light'
        }
    ]

    deal_of_the_day = Product.objects.filter(is_deal_of_day=True, is_available=True)[:6]
    featured_products = Product.objects.filter(is_featured=True, is_available=True)[:8]
    bestsellers = Product.objects.filter(is_bestseller=True, is_available=True)[:8]
    root_categories = Category.objects.filter(parent__isnull=True).prefetch_related('subcategories')[:6]

    # Category spotlight: Flagship Phones & Audio
    spotlight_electronics = Product.objects.filter(category__name__in=['Flagship Smartphones', 'Audio & Headphones', 'Smartwatches'])[:4]

    context = {
        'hero_slides': hero_slides,
        'deal_of_the_day': deal_of_the_day,
        'featured_products': featured_products,
        'bestsellers': bestsellers,
        'root_categories': root_categories,
        'spotlight_electronics': spotlight_electronics,
    }
    return render(request, 'core/home.html', context)


def search(request):
    q = request.GET.get('q', '').strip()
    category = request.GET.get('category', '').strip()

    url = reverse('store:product_list')
    params = []
    if q:
        params.append(f"q={q}")
    if category:
        params.append(f"category={category}")
    
    if params:
        url += '?' + '&'.join(params)
    return redirect(url)


def about(request):
    return render(request, 'core/about.html')


def contact(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        messages.success(request, f"Thank you {name}! Your message has been received. Our 24/7 Buyzone support team will reach out shortly.")
        return redirect('core:contact')
    return render(request, 'core/contact.html')
