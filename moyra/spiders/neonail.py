import re

import scrapy


def clean(data):
    data_cleaned = str(data).encode('ascii', errors='ignore').decode('unicode-escape')
    data_cleaned = data_cleaned.replace("\n", "")
    data_cleaned = data_cleaned.replace('\r', "")
    data_cleaned = data_cleaned.replace('\t', "")
    data_cleaned = data_cleaned.strip()
    return data_cleaned


def clean_attr(data):
    data_cleaned = data.replace('<p class="">', "")
    data_cleaned = data_cleaned.replace('<span class="hidden-xs">', "")
    data_cleaned = data_cleaned.replace('<span style=" color: #ff3399; font-weight: bold">', "")
    data_cleaned = data_cleaned.replace('</span>', "")
    data_cleaned = data_cleaned.replace('</p>', "")
    data_cleaned = data_cleaned.replace(':', "")
    return data_cleaned


def make_large_images(data):
    images = []
    for d in data:
        d = d.replace('/ProductPhotos/160x160/', "/ProductPhotos/Large/")
        images.append(d)
    return images


class NeonailSpider(scrapy.spiders.SitemapSpider):
    name = "neonail"
    sitemap_urls = ['https://www.neonail.be/ExportBestanden/SiteMap.php']

    def parse(self, response, **kwargs):
        title = response.xpath('//*[@id="Product"]/div[1]/div[2]/div[1]/div/span[1]/text()').get()
        short_description = response.xpath('//*[@id="Product"]/div[1]/div[2]/div[1]/div/p/text()').get()
        attr_1_name = response.xpath('//*[@id="AttributeCombinationInformation"]/div[1]/div/p').get()
        attr_2_name = response.xpath('//*[@id="AttributeCombinationInformation"]/div[2]/div/p').get()
        attr_3_name = response.xpath('//*[@id="AttributeCombinationInformation"]/div[3]/div/p').get()
        attr_4_name = response.xpath('//*[@id="AttributeCombinationInformation"]/div[4]/div/p').get()
        attr_1 = response.xpath('//*[@id="AttributeCombinationInformation"]/div[1]/span/p').get()
        attr_2 = response.xpath('//*[@id="AttributeCombinationInformation"]/div[2]/span/p').get()
        attr_3 = response.xpath('//*[@id="AttributeCombinationInformation"]/div[3]/span/p').get()
        attr_4 = response.xpath('//*[@id="AttributeCombinationInformation"]/div[4]/span/p').get()
        price_exc = response.xpath('//*[@id="Price1_exc"]/text()').get()
        price_inc = response.xpath('//*[@id="Price1_inc"]/text()').get()
        desc = response.xpath('//*[@id="tab-description"]/div[1]').get()
        main_image = response.xpath('//*[@id="zoom1"]/@src').get()
        images = response.xpath('//*[@id="ProductMedia_Thumbnails"]/div/a/img/@src').getall()
        crumb = response.xpath('//*[@class="martoni-crumb"]/a/text()').getall()
        breadcrumb = response.xpath('//*[@id="BreadCrumbs"]/li/a/text()').getall()
        categories = " > ".join(crumb) if len(crumb) != 0 else " > ".join(breadcrumb)
        if response.xpath('//*[@id="Product"]'):
            yield {
                "Title": clean(title),
                "Short description": clean(short_description),
                "Description": clean(re.sub('<a.*?>|</a> ', '', desc)),
                "Categories": categories,
                "Artikelnummer": clean(clean_attr(attr_1)) if attr_1_name else '',
                "Verwachte levertijd": clean(clean_attr(attr_2)) if attr_2_name else '',
                "Leveringstermijn": clean(clean_attr(attr_3)) if attr_3_name else '',
                "EAN": clean(clean_attr(attr_4)) if attr_4_name else '',
                "Price exc": clean(price_exc),
                "Price inc": clean(price_inc),
                "Images": make_large_images(images) if len(images) != 0 else main_image.replace('/ProductPhotos/MaxContent/', "/ProductPhotos/Large/"),
                "Url": response.request.url
            }