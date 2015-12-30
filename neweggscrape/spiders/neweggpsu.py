from sets import Set
from scrapy import Spider
from scrapy.http import Request
from scrapy.selector import Selector
from ..items import AresscrapePowersupply


class NeweggPowersupplySpider(Spider):
    name = "neweggpsu"
    allowed_domains = ['newegg.com']
    start_urls = [
        'http://www.newegg.com/Power-Supplies/SubCategory/ID-58/Page-%s?Pagesize=90'
        % page for page in xrange(1, 5)
    ]
    visitedURLs = Set()

    def parse(self, response):
        self.visitedURLs.add(response.url)
        products = Selector(response).xpath('//*[@class="itemCell"]')
        for product in products:
            item = AresscrapePowersupply()
            item['url'] = product.xpath('div[2]/div/a/@href').extract()[0]
            validprice = product.xpath('div[3]/ul/li[3]/strong/text()')
            # if price isnt found (example, 'view price in cart') skip the item entirely. Fuck you newegg.
            if not validprice:
                continue
            else:
                price1 = product.xpath('div[3]/ul/li[3]/strong/text()').extract()[0]
                price2 = product.xpath('div[3]/ul/li[3]/sup/text()').extract()[0]
                item['price'] = price1 + price2
            urls = Set([product.xpath('div[2]/div/a/@href').extract()[0]])
            print urls
            for url in urls:
                if url not in self.visitedURLs:
                    request = Request(url, callback=self.psuproductpage)
                    request.meta['item'] = item
                    yield request

    #  TODO: Update function to iterate through Specs fieldset
    def psuproductpage(self, response):
        specs = Selector(response).xpath('//*[@id="Specs"]')
        item = response.meta['item']
        for spec in specs:
            item['make'] = spec.xpath('fieldset[1]/dl[1]/dd/text()').extract()[0].encode('utf-8', 'ignore')
            item['model'] = spec.xpath('fieldset[1]/dl[2]/dd/text()').extract()[0].encode('utf-8', 'ignore')
            #item['modelname'] = spec.xpath('fieldset[1]/dl[3]/dd/text()').extract()[0].encode('utf-8', 'ignore')
            item['watt'] = spec.xpath('fieldset[2]/dl[2]/dd/text()').extract()[0].encode('latin-1', 'ignore').replace('Continuous', '')
        yield item