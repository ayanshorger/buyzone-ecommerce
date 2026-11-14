from django.db import models
from django.contrib.auth.models import User
from django.urls import reverse
from django.utils.text import slugify


class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=120, unique=True, blank=True)
    icon = models.CharField(max_length=50, blank=True, default='fa-tag', help_text="FontAwesome class e.g. fa-laptop, fa-mobile-screen")
    image = models.ImageField(upload_to='categories/', blank=True, null=True)
    image_url = models.URLField(blank=True, help_text="High-resolution CDN image URL")
    description = models.TextField(blank=True)
    parent = models.ForeignKey('self', on_delete=models.SET_NULL, null=True, blank=True, related_name='subcategories')
    is_featured = models.BooleanField(default=False)
    order = models.IntegerField(default=0)

    class Meta:
        verbose_name_plural = 'Categories'
        ordering = ['order', 'name']

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse('store:category_detail', kwargs={'slug': self.slug})

    def get_image(self):
        if self.image:
            return self.image.url
        if self.image_url:
            return self.image_url
        return 'https://images.unsplash.com/photo-1526738549149-8e07eca6c147?w=600&auto=format&fit=crop&q=80'

    def __str__(self):
        if self.parent:
            return f"{self.parent.name} > {self.name}"
        return self.name


class Product(models.Model):
    title = models.CharField(max_length=255)
    slug = models.SlugField(max_length=280, unique=True, blank=True)
    brand = models.CharField(max_length=100)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='products')
    sku = models.CharField(max_length=60, unique=True)
    description = models.TextField()
    short_description = models.CharField(max_length=350, blank=True)
    highlights = models.JSONField(default=list, blank=True, help_text="List of key feature bullets")
    specifications = models.JSONField(default=dict, blank=True, help_text="Key-value technical specifications")
    mrp_price = models.DecimalField(max_digits=10, decimal_places=2, help_text="List Price / MRP")
    selling_price = models.DecimalField(max_digits=10, decimal_places=2, help_text="Effective selling price")
    stock = models.PositiveIntegerField(default=50)
    is_available = models.BooleanField(default=True)
    is_featured = models.BooleanField(default=False)
    is_deal_of_day = models.BooleanField(default=False)
    is_bestseller = models.BooleanField(default=False)
    rating = models.FloatField(default=4.5)
    num_reviews = models.PositiveIntegerField(default=0)
    main_image = models.ImageField(upload_to='products/', blank=True, null=True)
    main_image_url = models.URLField(blank=True, help_text="CDN high-res product photo URL")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(self.title)
            slug = base_slug
            counter = 1
            while Product.objects.filter(slug=slug).exclude(pk=self.pk).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1
            self.slug = slug
        super().save(*args, **kwargs)

    @property
    def discount_percentage(self):
        if self.mrp_price > self.selling_price and self.mrp_price > 0:
            return round(((self.mrp_price - self.selling_price) / self.mrp_price) * 100)
        return 0

    @property
    def savings(self):
        if self.mrp_price > self.selling_price:
            return self.mrp_price - self.selling_price
        return 0

    @property
    def in_stock(self):
        return self.is_available and self.stock > 0

    def get_image(self):
        if self.main_image:
            return self.main_image.url
        if self.main_image_url:
            return self.main_image_url
        return 'https://images.unsplash.com/photo-1505740420928-5e560c06d30e?w=800&auto=format&fit=crop&q=80'

    def get_absolute_url(self):
        return reverse('store:product_detail', kwargs={'slug': self.slug})

    def update_rating(self):
        reviews = self.reviews.all()
        if reviews.exists():
            avg = sum(r.rating for r in reviews) / reviews.count()
            self.rating = round(avg, 1)
            self.num_reviews = reviews.count()
            self.save(update_fields=['rating', 'num_reviews'])

    def __str__(self):
        return f"{self.title} ({self.brand})"


class ProductImage(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='gallery_images')
    image = models.ImageField(upload_to='products/gallery/', blank=True, null=True)
    image_url = models.URLField(blank=True)
    alt_text = models.CharField(max_length=200, blank=True)
    order = models.IntegerField(default=0)

    class Meta:
        ordering = ['order', 'id']

    def get_image(self):
        if self.image:
            return self.image.url
        if self.image_url:
            return self.image_url
        return self.product.get_image()

    def __str__(self):
        return f"Gallery image for {self.product.title}"


class Review(models.Model):
    RATING_CHOICES = (
        (5, '5 - Outstanding'),
        (4, '4 - Very Good'),
        (3, '3 - Average'),
        (2, '2 - Poor'),
        (1, '1 - Terrible'),
    )

    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='reviews')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reviews')
    rating = models.PositiveSmallIntegerField(choices=RATING_CHOICES, default=5)
    headline = models.CharField(max_length=150)
    comment = models.TextField()
    is_verified_purchase = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        self.product.update_rating()

    def __str__(self):
        return f"{self.user.username}'s {self.rating}★ review on {self.product.title}"
