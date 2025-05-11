from scrapy import Spider
from scrapy.selector import Selector
from ..items import AresscrapeGPU
from scrapy.http import Request



class NeweggGPUSpider(Spider):
    name = "newegggpu"
    allowed_domains = ['newegg.com']
    start_urls = [
        'http://www.newegg.com/Desktop-Memory/SubCategory/ID-48/Page-%s?Pagesize=90' % page for page in range(1, 5)
    ]
    visitedURLs = set()

    def parse(self, response):
        products = Selector(response).xpath('//*[@class="itemCell"]')
        for product in products:
            item = AresscrapeGPU()
            item['url'] = product.xpath('div[2]/div/a/@href').extract()[0]
            item['newegg_sku'] = str(item['url']).replace("http://www.newegg.com/Product/Product.aspx?Item=", '')
            validprice = product.xpath('div[3]/ul/li[3]/strong/text()')
            # if price isnt found (example, 'view price in cart') skip the item entirely. Fuck you newegg.
            if not validprice:
                continue
            else:
                price1 = product.xpath('div[3]/ul/li[3]/strong/text()').extract()[0]
                price2 = product.xpath('div[3]/ul/li[3]/sup/text()').extract()[0]
                item['price'] = price1 + price2
            urls = {product.xpath('div[2]/div/a/@href').extract()[0]}
            for url in urls:
                if url not in self.visitedURLs:
                    request = Request(url, callback=self.gpuproductpage)
                    request.meta['item'] = item
                    yield request

    def gpuproductpage(self, response):
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
        if 'Brand' not in itemdict:
            yield None
        else:
            # image_urls passes image data to S3 pipeline
            item['image_urls'] = image
            item['make'] = itemdict['Brand']
            item['model'] = itemdict['GPU']
            item['modelname'] = itemdict['Model']
            item['ram'] = itemdict['Memory Size']
            item['bus_size'] = itemdict['Memory Interface']
            item['freq'] = itemdict['Core Clock']
            #print item
            yield item
