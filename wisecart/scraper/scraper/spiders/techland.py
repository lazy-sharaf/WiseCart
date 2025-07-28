import re
import scrapy
from shops.models import Shop
from scraper.scraper.items import ProductItem, SearchResultItem

class TechLandProductSpider(scrapy.Spider):
    name = "techland_product"
    allowed_domains = ["techlandbd.com"]

    def start_requests(self):
        url = getattr(self, "url", None)
        if not url:
            self.log(
                "No URL provided. Use -a url='https://www.techlandbd.com/product-name' to search."
            )
            return
        yield scrapy.Request(
            url=url,
            callback=self.parse,
            headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36"}
        )

    def parse(self, response):
        # Try multiple selectors for the product name
        name = response.css('h1.text-xl.sm\\:text-2xl.md\\:text-3xl.font-bold.text-gray-800::text').get()
        if not name:
            name = response.css('h1::text').get()
        if not name:
            name = response.css('.product-title::text').get()
        if not name:
            # Fallback - try any h1 tag
            name = response.css('h1::text').get()
        
        name = name.strip() if name else "TechLand Product"  # Fallback name if nothing found
        
        store = Shop.objects.get(name="TechLand")
        price = self.clean_price(
            response.css('span.text-lg.sm\\:text-xl.lg\\:text-2xl.font-bold.text-\\[\\#1c4289\\]::text').get()
        )
        
        stock_section_html = response.css('div.pt-2.text-sm').get()
        
        stock_text = response.css('span.text-green-600::text').get()
        if not stock_text:
            stock_text = response.css('span:contains("Stock")::text').get()
        
        stock = stock_text and ('in stock' in stock_text.lower())
        
        image_src = response.css('#main-image::attr(src)').get()
        if not image_src:
            image_src = response.css('img[alt*="product"]::attr(src)').get()
        
        # Overview: extract all <li> text from the overview div
        overview_list = response.css('div.text-xs.sm\\:text-sm.text-gray-600.break-words li::text').getall()
        overview = '\n'.join([t.strip() for t in overview_list if t.strip()]) if overview_list else None
        
        description_list = response.css('#description-tab > div *::text').getall()
        description = '\n'.join([t.strip() for t in description_list if t.strip()]) if description_list else None
        
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
        yield item

    def clean_price(self, price_str):
        if price_str:
            cleaned_price = re.sub(r"\D", "", price_str.strip())
            return int(cleaned_price) if cleaned_price else None
        return None

class TechLandSpider(scrapy.Spider):
    name = "techland"
    allowed_domains = ["techlandbd.com"]

    def __init__(self, search_term=None, search_obj=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.search_obj = search_obj
        self.search_words = search_term.lower().split() if search_term else []

    def start_requests(self):
        if not self.search_words:
            self.log(
                "No search term provided. Use -a search_term='product_name' to search."
            )
            return
        search_url = f"https://www.techlandbd.com/search/advance/product/result/{'+'.join(self.search_words)}"
        yield scrapy.Request(
            url=search_url,
            callback=self.parse,
            headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36"}
        )

    def parse(self, response):
        products = response.css('div.grid.grid-cols-2.md\:grid-cols-5.gap-4 > div')
        store = Shop.objects.get(name="TechLand")
        product_count = 0
        
        for product in products:
            if product_count >= 2:
                break
            title_element = product.css('div.p-4.flex-grow > div > a::text').get()
            if not title_element or not self.title_contains_search_words(title_element.strip()):
                continue
            raw_price = product.css('div.p-4.border-t.mt-auto span.text-lg.font-bold.text-red-600::text').get()
            product_url = product.css('div.p-4.flex-grow > div > a::attr(href)').get()
            image_url = product.css('div > a > img::attr(src)').get()
            stock_text = product.css('div.p-4.flex-grow > div.pt-2.text-sm > span::text').get()
            cleaned_price = self.clean_price(raw_price)
            product_url = response.urljoin(product_url) if product_url else None
            # Stock logic: check for 'In Stock' in stock_text
            stock = stock_text and ("in stock" in stock_text.lower())
            
            item = SearchResultItem(
                search_id=getattr(self.search_obj, 'id', None),
                title=title_element.strip(),
                price=cleaned_price,
                url=product_url,
                store_id=store.id,
                stock=stock,
                rating=0,
            )
            product_count += 1
            yield item
            
    def title_contains_search_words(self, title):
        title_lower = title.lower()
        return all(word in title_lower for word in self.search_words)
        
    def clean_price(self, price_str):
        if price_str:
            cleaned_price = re.sub(r"\D", "", price_str.strip())
            return int(cleaned_price) if cleaned_price else None
        return None 