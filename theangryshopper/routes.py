from flask import render_template, redirect, url_for, request
from theangryshopper import app, db
from theangryshopper.models import Categories, GourmetProducts, GourmetCategories, MetroProducts

@app.route('/')
def home():
	return redirect('/compare')

@app.route('/compare')
def compare_latest():
	categories = db.session.query(Categories).order_by(Categories.title.asc())
	latest = db.session.query(db.func.max(GourmetProducts.id)).group_by(GourmetProducts.product_id).all()
	query = db.session.query(GourmetProducts).filter(GourmetProducts.id.in_(latest), GourmetProducts.price > 0)
	limit = 50
	products = query.order_by(GourmetProducts.updated.desc()).limit(limit).all()
	return render_template('compare.html', products=products, count=limit, categories=categories) 

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
	return ("Browse")

supermarket_class = {'gourmet' : GourmetProducts, 'metro': MetroProducts}

@app.route('/browse/<supermarket>')
def browse_supermarket_latest(supermarket):
	target = supermarket_class[supermarket]
	categories = db.session.query(Categories).order_by(Categories.title.asc())
	latest = db.session.query(db.func.max(target.id)).group_by(target.product_id).all()
	query = db.session.query(target).filter(target.id.in_(latest), target.price > 0)
	limit = 50
	products = query.order_by(target.updated.desc()).limit(limit).all()
	changed = db.session.query(GourmetProducts.product_id).group_by(GourmetProducts.product_id).having(db.func.max(GourmetProducts.price) != db.func.min(GourmetProducts.price)).all()
	latest_changed = db.session.query(GourmetProducts.id).filter(GourmetProducts.id.in_(latest), GourmetProducts.product_id.in_(changed)).all()
	test = db.session.query(GourmetProducts.id, GourmetProducts.product_id, GourmetProducts.title, GourmetProducts.price).filter(GourmetProducts.product_id.in_(changed)).order_by(GourmetProducts.product_id.asc()).all()
	return render_template('browse.html', products=products, count=limit, categories=categories, test=test) 
