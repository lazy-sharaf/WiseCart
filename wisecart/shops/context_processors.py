from shops.models import FeaturedShop

def featured_shops(request):
    # You might want to add caching here
    return {
        'featured_shops': FeaturedShop.objects.select_related('shop').all()
    } 