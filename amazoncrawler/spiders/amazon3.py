import scrapy
from scrapy_splash import SplashRequest
from amazoncrawler.items import AmazonItems
from scrapy.loader import ItemLoader
import pymysql
import logging as log
import re
from util import log_crawled
from amazoncrawler.spiders.amazon4 import NO_FOLLOW
from amazoncrawler.model import DB


ASIN_RE = re.compile(r'.+asin=(.+?)&|.*?dp/(.+?)[/?.]|.*product/(.+?)[/?]|.*?dp/(.+)[/?.]?')


class Amazon3Spider(DB, scrapy.Spider):
    name = "amazon3"
    allowed_domains = ["www.amazon.de"]
    start_urls = [ ]

    def start_requests(self):
        self.init_urls()
        for url in self.start_urls:
            yield SplashRequest(url, callback=self.parse)

    def parse(self, response):
        more_urls = response.xpath(r'//a[@href]/@href').getall()
        if more_urls:
            for url in more_urls:
                if all(x not in url for x in NO_FOLLOW):
                    yield response.follow(url, callback=self.parse)
        item = ItemLoader(item=AmazonItems(), response=response)
        more_links = response.xpath(r'//*[contains(@href, "/dp/")]/@href').getall()
        if more_links:
            for link in more_links:
                if all(x not in link for x in NO_FOLLOW):
                    log.info('more link: %s'%link)
                    item.add_value('link', link)
                    self.nofollowpipe = True
                    yield item.load_item()
        seller_link = response.xpath(r'//a[contains(@id, "sellerProfile")]/@href').get()
        if seller_link:
            yield response.follow(seller_link, callback=self.parse_info)
        else:
            asin = self.get_asin(response)
            log.info('no seller link: %s'%asin)
            log_crawled(self.conn, self.cursor, asin)

    def get_asin(self, response):
        log.info('referer: %s'%response.request.headers.get('Referer'))
        asin_match = ASIN_RE.match(response.url) or ASIN_RE.match(str(response.request.headers.get('Referer')))
        return asin_match[1] or asin_match[2] or asin_match[3] or asin_match[4]

    def parse_si(self, response, item, is_cn):
        """ parse seller info """
        si = []
        ssi = list(z for z in (' '.join(y for y in re.split(r'\n|\xa0|\s', x) if y) for x in response.xpath(r'//div[contains(@id, "expander-about-seller")]/div').getall()) if z)
        text = ssi[0]
        for s in re.split(r'</?.?p>|</?.?br>', text):
            s.strip() and si.append(''.join(re.split(r'</?.*?>', s)))

        for t in si: # remove redundant text
            t_re = re.compile(r'.*?\.{3}.*')
            if t_re.match(t):
                index = si.index(t_re.match(t)[0])
                si = si[index+1:]
                break
        item.add_value('si_notes1' if not is_cn else 'cn_notes1', '\n'.join(x.replace(r'\n', '').replace('"', '\\"') for x in si if x))
        for i in range(len(si)):
            if re.match(r'Tel\.?:|Telefon:', si[i].strip()):
                item.add_value('si_phone' if not is_cn else 'cn_phone', si[i].split(':')[1].strip().replace(' ', ''))
            elif re.match(r'^Telefon$', si[i].strip()):
                item.add_value('si_phone' if not is_cn else 'cn_phone', si[i+1].strip().replace(' ', ''))
            elif re.match(r'E-Mail:', si[i].strip()):
                item.add_value('si_email' if not is_cn else 'cn_email', si[i].split(':')[1].strip())
            elif 'eMail' in si[i]:
                item.add_value('si_email' if not is_cn else 'cn_email', si[i+1].strip().replace(' ', ''))
            elif 'ustid' in si[i].lower():
                item.add_value('si_vat_id' if not is_cn else 'cn_vat_id', si[i].split(':')[1].strip())
            elif 'eingetragen im handelsregister des' in si[i].lower():
                try:
                    item.add_value('si_amtsgericht' if not is_cn else 'cn_amtsgericht', si[i].split('eingetragen im Handelsregister des')[1].strip())
                except Exception as e:
                    log.info("%s"%str(e))
            elif 'Handelsregister:' in si[i]:
                item.add_value('si_amtsgericht' if not is_cn else 'cn_amtsgericht', si[i].split('Handelsregister:')[1].strip())
            elif 'Registergericht:' in si[i]:
                item.add_value('si_amtsgericht' if not is_cn else 'cn_amtsgericht', si[i].split('Registergericht:')[1].strip())
            elif re.match(r'Tele.+?:', si[i]):
                item.add_value('si_phone' if not is_cn else 'cn_phone', re.split(r'Tele.+?:', si[i], flags=re.I)[1].strip())
            elif re.match(r'Geschäftsführer:|Inhaber:', si[i].strip()):
                item.add_value('si_business_owner' if not is_cn else 'cn_business_owner', si[i].split(':')[1].strip())
            elif re.match(r'.*Geschäftsführer', si[i].strip()):
                item.add_value('si_business_owner' if not is_cn else 'cn_business_owner', re.split(r'.*Geschäftsführer', si[i].strip())[1])

    def parse_dsi(self, response, item, is_cn):
        """ parse detailed seller info """
        dsi = list(z for z in (' '.join(y.strip() for y in x.replace('\n', '').split(' ') if y) for x in response.xpath(r'//div[contains(@id, "detail-seller-info")]//text()').getall()) if z)
        info = {}
        is_service = False
        is_business = False

        for i in range(len(dsi)):
            if 'Geschäftsname' in dsi[i]: info['businessname']= dsi[i+1]
            elif 'Geschäftsart' in dsi[i]: info['businesstype'] = dsi[i+1]
            elif 'Handelsregisternummer' in dsi[i]: info['trade_register_number']= dsi[i+1]
            elif 'ustid' in dsi[i].lower(): info['vat_number']= dsi[i+1]
            elif 'Telefonnummer' in dsi[i]: info['telephone']= dsi[i+1]
            elif 'E-Mail' in dsi[i]: info['email']= dsi[i+1]
            elif 'Kundendienstadresse' in dsi[i]:
                is_service = True
                info['customer_service_address']= ''
                continue
            elif "Handelsregister:" in dsi[i]:
                info['amtsgericht'] = dsi[i+1]
            elif 'eingetragen im Handelsregister des' in dsi[i]:
                info['amtsgericht'] = dsi[i]
            elif 'Geschäftsadresse' in dsi[i]:
                is_business = True
                info['business_address'] = ''
                continue
            if is_service:
                info['customer_service_address'] += ' '+dsi[i]
            if is_business:
                info['business_address'] += ' '+dsi[i]
            if re.match(r'^[A-Z]{2}$', dsi[i]):
                is_service = False
                is_business = False
                info['country'] = dsi[i]

        item.add_value('si_notes2' if not is_cn else 'cn_notes2', '\n'.join(x.replace(r'\n', '').replace('"', '\\"') for x in dsi if x))
        item.add_value('si_business_name' if not is_cn else 'cn_business_name', info.get('businessname'))
        item.add_value('si_business_type' if not is_cn else 'cn_business_type', info.get('businesstype'))
        item.add_value('si_amtsgericht' if not is_cn else 'cn_amtsgericht', info.get('amtsgericht'))
        item.add_value('si_trade_register_number' if not is_cn else 'cn_trade_register_number', info.get('trade_register_number'))
        item.add_value('si_vat_id' if not is_cn else 'cn_vat_id', info.get('vat_number'))
        item.add_value('si_phone' if not is_cn else 'cn_phone', info.get('telephone'))
        item.add_value('si_email' if not is_cn else 'cn_email', info.get('email'))
        item.add_value('si_customer_service_address' if not is_cn else 'cn_customer_service_address', info.get('customer_service_address'))
        item.add_value('si_business_address' if not is_cn else 'cn_business_address', info.get('business_address'))
        item.add_value('si_country' if not is_cn else 'cn_country', info.get('country'))

    def parse_info(self, response):
        item = ItemLoader(item=AmazonItems(), response=response)
        self.is_cn = is_cn  = bool(response.xpath(r'//span[contains(text(), "CN")]').get())
        self.asin = self.get_asin(response)
        item.add_value('si_detailed_link' if not is_cn else 'cn_detailed_link', response.url)
        item.add_xpath('si_store_name' if not is_cn else 'cn_store_name', r'//h1[@id="seller-name"]/text()')
        si_review = ' '.join([' '.join(y for y in (x.replace('\n', '').split(' ')) if y) for x in response.xpath(r'//div[contains(@id, "seller-info-feedback-summary")]//text()').getall()])
        num_si_review = re.match(r'.+\((\d+).+\)', si_review)
        item.add_value('si_review' if not is_cn else 'cn_review', num_si_review[1] if num_si_review else 0)
        self.parse_si(response, item, is_cn)
        self.parse_dsi(response, item, is_cn)
        self.nofollowpipe = False
        yield item.load_item()
