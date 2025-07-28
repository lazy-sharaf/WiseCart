import scrapy
import re
from scraper.scraper.items import ProductItem, SearchResultItem
from shops.models import Shop


class RioInternationalProductSpider(scrapy.Spider):
    name = "riointernational_product"
    allowed_domains = ["riointernational.com.bd"]

    def __init__(self, url=None, *args, **kwargs):
        super(RioInternationalProductSpider, self).__init__(*args, **kwargs)
        self.start_urls = [url] if url else []

    def parse(self, response):
        try:
            store = Shop.objects.get(slug="riointernational")
        except Shop.DoesNotExist:
            store = Shop.objects.get(name="Rio International")

        # Extract product details
        # Multiple fallback selectors for title
        title = response.css('body > div.page-wrapper > main > main > div > div > div > div > div.product.product-single.row > div:nth-child(2) > div > h1::text').get()
        if not title:
            title = response.css('h1::text').get()
        if not title:
            title = response.css('.product-title::text').get()
        if not title:
            title = response.css('.pd-title::text').get()
        
        # Multiple fallback selectors for price
        price_text = response.css('body > div.page-wrapper > main > main > div > div > div > div > div.product.product-single.row > div:nth-child(2) > div > div.pd-details-info-top > div.product-price > ins::text').get()
        if not price_text:
            price_text = response.css('div.product-price ins::text').get()
        if not price_text:
            price_text = response.css('ins.new-price::text').get()
        if not price_text:
            price_text = response.css('.price::text').get()
        
        # Clean price
        if price_text:
            # Remove currency symbols (৳, $, etc.) and extra spaces
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

        # Multiple fallback selectors for main image
        image_src = response.css('#swiper-wrapper-9bb561610aeb82103 > div.swiper-slide.swiper-slide-active > div > img:nth-child(1)::attr(src)').get()
        if not image_src:
            image_src = response.css('#swiper-wrapper-10a66d980edfa4ccd > div.swiper-slide.swiper-slide-active > div > img:nth-child(1)::attr(src)').get()
        if not image_src:
            image_src = response.css('div.swiper-slide.swiper-slide-active > div > img::attr(src)').get()
        if not image_src:
            image_src = response.css('img.main-image::attr(src)').get()
        if not image_src:
            image_src = response.css('img::attr(src)').get()
        
        # Description set to None as per user request
        description = None
        
        # Multiple fallback selectors for overview
        overview = response.css('body > div.page-wrapper > main > main > div > div > div > div > div.product.product-single.row > div:nth-child(2) > div > div.pd-details-info-top > div.product-short-desc *::text').getall()
        overview = self.clean_text_content(overview) if overview else ""
        
        if not overview:
            overview = response.css('div.product-short-desc *::text').getall()
            overview = self.clean_text_content(overview) if overview else ""
        
        # Stock set to IN STOCK by default as per user request
        stock = True
        
        item = ProductItem(
            store_id=store.id,
            name=title.strip() if title else "",
            price=price,
            stock=stock,
            url=response.url,
            image_src=image_src,
            description=description,
            overview=overview.strip() if overview else "",
        )

        yield item

    def clean_text_content(self, text_list):
        """Clean and join text content from CSS selector results"""
        if not text_list:
            return ""
        cleaned_texts = [text.strip() for text in text_list if text.strip()]
        return ' | '.join(cleaned_texts)


class RioInternationalSpider(scrapy.Spider):
    name = "riointernational"
    allowed_domains = ["riointernational.com.bd"]

    def __init__(self, search_term=None, search_obj=None, *args, **kwargs):
        super(RioInternationalSpider, self).__init__(*args, **kwargs)
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
        
        search_url = f"https://riointernational.com.bd/search/product?keyword={'+'.join(self.search_words)}"
        yield scrapy.Request(url=search_url, callback=self.parse)

    def parse(self, response):
        try:
            store = Shop.objects.get(slug="riointernational")
        except Shop.DoesNotExist:
            store = Shop.objects.get(name="Rio International")
        
        # Find product cards using the provided selector
        products = response.css('.product')
        
        # Debug: try multiple selectors if first one doesn't work
        if not products:
            selectors_to_try = [
                '#product_wrapper > div.product-wrapper.category-product-all > div',
                '.product-wrapper > div',
                '.product-item',
                '[class*="product"]'
            ]
            
            for selector in selectors_to_try:
                elements = response.css(selector)
                if elements:
                    break
            
            # Check if search term appears in page text (for debugging)
            page_text = response.text.lower()
            page_text_sample = page_text[:500] + '...' if len(page_text) > 500 else page_text
            
            if any(word in page_text for word in self.search_words):
                pass  # Products exist but selector is wrong
            else:
                pass  # Might be no results

        product_count = 0
        for product in products:
            if product_count >= 2:
                break
            
            # Extract product title using the provided selector
            title_element = product.css('h4.product-name a::text').get()
            
            if not title_element:
                continue
                
            if not self.title_contains_search_words(title_element.strip()):
                continue
            
            # Extract price using the provided selector
            raw_price = product.css('.product-price ins.new-price::text').get()
            
            cleaned_price = self.clean_price(raw_price)
            
            # Extract product URL using the provided selector
            product_url = product.css('h4.product-name a::attr(href)').get()
            
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
        return matching_words >= 1 