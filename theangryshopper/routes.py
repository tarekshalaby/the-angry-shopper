from flask import render_template, redirect, url_for, request
from sqlalchemy import or_
from theangryshopper import app, db
from theangryshopper.models import Categories, GourmetProducts, GourmetCategories, MetroProducts, MetroCategories, CommonProducts
from theangryshopper.supermarkets import supermarkets
from datetime import date, timedelta


@app.route('/')
def home():
	return redirect('/compare')


@app.route('/compare')
def compare_latest():
	path = request.path
	categories = db.session.query(Categories).order_by(Categories.title.asc())

	latest_gourmet_ids = db.session.query(db.func.max(GourmetProducts.id)).group_by(GourmetProducts.product_id).subquery()
	latest_metro_ids = db.session.query(db.func.max(MetroProducts.id)).group_by(MetroProducts.product_id).subquery()

	past_week = date.today() - timedelta(days=7)

	common_products = db.session.query(CommonProducts, GourmetProducts, MetroProducts).join(GourmetProducts, CommonProducts.gourmet_product_id == GourmetProducts.product_id).join(MetroProducts, CommonProducts.metro_product_id == MetroProducts.product_id).filter(GourmetProducts.id.in_(latest_gourmet_ids), GourmetProducts.price > 0, MetroProducts.id.in_(latest_metro_ids), MetroProducts.price > 0, db.func.greatest(GourmetProducts.updated, MetroProducts.updated) > past_week).order_by(db.func.abs(GourmetProducts.price - MetroProducts.price).desc()).limit(30).all()

	return render_template('compare_latest.html', products=common_products, categories=categories) 


@app.route('/compare/<category>')
def compare_category(category):
	path = request.path
	categories = db.session.query(Categories).order_by(Categories.title.asc())
	active_category = db.session.query(Categories).filter(Categories.path == category).one()

	latest_gourmet_ids = db.session.query(db.func.max(GourmetProducts.id)).join(GourmetCategories, GourmetCategories.category_title == GourmetProducts.category).join(Categories, Categories.id == GourmetCategories.category_id).filter(Categories.path == category).group_by(GourmetProducts.product_id).subquery()
	latest_metro_ids = db.session.query(db.func.max(MetroProducts.id)).join(MetroCategories, MetroCategories.category_title == MetroProducts.category).join(Categories, Categories.id == MetroCategories.category_id).filter(Categories.path == category).group_by(MetroProducts.product_id).subquery()

	query = db.session.query(CommonProducts, GourmetProducts, MetroProducts).join(GourmetProducts, CommonProducts.gourmet_product_id == GourmetProducts.product_id).join(MetroProducts, CommonProducts.metro_product_id == MetroProducts.product_id).filter(GourmetProducts.id.in_(latest_gourmet_ids), GourmetProducts.price > 0, MetroProducts.id.in_(latest_metro_ids), MetroProducts.price > 0)

	page = request.args.get('page', 1, type=int)
	products = query.order_by(GourmetProducts.title.asc()).paginate(page=page, per_page=50)
	count = query.count()

	return render_template('compare.html', current_category=category, active_category=active_category, products=products, count=count, categories=categories, path=path) 


@app.route('/browse/')
def browse():
	return redirect('/browse/gourmet')


@app.route('/browse/<supermarket>')
def browse_supermarket_latest(supermarket):
	supermarket_products_class = supermarkets[supermarket]['products_class']
	supermarket_logo = supermarkets[supermarket]['logo']

	for competitor in supermarkets:
		if competitor != supermarket:
			competitor_key = competitor
			competitor_logo = supermarkets[competitor]['logo']

	categories = db.session.query(Categories).order_by(Categories.title.asc())

	ultimate_ids = db.session.query(db.func.max(supermarket_products_class.id).label('max_id')).group_by(supermarket_products_class.product_id).subquery()
	penultimate_ids = db.session.query(db.func.max(supermarket_products_class.id)).filter(~supermarket_products_class.id.in_(ultimate_ids), supermarket_products_class.price > 0).group_by(supermarket_products_class.product_id).subquery()
	ultimate_prices = db.session.query(supermarket_products_class).filter(supermarket_products_class.id.in_(ultimate_ids), supermarket_products_class.price > 0).subquery()
	penultimate_prices = db.session.query(supermarket_products_class.id, supermarket_products_class.product_id, supermarket_products_class.price, supermarket_products_class.updated).filter(supermarket_products_class.id.in_(penultimate_ids)).order_by(supermarket_products_class.updated.desc()).subquery()

	products = db.session.query(ultimate_prices, penultimate_prices.c.updated.label('days'), (((ultimate_prices.c.price - penultimate_prices.c.price)/penultimate_prices.c.price)*100).label('difference')).join(penultimate_prices, ultimate_prices.c.product_id == penultimate_prices.c.product_id).filter(ultimate_prices.c.price != penultimate_prices.c.price).order_by(ultimate_prices.c.updated.desc()).limit(30).all()

	return render_template('browse_latest.html', supermarket=supermarket, supermarket_logo=supermarket_logo, categories=categories, products=products, competitor=competitor_key, competitor_logo=competitor_logo) 


@app.route('/browse/<supermarket>/<category>')
def browse_supermarket_category(supermarket, category):
	path = request.path

	supermarket_name = supermarkets[supermarket]['name']
	supermarket_products_class = supermarkets[supermarket]['products_class']
	supermarket_categories_class = supermarkets[supermarket]['categories_class']
	supermarket_products_id = supermarkets[supermarket]['common_products_id']
	supermarket_logo = supermarkets[supermarket]['logo']

	for competitor in supermarkets:
		if competitor != supermarket:
			competitor_key = competitor
			competitor_name = supermarkets[competitor]['name']
			competitor_products_class = supermarkets[competitor]['products_class']
			competitor_products_id = supermarkets[competitor]['common_products_id']
			competitor_logo = supermarkets[competitor]['logo']

	categories = db.session.query(Categories).order_by(Categories.title.asc())
	active_category = db.session.query(Categories).filter(Categories.path == category).one()

	ultimate_ids = db.session.query(db.func.max(supermarket_products_class.id).label('max_id'))\
		.join(supermarket_categories_class, supermarket_products_class.category == supermarket_categories_class.category_title)\
		.join(Categories, supermarket_categories_class.category_id == Categories.id)\
		.filter(Categories.path == category)\
		.group_by(supermarket_products_class.product_id).subquery()

	penultimate_ids = db.session.query(db.func.max(supermarket_products_class.id))\
		.join(supermarket_categories_class, supermarket_products_class.category == supermarket_categories_class.category_title)\
		.join(Categories, supermarket_categories_class.category_id == Categories.id)\
		.filter(~supermarket_products_class.id.in_(ultimate_ids), supermarket_products_class.price > 0, Categories.path == category)\
		.group_by(supermarket_products_class.product_id).subquery()

	ultimate_prices = db.session.query(supermarket_products_class).filter(supermarket_products_class.id.in_(ultimate_ids), supermarket_products_class.price > 0).subquery()

	penultimate_prices = db.session.query(supermarket_products_class.id, supermarket_products_class.product_id, supermarket_products_class.price, supermarket_products_class.updated)\
		.filter(supermarket_products_class.id.in_(penultimate_ids))\
		.order_by(supermarket_products_class.updated.desc()).subquery()

	competitor_ids = db.session.query(db.func.max(competitor_products_class.id)).group_by(competitor_products_class.product_id).subquery()
	competitor_products = db.session.query(competitor_products_class).filter(competitor_products_class.id.in_(competitor_ids)).subquery()

	query = db.session.query(ultimate_prices, penultimate_prices.c.updated.label('days'), (((ultimate_prices.c.price - penultimate_prices.c.price)/penultimate_prices.c.price)*100).label('difference'), competitor_products.c.price.label('competitor_price'))\
		.join(penultimate_prices, ultimate_prices.c.product_id == penultimate_prices.c.product_id)\
		.join(CommonProducts, supermarket_products_id == ultimate_prices.c.product_id, isouter=True)\
		.join(competitor_products, competitor_products.c.product_id == competitor_products_id, isouter=True)

	page = request.args.get('page', 1, type=int)
	products = query.order_by(ultimate_prices.c.title.asc()).paginate(page=page, per_page=50)
	count = query.count()

	return render_template('browse.html', supermarket=supermarket, supermarket_logo=supermarket_logo, path=path, categories=categories, active_category=active_category, current_category=category, products=products, count=count, competitor=competitor_key, competitor_name=competitor_name, competitor_logo=competitor_logo) 
