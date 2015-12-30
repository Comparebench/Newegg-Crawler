from sets import Set
from scrapy import Spider
from scrapy.http import Request
from scrapy.selector import Selector
from ..items import AresscrapeCPU


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
            item['newegg_sku'] = str(item['url']).replace("http://www.newegg.com/Product/Product.aspx?Item=", '')
            validprice = product.xpath('div[3]/ul/li[3]/strong/text()')
            productname = product.xpath('div[2]/div/a/span/text()').extract()[0].encode('utf-8', 'ignore')
            if 'Configurator' in productname:
                continue
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
            for url in urls:
                if url not in self.visitedURLs:
                    request = Request(url, callback=self.cpuproductpage)
                    request.meta['item'] = item
                    yield request

    def cpuproductpage(self, response):
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
        image = Selector(response).xpath('//*[@id="synopsis"]/div/div/div/a/span/img/@src').extract()
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
            item['cores'] = str(itemdict.get('# of Cores', None)).\
                replace("-Core", "").\
                replace("Dual", "2").\
                replace("Quad", "4")
            item['socket'] = str(itemdict.get('CPU Socket Type', None)).replace("Socket", "").replace("LGA", "").strip()
            yield item
