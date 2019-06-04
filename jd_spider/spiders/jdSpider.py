import re
from urllib import parse
import redis
import scrapy
from scrapy_redis.spiders import RedisSpider
from jd_spider.items import JdSpiderItem

"""

京东商城爬虫：
1.根据提供的关键字进行搜索
2.将搜索的结果中目标字段进行抽取
3.对无搜索结果的关键字进行单独标记并写入文件

"""
default_value = "null"  # 全局的变量，用于设定默认值，便于后期需求变更时代码的修改


class JDspider(RedisSpider):    # 继承于分布式爬虫
    name = "jdSpider"   # 为爬虫命名
    redis_key = "jdSpider:start_urls"   # 启动爬虫的命令
    """此时遗留一个问题未解决，不使用redis_key就可以开始爬取"""
    # 初始化方法
    def __init__(self):
        # 定全局的统计变量,已经采集完成的
        self.finshed = 0
        # 与获取的关键字做拼接获取第一次发送请求的url
        self.base_url = "https://search.jd.com/Search?keyword={0}&enc=utf-8&pvid=a4b0a79ce48146d89224f9b7a8708474&page={1}"
        # 与获取的前三十个商品id做拼接获取第二次Ajax的请求,page为当前页数加一
        self.search_url = "https://search.jd.com/s_new.php?keyword={0}&enc=utf-8&qrst=1&rt=1&stop=1&vt=2&page={1}&s=31&scrolling=y&log_id=1541636242.67866&tpl=1_M&show_items={2}"
        # # 这是在基于非分布式版本的部分采集结果基础上增添的代码，实际分布式时并不需要
        # self.finshed_keyword = self.read_finshed_keyword()

    def start_requests(self):
        connect = redis.Redis(host='127.0.0.1', port=6379, db=4,password='pengfeiQDS')  # 获取redis的链接
        keyword_total = connect.dbsize()  # 获取关键字的总数
        # 遍历获取每一个关键字
        for index in range(1360001,1480000):

            keyword = connect.get(str(index)).decode('utf-8')   # 使用get方法获取关键字
            target_url = self.base_url.format(parse.quote(keyword), str(1))     # 将获取的关键字与base_url做拼接获取目标url
            yield scrapy.Request(url=target_url, callback=self.parse_page)  # 将目标url加入爬去的队列中

    # 定义解析函数获取页面信息
    def parse_page(self, response):
        if response.status == 200:  # 判断页面是否响应成功
            current_url = response.url  # 获取当前网页的url
            keyword = re.compile('keyword=(.*?)&enc').findall(current_url)[0]  # 获取当前搜索的关键字
            """
            此处需要将无匹配结果的关键字写入一个文件中
            一种是无匹配内容但有推荐内容  //div[@class="check-error"]
            一种是无匹配的内容            //div[@class="ns-content"]/span

            """
            # # 这是处理部分采集数据时增加的代码，后期服务器运行时需要将此处代码删除
            # if parse.quote(keyword) not in self.finshed_keyword:
            # 判断是否出现无匹配结果的标签
            if response.xpath('//div[@class="check-error"]') or response.xpath('//div[@class="ns-content"]/span'):
                with open('./无匹配结果.txt', 'a+', encoding='utf-8') as f:  # 关键字无匹配结果将关键字写入文件
                    f.write(parse.unquote(keyword) + "\n")
            else:
                total_num = response.xpath('//span[@id="J_resCount"]/text()').extract()[0]  # 获取商品的总件数
                total_page_num = response.xpath('//div[@id="J_topPage"]/span/i/text()').extract()[0]    # 获取总页数
                current_page_num = response.xpath('//div[@id="J_topPage"]/span/b/text()').extract()[0]  # 获取当前页号
                pids = set()    # 创建集合用于商品id的去重
                try:
                    # 获取网页信息的列表
                    all_goods = response.xpath('//div[@id="J_goodsList"]/ul/li')
                    # 遍历所有商品列表获取每一个商品信息
                    for goods in all_goods:
                        item = JdSpiderItem()  # 创建items对象
                        # 获取每一个商品的信息,这里只能先获取整个标签然后将标签内包含的子标签用正则去除后匹配出需要的文字
                        product_info = goods.xpath('.//div[@class="p-name p-name-type-2"]//a//em').extract()
                        # 获取商品图片地址,这是已经加载完成的标签
                        img_url = goods.xpath('div/div[1]/a/img/@source-data-lazy-img').extract()
                        # ===============================================================================================
                        # # 获取商品图片的地址，这是未加载完成的标签,这里会包含已经加载完成的，为done，赋值时注意区分判断
                        # img_url_delay = goods.xpath('div/div[1]/a/img/@data-lazy-img').extract()
                        # # 查看未加载完成的商品图片地址
                        # print("查看未加载完成的商品图片地址:",img_url_delay,len(img_url_delay))
                        # 此处遇见一个比较坑的情况，浏览器审查元素看到的页面与响应回来的页面不一致
                        # ================================================================================================
                        comment_num = goods.xpath('.//div[@class="p-commit"]/strong/a/text()').extract()    # 获取商品评论数
                        shop_name = goods.xpath('.//div[@class="p-shop"]//a/text()').extract()   # 获取卖家
                        price = goods.xpath('.//div[@class="p-price"]/strong/i/text()').extract()   # 获取商品价格
                        pid = goods.xpath('./@data-sku').extract()  # 获取商品ID
                        detail_page = goods.xpath('div/div[1]/a/@href').extract()   # 获取商品详情页链接
                        shop_detail = goods.xpath('.//div[@class="p-shop"]//a/@href').extract()  # 获取店铺详情页链接
                        # 判断是否为空,不为空添加,为空则赋值为默认值，否则该条信息会丢失
                        if pid:
                            pids.add(pid[0])
                        item['keyword'] = parse.unquote(keyword)
                        item['total_num'] = total_num if total_num else default_value
                        item['product_info'] = re.sub(r'</?[^>]+>', "", product_info[0]) if product_info else default_value
                        item['img_url'] = img_url[0] if img_url else default_value
                        item['comment_num'] = comment_num[0] if comment_num else default_value
                        item['shop_name'] = shop_name[0] if shop_name else default_value
                        item['price'] = price[0] if price else default_value
                        item['detail_page'] = "https:" + detail_page[0] if detail_page else default_value
                        item['shop_detail'] = "https:" + shop_detail[0] if shop_detail else default_value
                        yield item
                    yield scrapy.Request(
                    url=self.search_url.format(keyword, str(int(current_page_num) * 2), ",".join(pids)),
                    meta={'current_page_num': current_page_num,
                          'total_page_num': total_page_num, 'keyword': keyword, 'total_num':total_num if total_num else default_value},
                    callback=self.next_half_parse)
                except Exception:
                    print("解析出错")
                # 此时请求的page 需要根据获取的当前页号来做最终请求url 的拼接，做乘2的处理即为请求另一半数据的url,并将当前页号和总页号传递给下一个解析函数
                #yield scrapy.Request(
                    #url=self.search_url.format(keyword, str(int(current_page_num) * 2), ",".join(pids)),
                    #meta={'item': item, 'current_page_num': current_page_num,
                          #'total_page_num': total_page_num, 'keyword': keyword},
                    #callback=self.next_half_parse)
            # else:
            #     with open('./完成搜索关键字.txt', 'a+', encoding='utf-8') as f:
            #         f.write(parse.unquote(keyword) + "\n")

    # 定义另一半数据的解析页面
    def next_half_parse(self, response):
        """
        首先根据获取的当前页和总页数来判断是返回解析后的items 还是有下一页继续回调解析函数解析页面
        此时响应回来的数据是另一半数据，响应回来的并不是整个页面的数据
        :param response:
        :return:
        """
        if response.status == 200:
            current_page_num = response.meta['current_page_num']  # 获取传递的当前页号
            total_page_num = response.meta['total_page_num']  # 获取总页号
            keyword = response.meta['keyword']  # 获取当前搜索关键字
            #item = response.meta['item']    # 获取items对象,在mongodb中会报错，故修改到循环里面
            try:
                all_goods = response.xpath('//li[@class="gl-item"]')    # 获取另一半数据的列表
                for goods in all_goods: # 遍历获取每一件商品对象
                    item = JdSpiderItem()  # 创建items对象
                    # 获取每一个商品的信息
                    product_info = goods.xpath('.//div[@class="p-name p-name-type-2"]//a//em').extract()
                    # 获取图片地址
                    img_url = goods.xpath('div/div[1]/a/img/@source-data-lazy-img').extract()
                    # 获取商品评论数
                    comment_num = goods.xpath('.//div[@class="p-commit"]/strong/a/text()').extract()
                    # 获取卖家
                    shop_name = goods.xpath('.//div[@class="p-shop"]//a/text()').extract()
                    # 获取商品价格
                    price = goods.xpath('.//div[@class="p-price"]/strong/i/text()').extract()
                    detail_page = goods.xpath('div/div[1]/a/@href').extract()  # 获取商品详情页链接
                    shop_detail = goods.xpath('.//div[@class="p-shop"]//a/@href').extract()  # 获取店铺详情页链接
                    # 判断是否为空,不为空添加，为空则赋值为默认值
                    item['keyword'] = keyword
                    item['total_num'] = response.meta['total_num']
                    item['product_info'] = re.sub(r'</?[^>]+>', "", product_info[0]) if product_info else default_value
                    item['img_url'] = img_url[0] if img_url else default_value
                    item['comment_num'] = comment_num[0] if comment_num else default_value
                    item['shop_name'] = shop_name[0] if shop_name else default_value
                    item['price'] = price[0] if price else default_value
                    item['detail_page'] = detail_page[0] if detail_page else default_value
                    item['shop_detail'] = shop_detail[0] if shop_detail else default_value
                    yield item
            except Exception:
                print("解析出错")
            # 判断当前页和总页数的关系，决定是否执行回调函数
            if current_page_num < total_page_num:
                # 如果当前页小于总页数，需要继续回调第一个解析函数获取一般数据的页面
                print('=====================', self.base_url.format(keyword, str(int(current_page_num) * 2 + 1)))
                yield scrapy.Request(url=self.base_url.format(keyword, str(int(current_page_num) * 2 + 1)),
                                     callback=self.parse_page)
                # 增加判断将已经完成的关键字写入文件之中
            elif current_page_num == total_page_num:
                self.finshed += 1
                print("目前共完成%s个关键字的爬取" % self.finshed)
                with open('./完成搜索关键字.txt', 'a+', encoding='utf-8') as f:
                    f.write(parse.unquote(keyword) + "\n")
