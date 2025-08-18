from crochet import setup, wait_for
from scrapy.crawler import CrawlerRunner
from scrapy.utils.project import get_project_settings
from django.shortcuts import render, Http404, redirect, get_object_or_404
from django.utils import timezone
from datetime import timedelta
from .models import Product, Bookmark
from shops.models import Shop
from scraper.scraper.spiders.startech import StartechProductSpider
from scraper.scraper.spiders.potakait import PotakaitProductSpider
from scraper.scraper.spiders.ucc import UCCProductSpider
from scraper.scraper.spiders.techland import TechLandProductSpider
from scraper.scraper.spiders.sumashtech import SumashTechProductSpider
from scraper.scraper.spiders.riointernational import RioInternationalProductSpider
import time
import logging
from urllib.parse import unquote, quote
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.contrib import messages
from django.core.paginator import Paginator

logger = logging.getLogger(__name__)
setup()  # Setup Crochet

PRODUCT_CACHE_HOURS = 24
MAX_RETRIES = 5
RETRY_DELAY = 0.5  # seconds
SPIDER_TIMEOUT = 30  # seconds


@wait_for(timeout=30)
def run_spider(product_url, store):
    """Run the appropriate spider based on store configuration."""
    # Set up Scrapy settings to enable DjangoPipeline
    settings = get_project_settings()
    settings.set(
        "ITEM_PIPELINES",
        {"scraper.scraper.pipelines.DjangoPipeline": 300},
    )
    runner = CrawlerRunner(settings)

    logger.info(f"Starting spider for URL: {product_url}")
    if store.name == "Startech":
        return runner.crawl(StartechProductSpider, url=product_url)
    elif store.name == "Potakait":
        return runner.crawl(PotakaitProductSpider, url=product_url)
    elif store.name == "UCC":
        return runner.crawl(UCCProductSpider, url=product_url)
    elif store.name == "TechLand":
        return runner.crawl(TechLandProductSpider, url=product_url)
    elif store.name == "Sumash Tech":
        return runner.crawl(SumashTechProductSpider, url=product_url)
    elif store.name == "Rio International":
        return runner.crawl(RioInternationalProductSpider, url=product_url)
    else:
        raise ValueError(f"Unsupported store: {store.name}")


def get_product_from_db(product_url, recent_only=False):
    """Fetch product from database with optional recency check."""
    query = Product.objects.filter(url=product_url)

    if recent_only:
        cache_threshold = timezone.now() - timedelta(hours=PRODUCT_CACHE_HOURS)
        query = query.filter(last_updated__gte=cache_threshold)

    return query.first()


def product_detail(request, store_name, product_url):
    """Handle product detail view with scraping fallback."""
    try:
        # Get the store
        store = Shop.objects.get(name__iexact=store_name)
        
        # Decode the product_url
        full_url = unquote(product_url)  # Decode the URL passed from the UI
        
        # Try to get existing product first (using decoded URL)
        product = Product.objects.filter(url=full_url).first()
        
        if product:
            # Check if product needs updating
            cache_threshold = timezone.now() - timedelta(hours=PRODUCT_CACHE_HOURS)
            if product.last_updated < cache_threshold:
                try:
                    run_spider(full_url, store)
                    product.refresh_from_db()
                except Exception as e:
                    logger.error(f"Error updating product: {str(e)}")
                    # Continue with existing product data if update fails
        else:
            # Product not found - try scraping
            try:
                run_spider(full_url, store)
                
                # Poll database for results (using consistent URL format)
                for attempt in range(MAX_RETRIES):
                    product = Product.objects.filter(url=full_url).first()
                    if product:
                        break
                    time.sleep(RETRY_DELAY)
                
                if not product:
                    raise Http404("Product not found after scraping")
                    
            except Exception as e:
                logger.error(f"Error during scraping: {str(e)}")
                raise Http404(f"Error fetching product: {str(e)}")

        # Check if user has bookmarked this product
        is_bookmarked = False
        if request.user.is_authenticated:
            is_bookmarked = Bookmark.objects.filter(user=request.user, product=product).exists()

        context = {
            'product': product,
            'is_bookmarked': is_bookmarked,
        }
        return render(request, 'products/product_detail.html', context)

    except Shop.DoesNotExist:
        raise Http404("Store not found")
    except Exception as e:
        logger.error(f"Error fetching product: {str(e)}")
        raise Http404(f"Error fetching product: {str(e)}")


@login_required
def add_bookmark(request, product_id):
    """Add a product to user's bookmarks."""
    if request.method == 'POST':
        product = get_object_or_404(Product, id=product_id)
        bookmark, created = Bookmark.objects.get_or_create(
            user=request.user,
            product=product
        )
        
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            # AJAX request
            return JsonResponse({
                'status': 'success',
                'action': 'added' if created else 'already_exists',
                'message': 'Product bookmarked!' if created else 'Product already in bookmarks'
            })
        else:
            # Regular request
            if created:
                messages.success(request, f'"{product.name}" has been added to your bookmarks!')
            else:
                messages.info(request, f'"{product.name}" is already in your bookmarks.')
            return redirect(request.META.get('HTTP_REFERER', 'wisecart:index'))
    
    return redirect('wisecart:index')


@login_required
def remove_bookmark(request, product_id):
    """Remove a product from user's bookmarks."""
    if request.method == 'POST':
        product = get_object_or_404(Product, id=product_id)
        bookmark = Bookmark.objects.filter(user=request.user, product=product)
        
        if bookmark.exists():
            bookmark.delete()
            removed = True
            message = 'Product removed from bookmarks!'
        else:
            removed = False
            message = 'Product was not in bookmarks.'
        
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            # AJAX request
            return JsonResponse({
                'status': 'success',
                'action': 'removed' if removed else 'not_found',
                'message': message
            })
        else:
            # Regular request
            if removed:
                messages.success(request, f'"{product.name}" has been removed from your bookmarks.')
            else:
                messages.warning(request, f'"{product.name}" was not in your bookmarks.')
            return redirect(request.META.get('HTTP_REFERER', 'wisecart:index'))
    
    return redirect('wisecart:index')


@login_required
def toggle_bookmark(request, product_id):
    """Toggle bookmark status for a product."""
    if request.method == 'POST':
        product = get_object_or_404(Product, id=product_id)
        bookmark = Bookmark.objects.filter(user=request.user, product=product)
        
        if bookmark.exists():
            bookmark.delete()
            is_bookmarked = False
            action = 'removed'
            message = 'Removed from bookmarks'
        else:
            Bookmark.objects.create(user=request.user, product=product)
            is_bookmarked = True
            action = 'added'
            message = 'Added to bookmarks'
        
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            # AJAX request
            return JsonResponse({
                'status': 'success',
                'action': action,
                'is_bookmarked': is_bookmarked,
                'message': message
            })
        else:
            # Regular request
            messages.success(request, f'"{product.name}" {message.lower()}!')
            # If coming from bookmarks page, stay there, otherwise go to referring page
            referer = request.META.get('HTTP_REFERER', '')
            if 'bookmarks' in referer:
                return redirect('products:bookmarks')
            return redirect(request.META.get('HTTP_REFERER', 'wisecart:index'))
    
    return redirect('wisecart:index')


@login_required
def bookmarks_list(request):
    """Display user's bookmarked products."""
    bookmarks = Bookmark.objects.filter(user=request.user).select_related('product', 'product__store')
    
    # Pagination
    items_per_page = request.GET.get('items_per_page', 12)
    if items_per_page == 'all':
        paginated_bookmarks = bookmarks
    else:
        try:
            items_per_page = int(items_per_page)
        except ValueError:
            items_per_page = 12
        
        paginator = Paginator(bookmarks, items_per_page)
        page_number = request.GET.get('page')
        paginated_bookmarks = paginator.get_page(page_number)
    
    context = {
        'bookmarks': paginated_bookmarks,
        'items_per_page': items_per_page,
        'total_bookmarks': bookmarks.count(),
    }
    return render(request, 'products/bookmarks.html', context)


def bookmark_count_view(request):
    """Return bookmark count for the current user."""
    if request.user.is_authenticated:
        count = Bookmark.objects.filter(user=request.user).count()
    else:
        count = 0
    
    return JsonResponse({'count': count})
