from django.db import models
from django.utils.text import slugify
from django.conf import settings

class Shop(models.Model):
    STORE_TYPE_CHOICES = [
        ('online', 'Online'),
        ('offline', 'Offline'),
        ('both', 'Online and Offline')
    ]

    name = models.CharField(max_length=255, unique=True)
    slug = models.SlugField(max_length=255, unique=True, blank=True)
    image = models.ImageField(upload_to="shops/")
    url = models.URLField(blank=True, null=True)
    category = models.CharField(max_length=255, blank=True, null=True)
    mod_rating = models.FloatField(blank=True, null=True)
    mod_comment = models.TextField()
    description = models.TextField()
    organization = models.CharField(max_length=255, blank=True, null=True)
    all_domains = models.TextField()
    store_type = models.CharField(max_length=10, choices=STORE_TYPE_CHOICES, default='online')
    payment_methods = models.CharField(max_length=255, blank=True, null=True)
    have_app = models.BooleanField(default=False)
    address = models.TextField()
    opening_hours = models.CharField(max_length=100, blank=True, null=True)
    contact_number = models.CharField(max_length=15, blank=True, null=True)
    email = models.EmailField(blank=True, null=True)
    social_media = models.CharField(max_length=255, blank=True, null=True)

    class Meta:
        ordering = ['name']  # Add this line to order shops by name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        self.slug = self.slug.lower()
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name

    @property
    def user_rating(self):
        reviews = self.reviews.all()
        if reviews:
            return round(sum(review.rating for review in reviews) / len(reviews), 1)
        return None

class Review(models.Model):
    shop = models.ForeignKey(Shop, related_name="reviews", on_delete=models.CASCADE)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, related_name="reviews", on_delete=models.CASCADE)
    rating = models.FloatField()
    comment = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('shop', 'user')
        ordering = ['-created_at']  # Add this line to order reviews by creation date

    def __str__(self):
        return f"Review by {self.user.username} for {self.shop.name}"

class FeaturedShop(models.Model):
    shop = models.OneToOneField(Shop, on_delete=models.CASCADE)
    featured_date = models.DateTimeField(auto_now_add=True)
    expiry_date = models.DateTimeField()
    priority = models.IntegerField(default=1, choices=[(i, i) for i in range(1, 11)])

    class Meta:
        verbose_name = "Featured Shop"
        verbose_name_plural = "Featured Shops"
        ordering = ['-priority', '-featured_date']

    def __str__(self):
        return f"Featured Shops ({self.featured_date.strftime('%Y-%m-%d')})"