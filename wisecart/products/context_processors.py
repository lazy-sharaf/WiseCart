from .models import FeaturedProduct, Bookmark
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

def bookmark_count(request):
    """
    Context processor to make bookmark count available globally
    """
    bookmark_count = 0
    if request.user.is_authenticated:
        bookmark_count = Bookmark.objects.filter(user=request.user).count()
    
    return {
        'bookmark_count': bookmark_count
    } 