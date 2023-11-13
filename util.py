#! /usr/bin/env python
# -*- coding: utf-8 -*-
from scrapypuppeteer import PuppeteerHtmlResponse
import logging as log
import re


def filter_title(text):
    text_m = re.match(r'(.*).Amazon.de.((\w\s?)+):?', text)
    if text_m and text_m[1]:
        return text_m[1]
    if text_m and text_m[2]:
        return text_m[2]
    return 'amazoncrawl'


def log_info(response: PuppeteerHtmlResponse):
    #url = response.xpath(r'//a[contains(@id, "sellerProfile")]/@href').get()
    # url = response.xpath(r'//img[contains(@src, "captcha")]/@src').get()
    #log.info('captcha url: %s' % url)
    name = filter_title(response.xpath(r'//title/text()').get())
    with open(r'test/%s.html'%name, 'w') as f:
        f.write(str(response.body.decode('utf-8')))


# crawled logs
def log_crawled(conn, cursor, asin):
    log.info('log entry: %s'%asin)
    sql = 'update url_links set crawled = 1 where link regexp "{}"'
    cursor.execute(sql.format(asin))
    conn.commit()


if __name__ == '__main__':
    pass
