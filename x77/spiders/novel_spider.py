import os

from x77 import settings
from x77.items import *
from x77.spiders import need_refresh


class NovelSpider(scrapy.Spider):
    name = "novel"
    # 文学欣赏被分为多个板块
    # 因此需要分开访问
    # 对于文学欣赏，我们要访问到它所有的页面
    start_urls = ["http://%s/bbs/thread.php?fid=8" % settings.HOST]

    def parse(self, response):
        if need_refresh(response.text):
            yield scrapy.Request(response.url, callback=self.parse, dont_filter=True)
        else:
            head = response.xpath('//head/base/@href').extract_first()
            name = response.xpath('//tr[@class="tr3"]/th[@class="new"]/h2/a/text()').extract()
            ref = response.xpath('//tr[@class="tr3"]/th[@class="new"]/h2/a/@href').extract()
            topics = name
            links = [head + n for n in ref]
            for (topic, url) in zip(topics, links):
                yield scrapy.Request(url, callback=self.parse_page)
            yield scrapy.Request(response.request.url, callback=self.parse_page)

    def parse_page(self, response):
        if need_refresh(response.text):
            yield scrapy.Request(response.url, callback=self.parse_page, dont_filter=True)
        else:
            # 共x页
            try:
                total_pages = int(response.xpath("//*[@id='sidebar']//div[@class='fl']/text()").extract_first()[1:-1])
                for p in range(1, total_pages + 1):
                    url = "%s&page=%s" % (response.request.url, p)
                    yield scrapy.Request(url, callback=self.parse_each_page)
            except Exception:
                yield scrapy.Request(response.url, callback=self.parse_page, dont_filter=True)

    def parse_each_page(self, response):
        if need_refresh(response.text):
            yield scrapy.Request(response.url, callback=self.parse_each_page, dont_filter=True)
        else:
            item = TopicItem()
            name = response.css('.subject_t').xpath('text()').extract()
            ref = response.css('.subject_t').xpath('@href').extract()
            head = response.xpath('//head/base/@href').extract_first()
            item['topic'] = name
            item['link'] = [head + n for n in ref]
            for (topic, url) in zip(item['topic'], item['link']):
                yield scrapy.Request(url, callback=self.parse_item)

    def parse_item(self, response):
        if need_refresh(response.text):
            yield scrapy.Request(response.url, callback=self.parse_item, dont_filter=True)
        else:
            item = TopicContentItem()
            dirpath = response.xpath('//*[@id="breadCrumb"]/a/text()').extract()[1:]
            item['filename'] = dirpath.pop() + ".txt"
            item['dirname'] = os.path.join(*dirpath)
            context = "\n".join(list(map(lambda x: x.strip(),
                    response.xpath('//*[@id="read_tpc"]/*/text() | //*[@id="read_tpc"]/text()').extract())))
            if not context or context == "":
                print("check it")
            item['context'] = response.url + "\n" + context
            yield item
