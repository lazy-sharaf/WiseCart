from .models import FeaturedProduct
from django.utils import timezone

def featured_products(request):
    """
    Context processor to make featured products available globally
    """
    featured_products = FeaturedProduct.objects.filter(
        expiry_date__gt=timezone.now()
    ).select_related('product', 'product__store')[:6]  # Limit to 6 products
    
    return {
        'featured_products': featured_products
    } 