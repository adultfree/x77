# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class TopicItem(scrapy.Item):
    # define the fields for your item here like:
    topic = scrapy.Field()
    link = scrapy.Field()
    datetime = scrapy.Field()


class TopicContentItem(scrapy.Item):
    image_urls = scrapy.Field()
    images = scrapy.Field()
    dirname = scrapy.Field()
    context = scrapy.Field()
    torrents = scrapy.Field()
