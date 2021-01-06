from theangryshopper.models import Categories, GourmetProducts, GourmetCategories, MetroProducts, MetroCategories, CommonProducts

supermarkets = {
	'gourmet': {
		'name': 'Gourmet',
		'products_class': GourmetProducts,
		'categories_class': GourmetCategories,
		'common_products_id': CommonProducts.gourmet_product_id
	},
	'metro': {
		'name': 'Metro',
		'products_class': MetroProducts,
		'categories_class': MetroCategories,
		'common_products_id': CommonProducts.metro_product_id
	}
}