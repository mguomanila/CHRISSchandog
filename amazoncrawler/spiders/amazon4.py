import scrapy
from scrapy_splash import SplashRequest
from amazoncrawler.items import AmazonItems
from scrapy.loader import ItemLoader
from util import log_info

NO_FOLLOW = ['http://', 'https://', 'cookie', 'javascript', 'footer', "#"]

class Amazon4Spider(scrapy.Spider):
    name = "amazon4"
    allowed_domains = ["www.amazon.de"]
    start_urls = [
        "/gp/bestsellers/?ref_=nav_cs_bestsellers",
        "/stores/node/1686827031/?field-lbr_brands_browse-bin=AmazonBasics&ref_=nav_cs_amazonbasics",
        "/gp/angebote?ref_=nav_cs_gb",
        "/music/unlimited?ref_=nav_cs_music",
        "/gp/new-releases/?ref_=nav_cs_newreleases",
        "/b%C3%BCcher-buch-lesen/b/?ie=UTF8&node=186606&ref_=nav_cs_books",
        "/Video-Games/b/?ie=UTF8&node=300992&ref_=nav_cs_video_games",
        "/k%C3%BCche-haushalt-wohnen/b/?ie=UTF8&node=3167641&ref_=nav_cs_home",
        "/Elektronik-Foto/b/?ie=UTF8&node=562066&ref_=nav_cs_electronics",
        "/Amazon-Fashion-Mode/b/?ie=UTF8&node=11961464031&ref_=nav_cs_fashion",
        "/gcx/-/gfhz/?ref_=nav_cs_giftfinder",
    ]

    def start_requests(self):
        yield SplashRequest("https://www.amazon.de", callback=self.parse)
        for url in self.start_urls:
            yield SplashRequest("https://www.amazon.de"+url, callback=self.parse)

    def parse(self, response):
        item = ItemLoader(item=AmazonItems(), response=response)
        urls = response.xpath(r'//a[contains(@href, "/dp/")]/@href').getall()
        item.add_value('link', urls)
        self.nofollowpipe = True
        yield item.load_item()

        #urls = set(response.xpath(r'//a[contains(@href, "UTF8&node=") or contains(@class, "nav-a")]/@href').getall())
        for url in urls:
            if all(x not in url for x in NO_FOLLOW):
                yield response.follow(url, callback=self.parse)

