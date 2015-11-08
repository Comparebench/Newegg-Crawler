# Newegg-Crawler

Newegg-Crawler uses [Scrapy](http://scrapy.org/) to crawl Newegg result and product pages.
 
Once Scrapy is installed, you can scrape the following Newegg searches using `scrapy crawl X` where X is the crawler.

* `neweggcpu` Processors

* `neweggintelboard` Intel motherboards

* `neweggram` Memory

* `newegggpu` GPUs

* `neweggcase` Cases

* `newegghdd` Hard Drives (not SSDs)

* `neweggpsu` Power Supplies

This crawler will also place an image of the product in an S3 bucket you designate in settings.py. You can specify sizes with:

```
IMAGES_THUMBS = {
    'small': (50, 50),
    'big': (300, 300)
}
```

This will place a 50x50 size image of the product in the "small" folder in your bucket, and a 300x300 size image in your "big" folder. 
It will also (by default) place the original file in the folder, "full".