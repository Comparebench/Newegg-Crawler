from scrapy import Spider
from scrapy.selector import Selector

from ..items import AresscrapeGPU


#  TODO: Update GPU spider to jump into URL instead of getting results from search page
class NeweggGPUSpider(Spider):
    name = "newegggpu"
    allowed_domains = ['newegg.com']
    start_urls = [
        'http://www.newegg.com/Desktop-Memory/SubCategory/ID-48'
    ]

    def parse(self, response):
        products = Selector(response).xpath('//*[@class="itemCell"]')
        for product in products:
            item = AresscrapeGPU()
            productname = product.xpath('div[2]/div/a/span/text()').extract()[0].encode('utf-8', 'ignore')
            productnamelist = str(productname).split(' ')
            print productnamelist
            item['make'] = productnamelist[0]
            if 'GDDR5' in productnamelist:
                item['bus_size'] = productnamelist[productnamelist.index('GDDR5') - 1]
                item['ram'] = productnamelist[productnamelist.index('GDDR5') - 2]
            elif 'DDR5' in productnamelist:
                item['bus_size'] = productnamelist[productnamelist.index('DDR5') - 1]
                item['ram'] = productnamelist[productnamelist.index('DDR5') - 2]
            item['url'] = product.xpath('div[2]/div/a/@href').extract()[0]
            validmodel = product.xpath('div[2]/ul[2]/li[5]/text()')
            if not validmodel:
                continue
            else:
                item['modelname'] = product.xpath('div[2]/ul[2]/li[5]/text()').extract()[0]
            if 'GeForce' in productnamelist:
                item['model'] = productnamelist[productnamelist.index('GeForce')] + ' ' + productnamelist[productnamelist.index('GeForce') + 1] + ' ' + productnamelist[productnamelist.index('GeForce') + 2]
            elif 'Radeon' in productnamelist:
                item['model'] = productnamelist[productnamelist.index('Radeon')] + ' ' + productnamelist[productnamelist.index('Radeon') + 1] + ' ' + productnamelist[productnamelist.index('Radeon') + 2]
            validprice = product.xpath('div[3]/ul/li[3]/strong/text()')
            # if price isnt found (example, 'view price in cart') skip the item entirely. Fuck you newegg.
            if not validprice:
                continue
            else:
                price1 = product.xpath('div[3]/ul/li[3]/strong/text()').extract()[0]
                price2 = product.xpath('div[3]/ul/li[3]/sup/text()').extract()[0]
                item['price'] = price1 + price2
            yield item