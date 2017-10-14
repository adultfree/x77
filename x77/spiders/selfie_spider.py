# coding=utf-8
from x77.items import *


class SelfieSpider(scrapy.Spider):
    name = "selfie"
    # 酒店幹白嫩的小女友國語對白，技术很好干的很给力鸡巴破皮 绝版香港之马交浴室现场直击
    start_urls = ["http://x77128.com/bbs/thread.php?fid=20&page=" + str(i) for i in range(1, 4)]

    def parse(self, response):
        item = TopicItem()
        head = response.xpath('//head/base/@href').extract_first()
        name = response.css('.subject_t').xpath('text()').extract()
        ref = response.css('.subject_t').xpath('@href').extract()
        item['topic'] = name
        item['link'] = [head + n for n in ref]
        i = 0
        for url in item['link']:
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
