# coding=utf-8
import os
import glob
from x77 import settings
from x77.items import *


class SelfieSpider(scrapy.Spider):
    name = "selfie"
    start_urls = ["http://x77113.com/bbs/thread.php?fid=20&page=" + str(i) for i in range(1, 25)]

    def parse(self, response):
        item = TopicItem()
        head = response.xpath('//head/base/@href').extract_first()
        name = response.css('.subject_t').xpath('text()').extract()
        ref = response.css('.subject_t').xpath('@href').extract()
        item['topic'] = name
        item['link'] = [head + n for n in ref]

        for (topic, url) in zip(item['topic'], item['link']):
            # skip the scenario where the torrent already exists
            dirname = topic.replace('/', '|')
            dirname = os.path.join(settings.IMAGES_STORE, dirname)
            if os.path.isdir(dirname) and glob.glob(os.path.join(dirname, "*.torrent")):
                continue
            yield scrapy.Request(url, callback=self.parse_item)

    def parse_item(self, response):
        if response.xpath('//div[@class="mt10"]/ol/li').extract():
            return
        item = TopicContentItem()
        item['image_urls'] = response.xpath('//div[@id="read_tpc"]/img/@src').extract()
        item['dirname'] = response.xpath('//h1[@id="subject_tpc"]/text()').extract()[1]
        item['context'] = "\n".join(response.xpath('//div[@id="read_tpc"]/text()').extract()).strip() + "\n".join(
            response.xpath('//div[@id="read_tpc"]/a/@href').extract()).strip() + "\nURL:" + response.url
        item['torrents'] = response.xpath('//div[@id="read_tpc"]/a/@href').extract()
        yield item
