#! /usr/bin/env python
# -*- coding: utf-8 -*-
import pymysql
import logging as log

from amazoncrawler.settings import (
    HOST,
    USER,
    PASSWD,
    DATABASE,
    PORT,
)

class DB:
    """ works only with spiders """
    def __init__(self, *args, **kwargs):
        self.conn = pymysql.connect(
            host=HOST,
            port=PORT,
            user=USER,
            password=PASSWD,
            database=DATABASE,
            cursorclass=pymysql.cursors.DictCursor,
        )
        self.cursor = self.conn.cursor()

    def init_urls(self):
        sql = "select link from url_links where crawled = 0;"
        self.cursor.execute(sql)
        result = self.cursor.fetchall()
        for data in result:
            self.start_urls.append("https://www.amazon.de"+data['link'])

    def close_spider(self, spider):
        self.cursor.close()
        self.conn.close()

    def __del__(self):
        try:
            self.cursor.close()
            self.conn.close()
        except Exception as e:
            log.info(str(e))


if __name__ == '__main__':
    pass

