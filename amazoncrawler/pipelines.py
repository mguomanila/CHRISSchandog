# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html

# useful for handling different item types with a single interface
from itemadapter import ItemAdapter
import re
import logging as log
from util import log_crawled
from amazoncrawler.model import DB
from amazoncrawler.spiders.amazon3 import ASIN_RE

class AmazonPipeline1(DB):
    def __init__(self, *args, **kwargs):
        super().__init__(self, *args, **kwargs)
        log.info('running pipeline1...')

    def process_item(self, item, spider):
        if not spider.nofollowpipe: return item
        adapter = ItemAdapter(item)
        try:
            for link in adapter.get('link'):
                asin_match = ASIN_RE.match(link)
                asin= asin_match[1] or asin_match[2] or asin_match[3] or asin_match[4]
                log.info('save more link: %s'%asin)
                self.cursor.execute("insert into `url_links` (link, crawled) values ('/dp/%s/', %s)" % (asin, 0))
                self.conn.commit()
        except Exception as e:
            log.info ('pipeline1 except: '%str(e))
            if 'Duplicate' in str(e):
                log.info('duplicate dp')
        finally:
            return item


class AmazonPipeline2(DB):
    """ For International Sellers """
    def __init__(self, *args, **kwargs):
        super().__init__(self, *args, **kwargs)
        log.info('running pipeline2...')

    def process_item(self, item, spider):
        log.info('nofollowpipe: %s'%spider.nofollowpipe)
        if getattr(spider, 'nofollowpipe') or spider.is_cn: return item
        try:
            self.cursor.execute('select id from url_links where link regexp "%s"' % spider.asin)
            link = self.cursor.fetchone()
            sql = 'insert into seller_info(link_id, store_name, detailed_link, review, business_name, business_owner, business_type, amtsgericht, trade_register_number, vat_id, phone_number, phone_number2, email, email2, customer_service_address, business_address, country, notes1, notes2) values("%s", "%s", "%s", "%s", "%s", "%s", "%s", "%s", "%s", "%s", "%s", "%s", "%s", "%s", "%s", "%s", "%s", "%s", "%s")'%(
                link.get('id'),
                item.get("si_store_name") and item.get("si_store_name")[0] or '',
                item.get("si_detailed_link") and item.get("si_detailed_link")[0] or '',
                item.get("si_review") and item.get("si_review")[0] or 0,
                item.get('si_business_name') and item.get('si_business_name')[0] or '',
                item.get('si_business_owner') and item.get('si_business_owner')[0] or '',
                item.get('si_business_type') and item.get('si_business_type')[0] or '',
                item.get('si_amtsgericht') and item.get('si_amtsgericht')[0] or '',
                item.get('si_trade_register_number') and item.get('si_trade_register_number')[0] or '',
                item.get('si_vat_id') and item.get('si_vat_id')[0] or '',
                item.get('si_phone') and item.get('si_phone')[0] or '',
                item.get('si_phone2') and item.get('si_phone2')[0] or '',
                item.get('si_email') and item.get('si_email')[0] or '',
                item.get('si_email2') and item.get('si_email2')[0] or '',
                item.get('si_customer_service_address') and item.get('si_customer_service_address')[0] or '',
                item.get('si_business_address') and item.get('si_business_address')[0] or '',
                item.get('si_country') and item.get('si_country')[0] or '',
                item.get('si_notes1') and item.get('si_notes1')[0] or '',
                item.get("si_notes2") and item.get("si_notes2")[0] or '')
            log.info('sql %s'%sql)
            self.cursor.execute(sql)
            self.cursor.execute('update url_links set crawled = 1 where id = %s'%link['id'])
            self.conn.commit()
        except Exception as e:
            log.info('pipeline error: %s' % str(e))
            if "Duplicate entry" in str(e):
                log_crawled(self.conn, self.cursor, spider.asin)
        finally:
            return item


class AmazonPipeline3(DB):
    """ For Chinese Sellers """
    def __init__(self, *args, **kwargs):
        super().__init__(self, *args, **kwargs)
        log.info('running chinese pipeline...')

    def process_item(self, item, spider):
        log.info('nofollowpipe: %s'%spider.nofollowpipe)
        if getattr(spider, 'nofollowpipe') or not spider.is_cn: return item
        try:
            self.cursor.execute('select id from url_links where link regexp "%s"' % spider.asin)
            link = self.cursor.fetchone()
            log.info('link: %s' %link['id'])
            sql = 'insert into chinese_sellers(link_id, store_name, detailed_link, review, business_name, business_owner, business_type, amtsgericht, trade_register_number, vat_id, phone_number, phone_number2, email, email2, customer_service_address, business_address, country, notes1, notes2) values("%s", "%s", "%s", "%s", "%s", "%s", "%s", "%s", "%s", "%s", "%s", "%s", "%s", "%s", "%s", "%s", "%s", "%s", "%s")'%(
                link.get('id'),
                item.get("cn_store_name") and item.get("cn_store_name")[0] or '',
                item.get("cn_detailed_link") and item.get("cn_detailed_link")[0] or '',
                item.get("cn_review") and item.get("cn_review")[0] or 0,
                item.get('cn_business_name') and item.get('cn_business_name')[0] or '',
                item.get('cn_business_owner') and item.get('cn_business_owner')[0] or '',
                item.get('cn_business_type') and item.get('cn_business_type')[0] or '',
                item.get('cn_amtsgericht') and item.get('cn_amtsgericht')[0] or '',
                item.get('cn_trade_register_number') and item.get('cn_trade_register_number')[0] or '',
                item.get('cn_vat_id') and item.get('cn_vat_id')[0] or '',
                item.get('cn_phone') and item.get('cn_phone')[0] or '',
                item.get('cn_phone2') and item.get('cn_phone2')[0] or '',
                item.get('cn_email') and item.get('cn_email')[0] or '',
                item.get('cn_email2') and item.get('cn_email2')[0] or '',
                item.get('cn_customer_service_address') and item.get('cn_customer_service_address')[0] or '',
                item.get('cn_business_address') and item.get('cn_business_address')[0] or '',
                item.get('cn_country') and item.get('cn_country')[0] or '',
                item.get('cn_notes1') and item.get('cn_notes1')[0] or '',
                item.get("cn_notes2") and item.get("cn_notes2")[0] or '')
            log.info('sql %s'%sql)
            self.cursor.execute(sql)
            self.cursor.execute('update url_links set crawled = 1 where id = %s'%link['id'])
            self.conn.commit()
        except Exception as e:
            log.info('pipeline error: %s' % str(e))
            if "Duplicate entry" in str(e):
                log_crawled(self.conn, self.cursor, spider.asin)
        finally:
            return item


class DuplicatesPipeline:
    def process_item(self, item, spider):
        seen = set()
        emails = item.get('si_email')
        if emails:
            for mail in emails:
                seen.add(mail)
            item['si_email'] = list(seen)
            if len(seen) > 1:
                item['si_email'] = [seen.pop()]
                item['si_email2'] = [seen.pop()]
            seen = set()
        emails = item.get('cn_email')
        if emails:
            for mail in emails:
                seen.add(mail)
            item['cn_email'] = list(seen)
            if len(seen) > 1:
                item['cn_email'] = [seen.pop()]
                item['cn_email2'] = [seen.pop()]
            seen = set()
        phones = item.get('si_phone')
        if phones:
            for phone in phones:
                seen.add(phone)
            if len(seen) > 1:
                item['si_phone'] = [seen.pop()]
                item['si_phone2'] = [seen.pop()]
            seen = set()
        phones = item.get('cn_phone')
        if phones:
            for phone in phones:
                seen.add(phone)
            if len(seen) > 1:
                item['cn_phone'] = [seen.pop()]
                item['cn_phone2'] = [seen.pop()]
            seen = set()
        return item



