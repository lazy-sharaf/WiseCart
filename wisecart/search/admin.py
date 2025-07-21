from django.contrib import admin
from .models import Search, SearchResult

@admin.register(Search)
class SearchAdmin(admin.ModelAdmin):
    list_display = ('query', 'time', 'user')
    search_fields = ['query']

@admin.register(SearchResult)
class SearchResultAdmin(admin.ModelAdmin):
    list_display = ('title', 'price', 'rating', 'stock', 'store', 'get_query')
    list_filter = ('stock', 'store', 'search__query')
    search_fields = ['title', 'search__query']

    def get_query(self, obj):
        return obj.search.query
    get_query.short_description = 'Search Query'
    get_query.admin_order_field = 'search__query'