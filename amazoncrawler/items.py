# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class AmazonItems(scrapy.Item):
    # define the fields for your item here like:
    link = scrapy.Field()
    # pipeline2
    si_store_name = scrapy.Field()
    si_detailed_link = scrapy.Field()
    si_review = scrapy.Field()
    si_business_name = scrapy.Field()
    si_business_owner = scrapy.Field()
    si_business_type = scrapy.Field()
    si_amtsgericht = scrapy.Field()
    si_trade_register_number = scrapy.Field()
    si_vat_id = scrapy.Field()
    si_phone = scrapy.Field()
    si_phone2 = scrapy.Field()
    si_email = scrapy.Field()
    si_email2 = scrapy.Field()
    si_customer_service_address = scrapy.Field()
    si_business_address = scrapy.Field()
    si_country = scrapy.Field()
    si_notes1 = scrapy.Field()
    si_notes2 = scrapy.Field()

    # pipeline3
    # chinese seller
    cn_store_name = scrapy.Field()
    cn_detailed_link = scrapy.Field()
    cn_review = scrapy.Field()
    cn_business_name = scrapy.Field()
    cn_business_owner = scrapy.Field()
    cn_business_type = scrapy.Field()
    cn_amtsgericht = scrapy.Field()
    cn_trade_register_number = scrapy.Field()
    cn_vat_id = scrapy.Field()
    cn_phone = scrapy.Field()
    cn_phone2 = scrapy.Field()
    cn_email = scrapy.Field()
    cn_email2 = scrapy.Field()
    cn_customer_service_address = scrapy.Field()
    cn_business_address = scrapy.Field()
    cn_country = scrapy.Field()
    cn_notes1 = scrapy.Field()
    cn_notes2 = scrapy.Field()
