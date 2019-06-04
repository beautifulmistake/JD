# -*- coding: utf-8 -*-

# Scrapy settings for jd_spider project
#
# For simplicity, this file contains only settings considered important or
# commonly used. You can find more settings consulting the documentation:
#
#     https://doc.scrapy.org/en/latest/topics/settings.html
#     https://doc.scrapy.org/en/latest/topics/downloader-middleware.html
#     https://doc.scrapy.org/en/latest/topics/spider-middleware.html
import os

BOT_NAME = 'jd_spider'  # 保持原配置

SPIDER_MODULES = ['jd_spider.spiders']  # 保持原配置
NEWSPIDER_MODULE = 'jd_spider.spiders'  # 保持原配置


# Crawl responsibly by identifying yourself (and your website) on the user-agent
#USER_AGENT = 'jd_spider (+http://www.yourdomain.com)'

# Obey robots.txt rules
ROBOTSTXT_OBEY = False  # 协议改为False
# 以下代码是将数据存储到mongodb时增加的代码
MONGO_IP = "localhost"
MONGO_PORT = 27017
MONGO_DB_NAME = 'f_jd'
MONGO_URL = "mongodb://admin:admin@139.217.99.231:22022"
JDRESULT_COLLECTIONS_NAME = 'jd_result'


# Configure maximum concurrent requests performed by Scrapy (default: 16)
#CONCURRENT_REQUESTS = 32

# Configure a delay for requests for the same website (default: 0)
# See https://doc.scrapy.org/en/latest/topics/settings.html#download-delay
# See also autothrottle settings and docs
DOWNLOAD_DELAY = 1  # 下载延迟，放缓爬取速度
# The download delay setting will honor only one of:
#CONCURRENT_REQUESTS_PER_DOMAIN = 16
#CONCURRENT_REQUESTS_PER_IP = 16

# Disable cookies (enabled by default)
#COOKIES_ENABLED = False

# Disable Telnet Console (enabled by default)
#TELNETCONSOLE_ENABLED = False

# Override the default request headers:
#DEFAULT_REQUEST_HEADERS = {
#   'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
#   'Accept-Language': 'en',
#}

# Enable or disable spider middlewares
# See https://doc.scrapy.org/en/latest/topics/spider-middleware.html
#SPIDER_MIDDLEWARES = {
#    'jd_spider.middlewares.JdSpiderSpiderMiddleware': 543,
#}

# Enable or disable downloader middlewares
# See https://doc.scrapy.org/en/latest/topics/downloader-middleware.html
DOWNLOADER_MIDDLEWARES = {
   #'jd_spider.middlewares.JdSpiderDownloaderMiddleware': 543,
   # 配置随机切换user_agent时添加
   'jd_spider.middlewares.RandomUserAgentMiddleware':543,
   # 以下是配置随机切换代理IP时添加
   'scrapy.downloadermiddlewares.retry.RetryMiddleware': 90,
   'scrapy_proxies.RandomProxy': 100,
   'scrapy.downloadermiddlewares.httpproxy.HttpProxyMiddleware': 110,

}

# Enable or disable extensions
# See https://doc.scrapy.org/en/latest/topics/extensions.html
#EXTENSIONS = {
#    'scrapy.extensions.telnet.TelnetConsole': None,
#}

# Configure item pipelines
# See https://doc.scrapy.org/en/latest/topics/item-pipeline.html
ITEM_PIPELINES = {
   #'jd_spider.pipelines.JdSpiderPipeline': 300,     # 优先按自己编写的逻辑保存目标字段
   'jd_spider.pipelines.JdToMongoPipeline': 300,     # 导入到Mongodb时增加
   #'scrapy_redis.pipelines.RedisPipeline': 400,     # 优先级较低同时也会在redis数据库保存一份
}

# Enable and configure the AutoThrottle extension (disabled by default)
# See https://doc.scrapy.org/en/latest/topics/autothrottle.html
#AUTOTHROTTLE_ENABLED = True
# The initial download delay
#AUTOTHROTTLE_START_DELAY = 5
# The maximum download delay to be set in case of high latencies
#AUTOTHROTTLE_MAX_DELAY = 60
# The average number of requests Scrapy should be sending in parallel to
# each remote server
#AUTOTHROTTLE_TARGET_CONCURRENCY = 1.0
# Enable showing throttling stats for every response received:
#AUTOTHROTTLE_DEBUG = False

# Enable and configure HTTP caching (disabled by default)
# See https://doc.scrapy.org/en/latest/topics/downloader-middleware.html#httpcache-middleware-settings
#HTTPCACHE_ENABLED = True
#HTTPCACHE_EXPIRATION_SECS = 0
#HTTPCACHE_DIR = 'httpcache'
#HTTPCACHE_IGNORE_HTTP_CODES = []
#HTTPCACHE_STORAGE = 'scrapy.extensions.httpcache.FilesystemCacheStorage'

# 分布式爬虫添加的配置信息
DUPEFILTER_CLASS = "scrapy_redis.dupefilter.RFPDupeFilter"   # 使用scrapy_redis 里的去重组件，不使用scrapy默认的去重方式
SCHEDULER = "scrapy_redis.scheduler.Scheduler"  # 使用scrapy_redis 里的调度器组件，不使用默认的调度器
SCHEDULER_PERSIST = True    # 允许暂停，redis请求记录不丢失
SCHEDULER_QUEUE_CLASS = "scrapy_redis.queue.SpiderPriorityQueue"    # 默认使用scrapy_redis请求队列形式（优先级）
# 队列形式，请求先进先出
# SCHEDULER_QUEUE_CLASS = "scrapy_redis.queue.SpiderQueue"
# 栈形式，请求先进后出
# SCHEDULER_QUEUE_CLASS = "scrapy_redis.queue.SpiderStack"
LOG_LEVEL = 'DEBUG'     # 日志级别
REDIS_HOST = '127.0.0.1'    # 连接本机
REDIS_PORT = '6379'   # 端口
REDIS_PARAMS = {
    'password': 'pengfeiQDS',
    'db': 0
}   # 密码一般不设置，使用数据0

# 以下为添加随机的user_agent 时编写
RANDOM_UA_TYPE = "random"   # 添加选用 User_agent 的方法

# 以下代码是随机切换代理IP时添加的配置
# Retry many times since proxies often fail
RETRY_TIMES = 10
# Retry on most error codes since proxies fail for different reasons
RETRY_HTTP_CODES = [500, 503, 504, 400, 403, 404, 408]

# Proxy list containing entries like
# http://host1:port
# http://username:password@host2:port
# http://host3:port

# 实际开发时编写的代码：
project_dir = os.path.abspath(os.path.dirname(__file__))
# 配置自己的代理IP文件,特别注意：在书写proxys.txt的路径时注意不要再添加项目名了
proxys_path = os.path.join(project_dir,'proxys.txt')
PROXY_LIST = proxys_path

# Proxy mode
# 0 = Every requests have different proxy
# 1 = Take only one proxy from the list and assign it to every requests
# 2 = Put a custom proxy to use in the settings
PROXY_MODE = 0
# If proxy mode is 2 uncomment this sentence :
# CUSTOM_PROXY = "http://host1:port"
