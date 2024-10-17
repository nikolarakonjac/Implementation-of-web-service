from flask import Flask, request, Response, jsonify
from sqlalchemy import func, desc, and_, or_, between, distinct
from sqlalchemy.sql.functions import coalesce

from configuration import Configuration
from models import *
from flask_jwt_extended import jwt_required, JWTManager
from authorization import roleCheck
import csv
import io


application = Flask(__name__)
application.config.from_object(Configuration)

jwt = JWTManager(application)





def validateFile(fileContent):

    try:
        stream = io.StringIO(fileContent)
        reader = csv.reader(stream)

        lineNumber = 0
        for row in reader:
            if len(row) < 3:
                raise ValueError(f"Incorrect number of values on line {lineNumber}.")

            productName = row[1]

            try:
                productPrice = float(row[2])
            except ValueError:
                raise ValueError(f"Incorrect price on line {lineNumber}.")

            if productPrice <= 0:
                raise ValueError(f"Incorrect price on line {lineNumber}.")

            product = Product.query.filter_by(name=productName).first()
            if product is not None:
                raise ValueError(f"Product {productName} already exists.")

            lineNumber = lineNumber + 1

    except ValueError as e:
        return jsonify({"message": str(e)}), 400


@application.route("/update", methods=['POST'])
@jwt_required()
@roleCheck("owner")
def update():
    if "file" not in request.files:
        return jsonify({"message": "Field file is missing."}), 400

    fileContent = request.files["file"].stream.read().decode("utf-8")

    # validateFile(fileContent)

    productNames = []

    try:
        stream = io.StringIO(fileContent)
        reader = csv.reader(stream)

        lineNumber = 0
        for row in reader:
            if len(row) < 3:
                raise ValueError(f"Incorrect number of values on line {lineNumber}.")

            productName = row[1]

            try:
                productPrice = float(row[2])
            except ValueError:
                raise ValueError(f"Incorrect price on line {lineNumber}.")

            if productPrice <= 0:
                raise ValueError(f"Incorrect price on line {lineNumber}.")

            if productName in productNames:
                raise ValueError(f"Product {productName} already exists.")
            else:
                productNames.append(productName)


            lineNumber = lineNumber + 1

    except ValueError as e:
        return jsonify({"message": str(e)}), 400


    stream = io.StringIO(fileContent)
    reader = csv.reader(stream)

    for row in reader:
        listOfCategoryNames = row[0].split("|")
        productName = row[1]
        productPrice = float(row[2])

        product = Product(name=productName, price=productPrice)
        database.session.add(product)
        database.session.commit()

        for categoryName in listOfCategoryNames:
            category = Category.query.filter_by(name=categoryName).first()
            if (not category):
                category = Category(name=categoryName)

            database.session.add(category)
            database.session.commit()

            productCategory = ProductCategory(productId=product.id, categoryId=category.id)

            database.session.add(productCategory)
            database.session.commit()

    return Response(status=200)

# @application.route("/update", methods=['POST'])
# @jwt_required()
# @roleCheck("owner")
# def update():
#     if "file" not in request.files:
#         return jsonify({"message": "Field file is missing."}), 400
#
#     fileContent = request.files["file"].stream.read().decode("utf-8")
#
#
#
#     stream = io.StringIO(fileContent)
#     reader = csv.reader(stream)
#
#     lineNumber = 0
#
#     try:
#         # pocetak transakcije
#         with database.session.begin(subtransactions=True):
#             for row in reader:
#                 if (len(row) < 3):
#                     raise ValueError(f"Incorrect number of values on line {lineNumber}.")
#
#                 listOfCategoryNames = row[0].split("|")
#                 productName = row[1]
#
#                 try:
#                     productPrice = float(row[2])
#                 except ValueError as e:
#                     raise ValueError(f"Incorrect price on line {lineNumber}.")
#
#                 if (productPrice <= 0):
#                     raise ValueError(f"Incorrect price on line {lineNumber}.")
#
#                 product = Product.query.filter_by(name=productName).first()
#                 if (product is not None):
#                     raise ValueError(f"Product {productName} already exists.")
#
#                 product = Product(name=productName, price=productPrice)
#                 database.session.add(product)
#                 database.session.flush()
#
#                 for categoryName in listOfCategoryNames:
#                     category = Category.query.filter_by(name=categoryName).first()
#                     if (not category):
#                         category = Category(name=categoryName)
#
#                     database.session.add(category)
#                     database.session.flush()
#
#                     productCategory = ProductCategory(productId=product.id, categoryId=category.id)
#
#                     database.session.add(productCategory)
#                     database.session.flush()
#
#                 lineNumber = lineNumber + 1
#
#
#
#     except ValueError as e:
#         # ako dodje do greske transakcija se prekida i baza se vraca na stanje pre zapocinjanja transakcije
#         database.session.rollback()
#         return jsonify({"message": str(e)}), 400
#
#     database.session.commit()
#
#     return Response(status=200)


@application.route("/product_statistics", methods=['GET'])
@jwt_required()
@roleCheck("owner")
def getProductStatistics():
    # proizvodi koji imaju makar jednu prodaju;
    # sold -> proizvodi u narudzbinama koje su dostavljene
    # waiting -> broj primeraka proizvoda koji pripadaju narudžbinama koje tek treba dostaviti kupcima

    result = (Product.query.join(OrderProduct).join(Order).group_by(Product.name).with_entities(
 Product.name,
        func.sum(func.IF(Order.status == "COMPLETE", OrderProduct.quantity, 0)).label("soldCounter"),
        func.sum(func.IF(Order.status != "COMPLETE", OrderProduct.quantity, 0)).label("waitingCounter")
    ).all())


    # result = (
    #     Product.query
    #     .join(OrderProduct)
    #     .join(Order)
    #     .group_by(Product.name)
    #     .having(
    #         func.sum(func.IF(Order.status == "COMPLETE", OrderProduct.quantity, 0)) > 0
    #         | func.sum(func.IF(Order.status != "COMPLETE", OrderProduct.quantity, 0)) > 0
    #     )
    #     .with_entities(
    #         Product.name,
    #         func.sum(func.IF(Order.status == "COMPLETE", OrderProduct.quantity, 0)).label("soldCounter"),
    #         func.sum(func.IF(Order.status != "COMPLETE", OrderProduct.quantity, 0)).label("waitingCounter")
    #     )
    #     .all()
    # )

    statistics = []

    for r in result:
        stat = {
            "name": r.name,
            "sold": int(r.soldCounter),
            "waiting": int(r.waitingCounter)
        }
        # statistics.append(stat)
        if int(r.soldCounter) > 0 or int(r.waitingCounter) > 0:
            statistics.append(stat)

    return jsonify({"statistics": statistics}), 200

@application.route("/vezba", methods=['GET'])
def vezba():
    return str(
        Product.query.join(OrderProduct).join(Order).all()
    )




@application.route("/category_statistics", methods=['GET'])
@jwt_required()
@roleCheck("owner")
def getCategoryStatistics():
    # imena kategorija sortiranih opadajuce po broju dostavljenih primeraka proizvoda koji pripadaju toj kategoriji

    query = Category.query.outerjoin(ProductCategory).outerjoin(Product).outerjoin(OrderProduct).outerjoin(Order).group_by(Category.name).with_entities(
        Category.name,
        func.sum(func.IF(Order.status == "COMPLETE", OrderProduct.quantity, 0)).label("soldCounter")
    ).order_by(
        func.sum(func.IF(Order.status == "COMPLETE", OrderProduct.quantity, 0)).desc(),
        Category.name
    ).all()

    statistics = []

    for category in query:
        # statistics.append({
        #     "name": category.name,
        #     "count": int(category.soldCounter)
        # })
        statistics.append(category.name)

    return jsonify({"statistics": statistics}), 200



@application.route("/proba", methods=['GET'])
@jwt_required()
@roleCheck("owner")
def proba():

    # orders = Order.query.all()
    # orders_str = '\n'.join(str(order) for order in orders)

    # database.session.query(Order.id, Order.price).all()
    # Order.query.with_entities(Order.id, Order.price).all()  radi istu stvar kao gornja linija

    #Order.query.with_entities(Order.id, Order.price).order_by(desc(Order.id)).all()

    # Order.query.filter(Order.id == 2).first()
    # Order.query.filter_by(id=3, status="COMPLETE").with_entities(Order.price).first()
    # Order.query.filter(Order.status == "COMPLETE").with_entities(Order.id, Order.price).order_by(desc(Order.price)).all()
    #Order.query.filter(and_(Order.status=="COMPLETE", Order.id==2)).all()

    #Order.query.filter(between(Order.price, 200, 750 )).all()

    #OrderProduct.query.with_entities(distinct(OrderProduct.orderId)).all()

    # OrderProduct.query.with_entities(OrderProduct.orderId, func.sum(OrderProduct.quantity)).group_by(OrderProduct.orderId).all()

    # OrderProduct.query.with_entities(OrderProduct.orderId, func.sum(OrderProduct.quantity)).group_by(OrderProduct.orderId).having(func.sum(OrderProduct.quantity) > 5).all()

    #vraca minimum i orderid kome odgovara taj minimum iz OrderProduct tabele
    #OrderProduct.query.with_entities(OrderProduct.orderId, func.min(OrderProduct.quantity)).group_by(OrderProduct.orderId).having(func.min(OrderProduct.quantity) == func.min(OrderProduct.quantity)).first()

    # orders = Order.query.join(OrderProduct).join(Product).with_entities(Order.id, Order.price,Product.name, OrderProduct.quantity).all()
    # orders_str = '\n'.join(str(order) for order in orders)

    #broj redova
    #OrderProduct.query.count()


    #za svaki proizvod koliko je para potroseno na njega
    # result = (Product.query.outerjoin(OrderProduct).
    #           with_entities(Product.id, Product.name, Product.price,coalesce(func.sum(OrderProduct.quantity), 0),
    #                         coalesce(func.round(func.sum(OrderProduct.quantity) * Product.price, 2), 0)).
    #             group_by(Product.id).order_by(desc (coalesce(func.round(func.sum(OrderProduct.quantity) * Product.price, 2), 0)))
    #           .limit(3)
    #           .all())
    #
    # strResult = "\n".join(str(r) for r in result)


    # result = (Product.query.join(ProductCategory).join(Category).join(OrderProduct)
    #         .with_entities(Product.id, Product.name, Category.name, func.sum(OrderProduct.quantity))
    #         .group_by(Product.id, Product.name, Category.name)  # Include Category.name in the GROUP BY clause
    #         .order_by(desc (func.sum(OrderProduct.quantity)))  # Use .desc() to order by sum descending
    #         .all())

    # result = (Category.query.outerjoin(ProductCategory).join(Product)
    #         .with_entities(Category.name, Product.id, Product.name, func.max(Product.price))
    #         .group_by(Category.name,Product.id, Product.name )
    #         .all()
    #         )

    # result = (database.session.query(ProductCategory.categoryId, func.max(Product.price).label('max_price'))
    #           .join(Product)
    #           .group_by(ProductCategory.categoryId)
    #           .all()
    #           )

    # result = (
    #         Category.query.
    #         join(ProductCategory).
    #         join(Product).
    #         with_entities(
    #             ProductCategory.categoryId,
    #             func.max(Product.price).label('max_price')
    #         )
    #         .group_by(ProductCategory.categoryId).all()
    #     )

    #
    # result = (Product.query.join(OrderProduct).join(Order).group_by(Product.name).with_entities(
    #     Product.name,
    #         func.sum(func.IF(Order.status == "COMPLETE", OrderProduct.quantity, 0)).label("sold"),
    #         func.sum(func.IF(Order.status != "COMPLETE", OrderProduct.quantity, 0)).label("waiting")
    #     )
    #     .having(func.sum(func.IF(Order.status == "COMPLETE", OrderProduct.quantity, 0)).label("sold") > 15)
    #     .all()
    # )

    # result = (Category.query.outerjoin(ProductCategory).join(Product).join(OrderProduct).join(Order).group_by(Category.id)
    #         .with_entities(
    #         Category.name,
    #         func.sum(func.IF(Order.status == 'COMPLETE', OrderProduct.quantity, 0))
    #         )
    #         .order_by(desc(func.sum(func.IF(Order.status == 'COMPLETE', OrderProduct.quantity, 0))))
    #         .all()
    #         )

    # strResult = "\n".join(str(r) for r in result)

    return " "



if (__name__ == "__main__"):
    database.init_app(application)
    application.run(debug=True, host="0.0.0.0", port=5001)
