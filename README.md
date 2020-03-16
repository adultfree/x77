# Xiao77论坛数据爬取

## 简介

Xiao77论坛从我读大学开始出现，陪我度过了许多难忘的夜晚。当时印象最深刻的是在“网友自拍”板块，用遨游(Maxthon)浏览器的鼠标插件一次性打开所有划过的链接(虽然遨游浏览器也用的IE内核，但它当时是对一个窗口多Tab支持的最好的浏览器)，头顶上几十个页面正在刷新是我最大的安慰。

无奈的是，高峰期Xiao77论坛的网速太慢，而且其系统时常因为负载、反爬虫等问题要求“按F5键刷新”。在兴起之时看不见想看的图片是最大的遗憾。

了解了HTTP请求的本质后，我开始自己写脚本爬取Xiao77论坛的数据，每次不用爬取太多，够用即可。

独乐乐不如众乐乐，我决定分享给大家。

## 爬取的板块

* 亚洲BT
* 网友自拍

时过境迁，现在Xiao77论坛支持的板块越来越多，但我依然喜欢原来的味道，仅爬取BT板块和自拍板块。

![Image of Main Page](https://raw.githubusercontent.com/adultfree/x77/master/images/main.png)

## 使用方法

```shell script
# 确认Python版本为Python3
python3 --version
root@adultfree:~/x77# python3 --version
Python 3.5.2
# 安装依赖包
root@adultfree:~/x77# python3 -m pip install -r requirements.txt
......
# 开始爬取亚洲BT
root@adultfree:~/x77# scrapy crawl asia_bt
# 开始爬取网友自拍
root@adultfree:~/x77# scrapy crawl selfie_photo
```

## 注意事项
在x77/settings.py文件中，有针对爬虫的各种设置。

常用的设置包括：

 * HOST地址(若Xiao77论坛地址改变)
 * 爬取页面范围
 * 爬取后数据的保存路径
 * 定义日志为文件、修改日志级别

## 爬取结果概览
[网友自拍](https://raw.githubusercontent.com/adultfree/x77/master/images/selfie_photo_result.png)
[亚洲BT](https://raw.githubusercontent.com/adultfree/x77/master/images/asia_bt_result.png)
[亚洲BT种子细节](https://raw.githubusercontent.com/adultfree/x77/master/images/asia_bt_torrent_result.png)