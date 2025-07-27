import re
import scrapy
from shops.models import Shop
from scraper.scraper.items import ProductItem, SearchResultItem

class TechLandProductSpider(scrapy.Spider):
    name = "techland_product"
    allowed_domains = ["techlandbd.com"]

    def start_requests(self):
        url = getattr(self, "url", None)
        print(f"TechLandProductSpider start_requests called with url: {url}")
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
        print(f"TechLandProductSpider parse called, response status: {response.status}, url: {response.url}")
        name = response.css('body > div.min-h-screen.bg-gray-100 > main > div.flex.flex-col.lg\\:flex-row.gap-4.sm\\:gap-6 > div.lg\\:w-3\\/4.order-1.lg\\:order-2 > div.bg-white.rounded-md.shadow-md.p-3.sm\\:p-4.md\\:p-6.mb-4.sm\\:mb-6 > div > div.lg\\:w-3\\/5 > h1::text').get()
        name = name.strip() if name else None
        print(f"TechLandProductSpider: name={name}")
        store = Shop.objects.get(name="TechLand")
        price = self.clean_price(
            response.css('body > div.min-h-screen.bg-gray-100 > main > div.flex.flex-col.lg\\:flex-row.gap-4.sm\\:gap-6 > div.lg\\:w-3\\/4.order-1.lg\\:order-2 > div.bg-white.rounded-md.shadow-md.p-3.sm\\:p-4.md\\:p-6.mb-4.sm\\:mb-6 > div > div.lg\\:w-3\\/5 > div.mt-2.sm\\:mt-6.grid.grid-cols-1.sm\\:grid-cols-1.md\\:grid-cols-2.gap-3.sm\\:gap-4 > div:nth-child(1) > div.flex.items-center.flex-wrap > span.text-lg.sm\\:text-xl.lg\\:text-2xl.font-bold.text-\\[\\#1c4289\\]::text').get()
        )
        print(f"TechLandProductSpider: price={price}")
        stock_section_html = response.css('div.pt-2.text-sm').get()
        print(f"TechLandProductSpider: stock_section_html={stock_section_html}")
        stock_text = response.css('body > div.min-h-screen.bg-gray-100 > main > div.flex.flex-col.lg\\:flex-row.gap-4.sm\\:gap-6 > div.lg\\:w-3\\/4.order-1.lg\\:order-2 > div.bg-white.rounded-md.shadow-md.p-3.sm\\:p-4.md\\:p-6.mb-4.sm\\:mb-6 > div > div.lg\\:w-3\\/5 > div.mt-3.sm\\:mt-4.flex.flex-wrap.gap-1.sm\\:gap-2 > div:nth-child(1) span::text').get()
        print(f"TechLandProductSpider: stock_text={stock_text}")
        stock = stock_text and ('in stock' in stock_text.lower())
        print(f"TechLandProductSpider: stock={stock}")
        image_src = response.css('#main-image::attr(src)').get()
        print(f"TechLandProductSpider: image_src={image_src}")
        # Overview: extract all <li> text from the overview div
        overview_list = response.css('div.text-xs.sm\\:text-sm.text-gray-600.break-words li::text').getall()
        overview = '\n'.join([t.strip() for t in overview_list if t.strip()]) if overview_list else None
        print(f"TechLandProductSpider: overview={overview}")
        description_list = response.css('#description-tab > div *::text').getall()
        description = '\n'.join([t.strip() for t in description_list if t.strip()]) if description_list else None
        print(f"TechLandProductSpider: description={description}")
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
        print(f"TechLandProductSpider: Created item with data: {item}")
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
        print("TechLandSpider __init__ called")
        super().__init__(*args, **kwargs)
        self.search_obj = search_obj
        self.search_words = search_term.lower().split() if search_term else []

    def start_requests(self):
        print("TechLandSpider start_requests called")
        if not self.search_words:
            self.log(
                "No search term provided. Use -a search_term='product_name' to search."
            )
            return
        search_url = f"https://www.techlandbd.com/search/advance/product/result/{'+'.join(self.search_words)}"
        print(f"TechLandSpider search_url: {search_url}")
        yield scrapy.Request(
            url=search_url,
            callback=self.parse,
            headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36"}
        )

    def parse(self, response):
        print(f"TechLandSpider parse called, response status: {response.status}, url: {response.url}")
        products = response.css('div.grid.grid-cols-2.md\:grid-cols-5.gap-4 > div')
        store = Shop.objects.get(name="TechLand")
        product_count = 0
        if not products:
            print("TechLandSpider: No products found on search page.")
        else:
            print(f"TechLandSpider: Found {len(products)} products on search page.")
        print(f"TechLandSpider: search_obj={self.search_obj}")
        for product in products:
            if product_count >= 2:
                break
            title_element = product.css('div.p-4.flex-grow > div > a::text').get()
            print(f"TechLandSpider: Raw title_element: {title_element}")
            if not title_element or not self.title_contains_search_words(title_element.strip()):
                print(f"TechLandSpider: Skipping product, title_element={title_element}, search_words={self.search_words}")
                continue
            raw_price = product.css('div.p-4.border-t.mt-auto span.text-lg.font-bold.text-red-600::text').get()
            print(f"TechLandSpider: Raw price: {raw_price}")
            product_url = product.css('div.p-4.flex-grow > div > a::attr(href)').get()
            print(f"TechLandSpider: Raw product_url: {product_url}")
            image_url = product.css('div > a > img::attr(src)').get()
            print(f"TechLandSpider: Raw image_url: {image_url}")
            stock_text = product.css('div.p-4.flex-grow > div.pt-2.text-sm > span::text').get()
            print(f"TechLandSpider: Raw stock_text: {stock_text}")
            cleaned_price = self.clean_price(raw_price)
            product_url = response.urljoin(product_url) if product_url else None
            # Stock logic: check for 'In Stock' in stock_text
            stock = stock_text and ("in stock" in stock_text.lower())
            print(f"TechLandSpider: Parsed stock: {stock}")
            print(f"TechLandSpider: Yielding SearchResultItem for title={title_element.strip()}, search_id={getattr(self.search_obj, 'id', None)}")
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