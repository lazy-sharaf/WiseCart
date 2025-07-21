import re
import scrapy
from shops.models import Shop
from scraper.scraper.items import SearchResultItem


class RyansSpider(scrapy.Spider):
    name = "ryans"
    allowed_domains = ["ryanscomputers.com"]

    def start_requests(self):
        search_term = getattr(self, "search_term", None)
        if not search_term:
            self.log("No search term provided. Use -a search_term='product_name' to search.")
            return

        self.search_words = search_term.lower().split()
        search_url = f"https://www.ryanscomputers.com/search?q={search_term}"
        yield scrapy.Request(url=search_url, callback=self.parse)

    def parse(self, response):
        products = response.css('div.grid-product-item')
        store = Shop.objects.get(name="Ryans")
        product_count = 0

        for product in products:
            if product_count >= 2:
                break

            title_element = product.css('p.card-text::text').get()
            if not title_element or not self.title_contains_search_words(title_element.strip()):
                continue

            raw_price = product.css('p.pr-text::text').get()
            cleaned_price = self.clean_price(raw_price)

            item = SearchResultItem(
                search_id=self.search_obj.id,
                title=title_element.strip(),
                price=cleaned_price,
                url=response.urljoin(product.css('a.product-card-link::attr(href)').get()),
                store_id=store.id,
                stock=bool(cleaned_price and cleaned_price > 0),
                rating=0,
            )
            product_count += 1
            yield item

    def title_contains_search_words(self, title):
        """Check if all search words are present in the title."""
        title_lower = title.lower()
        return all(word in title_lower for word in self.search_words)

    def clean_price(self, price_str):
        """Clean the price string and return an integer value."""
        if price_str:
            cleaned_price = re.sub(r'\D', '', price_str.strip())
            return int(cleaned_price) if cleaned_price else None
        return None