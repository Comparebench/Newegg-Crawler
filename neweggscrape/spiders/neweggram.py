from scrapy import Spider
from scrapy.selector import Selector
from ..items import AresscrapeMemory


#  TODO: Update ram spider to jump into URL instead of getting results from search page
class NeweggRamSpider(Spider):
    name = "neweggram"
    allowed_domains = ['newegg.com']
    start_urls = [
        'http://www.newegg.com/Desktop-Memory/SubCategory/ID-147'
    ]

    def parse(self, response):
        products = Selector(response).xpath('//*[@class="itemCell"]')
        for product in products:
            item = AresscrapeMemory()
            productname = product.xpath('div[2]/div/a/span/text()').extract()[0].encode('utf-8', 'ignore')
            productnamelist = str(productname).split(' ')
            item['make'] = productnamelist[0]
            item['modelname'] = productnamelist[productnamelist.index('Model') + 1]
            if 'GB' in productnamelist[1]:
                item['model'] = productnamelist[productnamelist.index('Model') + 1]
                item['size'] = productnamelist[1]
            elif 'GB' in productnamelist[2]:
                item['model'] = productnamelist[1]
                item['size'] = productnamelist[2].replace(')', '')
            elif 'GB' in productnamelist[3]:
                item['model'] = productnamelist[1] + ' ' + productnamelist[2]
                item['size'] = productnamelist[3]
            elif 'GB' in productnamelist[4]:
                item['size'] = productnamelist[4]
                item['model'] = productnamelist[1] + ' ' + productnamelist[2] + ' ' + productnamelist[3]
            else:
                item['model'] = productnamelist[1] + ' ' + productnamelist[2] + ' ' + productnamelist[3]
            if 'x' in productnamelist:
                item['modules'] = str(productnamelist[productnamelist.index('x') - 1].replace('(', ''))
            else:
                item['modules'] = 1
            item['type'] = productnamelist[productnamelist.index('SDRAM') - 1]
            item['url'] = product.xpath('div[2]/div/a/@href').extract()[0]
            price1 = product.xpath('div[3]/ul/li[3]/strong/text()').extract()[0]
            price2 = product.xpath('div[3]/ul/li[3]/sup/text()').extract()[0]
            item['price'] = price1 + price2
            print productnamelist
            yield item