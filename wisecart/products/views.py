from crochet import setup, wait_for
from scrapy.crawler import CrawlerRunner
from scrapy.utils.project import get_project_settings
from django.shortcuts import render, Http404
from django.utils import timezone
from datetime import timedelta
from .models import Product
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
        print(f"[DEBUG] Decoded product_url in view: {full_url}")
        
        # Try to get existing product first (using decoded URL)
        product = Product.objects.filter(url=full_url).first()
        print(f"[DEBUG] Found existing product: {product is not None}")
        
        if product:
            # Check if product needs updating
            cache_threshold = timezone.now() - timedelta(hours=PRODUCT_CACHE_HOURS)
            if product.last_updated < cache_threshold:
                try:
                    print(f"[DEBUG] Updating product with URL: {full_url}")
                    run_spider(full_url, store)
                    product.refresh_from_db()
                except Exception as e:
                    logger.error(f"Error updating product: {str(e)}")
                    # Continue with existing product data if update fails
        else:
            # Product not found - try scraping
            print(f"[DEBUG] Product not found, starting scraping for URL: {full_url}")
            try:
                run_spider(full_url, store)
                
                # Poll database for results (using consistent URL format)
                for attempt in range(MAX_RETRIES):
                    print(f"[DEBUG] Polling attempt {attempt + 1} for URL: {full_url}")
                    product = Product.objects.filter(url=full_url).first()
                    if product:
                        print(f"[DEBUG] Found product after scraping: {product.name}")
                        break
                    time.sleep(RETRY_DELAY)
                
                if not product:
                    print(f"[DEBUG] Product still not found after {MAX_RETRIES} attempts")
                    raise Http404("Product not found after scraping")
                    
            except Exception as e:
                logger.error(f"Error during scraping: {str(e)}")
                raise Http404(f"Error fetching product: {str(e)}")

        return render(request, 'products/product_detail.html', {"product": product})

    except Shop.DoesNotExist:
        raise Http404("Store not found")
    except Exception as e:
        logger.error(f"Error fetching product: {str(e)}")
        raise Http404(f"Error fetching product: {str(e)}")
