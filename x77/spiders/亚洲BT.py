import glob
import os
import urllib.parse

from x77 import settings
from x77.items import *
from x77.spiders.spider import Spider


class AsiaBTSpider(Spider):
    name = "asia_bt"
    start_urls = ["http://%s/bbs/thread.php?fid=20&page=%d" % (settings.HOST, i) for i in range(*settings.PAGE_RANGE)]

    def parse_page(self, response):
        item = self.get_topic_item(response)
        for (topic, url) in zip(item['topic'], item['link']):
            # skip the scenario where the torrent already exists
            dirpath = topic.replace('/', '.').replace('?', '.').replace(':', '.')
            dirpath = os.path.join(settings.IMAGES_STORE, "亚洲BT", dirpath)
            if os.path.isdir(dirpath) and glob.glob(os.path.join(dirpath, "*.torrent")):
                continue
            if topic.find("最新の欧美無碼精彩合集")> 0:
                yield scrapy.Request(url, callback=self.parse_topic)

    def parse_item(self, response):
        item = ImageItem()
        item['referer'] = response.request.url
        item['images'] = response.xpath('//div[@id="read_tpc"]/*/img/@src | //div[@id="read_tpc"]/img/@src').extract()
        item['dirname'] = os.path.join("亚洲BT", response.xpath('//h1[@id="subject_tpc"]/text()').extract()[1].replace('/', '.').replace('?', '.').replace(':', '.'))
        yield item

        item = FileItem()
        item['referer'] = response.request.url
        item['dirname'] = os.path.join("亚洲BT", response.xpath('//h1[@id="subject_tpc"]/text()').extract()[1].replace('/', '.').replace('?', '.').replace(':', '.'))
        context = response.xpath('//div[@id="read_tpc"]/*/text() | //div[@id="read_tpc"]/text()').extract()[0:-2]
        context = [e for e in context if e.strip()]
        item['context'] = "%s\n\n%s\n%s" % (response.url, "\n".join(context).strip(), "【下载地址】：" +
                                            ", ".join(response.xpath('//div[@id="read_tpc"]/*/a/@href | //div[@id="read_tpc"]/a/@href').extract()).strip())
        item['context'].encode().decode("UTF-8")

        files = []
        filenames = []
        torrents = response.xpath('//div[@id="read_tpc"]/*/a/@href | //div[@id="read_tpc"]/a/@href').extract()

        for i, torrent in enumerate(torrents):
            if torrent.find("aae3") > 0:
                item['filenames'] = [os.path.join(item['dirname'], str("%03d.torrent" % (i + 1)))]
                yield scrapy.Request(torrent, callback=self.parse_torrent, meta={"item": item})
            elif torrent.find("imedown") > 0:
                item['filenames'].append(os.path.join(item['dirname'], str("%03d.torrent" % (i + 1))))
                filename = urllib.parse.urlparse(torrent).query.split('=')[-1] + '.torrent'
                files.append("http://www.imedown.info/up/" + filename)
            elif torrent.find("luludown") > 0:
                item['filenames'].append(os.path.join(item['dirname'], str("%03d.torrent" % (i + 1))))
                filename = urllib.parse.urlparse(torrent).query.split('=')[-1] + '.torrent'
                files.append("http://www.luludown.info/up/" + filename)
            else:
                print("没有合适的模板：%s" % torrent)

        if len(files) > 0:
            item['filenames'] = filenames
            item['files'] = files
            yield item

    def parse_torrent(self, response):
        item = response.request.meta["item"]
        item['files'] = response.xpath('//a[@id="asddf"]/@href').extract()
        yield item
