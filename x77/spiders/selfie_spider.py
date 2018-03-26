import os
import glob

from x77 import settings
from x77.items import *


def need_refresh(text):
    if text == "请刷新页面或按键盘F5":
        print("NEED REFRESH!!!")
        return True
    return False


class SelfieSpider(scrapy.Spider):
    name = "selfie"
    start_urls = ["http://%s/bbs/thread.php?fid=20&page=%d" % (settings.HOST, i) for i in range(1, 30)]

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
                dirname = topic.replace('/', '.').replace('?', '.').replace(':', '.')
                dirname = os.path.join(settings.IMAGES_STORE, dirname)
                if os.path.isdir(dirname) and glob.glob(os.path.join(dirname, "*.torrent")):
                    continue
                # # temporary
                # if not topic.startswith("林美仑"):
                #     continue
                # # temporary
                yield scrapy.Request(url, callback=self.parse_item)

    def parse_item(self, response):
        if need_refresh(response.text):
            yield scrapy.Request(response.url, callback=self.parse_item, dont_filter=True)
        else:
            item = TopicContentItem()
            item['image_urls'] = response.xpath('//div[@id="read_tpc"]/*/img/@src | //div[@id="read_tpc"]/img/@src').extract()
            item['dirname'] = response.xpath('//h1[@id="subject_tpc"]/text()').extract()[1].replace('/', '.').replace('?', '.').replace(':', '.')
            context_list = response.xpath('//div[@id="read_tpc"]/*/text() | //div[@id="read_tpc"]/text()').extract()[0:-2]
            context_list = [e for e in context_list if e.strip()]
            item['context'] = "%s\n\n%s\n%s" % (response.url, "\n".join(context_list).strip(), "【下载地址】：" +
                                        ", ".join(response.xpath('//div[@id="read_tpc"]/*/a/@href | //div[@id="read_tpc"]/a/@href').extract()).strip())
            item['context'].encode().decode("UTF-8")
            item['torrents'] = response.xpath('//div[@id="read_tpc"]/*/a/@href | //div[@id="read_tpc"]/a/@href').extract()
            yield item
