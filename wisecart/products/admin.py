from django.contrib import admin
from .models import Product, FeaturedProduct, Bookmark
from django.utils import timezone

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'store', 'price', 'stock', 'rating', 'is_available')
    search_fields = ('name', 'store__name')
    ordering = ('-last_updated',)

    def is_available(self, obj):
        return obj.stock is not None and obj.stock > 0
    is_available.boolean = True
    is_available.short_description = 'Available'

@admin.register(FeaturedProduct)
class FeaturedProductAdmin(admin.ModelAdmin):
    list_display = ('get_product_name', 'featured_date', 'expiry_date', 'priority', 'is_active')
    list_filter = ('priority', 'featured_date', 'expiry_date')
    search_fields = ('product__name',)
    ordering = ('-featured_date',)

    def get_product_name(self, obj):
        return obj.product.name
    get_product_name.admin_order_field = 'product__name'
    get_product_name.short_description = 'Product Name'

    def is_active(self, obj):
        return obj.expiry_date >= timezone.now()
    is_active.boolean = True
    is_active.short_description = 'Active'

@admin.register(Bookmark)
class BookmarkAdmin(admin.ModelAdmin):
    list_display = ('user', 'get_product_name', 'get_store_name', 'created_at')
    list_filter = ('created_at', 'product__store')
    search_fields = ('user__username', 'user__email', 'product__name', 'product__store__name')
    ordering = ('-created_at',)
    readonly_fields = ('created_at',)

    def get_product_name(self, obj):
        return obj.product.name
    get_product_name.short_description = 'Product'
    get_product_name.admin_order_field = 'product__name'

    def get_store_name(self, obj):
        return obj.product.store.name
    get_store_name.short_description = 'Store'
    get_store_name.admin_order_field = 'product__store__name'