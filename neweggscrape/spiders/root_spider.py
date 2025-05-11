import scrapy


class NeweggSpider(scrapy.Spider):
    name = 'newegg_spider'
    handle_httpstatus_list = [404, 500]

    def parse(self, response):
        if response.status == 404:
            self.logger.error('Page not found: %s', response.url)
        elif response.status == 500:
            self.logger.error('Internal server error: %s', response.url)
        else:
            # Normal parsing code
            pass
