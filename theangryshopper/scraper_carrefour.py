from bs4 import BeautifulSoup
import requests
import time
import re
from selenium import webdriver
from selenium.webdriver.common.keys import Keys 

# Main URL to scrape from Carrefour
base_url = 'https://www.carrefouregypt.com'
path_english = '/mafegy/en'

sections = [
		'Food-Cupboard/c/FEGY1700000',
		'Fresh-Food/c/FEGY1600000',
		'Cleaning-Household/c/NFEGY3000000',
		'Beverages/c/FEGY1500000',
		'Beauty-Personal-Care/c/NFEGY2000000'
	]

driver = webdriver.Firefox()

for section in sections:
	driver.get(f'{base_url}/{path_english}/{section}')
	time.sleep(5)
	for i in range(0, 2):
		driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
		time.sleep(5)
	load_more = driver.find_element_by_xpath("//button[contains(text(),'Load More')]")
	while True:
		driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
		time.sleep(2)
		driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
		time.sleep(2)
		load_more.click()
		time.sleep(2)
	html = driver.page_source
	soup = BeautifulSoup(html, 'lxml')

	section = soup.find('title').text
	container = soup.find('ul', attrs={"data-testid": "scrollable-list-view"})
	products = container.find_all('ul')
	print(section)
	counter = 0
	for product in products:
		title = product.find('a')['title']
		url = base_url + product.find('a')['href']
		product_id = re.search('[A-Za-z0-9.]+$', url).group()
		image = product.find('a').find('img')['src']
		try:
			value = product.find('div', attrs={"data-testid": "product-card-discount-price"}).find('div').text
			price = re.sub(r'[^\d.]', '', value)
		except:
			value = product.find('div', attrs={"data-testid": "product-card-original-price"}).find('div').text
			price = re.sub(r'[^\d.]', '', value)
		
		counter += 1
		print(f"{counter}) id: {product_id}. Title: {title}. Price: {price}")
		print(f"url: {url}")
		print(f"image: {image}")
		print()

driver.close()