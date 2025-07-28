from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.contrib import messages
from django.urls import reverse
from .models import ComparisonSession, ComparedProduct
from products.models import Product
from search.models import SearchResult
from shops.models import Shop
from urllib.parse import unquote
import json
import logging
import time
from django.utils import timezone
from datetime import timedelta

# Import scraping functionality from products app
from scrapy.crawler import CrawlerRunner
from scrapy.utils.project import get_project_settings
from crochet import wait_for, setup
from scraper.scraper.spiders.startech import StartechProductSpider
from scraper.scraper.spiders.potakait import PotakaitProductSpider
from scraper.scraper.spiders.ucc import UCCProductSpider
from scraper.scraper.spiders.techland import TechLandProductSpider
from scraper.scraper.spiders.sumashtech import SumashTechProductSpider
from scraper.scraper.spiders.riointernational import RioInternationalProductSpider

logger = logging.getLogger(__name__)

# Setup Crochet for async operations
try:
    setup()
except RuntimeError:
    pass  # Already setup

SPIDER_TIMEOUT = 30  # seconds


def get_or_create_comparison_session(request):
    """Get or create a comparison session for the current user session"""
    if not request.session.session_key:
        request.session.create()
    
    session_key = request.session.session_key
    comparison_session, created = ComparisonSession.objects.get_or_create(
        session_key=session_key
    )
    return comparison_session


@wait_for(timeout=SPIDER_TIMEOUT)
def run_spider_for_product(product_url, store):
    """Run the appropriate spider to scrape complete product details."""
    # Set up Scrapy settings to enable DjangoPipeline
    settings = get_project_settings()
    settings.set(
        "ITEM_PIPELINES",
        {"scraper.scraper.pipelines.DjangoPipeline": 300},
    )
    runner = CrawlerRunner(settings)

    logger.info(f"Starting spider for comparison product URL: {product_url}")
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


def scrape_product_details(search_result):
    """Scrape complete product details from the store."""
    try:
        full_url = unquote(search_result.url)
        
        # Check if we already have a detailed product
        existing_product = Product.objects.filter(url=full_url).first()
        if existing_product and existing_product.image_src and existing_product.description:
            # We already have detailed info, return the existing product
            return existing_product
        
        # Run the spider to get detailed information
        run_spider_for_product(full_url, search_result.store)
        
        # Wait a bit and then try to get the updated product
        time.sleep(2)  # Give the spider time to complete
        
        # Try a few times to get the scraped product
        for attempt in range(5):
            product = Product.objects.filter(url=full_url).first()
            if product and (product.image_src or product.description or product.overview):
                # We got some detailed info, return it
                return product
            time.sleep(1)  # Wait 1 second between attempts
        
        # If scraping failed, create or return basic product
        if not existing_product:
            product = Product.objects.create(
                name=search_result.title,
                store=search_result.store,
                price=search_result.price,
                stock=search_result.stock,
                url=full_url,
                rating=search_result.rating or 0,
                image_src="",
                description="",
                overview=""
            )
        else:
            product = existing_product
            
        return product
        
    except Exception as e:
        logger.error(f"Error scraping product details: {str(e)}")
        # Return basic product on error
        full_url = unquote(search_result.url)
        product, created = Product.objects.get_or_create(
            url=full_url,
            defaults={
                'name': search_result.title,
                'store': search_result.store,
                'price': search_result.price,
                'stock': search_result.stock,
                'rating': search_result.rating or 0,
                'image_src': "",
                'description': "",
                'overview': ""
            }
        )
        return product


@require_POST
def add_to_compare(request):
    """Add a product to comparison via AJAX with full scraping"""
    try:
        data = json.loads(request.body)
        search_result_id = data.get('search_result_id')
        
        if not search_result_id:
            return JsonResponse({'success': False, 'message': 'Search result ID is required'})
        
        search_result = get_object_or_404(SearchResult, id=search_result_id)
        comparison_session = get_or_create_comparison_session(request)
        
        # Check limit before doing any expensive operations
        current_count = ComparedProduct.objects.filter(comparison_session=comparison_session).count()
        if current_count >= 4:
            return JsonResponse({'success': False, 'message': 'You can only compare up to 4 products'})
        
        # Scrape complete product details
        product = scrape_product_details(search_result)
        
        # Check if already in comparison
        if ComparedProduct.objects.filter(comparison_session=comparison_session, product=product).exists():
            return JsonResponse({'success': False, 'message': 'Product already in comparison'})
        
        # Add to comparison
        ComparedProduct.objects.create(comparison_session=comparison_session, product=product)
        
        # Get updated count
        new_count = ComparedProduct.objects.filter(comparison_session=comparison_session).count()
        
        return JsonResponse({
            'success': True, 
            'message': f'{product.name} added to comparison successfully',
            'count': new_count,
            'scraped': bool(product.image_src or product.description or product.overview)
        })
        
    except Exception as e:
        logger.error(f"Error in add_to_compare: {str(e)}")
        return JsonResponse({'success': False, 'message': 'An error occurred while adding the product to comparison'})


@require_POST
def remove_from_compare(request):
    """Remove a product from comparison via AJAX"""
    try:
        data = json.loads(request.body)
        product_id = data.get('product_id')
        
        if not product_id:
            return JsonResponse({'success': False, 'message': 'Product ID is required'})
        
        product = get_object_or_404(Product, id=product_id)
        comparison_session = get_or_create_comparison_session(request)
        
        # Remove from comparison
        compared_product = ComparedProduct.objects.filter(
            comparison_session=comparison_session, 
            product=product
        ).first()
        
        if compared_product:
            compared_product.delete()
            new_count = ComparedProduct.objects.filter(comparison_session=comparison_session).count()
            return JsonResponse({
                'success': True, 
                'message': f'{product.name} removed from comparison',
                'count': new_count
            })
        else:
            return JsonResponse({'success': False, 'message': 'Product not in comparison'})
            
    except Exception as e:
        return JsonResponse({'success': False, 'message': str(e)})


def comparison_page(request):
    """Display the comparison page with selected products"""
    comparison_session = get_or_create_comparison_session(request)
    compared_products = ComparedProduct.objects.filter(
        comparison_session=comparison_session
    ).select_related('product', 'product__store').order_by('added_at')
    
    context = {
        'compared_products': compared_products,
        'product_count': compared_products.count(),
    }
    
    return render(request, 'comparison/compare.html', context)


def get_compare_count(request):
    """Get the current count of products in comparison"""
    comparison_session = get_or_create_comparison_session(request)
    count = ComparedProduct.objects.filter(comparison_session=comparison_session).count()
    return JsonResponse({'count': count})


def clear_comparison(request):
    """Clear all products from comparison"""
    comparison_session = get_or_create_comparison_session(request)
    ComparedProduct.objects.filter(comparison_session=comparison_session).delete()
    return redirect('comparison:compare')
