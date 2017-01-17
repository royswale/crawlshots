# -*- coding: utf-8 -*-
import json

import scrapy
from scrapy import FormRequest

from crawlshots.items import CrawlshotsItem


class ShotsSpider(scrapy.Spider):
    name = "shots"
    allowed_domains = ["shots.net"]
    start_urls = ['http://www.shots.net/directory/people']

    def parse(self, response):
        headers = {
            'User-Agent':'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:50.0) Gecko/20100101 Firefox/50.0',
            'Cookie':'PHPSESSID=04ebe73eb415d69a1f9cab7b4b94b4c6; _ga=GA1.2.1519420203.1484489507; _hjIncludedInSample=1'
        }
        for i in range(0,int(77253/50)+1):
            yield FormRequest(url="http://www.shots.net/directory/getPeople", method="POST", headers=headers, formdata={'order':"",'offset':str(i*50)}, callback=self.data_parse)

    def data_parse(self,response):

        data = response.body # bytes encoded in ascii
        data = data.decode('utf-8') # from bytes to str
        data = json.loads(data) # from str to dict

        selector = scrapy.Selector(text=data['html'], type="html")
        for a in selector.xpath("//li[@class='directory-person']/a"):
            people_link = a.xpath("@href").extract()
            people_url = "http://www.shots.net{0}".format("".join(people_link))
            yield scrapy.Request(people_url, callback=self.parse_people)

    def parse_people(self, response):
        if response.status == 200:
            email = response.xpath("normalize-space(//ul[@id='directory-contacts']/li[@class='email']/a)").extract()
            if email[0]:
                item = CrawlshotsItem()
                name = response.xpath("//div[@id='article-intro']/h1/text()").extract()
                item['name'] = name[0].strip()
                item['email'] = email[0]
                yield item
        pass
