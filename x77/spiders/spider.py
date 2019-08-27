from x77.items import *


class Spider(scrapy.Spider):

    def parse(self, response):
        # 所有页面均可能出现让用户按F5刷新重试
        if response.text.endswith("F5"):
            yield scrapy.Request(response.url, callback=self.parse, dont_filter=True)
        else:
            yield from self.parse_page(response)

    def parse_topic(self, response):
        # 所有页面均可能出现让用户按F5刷新重试
        if response.text.endswith("F5"):
            yield scrapy.Request(response.url, callback=self.parse_topic, dont_filter=True)
        else:
            yield from self.parse_item(response)

    def parse_page(self, response):
        raise NotImplementedError('{}.parse_page callback is not defined'.format(self.__class__.__name__))

    def parse_item(self, response):
        raise NotImplementedError('{}.parse_item callback is not defined'.format(self.__class__.__name__))

    def get_topic_item(self, response):
        item = TopicItem()
        head = response.xpath('//head/base/@href').extract_first()
        name = response.css('.subject_t').xpath('text()').extract()
        ref = response.css('.subject_t').xpath('@href').extract()
        times = response.css('.subject_t').xpath("../../td[@class='author']/p/a/@title").extract()
        item['topic'] = name
        item['link'] = [head + n for n in ref]
        return item
