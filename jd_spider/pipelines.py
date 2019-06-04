# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html

from jd_spider.utils import get_db
mongo_db = get_db()


# 在分布式下此文件不需要做修改
class JdSpiderPipeline(object):
    # 创建文件方法
    def open_spider(self, spider):
        """
        在当前路径下创建文件记录爬取的目标字段
        路径的可以根据实际需求做修改
        :param spider:
        :return:
        """
        # 在当前目录下创建为文件
        self.file = open('./jdResult.txt', 'a+', encoding='utf-8')
    # 管道方法，对目标字段的入库或者写入文件等操作在此书写
    def process_item(self, item, spider):
        """
        处理获取的目标字段，将目标字段整理成统一规整的格式
        最后将目标字段写入文件之中
        :param item:
        :param spider:
        :return:
        """
        keyword = item['keyword']   # 获取当前搜索关键字
        print("查看搜索关键字====================：", keyword)
        total_num = item['total_num']   # 获取商品总件数
        # 查看商品总件数
        print("查看商品总件数====================：", total_num)
        product_info = item['product_info'] # 获取商品信息
        print("查看商品信息======================：", product_info)
        img_url = item['img_url']   # 获取商品图片地址
        print("查看商品图片地址==================：", img_url)
        comment_num = item['comment_num']   # 获取商品评论数
        print("查看商品评论数====================：", comment_num)
        shop_name = item['shop_name']    # 获取卖家
        print("查看卖家==========================：", shop_name)
        price = item['price']   # 获取商品价格
        print("查看商品价格======================：", price)
        # 将获取的目标字段整理成统一格式，定义一个变量用于拼接最后结果
        detail_page = item['detail_page']
        print("查看商品详情页====================：", detail_page)
        shop_detail = item['shop_detail']
        print("查看店铺详情页====================：", shop_detail)
        result_content = ""
        result_content = result_content.join(
            keyword + "ÿ" + total_num + "ÿ" + product_info + "ÿ" + img_url + "ÿ" +
            comment_num + "ÿ" + shop_name + "ÿ" + price + "ÿ" + detail_page + "ÿ" + shop_detail + "ÿ" + "\n"
        )
        # 将文件写入本地文件
        self.file.write(result_content)
        self.file.flush()
        return item
    # 关闭文件的方法
    def close_spider(self,spider):
        # 文件写入完成，关闭文件
        self.file.close()

class JdToMongoPipeline(object):
    """抓取结果导入 mongo"""

    def __init__(self, settings):
        self.collections_name = settings.get('JDRESULT_COLLECTIONS_NAME')

    @classmethod
    def from_crawler(cls, crawler):
        settings = crawler.settings
        return cls(settings)

    def process_item(self, item, spider):
        mongo_db[self.collections_name].insert(item)
        return item
