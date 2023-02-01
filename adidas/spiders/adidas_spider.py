import codecs
import json
import requests
import scrapy
from bs4 import BeautifulSoup


class AdidasSpider(scrapy.Spider):
	name = "AdidasSpider"
	start_urls = [
		"https://www.adidas.co.uk/running-shoes"
	]

	file_name = "adidas_data.json"
	BASE_URL = "https://www.adidas.co.uk"

	products_information = {}

	def start_requests(self):
		for url in self.start_urls:
			yield scrapy.Request(url=url, callback=self.parse)

	def parse(self, response, **kwargs):
		cards = response.css(".grid-item___3rAkS")
		products_hrefs = cards.css("a::attr(href)")

		for product_href in products_hrefs:
			product_link = self.BASE_URL + product_href.get()
			product_price = self.scrap_page(product_link)
			self.products_information[product_link] = product_price

		# Jump to next page
		next_page_url = response.css(".pagination__control--next___ra6HI a::attr(href)").get()
		if next_page_url:
			yield scrapy.Request(response.urljoin(self.BASE_URL + next_page_url))
		else:
			self.write_records(self.products_information)

	@staticmethod
	def scrap_page(product_link):
		crawl_url = requests.get(product_link, headers={'User-Agent': 'Mozilla/5.0'})
		soup = BeautifulSoup(crawl_url.text, 'html.parser')
		return soup.select(".gl-price-item.notranslate")[0].text

	def write_records(self, products_information):
		with codecs.open(self.file_name, 'w', encoding='utf-8') as file:
			json.dump(products_information, file, ensure_ascii=False)
