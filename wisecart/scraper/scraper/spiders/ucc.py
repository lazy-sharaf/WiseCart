import re
import scrapy
from shops.models import Shop
from scraper.scraper.items import ProductItem, SearchResultItem

class UCCSpider(scrapy.Spider):
    name = "ucc"
    allowed_domains = ["ucc.com.bd"]

    def __init__(self, search_term=None, search_obj=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.search_obj = search_obj
        self.search_words = search_term.lower().split() if search_term else []

    def start_requests(self):
        if not self.search_words:
            self.log("No search term provided. Use -a search_term='product_name' to search.")
            return
        # UCC search URL pattern: /index.php?route=product/search&search=...&description=true
        search_url = f"https://www.ucc.com.bd/index.php?route=product/search&search={'+'.join(self.search_words)}&description=true"
        print(f"UCCSpider search_url: {search_url}")
        yield scrapy.Request(
            url=search_url,
            callback=self.parse,
            headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36"}
        )

    def parse(self, response):
        print(f"UCCSpider parse called, response status: {response.status}, url: {response.url}")
        print(f"UCCSpider: search_obj={self.search_obj}")
        # Use provided selector for product container
        products = response.css('#content > div.main-products-wrapper > div.main-products.product-grid > div')
        store = Shop.objects.get(name="UCC")
        product_count = 0
        if not products:
            print("UCCSpider: No products found on search page.")
        else:
            print(f"UCCSpider: Found {len(products)} products on search page.")
        for product in products:
            if product_count >= 2:
                break
            # Title
            title = product.css('div.caption > div.name a::text').get()
            title = title.strip() if title else None
            # URL
            url = product.css('div.caption > div.name a::attr(href)').get()
            print(f"UCCSpider: extracted title={title}, url={url}")
            # Price
            price = product.css('div.caption > div.buttons-wrapper > div.price > div > span::text').get()
            price = self.clean_price(price)
            # Image
            image = product.css('div.image > a > div::attr(data-bg)').get() or product.css('div.image > a > img::attr(src)').get()
            overview = None
            description = None
            if title and url:
                item = SearchResultItem(
                    title=title,
                    price=price,
                    url=url,
                    store_id=store.id,
                    search_id=self.search_obj.id if self.search_obj else None,
                )
                print(f"UCCSpider yielding SearchResultItem: {item}")
                print(f"UCCSpider yielding dict: {dict(item)}")
                product_count += 1
                yield item

    @staticmethod
    def clean_price(price):
        if not price:
            return None
        price = re.sub(r"[^0-9.]", "", price)
        try:
            return float(price)
        except Exception:
            return None

class UCCProductSpider(scrapy.Spider):
    name = "ucc_product"
    allowed_domains = ["ucc.com.bd"]
    custom_settings = {
        "ITEM_PIPELINES": {"scraper.scraper.pipelines.DjangoPipeline": 300}
    }

    def __init__(self, url=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.url = url

    def start_requests(self):
        url = getattr(self, "url", None)
        print(f"UCCProductSpider start_requests called with url: {url}")
        if not url:
            self.log("No URL provided. Use -a url='https://www.ucc.com.bd/product-name' to search.")
            return
        yield scrapy.Request(
            url=url,
            callback=self.parse,
            headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36"}
        )

    def parse(self, response):
        print(f"UCCProductSpider parse called, response status: {response.status}, url: {response.url}")
        # Name
        name = response.css('#product > div.title.page-title::text').get()
        name = name.strip() if name else None
        print(f"UCCProductSpider: name={name}")
        store = Shop.objects.get(name="UCC")
        # Price
        price = response.css('#product > div.product-price-group > div > div.price-group > div::text').get()
        price = self.clean_price(price)
        print(f"UCCProductSpider: price={price}")
        # Stock: Check for in-stock class using the specific selector
        in_stock_element = response.css('#product > div.product-stats > ul > li.product-stock.in-stock > b').get()
        stock = bool(in_stock_element)
        print(f"UCCProductSpider: stock={stock} (in_stock_element found: {in_stock_element is not None})")
        # Main image: select the first image in the product-image container
        image = response.css('div.product-image img::attr(src)').get()
        print(f"UCCProductSpider: image={image}")
        # Overview: join all text from the overview list
        overview_list = response.css('#product > div.button-group-page > div.short_description_product-page > div > ul *::text').getall()
        overview = '\n'.join([t.strip() for t in overview_list if t.strip()]) if overview_list else None
        print(f"UCCProductSpider: overview={overview}")
        # Description: join all text from the description div (using flexible selector)
        description_list = response.css('#blocks-6881f58164c28-tab-1 > div > div.block-wrapper > div *::text').getall()
        description = '\n'.join([t.strip() for t in description_list if t.strip()]) if description_list else None
        print(f"UCCProductSpider: description={description}")
        # Yield ProductItem
        try:
            print("UCCProductSpider: About to create ProductItem")
            item = ProductItem()
            print("UCCProductSpider: ProductItem created successfully")
            item["name"] = name
            item["price"] = price
            item["stock"] = stock
            item["image_src"] = image
            item["overview"] = overview
            item["description"] = description
            item["url"] = self.url  # Always use the original URL passed to the spider
            item["store_id"] = 8  # UCC shop id, update if different in your DB
            print(f"UCCProductSpider: yielding ProductItem: {item}")
            yield item
            print("UCCProductSpider: Successfully yielded ProductItem")
        except Exception as e:
            print(f"UCCProductSpider: ERROR creating/yielding ProductItem: {e}")
            import traceback
            traceback.print_exc()

    @staticmethod
    def clean_price(price):
        if not price:
            return None
        price = re.sub(r"[^0-9.]", "", price)
        try:
            return float(price)
        except Exception:
            return None 