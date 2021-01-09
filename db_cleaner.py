from theangryshopper import db
from theangryshopper.models import Categories, GourmetProducts, GourmetCategories, MetroProducts, MetroCategories, CommonProducts
from sqlalchemy import create_engine

# Choose table to clean
supermarket = MetroProducts

# Find the products with  any price changes
products_ids = db.session.query(supermarket.product_id, supermarket.title, db.func.max(supermarket.price).label('max_price'), db.func.min(supermarket.price).label('min_price')).group_by(supermarket.product_id, supermarket.title).having(db.func.max(supermarket.price) != db.func.min(supermarket.price)).all()

# Start with the number of products whose ids will be cleaned/deleted
counter = len(products_ids)

# Loop through each of the product ids
for product in products_ids:
	# Get all ofthe entries for each of the products, in reverse chronological order
	query = db.session.query(supermarket).filter(supermarket.product_id == product.product_id).order_by(supermarket.updated.asc()).all()

	# Empty list to add the ids of the rows that will be deleted
	ids_to_delete = []
	previous_price = 0

	# Loop through each row
	for entry in query:
		current_price = entry.price
		if current_price == None:
			current_price = 0
		# Add the ids where the price hasn't changed from the previous id
		if current_price == previous_price:
			ids_to_delete.append(entry.id)
		# Reset previous price to this row's price so that the next id can be compared
		previous_price = current_price

	# Raw SQL engine and query to delete entries
	engine = db.engine
	connection = engine.connect()

	# Only delete if there are actually any ids in the  list whose rows need to be deleted
	if len(ids_to_delete) != 0: 
		result = connection.execute("""

			DELETE FROM metro_products
			WHERE product_id = (%s) 
			  AND id IN %s

			""", (product.product_id, ids_to_delete))
	# Subtract one from the total number of products to be cleaned
	counter -= 1

	print(counter)

	connection.close()
