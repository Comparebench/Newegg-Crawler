from scrapy import Spider
from scrapy.selector import Selector
from ..items import AresscrapeCase


#  TODO: Update Case spider to jump into URL instead of getting results from search page
class NeweggCaseSpider(Spider):
    name = "neweggcase"
    allowed_domains = ['newegg.com']
    start_urls = [
        'http://www.newegg.com/Desktop-Memory/SubCategory/ID-7'
    ]

    def parse(self, response):
        products = Selector(response).xpath('//*[@class="itemCell"]')
        for product in products:
            item = AresscrapeCase()
            productname = product.xpath('div[2]/div/a/span/text()').extract()[0].encode('utf-8', 'ignore')
            productnamelist = str(productname).split(' ')
            print(productnamelist)
            if 'Master' in productnamelist or 'WIN' in productnamelist:
                item['make'] = productnamelist[0] + ' ' + productnamelist[1]
                item['model'] = productnamelist[2] + ' ' + productnamelist[3]
            elif productnamelist[0] == 'Corsair':
                item['make'] = productnamelist[0]
                item['model'] = productnamelist[2] + ' ' + productnamelist[3] + ' ' + productnamelist[4]
            else:
                item['make'] = productnamelist[0]
                item['model'] = productnamelist[1] + ' ' + productnamelist[2]
            item['url'] = product.xpath('div[2]/div/a/@href').extract()[0]
            validmodel = product.xpath('div[2]/ul[2]/li[5]/text()')
            if not validmodel:
                continue
            else:
                item['modelname'] = product.xpath('div[2]/ul[2]/li[5]/text()').extract()[0]
            validprice = product.xpath('div[3]/ul/li[3]/strong/text()')
            # if price isnt found (example, 'view price in cart') skip the item entirely. Fuck you newegg.
            if not validprice:
                continue
            else:
                price1 = product.xpath('div[3]/ul/li[3]/strong/text()').extract()[0]
                price2 = product.xpath('div[3]/ul/li[3]/sup/text()').extract()[0]
                item['price'] = price1 + price2
            yield item