import scrapy
from scrapy import Selector
from scrapy.exceptions import CloseSpider

from scrapy.loader import ItemLoader

from ..items import SgbplItem
from itemloaders.processors import TakeFirst

import requests

base_url = "https://www.sgb.pl/aktualnosci/page/{}/"

payload = {}
headers = {
  'Connection': 'keep-alive',
  'Pragma': 'no-cache',
  'Cache-Control': 'no-cache',
  'sec-ch-ua': '"Chromium";v="88", "Google Chrome";v="88", ";Not A Brand";v="99"',
  'Accept': '*/*',
  'X-Requested-With': 'XMLHttpRequest',
  'sec-ch-ua-mobile': '?0',
  'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.190 Safari/537.36',
  'Sec-Fetch-Site': 'same-origin',
  'Sec-Fetch-Mode': 'cors',
  'Sec-Fetch-Dest': 'empty',
  'Referer': 'https://www.sgb.pl/aktualnosci/',
  'Accept-Language': 'en-US,en;q=0.9,bg;q=0.8',
  'Cookie': '_gcl_au=1.1.1822426739.1614262997; _ga=GA1.2.240044703.1614262997; _fbp=fb.1.1614262997043.1886431886; pll_language=pl; cookies=1; _gid=GA1.2.1026114084.1615466169; _gat_UA-144946597-1=1'
}


class SgbplSpider(scrapy.Spider):
	name = 'sgbpl'
	start_urls = ['https://www.sgb.pl/aktualnosci/']
	page = 1

	def parse(self, response):
		data = requests.request("GET", base_url.format(self.page), headers=headers, data=payload)

		post_links = Selector(text=data.text).xpath('//a[contains(@class, "container-box")]/@href').getall()
		marker = Selector(text=data.text).xpath('//script').get()
		yield from response.follow_all(post_links, self.parse_post)
		if self.page > 1 and marker:
			raise CloseSpider('no more pages')

		self.page += 1
		yield response.follow(response.url, self.parse, dont_filter=True)


	def parse_post(self, response):
		title = response.xpath('//h1//text()[normalize-space()]').get()
		description = response.xpath('//div[@class="wrapper wp-custom"]//text()[normalize-space()]').getall()
		description = [p.strip() for p in description]
		description = ' '.join(description).strip()
		date = response.xpath('//div[@class="data-wpisu"]/text()').get()

		item = ItemLoader(item=SgbplItem(), response=response)
		item.default_output_processor = TakeFirst()
		item.add_value('title', title)
		item.add_value('description', description)
		item.add_value('date', date)

		return item.load_item()
