import os

from x77 import settings
from x77.items import *
from x77.spiders import need_refresh


class EastBeautySpider(scrapy.Spider):
    name = "east_beauty"
    start_urls = ["http://%s/bbs/thread.php?fid=6&page=%d" % (settings.HOST, i) for i in range(*settings.PAGE_RANGE)]

    def parse(self, response):
        if need_refresh(response.text):
            yield scrapy.Request(response.url, callback=self.parse, dont_filter=True)
        else:
            item = TopicItem()
            head = response.xpath('//head/base/@href').extract_first()
            name = response.css('.subject_t').xpath('text()').extract()
            ref = response.css('.subject_t').xpath('@href').extract()
            item['topic'] = name
            item['link'] = [head + n for n in ref]

            for (topic, url) in zip(item['topic'], item['link']):
                yield scrapy.Request(url, callback=self.parse_item)

    def parse_item(self, response):
        if need_refresh(response.text):
            yield scrapy.Request(response.url, callback=self.parse_item, dont_filter=True)
        else:
            item = TopicContentItem()
            item['image_urls'] = response.xpath('//div[@id="read_tpc"]/*/img/@src | //div[@id="read_tpc"]/img/@src').extract()
            item['dirname'] = os.path.join("唯美清纯", response.xpath('//h1[@id="subject_tpc"]/text()').extract()[1].replace('/', '.').replace('?', '.').replace(':', '.'))
            yield item
