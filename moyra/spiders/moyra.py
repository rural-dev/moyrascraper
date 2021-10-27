import scrapy


def clean(data):
    data_clened = str(data).encode('ascii', errors='ignore').decode('unicode-escape')
    data_clened = data_clened.replace("\n", "")
    data_clened = data_clened.replace('\r', "")
    data_clened = data_clened.replace('\t', "")
    data_clened = data_clened.strip()
    return data_clened


class MoyraSpider(scrapy.Spider):
    name = "moyra"

    def start_requests(self):
        urls = [
            'https://www.nagelproduct.nl/c-4683493/moyra/'
        ]
        for url in urls:
            yield scrapy.Request(url=url, callback=self.parse_categories)

    def parse_categories(self, response, **kwargs):
        categories = response.xpath('//*[@id="centercolumn"]/div/table/tr/td/p/a/@href').getall()

        for category in categories:
            print("Scraping Category: ", category)
            yield scrapy.Request(url=category, callback=self.parse_products, cb_kwargs={"category_title": None})

    def parse_products(self, response, **kwargs):
        title = clean(response.xpath('//title/text()').get().split('|')[0])
        category_title = f'{kwargs["category_title"]} > {title}' if kwargs["category_title"] else title
        sub_categories = response.xpath('//*[@id="centercolumn"]/div/div/ul/li/a/@href').getall()
        products = response.xpath('//*[@class="products list"]/li/span[2]/div/a/@href').getall()
        if response.xpath('//*[@class="products list"]'):
            for product in products:
                print("Scraping Product: ", product)
                yield scrapy.Request(url=product, callback=self.parse_product, cb_kwargs={"category_title": category_title, "url": product})

        # Scraping subcategories if there are subcategories
        else:
            for sub_category in sub_categories:
                print("Scraping Subcategory: ", sub_category)
                yield scrapy.Request(url=sub_category, callback=self.parse_products, cb_kwargs={"category_title": category_title})

    def parse_product(self, response, **kwargs):
        title = response.xpath('//*[@class="product-title"]/text()').get()
        original_price = response.xpath('//*[@class="original_price"]/i/text()').get()
        original_price_sup = response.xpath('//*[@class="original_price"]/i/sup/text()').get()
        sale_price = response.xpath('//*[@class="pricetag"]/*[@class="action"]/text()').get()
        sale_price_sup = response.xpath('//*[@class="pricetag"]/*[@class="action"]/sup/text()').get()
        regular_price = response.xpath('//*[@class="pricetag"]/*[@class="regular"]/text()').get()
        regular_price_sup = response.xpath('//*[@class="pricetag"]/*[@class="regular"]/sup/text()').get()
        large_images = response.xpath('//*[@class="images"]/div/a/img/@src').getall()
        thumbs = response.xpath('//*[@class="thumbs"]/li/a/img/@src').getall()
        images = large_images + thumbs
        desc = response.xpath('//*[@class="rte_content fullwidth"]/*').getall()
        short_description = response.xpath('//*[@class="rte_content fullwidth"]/*/text()').get()
        description = "".join(desc)

        yield {
            "title": clean(title),
            "short_description": clean(short_description) if short_description else '',
            "description": description,
            "category": clean(kwargs["category_title"]),
            "original_price": clean(original_price + original_price_sup) if original_price else '',
            "sale_price": clean(sale_price + sale_price_sup) if sale_price else '',
            "regular_price": clean(regular_price + regular_price_sup) if regular_price else '',
            "images": images,
            "url": kwargs["url"]
        }