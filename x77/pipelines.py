# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html
import os

import scrapy
from scrapy.pipelines.files import FilesPipeline
from scrapy.pipelines.images import ImagesPipeline

from . import settings


class x77ImagesPipeline(ImagesPipeline):

    # 当一个Request的所有image下载请求返回后，会回调该函数
    def item_completed(self, results, item, info):
        return super().item_completed(results, item, info)

    def get_media_requests(self, item, info):
        # item中包含images才处理image的下载
        if 'images' not in item: return

        # 为images创建一个目录用于存放图片
        dirpath = os.path.join(settings.IMAGES_STORE, item['dirname'])
        os.makedirs(dirpath, exist_ok=True)

        for i, image_url in enumerate(item['images']):
            _, extension = os.path.splitext(image_url)
            # 图片文件名范围001~009
            filename = "%03d%s" % (i + 1, extension)
            filepath = os.path.join(dirpath, filename)
            yield scrapy.Request(image_url, headers={"Referer": item['referer']}, meta={'filename': filepath})

            if 'context' in item and item['context']:
                # write the context file
                context_file = os.path.join(dirpath, 'info.txt')
                if not os.path.exists(context_file):
                    with open(context_file, 'w', encoding="utf-8") as file:
                        file.write(item['context'])

    def file_path(self, request, response=None, info=None):
        return request.meta["filename"]


class x77FilesPipeline(FilesPipeline):
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

    def item_completed(self, results, item, info):
        items = super().item_completed(results, item, info)
        return items

    def handle_torrent_download(self, item, info):
        # download the torrent files
        dirname = item['dirname']
        if not os.path.isdir(os.path.join(settings.FILES_STORE, dirname)):
            os.makedirs(os.path.join(settings.FILES_STORE, dirname))
        for filename, link in zip(item['filenames'], item['files']):
            # 如果文件已存在，直接忽略该文件
            if os.path.exists(os.path.join(settings.FILES_STORE, filename)):
                continue
            if link.find("aae3") > 0 or link.find("imedown") > 0:
                yield scrapy.Request(link, meta={'filename': filename})
            elif link.find("luludown") > 0:
                body = self.bodyStartWithRef + filename + self.bodyEnd
                yield scrapy.Request(link, None, 'POST', self.headers, body, meta={'filename': filename})
            else:
                print(link)

    def get_media_requests(self, item, info):
        # item中包含files才处理file的下载
        if 'files' not in item: return

        if item['filenames'][0].endswith("torrent"):
            yield from self.handle_torrent_download(item, info)

    def file_path(self, request, response=None, info=None):
        return request.meta["filename"]


class NovelFilesPipeline(FilesPipeline):
    def get_media_requests(self, item, info):
        # 保存文件内容即可
        dirname = item['dirname']
        dirpath = os.path.join(settings.IMAGES_STORE, dirname)
        if not os.path.isdir(dirpath):
            os.makedirs(dirpath)
        if 'context' in item:
            filepath = os.path.join(dirpath, item['filename'])
            while os.path.exists(filepath):
                paths = os.path.splitext(filepath)
                filepath = paths[0] + 'x' + paths[1]
            with open(filepath, 'w', encoding="utf-8") as file:
                file.write(item['context'])
