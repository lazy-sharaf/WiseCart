import re
import scrapy
from shops.models import Shop
from scraper.scraper.items import ProductItem, SearchResultItem


class StartechProductSpider(scrapy.Spider):
    name = "startech_product"
    allowed_domains = ["startech.com.bd"]

    def start_requests(self):
        url = getattr(self, "url", None)
        if not url:
            self.log(
                "No URL provided. Use -a url='https://www.startech.com.bd/product-name' to search."
            )
            return
        yield scrapy.Request(url=url, callback=self.parse)

    def parse(self, response):
        # Extract data
        name = response.css("div.product-short-info h1.product-name::text").get()
        name = name.strip() if name else None
        store = Shop.objects.get(name="Startech")
        # Extract price - prioritize <ins> tag (current price), fallback to any text
        price_current = response.css("div.product-short-info td.product-price ins::text").get()
        if not price_current:
            # Fallback to first available price text if no <ins> tag
            price_current = response.css("div.product-short-info td.product-price *::text").get()
        
        self.logger.info(f"Price extraction - Raw text: {repr(price_current)}")
        price = self.clean_price(price_current)
        self.logger.info(f"Price extraction - Cleaned price: {price}")
        stock = (
            True
            if response.css("div.product-short-info td.product-status::text")
            .get()
            and response.css("div.product-short-info td.product-status::text")
            .get()
            .lower()
            == "in stock"
            else False
        )
        
        # Overview: join all text from the overview list using the provided selector
        overview_list = response.css('#product > div > div.short-description > ul *::text').getall()
        overview = '\n'.join([t.strip() for t in overview_list if t.strip()]) if overview_list else None
        # Description: join all text from the description section using the provided selector
        description_list = response.css('#description > div.full-description *::text').getall()
        description = '\n'.join([t.strip() for t in description_list if t.strip()]) if description_list else None

        # Create item
        item = ProductItem(
            name=name,
            store_id=store.id,
            price=price,
            stock=stock,
            url=response.url,
            rating=0,
            image_src=response.css("img.main-img::attr(src)").get(),
            description=description,
            overview=overview
        )
        
        yield item

    def clean_price(self, price_str):
        """Clean the price string and return an integer value."""
        if price_str:
            cleaned_price = re.sub(r"\D", "", price_str.strip())
            return int(cleaned_price) if cleaned_price else None
        return None


class StartechSpider(scrapy.Spider):
    name = "startech"
    allowed_domains = ["startech.com.bd"]

    def start_requests(self):
        search_term = getattr(self, "search_term", None)
        if not search_term:
            self.log(
                "No search term provided. Use -a search_term='product_name' to search."
            )
            return

        self.search_words = search_term.lower().split()
        search_url = f"https://www.startech.com.bd/product/search?search={search_term}"
        yield scrapy.Request(url=search_url, callback=self.parse)

    def parse(self, response):
        products = response.css("div.p-item")
        store = Shop.objects.get(name="Startech")
        product_count = 0

        for product in products:
            if product_count >= 2:
                break

            title_element = product.css("h4.p-item-name a::text").get()
            if not title_element or not self.title_contains_search_words(title_element.strip()):
                continue

            raw_price = product.css("div.p-item-price span::text").get()
            cleaned_price = self.clean_price(raw_price)

            item = SearchResultItem(
                search_id=self.search_obj.id,
                title=title_element.strip(),
                price=cleaned_price,
                url=response.urljoin(product.css("div.p-item-img a::attr(href)").get()),
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
            cleaned_price = re.sub(r"\D", "", price_str.strip())
            return int(cleaned_price) if cleaned_price else None
        return None
