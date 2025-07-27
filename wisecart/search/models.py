from django.db import models
from shops.models import Shop  # Make sure this import path is correct


class Search(models.Model):
    query = models.CharField(max_length=255)
    time = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(
        "users.CustomUser",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        default=None,
    )

    def __str__(self):
        return f"Search: {self.query}"


class SearchResult(models.Model):
    search = models.ForeignKey(Search, on_delete=models.CASCADE, related_name="results")
    title = models.CharField(max_length=255)
    rating = models.FloatField(null=True, blank=True)
    stock = models.BooleanField(default=True)
    url = models.CharField(max_length=500)
    price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    store = models.ForeignKey(Shop, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.title} - {self.store}"

    class Meta:
        ordering = ['price']  # default ordering low to high
        indexes = [
            models.Index(fields=['price']),
            models.Index(fields=['-price']),
            models.Index(fields=['rating']),
            models.Index(fields=['-rating']),
        ]

    @classmethod
    def price_low_to_high(cls):
        return cls.objects.order_by('price')

    @classmethod
    def price_high_to_low(cls):
        return cls.objects.order_by('-price')

    @classmethod
    def rating_high_to_low(cls):
        return cls.objects.order_by('-rating')

    @classmethod
    def rating_low_to_high(cls):
        return cls.objects.order_by('rating')
