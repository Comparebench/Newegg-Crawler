import fnmatch
from scrapy import Spider
from scrapy.http import Request
from scrapy.selector import Selector

from .utils import parse_product_page, parse_base_details
from ..items import AresscrapeBoard


class NeweggAmdBoardSpider(Spider):
    name = "neweggamdboard"
    allowed_domains = ['newegg.com']
    start_urls = [
        'https://www.newegg.com/AMD-Motherboards/SubCategory/ID-22/Page-%s?PageSize=96'
        % page for page in range(1, 2)
    ]
    visitedURLs = set()

    def parse(self, response):
        if response.status == 400:
            print("BAD REQUEST")
        products = Selector(response).xpath('//*[@class="item-cell"]')
        for product in products:
            parsed_item = parse_base_details(AresscrapeBoard, product)
            if parsed_item and parsed_item["url"] not in self.visitedURLs:
                request = Request(parsed_item["url"], callback=self.boardproductpage)
                request.meta["item"] = parsed_item
                yield request

    def boardproductpage(self, response):
        itemdict = parse_product_page(response)
        item = response.meta["item"]
        image = (
            Selector(response).css(".swiper-zoom-container").xpath("./img/@src").get()
        )
        item["image_urls"] = image
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
            item['chipset'] = str(itemdict.get('Chipset', None)).replace("AMD ", "").strip()
            yield item
