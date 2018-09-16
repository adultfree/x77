import glob
import os

from x77 import settings
from x77.items import *
from x77.spiders import need_refresh


class SelfieSpider(scrapy.Spider):
    name = "selfie"
    start_urls = ["http://%s/bbs/thread.php?fid=20&page=%d" % (settings.HOST, i) for i in range(*settings.PAGE_RANGE)]

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
                # skip the scenario where the torrent already exists
                dirpath = topic.replace('/', '.').replace('?', '.').replace(':', '.')
                dirpath = os.path.join(settings.IMAGES_STORE, "亚洲BT", dirpath)
                if os.path.isdir(dirpath) and glob.glob(os.path.join(dirpath, "*.torrent")):
                    continue
                yield scrapy.Request(url, callback=self.parse_item)

    def parse_item(self, response):
        if need_refresh(response.text):
            yield scrapy.Request(response.url, callback=self.parse_item, dont_filter=True)
        else:
            item = TopicContentItem()
            item['image_urls'] = response.xpath('//div[@id="read_tpc"]/*/img/@src | //div[@id="read_tpc"]/img/@src').extract()
            item['dirname'] = os.path.join("亚洲BT", response.xpath('//h1[@id="subject_tpc"]/text()').extract()[1].replace('/', '.').replace('?', '.').replace(':', '.'))
            context_list = response.xpath('//div[@id="read_tpc"]/*/text() | //div[@id="read_tpc"]/text()').extract()[0:-2]
            context_list = [e for e in context_list if e.strip()]
            item['context'] = "%s\n\n%s\n%s" % (response.url, "\n".join(context_list).strip(), "【下载地址】：" +
                                                ", ".join(response.xpath('//div[@id="read_tpc"]/*/a/@href | //div[@id="read_tpc"]/a/@href').extract()).strip())
            item['context'].encode().decode("UTF-8")
            item['torrents'] = response.xpath('//div[@id="read_tpc"]/*/a/@href | //div[@id="read_tpc"]/a/@href').extract()
            yield item
