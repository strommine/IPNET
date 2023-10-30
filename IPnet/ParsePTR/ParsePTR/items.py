# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class WebDataItem(scrapy.Item):
    ipv6 = scrapy.Field()
    query = scrapy.Field()
    urls = scrapy.Field()
    web_texts = scrapy.Field()
