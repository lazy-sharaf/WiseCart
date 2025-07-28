import scrapy
import re
import json
from scraper.scraper.items import ProductItem, SearchResultItem
from shops.models import Shop
from search.models import Search


class SumashTechProductSpider(scrapy.Spider):
    name = "sumashtech_product"
    allowed_domains = ["sumashtech.com"]

    def __init__(self, url=None, *args, **kwargs):
        super(SumashTechProductSpider, self).__init__(*args, **kwargs)
        self.start_urls = [url] if url else []

    def parse(self, response):
        try:
            store = Shop.objects.get(slug="sumashtech")
        except Shop.DoesNotExist:
            store = Shop.objects.get(name="Sumash Tech")

        # Extract product details - using correct selectors from manual analysis
        # Title selector from manual analysis: div.product__widget > div.main-info > div > h1
        title = response.css('div.product__widget > div.main-info > div > h1::text').get()
        if not title:
            title = response.css('h1::text').get()
        
        # Extract price - using the exact selector from manual analysis
        # First try to get the price from the <b> tag inside the div
        price_text = response.css('div.single__product_wrapper > div > div > div:nth-child(2) > div > div.product__widget > div.main-info > span:nth-child(2) > div > div b::text').get()
        
        # If that fails, try getting it from the div directly
        if not price_text:
            price_text = response.css('div.single__product_wrapper > div > div > div:nth-child(2) > div > div.product__widget > div.main-info > span:nth-child(2) > div > div::text').get()
        
        # If both fail, try a simpler selector
        if not price_text:
            price_text = response.css('div.product__sale_price b::text').get()
        
        # Clean price using the same logic as search page
        if price_text:
            # First, remove currency symbol and whitespace
            price_text = re.sub(r'[৳$₹€£]', '', price_text).strip()
            
            # Remove commas from the number
            price_text_no_commas = price_text.replace(',', '')
            
            try:
                # Convert directly to float
                price = float(price_text_no_commas)
            except ValueError:
                # If direct conversion fails, try to extract just the numbers
                price_matches = re.findall(r'\d+', price_text_no_commas)
                if price_matches:
                    price = float(price_matches[0])
                else:
                    price = 0
        else:
            price = 0

        # Extract image from manual analysis: div.d-lg-block > img
        image_src = response.css('div.d-lg-block > img::attr(src)').get()
        if not image_src:
            image_src = response.css('img::attr(src)').get()

        # Extract description from manual analysis
        description = response.css('div.container > div > div.col-12.col-sm-12.col-md-12.col-lg-8.order-2.order-sm-2.order-lg-1.order-md-2 > div:nth-child(2) *::text').getall()
        description = ' '.join(description).strip() if description else ""
        
        if not description:
            # Try alternative selectors
            description = response.css('div.col-12.col-sm-12.col-md-12.col-lg-8 > div:nth-child(2) *::text').getall()
            description = ' '.join(description).strip() if description else ""
        
        if not description:
            description = response.css('p::text').get() or ""

        # Extract overview from manual analysis
        overview = response.css('div.single__product_wrapper > div > div > div:nth-child(2) > div > div.product__widget > div.product__short_description > ul li::text').getall()
        overview = ' | '.join(overview).strip() if overview else ""
        
        if not overview:
            # Try alternative selectors
            overview = response.css('div.product__widget > div.product__short_description > ul li::text').getall()
            overview = ' | '.join(overview).strip() if overview else ""
        
        if not overview:
            overview = response.css('div.product__short_description ul li::text').getall()
            overview = ' | '.join(overview).strip() if overview else ""

        item = ProductItem(
            store_id=store.id,
            name=title.strip() if title else "",
            price=price,
            stock=True if price > 0 else False,
            url=response.url,
            image_src=image_src,
            description=description.strip() if description else "",
            overview=overview.strip() if overview else "",
        )

        yield item


class SumashTechSpider(scrapy.Spider):
    name = "sumashtech"
    allowed_domains = ["sumashtech.com"]

    def __init__(self, search_term=None, search_obj=None, *args, **kwargs):
        super(SumashTechSpider, self).__init__(*args, **kwargs)
        self.search_term = search_term
        self.search_obj = search_obj
        if search_term:
            self.search_words = search_term.lower().split()
        else:
            self.search_words = []

    def start_requests(self):
        if not self.search_words:
            self.log(
                "No search term provided. Use -a search_term='product_name' to search."
            )
            return
        
        search_url = f"https://www.sumashtech.com/query/{'%20'.join(self.search_words)}"
        yield scrapy.Request(url=search_url, callback=self.parse)

    def parse(self, response):
        try:
            store = Shop.objects.get(slug="sumashtech")
        except Shop.DoesNotExist:
            store = Shop.objects.get(name="Sumash Tech")
        
        # Find product cards - using correct selectors from manual analysis
        products = response.css('div.product__items > div > div')

        product_count = 0
        for product in products:
            if product_count >= 2:
                break
            
            # Correct selectors from manual analysis
            title_element = product.css('div > div > a > h3::text').get()
            
            if not title_element:
                continue
                
            if not self.title_contains_search_words(title_element.strip()):
                continue
            
            # Price selector - try multiple approaches
            raw_price = product.css('div.product__price > div > strong::text').get()
            if not raw_price:
                raw_price = product.css('div.product__price::text').get()
            if not raw_price:
                raw_price = product.css('.product__price::text').get()
            if not raw_price:
                raw_price = product.css('strong::text').get()
            
            cleaned_price = self.clean_price(raw_price)
            product_url = product.css('div > div > a::attr(href)').get()
            
            item = SearchResultItem(
                search_id=self.search_obj.id if self.search_obj else None,
                title=title_element.strip(),
                price=cleaned_price,
                url=response.urljoin(product_url),
                store_id=store.id,
                stock=bool(cleaned_price and cleaned_price > 0),
                rating=0,
            )
            product_count += 1
            yield item

    def clean_price(self, price_text):
        if not price_text:
            return 0
        
        # Remove currency symbols (৳, $, etc.) and extra spaces
        price_text = re.sub(r'[৳$₹€£]', '', price_text).strip()
        
        # Handle different price formats
        # First, remove commas from the text
        price_text_no_commas = price_text.replace(',', '')
        
        # Look for any number in the text
        number_matches = re.findall(r'(\d+)', price_text_no_commas)
        
        if number_matches:
            # Take the first number found
            price = float(number_matches[0])
            return price
        
        return 0

    def title_contains_search_words(self, title):
        title_lower = title.lower()
        matching_words = sum(1 for word in self.search_words if word in title_lower)
        
        # More strict matching logic:
        # 1. If search has 1-2 words, require all words to match
        # 2. If search has 3+ words, require at least 50% of words to match
        # 3. Always check if the first word (usually brand) matches
        if len(self.search_words) <= 2:
            required_matches = len(self.search_words)
        else:
            required_matches = max(2, int(len(self.search_words) * 0.5))
        
        # Special check: if first word is a brand name, it should match
        first_word_matches = self.search_words[0] in title_lower if self.search_words else False
        
        # Return true if we have enough matches OR if it's a very specific brand match
        return matching_words >= required_matches or (first_word_matches and matching_words >= 2) 