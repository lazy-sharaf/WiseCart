# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class ProductItem(scrapy.Item):
    # define the fields for your item here like:
    name = scrapy.Field()
    store_id = scrapy.Field()
    price = scrapy.Field()
    stock = scrapy.Field()
    url = scrapy.Field()
    rating = scrapy.Field()
    image_src = scrapy.Field()
    description = scrapy.Field()
    overview = scrapy.Field()


class SearchResultItem(scrapy.Item):
    search_id = scrapy.Field()
    title = scrapy.Field()
    price = scrapy.Field()
    url = scrapy.Field()
    store_id = scrapy.Field()
    stock = scrapy.Field()
    rating = scrapy.Field()
