import copy
import glob
import os
import urllib.parse

from x77 import settings
from x77.items import *
from x77.spiders.spider import Spider


class AsiaBTSpider(Spider):
    name = "asia_bt"
    page_range = settings.PAGE_RANGE
    # page_range = (10, 11)
    start_urls = ["http://%s/bbs/thread.php?fid=20&page=%d" % (settings.HOST, i) for i in range(*page_range)]

    def parse_page(self, response):
        item = self.get_topic_item(response)
        for (topic, url) in zip(item['topic'], item['link']):
            # skip the scenario where the torrent already exists
            dirname = topic.replace('/', '.').replace('?', '.').replace(':', '.')
            dirpath = os.path.join(settings.IMAGES_STORE, "亚洲BT", dirname)
            if os.path.isdir(dirpath) and glob.glob(os.path.join(dirpath, "*.torrent")):
                continue
            yield scrapy.Request(url, callback=self.parse_topic)

    def parse_item(self, response):
        item = ImageItem()
        item['referer'] = response.request.url
        item['images'] = response.xpath('//div[@id="read_tpc"]/*/img/@src | //div[@id="read_tpc"]/img/@src').extract()
        item['dirpath'] = os.path.join("亚洲BT", response.xpath('//h1[@id="subject_tpc"]/text()').extract()[1].replace('/', '.').replace('?', '.').replace(':', '.'))
        context = response.xpath('//div[@id="read_tpc"]/*/text() | //div[@id="read_tpc"]/text()').extract()[0:-2]
        context = [e for e in context if e.strip()]
        item['context'] = "%s\n\n%s\n%s" % (response.url, "\n".join(context).strip(), "【下载地址】：" +
                                            ", ".join(response.xpath('//div[@id="read_tpc"]/*/a/@href | //div[@id="read_tpc"]/a/@href').extract()).strip())
        item['context'].encode().decode("UTF-8")
        yield item

        item = FileItem()
        dirname = response.xpath('//h1[@id="subject_tpc"]/text()').extract()[1].replace('/', '.').replace('?', '.').replace(':', '.')
        item['referer'] = response.request.url
        item['dirpath'] = os.path.join("亚洲BT", dirname)
        torrents = response.xpath('//div[@id="read_tpc"]/*/a/@href | //div[@id="read_tpc"]/a/@href').extract()

        item['files'] = []
        item['filenames'] = []

        for i, torrent in enumerate(torrents):
            filename = "%03d.torrent" % (i + 1) if len(torrents) > 1 else "%s.torrent" % dirname
            if torrent.find("aae3") > 0:
                # 对于aae3的网站，情况较为特殊，需要请求BT下载页面才能得到random code
                aae3_item = copy.deepcopy(item)
                aae3_item['files'] = []
                aae3_item['filenames'] = [filename]
                yield scrapy.Request(torrent, callback=self.parse_torrent, meta={"item": aae3_item})
            else:
                # 对于其它网站，可以直接通过BT下载页面的结构决定下载链接
                item['filenames'].append(filename)
                if torrent.find("imedown") > 0:
                    item['files'].append("http://www.imedown.info/up/" + urllib.parse.urlparse(torrent).query.split('=')[-1] + '.torrent')
                elif torrent.find("luludown") > 0:
                    item['files'].append("http://www.luludown.info/up/" + urllib.parse.urlparse(torrent).query.split('=')[-1] + '.torrent')
                else:
                    self.logger.error("没有合适的模板处理种子：%s" % torrent)
        # 对于aae3的网站，在其逻辑中已经yield处理了
        # 对于其它网站，items中应该保存着所有的链接，进行统一处理即可
        if len(item['files']) > 0: yield item

    def parse_torrent(self, response):
        item = response.request.meta["item"]
        item['files'] = response.xpath('//a[@id="asddf"]/@href').extract()
        yield item
