# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class TopicItem(scrapy.Item):
    topic = scrapy.Field()
    link = scrapy.Field()


class ImageItem(scrapy.Item):
    referer = scrapy.Field()
    images = scrapy.Field()
    dirpath = scrapy.Field()
    context = scrapy.Field()


class FileItem(scrapy.Item):
    referer = scrapy.Field()
    files = scrapy.Field()
    filenames = scrapy.Field()
    dirpath = scrapy.Field()
