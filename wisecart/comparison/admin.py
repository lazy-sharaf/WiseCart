from django.contrib import admin
from .models import ComparisonSession, ComparedProduct


@admin.register(ComparisonSession)
class ComparisonSessionAdmin(admin.ModelAdmin):
    list_display = ('session_key', 'created_at', 'updated_at', 'product_count')
    list_filter = ('created_at', 'updated_at')
    search_fields = ('session_key',)
    readonly_fields = ('created_at', 'updated_at')
    
    def product_count(self, obj):
        return obj.compared_products.count()
    product_count.short_description = 'Products'


@admin.register(ComparedProduct)
class ComparedProductAdmin(admin.ModelAdmin):
    list_display = ('product', 'comparison_session', 'added_at')
    list_filter = ('added_at', 'product__store')
    search_fields = ('product__name', 'comparison_session__session_key')
    readonly_fields = ('added_at',)
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('product', 'product__store', 'comparison_session')
