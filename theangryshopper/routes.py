from flask import render_template, redirect, url_for, request
from sqlalchemy import or_
from theangryshopper import app, db
from theangryshopper.models import Categories, GourmetProducts, GourmetCategories, MetroProducts, MetroCategories, CommonProducts
from datetime import date


@app.route('/')
def home():
	return redirect('/compare')


@app.route('/compare')
def compare_latest():
	path = request.path
	categories = db.session.query(Categories).order_by(Categories.title.asc())

	latest_gourmet_ids = db.session.query(db.func.max(GourmetProducts.id)).group_by(GourmetProducts.product_id).all()
	latest_metro_ids = db.session.query(db.func.max(MetroProducts.id)).group_by(MetroProducts.product_id).all()

	limit = 50
	common_products = db.session.query(CommonProducts, GourmetProducts, MetroProducts).join(GourmetProducts, CommonProducts.gourmet_product_id == GourmetProducts.product_id).join(MetroProducts, CommonProducts.metro_product_id == MetroProducts.product_id).filter(GourmetProducts.id.in_(latest_gourmet_ids), GourmetProducts.price > 0, MetroProducts.id.in_(latest_metro_ids), MetroProducts.price > 0).order_by(db.func.greatest(GourmetProducts.updated, MetroProducts.updated).desc()).limit(limit).all()

	return render_template('compare.html', products=common_products, categories=categories) 


@app.route('/compare/<category>')
def compare_category(category):
	path = request.path
	categories = db.session.query(Categories).order_by(Categories.title.asc())
	active_category = db.session.query(Categories).filter(Categories.path == category).one()
	latest = db.session.query(db.func.max(GourmetProducts.id)).filter(GourmetProducts.category == category).group_by(GourmetProducts.product_id).all()
	query = db.session.query(GourmetProducts).filter(GourmetProducts.id.in_(latest), GourmetProducts.price > 0)
	products = query.order_by(GourmetProducts.title.asc())
	count = query.count()

	return render_template('compare.html', active_category=active_category, products=products, count=count, categories=categories, path=path) 


@app.route('/browse/')
def browse():
	return redirect('/browse/gourmet')


supermarket_products_class = {'gourmet' : GourmetProducts, 'metro': MetroProducts}
supermarket_categories_class = {'gourmet': GourmetCategories, 'metro': MetroCategories}

@app.route('/browse/<supermarket>')
def browse_supermarket_latest(supermarket):
	supermarket_products = supermarket_products_class[supermarket]

	categories = db.session.query(Categories).order_by(Categories.title.asc())

	ultimate_ids = db.session.query(db.func.max(supermarket_products.id).label('max_id')).group_by(supermarket_products.product_id).all()
	penultimate_ids = db.session.query(db.func.max(supermarket_products.id)).filter(~supermarket_products.id.in_(ultimate_ids), supermarket_products.price > 0).group_by(supermarket_products.product_id).all()
	ultimate_prices = db.session.query(supermarket_products).filter(supermarket_products.id.in_(ultimate_ids), supermarket_products.price > 0).subquery()
	penultimate_prices = db.session.query(supermarket_products.id, supermarket_products.product_id, supermarket_products.price, supermarket_products.updated).filter(supermarket_products.id.in_(penultimate_ids)).order_by(supermarket_products.updated.desc()).subquery()

	products = db.session.query(ultimate_prices, penultimate_prices.c.updated.label('days'), (((ultimate_prices.c.price - penultimate_prices.c.price)/penultimate_prices.c.price)*100).label('difference')).join(penultimate_prices, ultimate_prices.c.product_id == penultimate_prices.c.product_id).filter(ultimate_prices.c.price != penultimate_prices.c.price).limit(50).all()

	return render_template('browse.html', supermarket=supermarket, categories=categories, products=products) 


@app.route('/browse/<supermarket>/<category>')
def browse_supermarket_category(supermarket, category):
	path = request.path
	supermarket_products = supermarket_products_class[supermarket]
	supermarket_categories = supermarket_categories_class[supermarket]

	categories = db.session.query(Categories).order_by(Categories.title.asc())
	active_category = db.session.query(Categories).filter(Categories.path == category).one()

	ultimate_ids = db.session.query(db.func.max(supermarket_products.id).label('max_id')).join(supermarket_categories, supermarket_products.category == supermarket_categories.category_title).join(Categories, supermarket_categories.category_id == Categories.id).filter(Categories.path == category).group_by(supermarket_products.product_id).all()
	penultimate_ids = db.session.query(db.func.max(supermarket_products.id)).join(supermarket_categories, supermarket_products.category == supermarket_categories.category_title).join(Categories, supermarket_categories.category_id == Categories.id).filter(~supermarket_products.id.in_(ultimate_ids), supermarket_products.price > 0, Categories.path == category).group_by(supermarket_products.product_id).all()
	ultimate_prices = db.session.query(supermarket_products).filter(supermarket_products.id.in_(ultimate_ids), supermarket_products.price > 0).subquery()
	penultimate_prices = db.session.query(supermarket_products.id, supermarket_products.product_id, supermarket_products.price, supermarket_products.updated).filter(supermarket_products.id.in_(penultimate_ids)).order_by(supermarket_products.updated.desc()).subquery()

	query = db.session.query(ultimate_prices, penultimate_prices.c.updated.label('days'), (((ultimate_prices.c.price - penultimate_prices.c.price)/penultimate_prices.c.price)*100).label('difference')).join(penultimate_prices, ultimate_prices.c.product_id == penultimate_prices.c.product_id)
	products = query.order_by(ultimate_prices.c.title.asc())
	count = query.count()

	return render_template('browse.html', supermarket=supermarket, path=path, categories=categories, active_category=active_category, products=products, count=count) 
