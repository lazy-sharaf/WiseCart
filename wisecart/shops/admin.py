from django.contrib import admin
from django.utils import timezone
from .models import Shop, Review, FeaturedShop

@admin.register(Shop)
class ShopAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'store_type', 'have_app')
    search_fields = ('name', 'category', 'store_type')
    list_filter = ('store_type', 'have_app')

@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ('shop', 'user', 'rating', 'created_at')
    search_fields = ('shop__name', 'user__username', 'rating')
    list_filter = ('rating', 'created_at')

@admin.register(FeaturedShop)
class FeaturedShopAdmin(admin.ModelAdmin):
    list_display = ('shop', 'featured_date', 'expiry_date', 'priority', 'is_active')
    search_fields = ('shop__name',)
    list_filter = ('priority', 'featured_date', 'expiry_date')
    ordering = ('-priority', '-featured_date')

    def is_active(self, obj):
        return obj.expiry_date >= timezone.now()
    is_active.boolean = True
    is_active.short_description = 'Active'