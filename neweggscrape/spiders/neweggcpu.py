import logging

from scrapy import Spider
from scrapy.http import Request
from scrapy.selector import Selector

from ..items import AresscrapeCPU
SKIP_SOCKETS = [
    'LGA 1700'
]

class NeweggCPUSpider(Spider):
    name = "neweggcpu"
    allowed_domains = ["newegg.com"]
    start_urls = [
        "https://www.newegg.com/Desktop-CPU-Processor/SubCategory/ID-343/Page-%s?PageSize=96"
        % page
        for page in range(1, 2)
    ]
    visitedURLs = set()

    def parse(self, response):
        if response.status == 400:
            print("BAD REQUEST")
        products = Selector(response).xpath('//*[@class="item-cell"]')
        for product in products:
            item = AresscrapeCPU()
            item["url"] = product.css(".item-title").xpath("@href").get()
            item["newegg_sku"] = item["url"].split("/")[-1]
            item["price"] = product.css(".price-current").xpath("strong/text()").get()
            productname = product.css(".item-title").xpath("text()").get()
            if "Configurator" in productname:
                continue
            # if price isnt found (example, 'view price in cart') skip the item entirely. Fuck you newegg.
            if not item["price"]:
                continue
            # If product is refurb, skip.
            elif str(productname).startswith("Refurbished"):
                continue
            if item["url"] not in self.visitedURLs:
                request = Request(item["url"], callback=self.cpuproductpage)
                request.meta["item"] = item
                yield request

    def cpuproductpage(self, response):
        # specs = Selector(response).xpath('//*[@id="Specs"]/fieldset')
        # specs = Selector(response).css("#product-details").xpath("//table")[1]
        # table_specs = Selector(response).css("#product-details").xpath("//table//tr")

        itemdict = {}
        table_specs = Selector(response).xpath("//table")
        for spec in table_specs.xpath("tbody/tr"):
            if len(spec.xpath("td/text()").getall()) > 1:
                itemdict[spec.xpath("th/text()").get()] = spec.xpath("td/text()").getall()
            else:
                itemdict[spec.xpath("th/text()").get()] = spec.xpath("td/text()").get()
            print(spec)
        item = response.meta["item"]
        image = (
            Selector(response).css(".swiper-zoom-container").xpath("./img/@src").get()
        )
        # If the product doesnt have a model or brand, don't do anything with it.
        if "Name" not in itemdict or "Brand" not in itemdict:
            yield None
        else:
            validated = validate_cpu(itemdict['CPU Socket Type'])
            if not validated:
                return
            # image_urls passes image data to S3 pipeline
            item["image_urls"] = image
            item["make"] = itemdict["Brand"]
            item["model"] = itemdict["Name"]
            try:
                if type(itemdict["Max Turbo Frequency"]) == list:
                    for freq in itemdict["Max Turbo Frequency"]:
                        if "E-core Max Turbo" in freq:
                            item["freq"] = get_frequency(freq)
                        elif "P-core Max Turbo Frequency" in freq:
                            item["turbo"] = get_frequency(freq)
                        elif "Intel Turbo Boost Max" in freq:
                            item["turbo"] = get_frequency(freq)
                        item["freq"] = get_frequency
                else:
                    item["freq"] = get_frequency(itemdict["Operating Frequency"])
                    item["turbo"] = get_frequency(itemdict["Max Turbo Frequency"])
            except Exception as e:
                logging.info(e)
            item["die_size"] = itemdict.get("Manufacturing Tech", None)
            item["lanes"] = itemdict.get("Max Number of PCI Express Lanes", None)
            item["threads"] = itemdict.get("# of Threads", "").replace("-Threads", "")
            item["l2"] = itemdict.get("L2 Cache", "").split("MB")[0]
            item["l3"] = itemdict.get("L3 Cache", "").split("MB")[0]
            item["cores"] = (
                str(itemdict.get("# of Cores", None))
                .replace("-Core", "")
                .replace("Dual", "2")
                .replace("Quad", "4")
            )
            item["socket"] = (
                str(itemdict.get("CPU Socket Type", None))
                .replace("Socket", "")
                .replace("LGA", "")
                .strip()
            )
            yield item

def validate_cpu(socket):
    if socket in SKIP_SOCKETS:
        return False
    else:
        return True

def get_frequency(frequency_value):
    return int(
        float(
            frequency_value.lower()
            .replace("ghz", "")
            .replace("up to", "")
            .replace("intel turbo boost max technology 3.0 frequency:", "")
            .replace("p-core max turbo frequency:", "")
            .replace("e-core max turbo frequency:", "")
            .strip()
        )
        * 1000
    )
