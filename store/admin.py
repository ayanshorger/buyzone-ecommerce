from django.contrib import admin
from .models import Category, Product, ProductImage, Review


class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 1


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'parent', 'is_featured', 'order')
    prepopulated_fields = {'slug': ('name',)}
    list_filter = ('is_featured', 'parent')
    search_fields = ('name',)


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('title', 'brand', 'category', 'selling_price', 'mrp_price', 'stock', 'is_available', 'is_featured', 'rating')
    list_filter = ('category', 'brand', 'is_available', 'is_featured', 'is_deal_of_day', 'is_bestseller')
    search_fields = ('title', 'brand', 'sku', 'description')
    prepopulated_fields = {'slug': ('title',)}
    inlines = [ProductImageInline]


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ('product', 'user', 'rating', 'headline', 'created_at', 'is_verified_purchase')
    list_filter = ('rating', 'is_verified_purchase', 'created_at')
    search_fields = ('product__title', 'user__username', 'headline', 'comment')
