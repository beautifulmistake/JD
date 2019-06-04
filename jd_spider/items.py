# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class JdSpiderItem(scrapy.Item):
    """
    在分布式爬虫下的items.py 文件并不需要做修改

    """
    # define the fields for your item here like:
    # name = scrapy.Field()
    _id = scrapy.Field()
    # 当前搜索的关键字
    keyword = scrapy.Field()
    # 获取总件数
    total_num = scrapy.Field()
    # 获取商品信息
    product_info = scrapy.Field()
    # 获取商品图片地址
    img_url = scrapy.Field()
    # 获取商品评论数
    comment_num = scrapy.Field()
    # 获取卖家
    shop_name = scrapy.Field()
    # 获取价格
    price = scrapy.Field()
    # 获取商品详情页链接
    detail_page = scrapy.Field()
    # 获取店铺详情页链接
    shop_detail = scrapy.Field()
