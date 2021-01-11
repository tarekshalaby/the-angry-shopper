from bs4 import BeautifulSoup
import requests
import re
from datetime import datetime
from decimal import Decimal
import mysql.connector
import config

# Connect to the main "the_angry_shopper" database and start connection
db = mysql.connector.connect(
		host= "localhost",
		user= config.mysql_configuration["username"],
		passwd= config.mysql_configuration["password"],
		database= "the_angry_shopper"
	)
cursor = db.cursor(buffered=True)

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

	# Main function to grab information on products, taking the url (or page) as argument
	def get_products(url):
		source =  requests.get(url).text
		soup =  BeautifulSoup(source, 'lxml')

		# Loop to scrape the actual information on each product
		products = soup.find_all('div', class_='product-card')
		if(products):
			for product in products:
				id = product['data-id']
				title = product.find('h5').text.strip()
				# Get the price, strip the currency. NULL is there isn't a price.
				try:
					value = product.find('p', class_='after').text
					price = Decimal(re.sub(r'[^\d.]', '', value))
				except Exception as e:
					price = None
				url = product.find('a')['href']
				# Get the URL of the full resolution image from the link to compressed version 
				image_compressed = product.find('div', class_='img-holder')['data-src']
				image_file_name = re.search('[A-Za-z0-9.]+$', image_compressed)
				image = f'https://www.metro-markets.com/storage/products/{image_file_name.group()}'
				# Get the date and time and format it
				now = datetime.utcnow()
				updated = now.strftime("%Y-%m-%d %H:%M:%S")

				# Preparing SQL query to INSERT a record into the database.
				insert_statement = (
				   "INSERT INTO metro_products(product_id, title, price, url, image, category, updated)"
				   "VALUES (%s, %s, %s, %s, %s, %s, %s)"
				)
				insert_data = (id, title, price, url, image, category, updated)

				# Prepare query to see if product already exists
				query_product = ("SELECT price FROM metro_products WHERE product_id = %s ORDER BY updated DESC")
				product_id = (id,)
				cursor.execute(query_product, product_id)
				check_product = cursor.fetchone()
				if check_product == None:
					cursor.execute(insert_statement, insert_data)
					db.commit()
				else:
					last_price = check_product[0]
					if last_price != price:
						cursor.execute(insert_statement, insert_data)
						db.commit()

			# If there's a link a next page, go there (after scraping all products on this page)
			if soup.find_all('li', class_='page-item')[-1].a:
				next_page = soup.find_all('li', class_='page-item')[-1].a['href']
				get_products(next_page)

	get_products(section_link)
