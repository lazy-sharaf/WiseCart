from itemadapter import ItemAdapter
from products.models import Product
from shops.models import Shop
from django.db import transaction
from django.utils import timezone
import logging
from search.models import SearchResult
from scraper.scraper.items import SearchResultItem

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
            if spider.name == "startech_product":
                # Get store object from store_id
                store = Shop.objects.get(id=item["store_id"])

                # Try to get existing product or create new one
                product, created = Product.objects.update_or_create(
                    url=item["url"],
                    defaults={
                        "name": item["name"],
                        "store": store,
                        "price": item["price"],
                        "stock": item["stock"],
                        "rating": item.get("rating", 0),
                        "image_src": item.get("image_src"),
                        "description": item.get("description", ""),
                        "overview": item.get("overview", ""),
                        "last_updated": timezone.now(),
                    },
                )

                logger.info(
                    f"{'Created' if created else 'Updated'} product: {product.name}"
                )

            return item

        except Exception as e:
            logger.error(f"Error saving product: {str(e)}")
            raise


class SearchResultPipeline:
    def process_item(self, item, spider):
        if not isinstance(item, SearchResultItem):
            # If it's not a SearchResultItem, skip this pipeline
            return item

        adapter = ItemAdapter(item)

        # Create the SearchResult object
        search_result = SearchResult(
            search_id=adapter["search_id"],
            title=adapter["title"],
            rating=adapter.get("rating", 0),  # Default to 0 if not provided
            stock=adapter["stock"],
            url=adapter["url"],
            price=adapter["price"],
            store_id=adapter["store_id"],
        )

        search_result.save()
        return item
