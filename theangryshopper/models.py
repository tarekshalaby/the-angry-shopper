from datetime import datetime
from theangryshopper import db


class Categories(db.Model):
	__tablename__ = 'categories'
	id = db.Column(db.Integer, primary_key=True)
	title = db.Column(db.String(100), unique=True, nullable=False)
	path = db.Column(db.String(100), unique=True, nullable=False)
	icon = db.Column(db.String(100))

	def __repr__(self):
		return f"Categories('{self.id}', '{self.title}', '{self.path}', '{self.icon}')"


class GourmetProducts(db.Model):
	__tablename__ = 'gourmet_products'
	id = db.Column(db.Integer, primary_key=True)
	product_id = db.Column(db.Integer, unique=True, nullable=False)
	title = db.Column(db.String(100))
	size = db.Column(db.String(50))
	price = db.Column(db.Numeric(6,2))
	url = db.Column(db.String(100))
	image = db.Column(db.String(100))
	category = db.Column(db.String(100))
	updated = db.Column(db.DateTime, default=datetime.utcnow)

	def __repr__(self):
		return f"GourmetProducts('{self.title}', '{self.size}', {self.price}, '{self.url}', '{self.image}', '{self.category}')"


class GourmetCategories(db.Model):
	__tablename__ = 'gourmet_categories'
	id = db.Column(db.Integer, primary_key=True)
	category_title = db.Column(db.String(100))
	category_id = db.Column(db.Integer, db.ForeignKey('categories.id'))

	def __repr__(self):
		return f"GourmetCategories('{self.category_title}, {self.category_id}')"


class MetroProducts(db.Model):
	__tablename__ = 'metro_products'
	id = db.Column(db.Integer, primary_key=True)
	product_id = db.Column(db.Integer, unique=True, nullable=False)
	title = db.Column(db.String(100))
	price = db.Column(db.Numeric(6,2))
	url = db.Column(db.String(100))
	image = db.Column(db.String(100))
	category = db.Column(db.String(100))
	updated = db.Column(db.DateTime, default=datetime.utcnow)

	def __repr__(self):
		return f"MetroProducts('{self.title}', {self.price}, '{self.url}', '{self.image}', '{self.category}')"


class MetroCategories(db.Model):
	__tablename__ = 'metro_categories'
	id = db.Column(db.Integer, primary_key=True)
	category_title = db.Column(db.String(100))
	category_id = db.Column(db.Integer, db.ForeignKey('categories.id'))

	def __repr__(self):
		return f"MetroCategories('{self.category_title}, {self.category_id}')"
