# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html
import os
from urllib.parse import to_bytes
from lxml import html
import scrapy
import urllib
from . import settings
from scrapy.http import Request
from scrapy.pipelines.images import ImagesPipeline
from scrapy.pipelines.files import FilesPipeline
import requests

class SelfieImagesPipeline(ImagesPipeline):
    def get_media_requests(self, item, info):
        dirname = item['dirname']
        dirpath = os.path.join(settings.IMAGES_STORE, dirname)
        if not os.path.isdir(dirpath):
            os.makedirs(dirpath)
        i = 0
        for image_url in item['image_urls']:
            filename = 'error'
            i += 1
            if i < 10:
                filename = '0' + str(i) + '.jpg'
            elif i < 100:
                filename = str(i) + '.jpg'
            filepath = os.path.join(dirpath, filename)
            if os.path.exists(os.path.join(filepath)):
                continue
            yield scrapy.Request(image_url, meta={'filename': filepath})
        # write the context file
        context_file = os.path.join(dirpath, 'info.txt')
        if not os.path.exists(context_file):
            with open(context_file, 'w') as file:
                file.write(item['context'])


    def file_path(self, request, response=None, info=None):
        # start of deprecation warning block (can be removed in the future)
        def _warn():
            from scrapy.exceptions import ScrapyDeprecationWarning
            import warnings
            warnings.warn('ImagesPipeline.image_key(url) and file_key(url) methods are deprecated, '
                          'please use file_path(request, response=None, info=None) instead',
                          category=ScrapyDeprecationWarning, stacklevel=1)

        # check if called from image_key or file_key with url as first argument
        if not isinstance(request, Request):
            _warn()
            url = request
        else:
            url = request.url

        # detect if file_key() or image_key() methods have been overridden
        if not hasattr(self.file_key, '_base'):
            _warn()
            return self.file_key(url)
        elif not hasattr(self.image_key, '_base'):
            _warn()
            return self.image_key(url)
            # end of deprecation warning block
        filename = request.meta['filename']
        return '%s' % filename


class SelfieFilesPipeline(FilesPipeline):
    headers = {
        'content-type': "multipart/form-data; boundary=----WebKitFormBoundary7MA4YWxkTrZu0gW",
        'connection': "keep-alive",
        'cache-control': "no-cache",
        'upgrade-insecure-requests': "1",
        'user-agent': "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/56.0.2924.87 Safari/537.36",
        'accept': "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
        'dnt': "1",
        'accept-encoding': "gzip, deflate",
        'accept-language': "en-US,en;q=0.8,zh-CN;q=0.6,zh;q=0.4,zh-TW;q=0.2"
    }
    bodyStartWithRef = """------WebKitFormBoundary7MA4YWxkTrZu0gW
Content-Disposition: form-data; name="ref"

"""
    bodyStartWithMcncc = """------WebKitFormBoundary7MA4YWxkTrZu0gW
Content-Disposition: form-data; name="Mcncc"

"""
    bodyEnd = """
------WebKitFormBoundary7MA4YWxkTrZu0gW
Content-Disposition: form-data; name="rulesubmit"

请点这里下载
------WebKitFormBoundary7MA4YWxkTrZu0gW"""

    def get_media_requests(self, item, info):
        # download the torrent files
        dirname = item['dirname']
        if not os.path.isdir(os.path.join(settings.FILES_STORE, dirname)):
            os.makedirs(os.path.join(settings.FILES_STORE, dirname))
        if 'torrents' in item:
            for torrent in item['torrents']:
                if torrent.find("imedown") > 0:
                    filename = urllib.parse.urlparse(torrent).query.split('=')[-1] + '.torrent'
                    torrentlink = "http://www.imedown.info/up/" + filename
                    filename = os.path.join(dirname, filename)
                    if os.path.exists(os.path.join(settings.FILES_STORE, filename)):
                        continue
                    yield scrapy.Request(torrentlink, meta={'filename': filename})
                elif torrent.find("luludown") > 0:
                    filename = urllib.parse.urlparse(torrent).query.split('=')[-1] + '.torrent'
                    torrentlink = "http://www.luludown.info/up/" + filename
                    body = self.bodyStartWithRef + filename + self.bodyEnd
                    filename = os.path.join(dirname, filename)
                    if os.path.exists(os.path.join(settings.FILES_STORE, filename)):
                        continue
                    yield scrapy.Request(torrentlink, None, 'POST', self.headers, body,
                                         meta={'filename': filename})
                elif torrent.find("xhh8") > 0:
                    filename = urllib.parse.urlparse(torrent).query.split('=')[-1]
                    if torrent.find("avsd") > 0:
                        # deal with torrent download page URL:
                        # http://www1.xhh8.com/avsd.php?hash=20AJaVrwyz
                        link = "http://www.downdvs.com:8080/load.php"
                        body = self.bodyStartWithRef + filename + self.bodyEnd
                        filename = os.path.join(dirname, filename + ".torrent")
                        if os.path.exists(os.path.join(settings.FILES_STORE, filename)):
                            continue
                        yield scrapy.Request(link, None, 'POST', self.headers, body,
                                             meta={'filename': filename})
                    elif torrent.find("x7btc") > 0:
                        # deal with torrent download page URL:
                        # http://www.xhh8.info/bt/cl/x7btc.php?hash=18165f592f47736211c3d204d0dfaa812e5161f48ca
                        filename = urllib.parse.urlparse(torrent).query.split('=')[-1]
                        filename = os.path.join(dirname, filename + ".torrent")
                        if os.path.exists(os.path.join(settings.FILES_STORE, filename)):
                            continue
                        doc = html.fromstring(requests.get(torrent).content)
                        url = doc.xpath('//*[@id="asddf"]')[0].attrib['href']
                        yield scrapy.Request(url, None, 'GET', meta={'filename': filename})
                    else:
                        body = self.bodyStartWithMcncc + filename + self.bodyEnd
                        filename = os.path.join(dirname, filename + ".torrent")
                        if os.path.exists(os.path.join(settings.FILES_STORE, filename)):
                            continue
                        yield scrapy.Request(torrent, None, 'POST', self.headers, body,
                                             meta={'filename': filename})
                else:
                    print(torrent)

    def file_path(self, request, response=None, info=None):
        # start of deprecation warning block (can be removed in the future)
        def _warn():
            from scrapy.exceptions import ScrapyDeprecationWarning
            import warnings
            warnings.warn('FilesPipeline.file_key(url) method is deprecated, please use '
                          'file_path(request, response=None, info=None) instead',
                          category=ScrapyDeprecationWarning, stacklevel=1)

        # check if called from file_key with url as first argument
        if not isinstance(request, Request):
            _warn()
            url = request
        else:
            url = request.url

        # detect if file_key() method has been overridden
        if not hasattr(self.file_key, '_base'):
            _warn()
            return self.file_key(url)
        # end of deprecation warning block
        filename = request.meta['filename']
        return '%s' % filename
