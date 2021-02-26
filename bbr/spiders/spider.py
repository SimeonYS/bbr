import re

import scrapy

from scrapy.loader import ItemLoader
from ..items import BbrItem
from itemloaders.processors import TakeFirst
pattern = r'(\xa0)?'

class BbrSpider(scrapy.Spider):
	name = 'bbr'
	start_urls = ['https://bbr.bg/bg/news',
				  'https://bbr.bg/bg/in-media'
				  ]

	def parse(self, response):
		articles = response.xpath('//div[@class="text"]')
		for article in articles:
			date = article.xpath('.//time/@datetime').get()
			post_links = article.xpath('.//h2/a/@href').get()
			yield response.follow(post_links, self.parse_post,cb_kwargs=dict(date=date))

		next_page = response.xpath('//a[@rel="next"]/@href').get()
		if next_page:
			yield response.follow(next_page, self.parse)


	def parse_post(self, response,date):
		title = response.xpath('//h1[@class="header"]/text()').get()
		content = response.xpath('//div[@class="text"]//text()[not (ancestor::h1)]').getall()
		content = [p.strip() for p in content if p.strip()]
		content = re.sub(pattern, "",' '.join(content))


		item = ItemLoader(item=BbrItem(), response=response)
		item.default_output_processor = TakeFirst()

		item.add_value('title', title)
		item.add_value('link', response.url)
		item.add_value('content', content)
		item.add_value('date', date)

		return item.load_item()
