from datetime import datetime

from flask_sqlalchemy import SQLAlchemy

database = SQLAlchemy()


#many-to-many veza izmedju Product i Category (1 product moze da ima vise kategorija a 1 kategorija moze da pripada vise proizvoda)
class ProductCategory(database.Model):
    __tablename__ = "productcategory"

    id = database.Column(database.Integer, primary_key=True)
    productId = database.Column(database.Integer, database.ForeignKey("products.id"), nullable=False)
    categoryId = database.Column(database.Integer, database.ForeignKey("categories.id"), nullable=False)


class OrderProduct(database.Model):
    __tablename__ = "orderproduct"

    id = database.Column(database.Integer, primary_key=True)
    orderId = database.Column(database.Integer, database.ForeignKey("orders.id"), nullable=False)
    productId = database.Column(database.Integer, database.ForeignKey("products.id"), nullable=False)
    quantity = database.Column(database.Integer, nullable=False)

class Product(database.Model):
    __tablename__ = "products"

    id = database.Column(database.Integer, primary_key=True)
    name = database.Column(database.String(256), nullable=False, unique=True)
    price = database.Column(database.Float, nullable=False)

    categories = database.relationship("Category", secondary=ProductCategory.__table__, back_populates="products")

    orders = database.relationship("Order", secondary=OrderProduct.__table__, back_populates="products")

    def __repr__(self):
        return "({}, {}, {}, {})".format(str(self.categories), self.id, self.name, self.price)


class Category(database.Model):
    __tablename__ = "categories"

    id = database.Column(database.Integer, primary_key=True)
    name = database.Column(database.String(256), nullable=False, unique=True)

    products = database.relationship("Product", secondary=ProductCategory.__table__, back_populates="categories")

    def __repr__(self):
        return "({}, {})".format(self.id, self.name)



class Order(database.Model):
    __tablename__ = "orders"

    id = database.Column(database.Integer, primary_key=True)
    price = database.Column(database.Float, nullable=False)
    status = database.Column(database.String(256), nullable=False, default="CREATED")
    time = database.Column(database.DateTime, nullable=False, default=datetime.utcnow)
    userEmail = database.Column(database.String(256), nullable=False)

    products = database.relationship("Product", secondary=OrderProduct.__table__, back_populates="orders")

    def __repr__(self):
        return "({}, {}, {}, {}, {}, {})".format(self.id, str(self.products), self.price, self.status, self.time, self.userEmail)






