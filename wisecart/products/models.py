from django.db import models
from shops.models import Shop


class Product(models.Model):
    name = models.CharField(max_length=255)
    store = models.ForeignKey(Shop, on_delete=models.CASCADE, default=1)
    price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    stock = models.BooleanField(default=True, null=True, blank=True)
    url = models.CharField(max_length=500)
    rating = models.FloatField(null=True, blank=True)
    image_src = models.URLField(max_length=200, null=True, blank=True)
    description = models.TextField(null=True, blank=True)
    overview = models.TextField(null=True, blank=True)
    last_updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name


class FeaturedProduct(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    image = models.ImageField(upload_to="featured_products/", null=True, blank=True)
    featured_date = models.DateTimeField(auto_now_add=True)
    expiry_date = models.DateTimeField()
    priority = models.IntegerField(default=1, choices=[(i, i) for i in range(1, 11)])

    class Meta:
        verbose_name = "Featured Product"
        verbose_name_plural = "Featured Products"
        ordering = ["-priority", "-featured_date"]

    def __str__(self):
        return f"Featured Product: {self.product.name}"
