from itemadapter import ItemAdapter
from products.models import Product
from shops.models import Shop
from django.db import transaction
from django.utils import timezone
import logging
from search.models import SearchResult
from scraper.scraper.items import SearchResultItem
import traceback
import urllib.parse

logger = logging.getLogger(__name__)


class ScrapersPipeline:
    def process_item(self, item, spider):
        return item


class DjangoPipeline:
    def __init__(self):
        logger.info("DatabasePipeline initialized")

    @transaction.atomic
    def process_item(self, item, spider):
        try:
            if spider.name in ["startech_product", "potakait_product", "ucc_product", "techland_product", "sumashtech_product", "riointernational_product"]:
                # Get store object from store_id
                store = Shop.objects.get(id=item["store_id"])

                # Always save the product with a fully encoded URL
                url = item.get('url') or item.get('url_src')
                encoded_url = urllib.parse.quote(url, safe=':/?&=%') if url else None
                # Use encoded_url when saving to the Product model
                product, created = Product.objects.update_or_create(
                    url=encoded_url,
                    defaults={
                        "name": item.get("name") or item.get("title"),
                        "store": store,
                        "price": item.get("price"),
                        "stock": item.get("stock"),
                        "rating": item.get("rating", 0),
                        "image_src": item.get("image") or item.get("image_src"),
                        "description": item.get("description", ""),
                        "overview": item.get("overview", ""),
                        "last_updated": timezone.now(),
                    },
                )

                logger.info(
                    f"{'Created' if created else 'Updated'} product: {product.name} from spider: {spider.name}"
                )
            else:
                logger.debug(f"DjangoPipeline skipped for spider: {spider.name}")
            return item
        except Exception as e:
            traceback.print_exc()
            logger.error(f"Error saving product: {str(e)}")
            raise


class SearchResultPipeline:
    def process_item(self, item, spider):
        if not isinstance(item, SearchResultItem):
            # If it's not a SearchResultItem, skip this pipeline
            return item

        adapter = ItemAdapter(item)
        try:
            # Create the SearchResult object
            search_result = SearchResult(
                search_id=adapter["search_id"],
                title=adapter.get("title") or adapter.get("name"),
                rating=adapter.get("rating", 0),  # Default to 0 if not provided
                stock=adapter.get("stock", True),
                url=adapter["url"],
                price=adapter["price"],
                store_id=adapter["store_id"],
            )
            search_result.save()
        except Exception as e:
            logger.error(f"SearchResultPipeline: error saving SearchResult: {e}")
        return item
