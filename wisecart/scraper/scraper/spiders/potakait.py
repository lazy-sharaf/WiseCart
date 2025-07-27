import re
import scrapy
from shops.models import Shop
from scraper.scraper.items import ProductItem, SearchResultItem


class PotakaitProductSpider(scrapy.Spider):
    name = "potakait_product"
    allowed_domains = ["potakait.com"]

    def start_requests(self):
        url = getattr(self, "url", None)
        print(f"PotakaitProductSpider start_requests called with url: {url}")
        if not url:
            self.log(
                "No URL provided. Use -a url='https://potakait.com/product-name' to search."
            )
            return
        yield scrapy.Request(
            url=url,
            callback=self.parse,
            headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36"}
        )

    def parse(self, response):
        print(f"PotakaitProductSpider parse called, response status: {response.status}, url: {response.url}")
        # Use precise selectors for the main product only
        name = response.css('#product > div > h1::text').get()
        name = name.strip() if name else None
        print(f"PotakaitProductSpider: name={name}")
        store = Shop.objects.get(name="Potakait")
        price = self.clean_price(
            response.css('#product > div > div.price-wrapper > span.special::text').get()
        )
        print(f"PotakaitProductSpider: price={price}")
        stock = bool(response.css("button#buy-now"))
        print(f"PotakaitProductSpider: stock={stock}")
        image_src = response.css('#main-image::attr(src)').get()
        print(f"PotakaitProductSpider: image_src={image_src}")
        # Overview: join all text from the overview list
        overview_list = response.css('#product > div > div.product-details__short-description > div > ul *::text').getall()
        overview = '\n'.join([t.strip() for t in overview_list if t.strip()]) if overview_list else None
        print(f"PotakaitProductSpider: overview={overview}")
        # Description: join all text from the description div
        description_list = response.css('#description > div > div *::text').getall()
        description = '\n'.join([t.strip() for t in description_list if t.strip()]) if description_list else None
        print(f"PotakaitProductSpider: description={description}")

        # Create item
        item = ProductItem(
            name=name,
            store_id=store.id,
            price=price,
            stock=stock,
            url=response.url,
            rating=0,
            image_src=image_src,
            description=description,
            overview=overview
        )

        print(f"PotakaitProductSpider: Created item with data: {item}")
        yield item

    def clean_price(self, price_str):
        """Clean the price string and return an integer value."""
        if price_str:
            cleaned_price = re.sub(r"\D", "", price_str.strip())
            return int(cleaned_price) if cleaned_price else None
        return None


class PotakaitSpider(scrapy.Spider):
    name = "potakait"
    allowed_domains = ["potakait.com"]

    def __init__(self, search_term=None, search_obj=None, *args, **kwargs):
        print("PotakaitSpider __init__ called")
        super().__init__(*args, **kwargs)
        self.search_obj = search_obj
        self.search_words = search_term.lower().split() if search_term else []

    def start_requests(self):
        print("PotakaitSpider start_requests called")
        search_term = getattr(self, "search_words", None)
        if not self.search_words:
            self.log(
                "No search term provided. Use -a search_term='product_name' to search."
            )
            return
        # Correct Potakait search URL pattern
        search_url = f"https://potakait.com/product/search?search={'+'.join(self.search_words)}"
        print(f"PotakaitSpider search_url: {search_url}")
        yield scrapy.Request(
            url=search_url,
            callback=self.parse,
            headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36"}
        )

    def parse(self, response):
        print(f"PotakaitSpider parse called, response status: {response.status}, url: {response.url}")
        products = response.css(".product-item.extra")
        store = Shop.objects.get(name="Potakait")
        product_count = 0

        if not products:
            print("PotakaitSpider: No products found on search page.")
        else:
            print(f"PotakaitSpider: Found {len(products)} products on search page.")
        print(f"PotakaitSpider: search_obj={self.search_obj}")

        for product in products:
            if product_count >= 2:
                break

            title_element = product.css(".product-info .title a::text").get()
            if not title_element or not self.title_contains_search_words(title_element.strip()):
                continue

            raw_price = product.css(".price-info .price::text").get()
            cleaned_price = self.clean_price(raw_price)

            print(f"PotakaitSpider: Yielding SearchResultItem for title={title_element.strip()}, search_id={getattr(self.search_obj, 'id', None)}")

            item = SearchResultItem(
                search_id=getattr(self.search_obj, 'id', None),
                title=title_element.strip(),
                price=cleaned_price,
                url=response.urljoin(product.css("a::attr(href)").get()),
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