from bs4 import BeautifulSoup
import requests
from re import sub
from datetime import datetime
from decimal import Decimal
import mysql.connector
from db_config import mysql_configuration 

# Connect to the main "the_angry_shopper" database and start connection
db = mysql.connector.connect(
		host= "localhost",
		user= mysql_configuration['username'],
		passwd= mysql_configuration['password'],
		database= "the_angry_shopper"
	)
cursor = db.cursor(buffered=True)

# Main URL to scrape from Gourmet
base_url = 'https://www.gourmetegypt.com'

# Get the content of the website. Use BeautifulSoup to parse it.
source =  requests.get(base_url).text
soup =  BeautifulSoup(source, 'lxml')

# Loop to get the main sections on the Gourmet website
for nav in soup.find_all('li', class_='ms-level0'):
	category_path = nav.find('a')['href'].split('/')[1]
	category_url = f'{base_url}/{category_path}'
	category_name = nav.find('span', class_='mm-text').text
	# Loop to get each of the categories, skipping the categories in the list
	if category_path not in ['weber-grills', 'household']:
		source =  requests.get(category_url).text
		soup =  BeautifulSoup(source, 'lxml')
		# Loop through each of the subcategories
		for list_item in soup.find('div', class_='top-category-links').find_all('li'):
			sub_category_name = list_item.find('a').text.strip()
			sub_category_link = list_item.find('a')['href']
			if sub_category_link != 'javascript:void(0);':
				# Main function to grab information on products, taking the url (or page) as argument
				def get_products(url):
					# Start or restart counter to keep track of number of products scraped
					source =  requests.get(url).text
					soup =  BeautifulSoup(source, 'lxml')
					
					# Loop to scrape the actual information on each product
					for product in soup.find_all('li', class_='product'):
						id = product.find('div', class_='upperRelativeDiv')['class'][1]
						title = product.find('a', class_='product-item-link').text.strip()
						url = product.find('a', class_='product-item-link')['href']
						size = product.find('div', class_='product-weight').text.strip()
						# Find the price and strip the currency. If the product doesn't have a price, use NULL.   
						try:
							value = product.find('span', class_='price').text
							price = Decimal(sub(r'[^\d.]', '', value))
						except Exception as e:
							price = None
						image = product.find('img', class_='product-image-photo')['src'].strip()
						# Get the UTC date and time, and format it for the database
						now = datetime.utcnow()
						updated = now.strftime("%Y-%m-%d %H:%M:%S")

						# Database insert statement to use below		
						insert_statement = (
						   "INSERT INTO gourmet_products(product_id, title, size, price, url, image, category, updated)"
						   "VALUES (%s, %s, %s, %s, %s, %s, %s, %s)"
						)
						insert_data = (id, title, size, price, url, image, sub_category_name, updated)

						# Prepare query to see if product already exists
						query_product = ("SELECT price FROM gourmet_products WHERE product_id = %s ORDER BY updated DESC")
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
					if soup.find('li', class_='pages-item-next'):
						next_page = soup.find('li', class_='pages-item-next').a['href']
						get_products(next_page)

				get_products(sub_category_link)