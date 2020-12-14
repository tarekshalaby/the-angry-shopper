from bs4 import BeautifulSoup
import requests
import re
from decimal import Decimal
from datetime import datetime
import sqlite3

## Connect to sqlite database and then creae a table for Gourmet's products
connection = sqlite3.connect('cairo-supermarkets.db')
cursor = connection.cursor()

cursor.execute("""CREATE TABLE IF NOT EXISTS 
					metro_products(
						id INTEGER,
						title TEXT,
						url TEXT,
						price REAL,
						image TEXT,
						category TEXT,
						updated TEXT
					)""")

# URLs of the different sections to scrape from Metro
sections = ['Bakery/9', 'Beverage/22', 'Canned-Food/14', 'Confectionary/20', 'Dairy/6', 'Deli/5', 'Eatery/2', 'Fresh-Juices/8', 'Frozen-Food/10', 'Fruits/1', 'Commodities/15', 'Health&-Beauty/28', 'Home-Bake/16', 'Hot-Drinks/21', 'Meat/11', 'Milk/18', 'Paper-Products/25', 'Pets/17', 'Poultry/12', 'Sea-Food/13', 'Snacks/19', 'Vegetables/3']

# Main URL to scrape from Metro
base_url = 'https://www.metro-markets.com/categoryl1/'

# Loop through each of the sections from the sections' list above
for section in sections:
	section_link = f'{base_url}{section}'
	source =  requests.get(section_link).text
	soup =  BeautifulSoup(source, 'lxml')

	category = soup.find_all('li', class_='breadcrumb-item')[-1].a.text

	print('------------------------------')
	print(f'{category}')
	print('------------------------------')

	# Main function to grab information on products, taking the url (or page) as argument
	def get_products(url):
		# Start or restart counter to keep track of number of products scraped
		products_scraped = 0
		source =  requests.get(url).text
		soup =  BeautifulSoup(source, 'lxml')

		# Loop to scrape the actual information on each product
		products = soup.find_all('div', class_='product-card')
		if(products):
			for product in products:
				id = product['data-id']
				title = product.find('h5').text.strip()
				try:
					value = product.find('p', class_='after').text
					price = re.sub(r'[^\d.]', '', value)
				except Exception as e:
					price = None
				url = product.find('a')['href']
				image_compressed = product.find('div', class_='img-holder')['data-src']
				image_file_name = re.search('[A-Za-z0-9.]+$', image_compressed)
				image = f'https://www.metro-markets.com/storage/products/{image_file_name.group()}'
				now = datetime.utcnow()
				format = "%d/%m/%Y %H:%M"
				updated = now.strftime(format)

				# Insert product info into database
				cursor.execute("INSERT INTO metro_products VALUES (?,?,?,?,?,?,?)", (id, title, url, price, image, category, updated))
				connection.commit()

				products_scraped +=1

			# If there's a link a next page, go there (after scraping all products on this page)
			if soup.find_all('li', class_='page-item')[-1].a:
				next_page = soup.find_all('li', class_='page-item')[-1].a['href']
				get_products(next_page)

			print(f'Got {products_scraped} products.')

	get_products(section_link)