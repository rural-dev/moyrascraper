import scrapy


def clean(data):
    data_clened = str(data).encode('ascii', errors='ignore').decode('unicode-escape')
    data_clened = data_clened.replace("\n", "")
    data_clened = data_clened.replace('\r', "")
    data_clened = data_clened.replace('\t', "")
    data_clened = data_clened.strip()
    return data_clened


class PNSSpider(scrapy.Spider):
    name = "pns"

    def start_requests(self):
        urls = [
            'https://www.nagelproduct.nl/c-4683493/moyra/'
        ]
        for url in urls:
            yield scrapy.Request(url=url, callback=self.parse_categories)

    def parse_categories(self, response, **kwargs):
        categories = response.xpath('//*[@id="centercolumn"]/div/table/tr/td//a/@href').getall()

        for idx, category in enumerate(categories):
            print("Scraping Category: ", category)
            yield scrapy.Request(url=category, callback=self.parse_products, cb_kwargs={"category_title": None, "category_idx": idx + 1})

    def parse_products(self, response, **kwargs):
        title = clean(response.xpath('//title/text()').get().split('|')[0])
        if "next" in kwargs:
            category_title = kwargs["category_title"]
        else:
            category_title = f'{kwargs["category_title"]} > {title}' if kwargs["category_title"] else title

        sub_categories = response.xpath('//*[@id="centercolumn"]/div/div/ul/li/a/@href').getall()
        products = response.xpath('//ul/li/span/div/a/@href').getall()
        next = response.xpath('//a[@class="next"]/@href').get()

        # Scraping subcategories if there are subcategories
        if len(sub_categories) > 0:
            for idx, sub_category in enumerate(sub_categories):
                print("Scraping Subcategory: ", sub_category)
                category_idx = kwargs["category_idx"]
                sub_category_idx = idx + 1
                yield scrapy.Request(url=sub_category,
                                     callback=self.parse_products,
                                     cb_kwargs={"category_title": category_title,
                                                "category_idx": category_idx,
                                                "sub_category_idx": sub_category_idx
                                                },
                                     )

        else:
            for idx, product in enumerate(products):
                page = response.xpath('//a[@class="active"]/text()').get()
                print("Scraping Product: ", product)
                sub_category_idx = kwargs['sub_category_idx'] if "sub_category_idx" in kwargs else None
                yield scrapy.Request(url=product, callback=self.parse_product,
                                     cb_kwargs={"category_title": category_title,
                                                "category_idx": kwargs['category_idx'],
                                                "sub_category_idx": sub_category_idx,
                                                "category_url": response.request.url,
                                                "page": page,
                                                "url": product,
                                                "product_idx": idx + 1})

        if next:
            yield scrapy.Request(url=next,
                                 callback=self.parse_products,
                                 cb_kwargs={"category_title": category_title,
                                            "category_idx": kwargs['category_idx'],
                                            "url": next,
                                            "next": True})

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
            "category_idx": clean(kwargs["category_idx"]),
            "sub_category_idx": clean(kwargs["sub_category_idx"]),
            "category_url": clean(kwargs["category_url"]),
            "page": kwargs["page"],
            "product_idx": kwargs['product_idx'],
            "original_price": clean(original_price + original_price_sup) if original_price else '',
            "sale_price": clean(sale_price + sale_price_sup) if sale_price else '',
            "regular_price": clean(regular_price + regular_price_sup) if regular_price else '',
            "images": images,
            "url": kwargs["url"]
        }