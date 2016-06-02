# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

from scrapy.item import Field, Item


class AresscrapeCPU(Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    make = Field()
    model = Field()
    url = Field()
    newegg_sku = Field()
    price = Field()
    socket = Field()
    freq = Field()
    l2 = Field()
    l3 = Field()
    cores = Field()
    turbo = Field()
    die_size = Field()
    lanes = Field()
    threads = Field()
    updated_ts = Field()
    created_ts = Field()
    image_urls = Field()
    images = Field()


class AresscrapeBoard(Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    make = Field()
    model = Field()
    url = Field()
    price = Field()
    socket = Field()
    chipset = Field()
    ram_type = Field()


class AresscrapeMemory(Item):
    make = Field()
    model = Field()
    modelname = Field()
    url = Field()
    price = Field()
    type = Field()
    size = Field()
    modules = Field()


class AresscrapeGPU(Item):
    make = Field()
    model = Field()
    modelname = Field()
    url = Field()
    price = Field()
    bus_size = Field()
    ram = Field()
    freq = Field()
    newegg_sku = Field()
    created_ts = Field()
    updated_ts = Field()
    image_urls = Field()
    images = Field()


class AresscrapeCase(Item):
    make = Field()
    model = Field()
    modelname = Field()
    url = Field()
    price = Field()
    created_ts = Field()
    updated_ts = Field()


class AresscrapeStorage(Item):
    make = Field()
    model = Field()
    modelname = Field()
    form_factor = Field()
    size = Field()
    type = Field()
    url = Field()
    price = Field()
    max_seq_read = Field()
    max_seq_write = Field()
    k_ran_read = Field()
    k_ran_write = Field()
    controller = Field()
    image_urls = Field()
    images = Field()
    created_ts = Field()
    updated_ts = Field()


class AresscrapePowersupply(Item):
    make = Field()
    model = Field()
    watt = Field()
    url = Field()
    price = Field()
    created_ts = Field()
    updated_ts = Field()