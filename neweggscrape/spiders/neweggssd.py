from scrapy import Spider
from scrapy.http import Request
from scrapy.selector import Selector
from ..items import AresscrapeStorage


class NeweggSsdSpider(Spider):
    name = "neweggssd"
    allowed_domains = ['newegg.com']
    start_urls = [
        'http://www.newegg.com/Internal-SSDs/SubCategory/ID-636/Page-%s?Pagesize=90'
        % page for page in range(1, 8)
    ]
    visitedURLs = set()

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
            urls = {product.xpath('div[2]/div/a/@href').extract()[0]}
            print(urls)
            for url in urls:
                if url not in self.visitedURLs:
                    request = Request(url, callback=self.ssdproductpage)
                    request.meta['item'] = item
                    yield request

    #  TODO: Update function to get images
    def ssdproductpage(self, response):
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
            item['image_urls'] = image
            item['form_factor'] = itemdict['Form Factor']
            item['make'] = itemdict['Brand']
            item['modelname'] = getattr(itemdict, 'Model', None)
            if 'Series' not in itemdict:
                item['model'] = getattr(itemdict, 'Model', None)
            else:
                item['model'] = itemdict['Series']
            item['size'] = itemdict['Capacity']
            item['max_seq_read'] = itemdict['Max Sequential Read']
            item['max_seq_write'] = itemdict['Max Sequential Write']
            item['k_ran_read'] = itemdict['4KB Random Read']
            item['k_ran_write'] = itemdict['4KB Random Write']
            item['controller'] = getattr(itemdict, 'Controller', None)
        yield item
