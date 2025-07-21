from crochet import setup, wait_for
from scrapy.crawler import CrawlerRunner
from scrapy.utils.project import get_project_settings
from django.shortcuts import render, Http404
from django.utils import timezone
from datetime import timedelta
from .models import Product
from shops.models import Shop
from scraper.scraper.spiders.startech import StartechProductSpider
import time
import logging

logger = logging.getLogger(__name__)
setup()  # Setup Crochet

PRODUCT_CACHE_HOURS = 24
MAX_RETRIES = 5
RETRY_DELAY = 0.5  # seconds
SPIDER_TIMEOUT = 30  # seconds


@wait_for(timeout=SPIDER_TIMEOUT)
def run_spider(product_url, store):
    """Run the appropriate spider based on store configuration."""
    settings = get_project_settings()
    settings.set("ITEM_PIPELINES", {"scraper.scraper.pipelines.DjangoPipeline": 300})

    logger.info(f"Starting spider for URL: {product_url}")
    if store.name == "Startech":
        return CrawlerRunner(settings).crawl(StartechProductSpider, url=product_url)
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
        
        # Construct full URL
        full_url = product_url

        # Try to get existing product first
        product = Product.objects.filter(url=full_url).first()
        
        if product:
            # Check if product needs updating
            cache_threshold = timezone.now() - timedelta(hours=PRODUCT_CACHE_HOURS)
            if product.last_updated < cache_threshold:
                try:
                    run_spider(full_url)
                    product.refresh_from_db()
                except Exception as e:
                    logger.error(f"Error updating product: {str(e)}")
                    # Continue with existing product data if update fails
        else:
            # Product not found - try scraping
            run_spider(full_url, store)
            
            # Poll database for results
            for _ in range(MAX_RETRIES):
                product = Product.objects.filter(url=full_url).first()
                if product:
                    break
                time.sleep(RETRY_DELAY)
            
            if not product:
                raise Http404("Product not found after scraping")

        return render(request, 'products/product_detail.html', {"product": product})

    except Shop.DoesNotExist:
        raise Http404("Store not found")
    except Exception as e:
        logger.error(f"Error fetching product: {str(e)}")
        raise Http404(f"Error fetching product: {str(e)}")
