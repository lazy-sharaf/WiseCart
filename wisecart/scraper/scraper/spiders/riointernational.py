import scrapy
import re
from scraper.scraper.items import ProductItem, SearchResultItem
from shops.models import Shop
from search.models import Search


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

        print(f"Rio International product spider: Processing URL: {response.url}")
        print(f"Rio International product spider: Response status: {response.status}")

        # Extract product details - try multiple selectors for title
        title = response.css('h1::text').get()
        if not title:
            title = response.css('.product-title::text').get()
        if not title:
            title = response.css('[class*="title"]::text').get()
        print(f"Rio International product spider: Title found: {title}")
        
        # Extract price - try multiple selectors
        price_text = response.css('.product-price ins::text').get()
        if not price_text:
            price_text = response.css('ins.new-price::text').get()
        if not price_text:
            price_text = response.css('[class*="price"]::text').get()
        print(f"Rio International product spider: Price text found: {price_text}")
        
        # Clean price
        if price_text:
            # Remove currency symbol and whitespace
            price_text = re.sub(r'[৳$₹€£]', '', price_text).strip()
            print(f"Rio International product spider: Price text after removing currency: {price_text}")
            
            # Remove commas from the number
            price_text_no_commas = price_text.replace(',', '')
            print(f"Rio International product spider: Price text after removing commas: {price_text_no_commas}")
            
            try:
                # Convert directly to float
                price = float(price_text_no_commas)
                print(f"Rio International product spider: Final price: {price}")
            except ValueError:
                # If direct conversion fails, try to extract just the numbers
                price_matches = re.findall(r'\d+', price_text_no_commas)
                if price_matches:
                    price = float(price_matches[0])
                    print(f"Rio International product spider: Extracted price from numbers: {price}")
                else:
                    price = 0
                    print("Rio International product spider: Could not extract price, using 0")
        else:
            price = 0
            print("Rio International product spider: No price text found, using 0")

        # Extract main product image using the exact selector provided
        image_src = response.css('#swiper-wrapper-9bb561610aeb82103 > div.swiper-slide.swiper-slide-active > div > img:nth-child(1)::attr(src)').get()
        if not image_src:
            # Fallback: try a more generic swiper selector
            image_src = response.css('[id*="swiper-wrapper"] > div.swiper-slide.swiper-slide-active > div > img:nth-child(1)::attr(src)').get()
        if not image_src:
            # Fallback: try any active swiper slide
            image_src = response.css('div.swiper-slide.swiper-slide-active img::attr(src)').get()
        if not image_src:
            # Final fallback: product media
            image_src = response.css('figure.product-media img::attr(src)').get()
        
        # Make sure image URL is absolute
        if image_src and not image_src.startswith('http'):
            image_src = response.urljoin(image_src)
            
        print(f"Rio International product spider: Image src: {image_src}")

        # Set description to None for Rio International
        description = None
        print(f"Rio International product spider: Description: None")

        # Extract overview - try multiple selectors
        overview = response.css('.product-short-desc *::text').getall()
        if not overview:
            overview = response.css('.product-summary *::text').getall()
        if not overview:
            overview = response.css('[class*="short"] *::text').getall()
        overview = ' '.join(overview).strip() if overview else ""
        print(f"Rio International product spider: Overview: {overview[:100] if overview else 'None'}")
        
        # Set all Rio International products to IN STOCK by default
        stock = True
        print(f"Rio International product spider: Stock set to IN STOCK (default)")

        item = ProductItem(
            store_id=store.id,
            name=title.strip() if title else "",
            price=price,
            stock=stock,  # Use the stock detection result directly
            url=response.url,
            image_src=image_src,
            description=description,
            overview=overview,
        )

        print(f"Rio International product spider: Yielding product: {title}")
        yield item


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
        
        search_url = f"https://riointernational.com.bd/search/product?keyword={'%20'.join(self.search_words)}"
        print(f"Rio International spider: Processing URL: {search_url}")
        yield scrapy.Request(url=search_url, callback=self.parse)

    def parse(self, response):
        try:
            store = Shop.objects.get(slug="riointernational")
        except Shop.DoesNotExist:
            store = Shop.objects.get(name="Rio International")
        
        print(f"Rio International spider: Store found: {store.name} (ID: {store.id})")
        print(f"Rio International spider: Search words: {self.search_words}")
        print(f"Rio International spider: Response URL: {response.url}")
        print(f"Rio International spider: Response status: {response.status}")

        # Find product containers using correct selector from JS analysis
        products = response.css('.product')
        print(f"Rio International spider: Found {len(products)} products on search page")
        
        # Debug: Try different selectors to see what's available
        debug_selectors = [
            'div.product',
            '.product.style-2',
            'div',
            '[class*="product"]'
        ]
        
        for selector in debug_selectors:
            elements = response.css(selector)
            print(f"Rio International spider: Selector '{selector}' found {len(elements)} elements")
            if elements and selector == 'div':
                break  # Don't print too many divs
                
        # If no products found, let's see the page content
        if len(products) == 0:
            page_text = response.css('body *::text').getall()
            page_text_sample = ' '.join(page_text)[:500]
            print(f"Rio International spider: Page content sample: {page_text_sample}")
            
            # Check if we can find product names in the text
            if 'redmi' in page_text_sample.lower():
                print("Rio International spider: Found 'redmi' in page text - products exist but selector is wrong")
            else:
                print("Rio International spider: No 'redmi' found in page text - might be no results")

        product_count = 0
        for product in products:
            if product_count >= 2:
                break
            
            # Extract product details using correct selectors from JS analysis
            title_element = product.css('h4.product-name a::text').get()
            print(f"Rio International spider: Found product with title: {title_element}")
            
            if not title_element:
                print("Rio International spider: No title found, skipping")
                continue
                
            if not self.title_contains_search_words(title_element.strip()):
                print("Rio International spider: Title doesn't match search words, skipping")
                continue
            
            # Extract price using correct selector from JS analysis
            raw_price = product.css('.product-price ins.new-price::text').get()
            print(f"Rio International spider: Raw price found: {raw_price}")
            cleaned_price = self.clean_price(raw_price)
            
            # Extract product URL using correct selector from JS analysis
            product_url = product.css('h4.product-name a::attr(href)').get()
            print(f"Rio International spider: Product URL: {product_url}")
            
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
            print(f"Rio International spider: Yielding product: {title_element.strip()}")

    def clean_price(self, price_text):
        if not price_text:
            return 0
        
        print(f"Rio International spider: Cleaning price text: '{price_text}'")
        
        # Remove currency symbols (৳) and extra spaces
        price_text = re.sub(r'[৳$₹€£]', '', price_text).strip()
        
        # Handle different price formats
        price_text_no_commas = price_text.replace(',', '')
        
        # Look for any number in the text
        number_matches = re.findall(r'(\d+)', price_text_no_commas)
        
        if number_matches:
            # Take the first number found
            price = float(number_matches[0])
            print(f"Rio International spider: Extracted price: {price}")
            return price
        
        print(f"Rio International spider: No numbers found in text: '{price_text}'")
        return 0

    def title_contains_search_words(self, title):
        title_lower = title.lower()
        matching_words = sum(1 for word in self.search_words if word in title_lower)
        print(f"Rio International spider: Checking product '{title}' against search words {self.search_words}")
        print(f"Rio International spider: Matching words: {matching_words}")
        # Be lenient - require at least 1 matching word
        return matching_words >= 1 