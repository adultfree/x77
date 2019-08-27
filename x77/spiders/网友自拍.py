import os

from x77 import settings
from x77.items import *

from x77.spiders.spider import Spider


# 网友自拍
class SelfiePhotoSpider(Spider):
    name = "selfie_photo"
    page_range = (11, 12)
    # page_range = settings.PAGE_RANGE
    start_urls = ["http://%s/bbs/thread.php?fid=18&page=%d" % (settings.HOST, i) for i in range(*page_range)]

    def parse_page(self, response):
        item = self.get_topic_item(response)
        for (topic, url) in zip(item['topic'], item['link']):
            yield scrapy.Request(url, callback=self.parse_topic)

    def parse_item(self, response):
        item = ImageItem()
        item['referer'] = response.request.url
        item['images'] = response.xpath('//div[@id="read_tpc"]/*/img/@src | //div[@id="read_tpc"]/img/@src').extract()
        item['dirpath'] = os.path.join("网友自拍", response.xpath('//h1[@id="subject_tpc"]/text()').extract()[1].replace('/', '.').replace('?', '.').replace(':', '.'))
        yield item
