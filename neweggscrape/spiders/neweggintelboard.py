import fnmatch
from sets import Set
from scrapy import Spider
from scrapy.http import Request
from scrapy.selector import Selector
from ..items import AresscrapeBoard


class NeweggIntelBoardSpider(Spider):
    name = "neweggintelboard"
    allowed_domains = ['newegg.com']
    start_urls = [
        'http://www.newegg.com/Intel-Motherboards/SubCategory/ID-280/Page-%s?Pagesize=90'
        % page for page in xrange(1, 5)
    ]
    visitedURLs = Set()

    def parse(self, response):
        products = Selector(response).xpath('//*[@class="itemCell"]')
        for product in products:
            item = AresscrapeBoard()
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
                    request = Request(url, callback=self.boardproductpage)
                    request.meta['item'] = item
                    yield request

    def boardproductpage(self, response):
        specs = Selector(response).xpath('//*[@id="Specs"]/fieldset')
        itemdict = {}
        for i in specs:
            test = i.xpath('dl')
            for t in test:
                name = t.xpath('dt/text()').extract()[0]
                if name == ' ':
                    name = t.xpath('dt/a/text()').extract()[0]
                itemdict[name] = t.xpath('dd/text()').extract()[0]
        item = response.meta['item']
        if 'Model' not in itemdict or 'Brand' not in itemdict:
            yield None
        else:
            item['make'] = itemdict['Brand']
            item['model'] = itemdict['Model']
            ramlist = str(itemdict['Memory Standard']).split(" ")
            ram = fnmatch.filter(ramlist, "DDR?")
            if ram:
                item['ram_type'] = ram[0]
            else:
                item['ram_type'] = None
            item['socket'] = str(itemdict.get('CPU Socket Type', None)).replace("Socket", "").replace("LGA", "").strip()
            item['chipset'] = str(itemdict.get('Chipset', None)).replace("Intel ", "").strip()
            yield item
