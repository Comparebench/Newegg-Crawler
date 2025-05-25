from scrapy.selector import Selector


def parse_base_details(item_type, product):
    item = item_type()
    item["url"] = product.css(".item-title").xpath("@href").get()
    item["newegg_sku"] = item["url"].split("/")[-1]
    item["price"] = product.css(".price-current").xpath("strong/text()").get()
    productname = product.css(".item-title").xpath("text()").get()
    if "Configurator" in productname:
        return None
    # if price isnt found (example, 'view price in cart') skip the item entirely. Fuck you newegg.
    if not item["price"]:
        return None
    # If product is refurb, skip.
    elif str(productname).startswith("Refurbished"):
        return None
    return item

def parse_product_page(response):
    itemdict = {}
    table_specs = Selector(response).xpath("//table")
    for spec in table_specs.xpath("tbody/tr"):
        if len(spec.xpath("td/text()").getall()) > 1:
            itemdict[spec.xpath("th/text()").get()] = spec.xpath("td/text()").getall()
        else:
            itemdict[spec.xpath("th/text()").get()] = spec.xpath("td/text()").get()
        print(spec)
    return itemdict
