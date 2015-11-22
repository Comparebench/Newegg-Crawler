import fnmatch
from sets import Set
from scrapy import Spider
from scrapy.http import Request
from scrapy.selector import Selector
from scrapy.spiders import Rule, CrawlSpider
from scrapy.contrib.linkextractors import LinkExtractor

from ..items import AresscrapeCPU, AresscrapeBoard, AresscrapeMemory, AresscrapeGPU, AresscrapeCase, AresscrapeStorage, \
    AresscrapePowersupply
import timeit


class NeweggCPUSpider(Spider):
    name = "neweggcpu"
    allowed_domains = ["newegg.com"]
    start_urls = [
        "http://www.newegg.com/Processors-Desktops/SubCategory/ID-343/Page-%s?Pagesize=90"
        % page for page in xrange(1, 5)
    ]
    visitedURLs = Set()

    def parse(self, response):
        products = Selector(response).xpath('//*[@class="itemCell"]')
        for product in products:
            item = AresscrapeCPU()
            item['url'] = product.xpath('div[2]/div/a/@href').extract()[0]
            validprice = product.xpath('div[3]/ul/li[3]/strong/text()')
            productname = product.xpath('div[2]/div/a/span/text()').extract()[0].encode('utf-8', 'ignore')
            # if price isnt found (example, 'view price in cart') skip the item entirely. Fuck you newegg.
            if not validprice:
                continue
            # If product is refurb, skip.
            elif str(productname).startswith('Refurbished'):
                continue
            else:
                price1 = product.xpath('div[3]/ul/li[3]/strong/text()').extract()[0]
                price2 = product.xpath('div[3]/ul/li[3]/sup/text()').extract()[0]
                item['price'] = price1 + price2
            urls = Set([product.xpath('div[2]/div/a/@href').extract()[0]])
            print urls
            for url in urls:
                if url not in self.visitedURLs:
                    request = Request(url, callback=self.cpuproductpage)
                    request.meta['item'] = item
                    yield request

    def cpuproductpage(self, response):
        specs = Selector(response).xpath('//*[@id="Specs"]/fieldset')
        itemdict = {}
        print specs
        for i in specs:
            test = i.xpath('dl')
            for t in test:
                name = t.xpath('dt/text()').extract()[0]
                if name == ' ':
                    name = t.xpath('dt/a/text()').extract()[0]
                itemdict[name] = t.xpath('dd/text()').extract()[0]
        print itemdict
        item = response.meta['item']
        image = Selector(response).xpath('//*[@id="synopsis"]/div/div/div/a/span/img/@src').extract()
        print image
        if image:
            image = [image[0].replace("?$S300W$", "").replace("?$S300$", "")]
        # If the product doesnt have a model or brand, don't do anything with it.
        if 'Name' not in itemdict or 'Brand' not in itemdict:
            yield None
        else:
            # image_urls passes image data to S3 pipeline
            item['image_urls'] = image
            item['make'] = itemdict['Brand']
            item['model'] = itemdict['Name']
            item['freq'] = itemdict['Operating Frequency']
            item['turbo'] = itemdict.get('Max Turbo Frequency', None)
            item['die_size'] = itemdict.get('Manufacturing Tech', None)
            item['lanes'] = itemdict.get('Max Number of PCI Express Lanes', None)
            item['threads'] = itemdict.get('# of Threads', None)
            item['l2'] = itemdict.get('L2 Cache', None)
            item['l3'] = itemdict.get('L3 Cache', None)
            item['socket'] = str(itemdict.get('CPU Socket Type', None)).replace("Socket", "").replace("LGA", "")
            yield item


class NeweggBoardSpider(Spider):
    name = "neweggintelboard"
    allowed_domains = ['newegg.com']
    start_urls = [
        'http://www.newegg.com/Intel-Motherboards/SubCategory/ID-280'
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
        #print specs
        for i in specs:
            test = i.xpath('dl')
            for t in test:
                name = t.xpath('dt/text()').extract()[0]
                if name == ' ':
                    name = t.xpath('dt/a/text()').extract()[0]
                itemdict[name] = t.xpath('dd/text()').extract()[0]
        print itemdict
        item = response.meta['item']
        if 'Model' not in itemdict or 'Brand' not in itemdict:
            yield None
        else:
            item['make'] = itemdict['Brand']
            item['model'] = itemdict['Model']
            ramlist = str(itemdict['Memory Standard']).split(" ")
            ram = fnmatch.filter(ramlist, "DDR?")
            print ram
            if ram:
                item['ram_type'] = ram[0]
            else:
                item['ram_type'] = None
            if 'CPU Socket Type' in itemdict:
                item['socket'] = str(itemdict['CPU Socket Type']).replace("Socket", "")
            if 'Chipset' in itemdict:
                item['chipset'] = str(itemdict['Chipset']).replace("Intel ", "")
            yield item

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
            print productnamelist
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


class NeweggHarddriveSpider(Spider):
    name = "newegghdd"
    allowed_domains = ['newegg.com']
    start_urls = [
        'http://www.newegg.com/All-Desktop-Hard-Drives/SubCategory/ID-14'
    ]
    visitedURLs = Set()

    def parse(self, response):
        self.visitedURLs.add(response.url)
        products = Selector(response).xpath('//*[@class="itemCell"]')
        for product in products:
            item = AresscrapeStorage()
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
                    request = Request(url, callback=self.hddproductpage)
                    request.meta['item'] = item
                    yield request

    #  TODO: Update function to get images
    def hddproductpage(self, response):
        fieldsets = Selector(response).xpath('//*[@id="Specs"]/fieldset')
        itemdict = {}
        for i in fieldsets:
            titles = i.xpath('dl')
            for t in titles:
                name = t.xpath('dt/text()').extract()[0]
                if name is not None:
                    if name == ' ':
                        try:
                            name = t.xpath('dt/a/text()').extract()[0]
                        except:
                            pass
                    itemdict[name] = t.xpath('dd/text()').extract()[0]
                else:
                    yield None
        item = response.meta['item']
        image = Selector(response).xpath('//*[@id="synopsis"]/div/div/div/a/span/img/@src').extract()
        if image:
            image = [image[0].replace("?$S300W$", "").replace("?$S300$", "")]
        # If the product doesnt have a model or brand, don't do anything with it.
        if 'Brand' not in itemdict:
            yield None
        else:
            item['make'] = itemdict['Brand']

            item['modelname'] = itemdict['Model']
            if 'Series' not in itemdict:
                item['model'] = itemdict['Model']
            else:
                item['model'] = itemdict['Series']
            item['size'] = itemdict['Capacity']
        yield item


class NeweggPowersupplySpider(Spider):
    name = "neweggpsu"
    allowed_domains = ['newegg.com']
    start_urls = [
        'http://www.newegg.com/Power-Supplies/SubCategory/ID-58'
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