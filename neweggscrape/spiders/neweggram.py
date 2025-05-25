from scrapy.http import Request

from scrapy import Spider
from scrapy.selector import Selector

from .utils import parse_base_details, parse_product_page
from ..items import AresscrapeMemory


class NeweggRamSpider(Spider):
    name = "neweggram"
    allowed_domains = ['newegg.com']
    start_urls = [
        "https://www.newegg.com/Desktop-Memory/SubCategory/ID-147/Page-%s?PageSize=96"
        % page
        for page in range(2, 6)
    ]
    visitedURLs = set()

    def parse(self, response):
        if response.status == 400:
            print("BAD REQUEST")
        products = Selector(response).xpath('//*[@class="item-cell"]')
        for product in products:
            parsed_item = parse_base_details(AresscrapeMemory, product)
            if parsed_item and parsed_item["url"] not in self.visitedURLs:
                request = Request(parsed_item["url"], callback=self.memoryproductpage)
                request.meta["item"] = parsed_item
                yield request


    def memoryproductpage(self, response):
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
            if "ddr5" in itemdict['Speed'].lower():
                item['ram_type'] = "DDR5"
            if "ddr4" in itemdict['Speed'].lower():
                item['ram_type'] = "DDR4"
            item['speed'] = itemdict['Speed'].split(item['ram_type'])[1].split("(")[0].strip()
            item['timing'] = itemdict['Timing']
            item['voltage'] = itemdict['Voltage']
            if " x " in itemdict['Capacity']:
                # Multi-stick kit
                split_capacity_title = itemdict['Capacity'].split(" x ")
                num_modules = split_capacity_title[0][-1]
                total_capacity = split_capacity_title[0].split(" ")[0].split("GB")[0]
                dimm_size = int(int(total_capacity)/int(num_modules))
                item['capacity'] = int(total_capacity)
                item['dimm_size'] = dimm_size
                item['modules'] = int(num_modules)
            else:
                # single dimm product
                item['capacity'] = itemdict['Capacity']
                item['dimm_size'] = itemdict['Capacity']
                item['modules'] = 1
            yield item