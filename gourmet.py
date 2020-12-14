from bs4 import BeautifulSoup
import requests
from re import sub
from decimal import Decimal
from datetime import datetime
import mysql.connector
import os

# MySQL database credentials
db_user = os.environ.get('DB_USER')
db_pass = os.environ.get('DB_PASS')

# Connect to the main "the_angry_shopper" database and start connection
db = mysql.connector.connect(
		host="localhost",
		user=db_user,
		passwd=db_pass,
		database="the_angry_shopper"
	)

cursor = db.cursor()

## Main URL to scrape from Gourmet
base_url = 'https://www.gourmetegypt.com'

source =  requests.get(base_url).text
soup =  BeautifulSoup(source, 'lxml')

## Loop to get the main sections on the Gourmet website
for nav in soup.find_all('li', class_='ms-level0'):
	category_path = nav.find('a')['href'].split('/')[1]
	category_url = f'{base_url}/{category_path}'
	category_name = nav.find('span', class_='mm-text').text
	#Loop to get each of the categories
	if category_path not in ['weber-grills', 'household']:
		source =  requests.get(category_url).text
		soup =  BeautifulSoup(source, 'lxml')

		print('------------------------------')
		print(f'{category_name}')
		print('------------------------------')

		for list_item in soup.find('div', class_='top-category-links').find_all('li'):
			sub_category_name = list_item.find('a').text.strip()
			sub_category_link = list_item.find('a')['href']
			if sub_category_link != 'javascript:void(0);':

				print(f'- {sub_category_name}.', end=' ')

				# Main function to grab information on products, taking the url (or page) as argument
				def get_products(url):
					# Start or restart counter to keep track of number of products scraped
					products_scraped = 0
					source =  requests.get(url).text
					soup =  BeautifulSoup(source, 'lxml')

					# Loop to scrape the actual information on each product
					for product in soup.find_all('li', class_='product'):
						id = product.find('div', class_='upperRelativeDiv')['class'][1]
						title = product.find('a', class_='product-item-link').text.strip()
						url = product.find('a', class_='product-item-link')['href']
						size = product.find('div', class_='product-weight').text.strip()
						try:
							value = product.find('span', class_='price').text
							price = sub(r'[^\d.]', '', value)
						except Exception as e:
							price = None
						image = product.find('img', class_='product-image-photo')['src'].strip()
						now = datetime.utcnow()
						format = "%d/%m/%Y %H:%M"
						updated = now.strftime(format)

						# Insert product info into database
						cursor.execute("INSERT INTO gourmet_products VALUES (?,?,?,?,?,?,?,?)", (id, title, size, url, price, image, sub_category_name, updated))
						connection.commit()

						# Add 1 to the counter 
						products_scraped +=1

					# If there's a link a next page, go there (after scraping all products on this page)
					if soup.find('li', class_='pages-item-next'):
						next_page = soup.find('li', class_='pages-item-next').a['href']
						get_products(next_page)

					print(f'Got {products_scraped} products.', end=' ')
					print()

				get_products(sub_category_link)