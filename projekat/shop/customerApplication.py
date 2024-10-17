from collections import OrderedDict

from flask import Flask, request, Response, jsonify
from sqlalchemy import and_, desc

from configuration import Configuration
from models import *
from flask_jwt_extended import jwt_required, JWTManager, get_jwt_identity

from authorization import roleCheck

application = Flask(__name__)
application.config.from_object(Configuration)

jwt = JWTManager(application)


@application.route("/search", methods=['GET'])
@jwt_required()
@roleCheck("customer")
def search():
    productName = request.args.get('name', "")
    categoryName = request.args.get('category', "")

    categories = Category.query.filter(
        and_(
            Category.name.contains(categoryName),
            Category.products.any(Product.name.contains(productName))
        )

    ).all()

    categoryNames = [category.name for category in categories]

    products = Product.query.filter(
        and_(
            Product.name.contains(productName),
            Product.categories.any(Category.name.contains(categoryName))
        )
    ).all()

    productsList = [
        {
            "categories": [category.name for category in product.categories],
            "id": product.id,
            "name": product.name,
            "price": product.price
        }
        for product in products
    ]

    result = {
        "categories": categoryNames,
        "products": productsList,
    }

    return jsonify(result), 200


@application.route("/order", methods=['POST'])
@jwt_required()
@roleCheck("customer")
def order():
    if 'requests' not in request.json:
        return jsonify({"message": "Field requests is missing."}), 400

    userEmail = get_jwt_identity()

    try:
        for i, requestData in enumerate(request.json["requests"]):
            requestId = requestData.get('id', "")
            quantity = requestData.get('quantity', "")

            if requestId == "":
                raise ValueError(f"Product id is missing for request number {i}.")

            if quantity == "":
                raise ValueError(f"Product quantity is missing for request number {i}.")

            if not isinstance(requestId, int) or requestId <= 0:
                raise ValueError(f"Invalid product id for request number {i}.")

            if not isinstance(quantity, int) or quantity <= 0:
                raise ValueError(f"Invalid product quantity for request number {i}.")

            product = Product.query.filter_by(id=requestId).first()
            if product is None:
                raise ValueError(f"Invalid product for request number {i}.")

    except ValueError as e:
        return jsonify({"message": str(e)}), 400

    totalPrice = 0.0
    order = Order(
        price=0.0,
        status="CREATED",
        time=datetime.utcnow(),
        userEmail=userEmail
    )

    database.session.add(order)
    database.session.commit()

    for i, requestData in enumerate(request.json["requests"]):
        requestId = requestData.get('id', "")
        quantity = requestData.get('quantity', "")

        product = Product.query.filter_by(id=requestId).first()

        orderProduct = OrderProduct(orderId=order.id, productId=product.id, quantity=quantity)
        database.session.add(orderProduct)
        database.session.commit()

        totalPrice = totalPrice + (product.price * quantity)

    order.price = totalPrice
    database.session.commit()

    return jsonify({"id": order.id}), 200



# @application.route("/order", methods=['POST'])
# @jwt_required()
# @roleCheck("customer")
# def order():
#     if 'requests' not in request.json:
#         return jsonify({"message": "Field requests is missing."}), 400
#
#     userEmail = get_jwt_identity()
#
#     totalPrice = 0.0
#
#     try:
#         with database.session.begin(subtransactions=True):
#             order = Order(
#                 price=0.0,
#                 status="CREATED",
#                 time=datetime.utcnow(),
#                 userEmail=userEmail
#             )
#
#             database.session.add(order)
#             database.session.flush()
#
#             for i, requestData in enumerate(request.json["requests"]):
#                 requestId = requestData.get('id', "")
#                 quantity = requestData.get('quantity', "")
#
#                 if requestId == "":
#                     raise ValueError(f"Product id is missing for request number {i}.")
#
#                 if quantity == "":
#                     raise ValueError(f"Product quantity is missing for request number {i}.")
#
#                 if not isinstance(requestId, int) or requestId <= 0:
#                     raise ValueError(f"Invalid product id for request number {i}.")
#
#                 if not isinstance(quantity, int) or quantity <= 0:
#                     raise ValueError(f"Invalid product quantity for request number {i}.")
#
#                 product = Product.query.filter_by(id=requestId).first()
#
#                 if product is None:
#                     raise ValueError(f"Invalid product for request number {i}.")
#
#                 orderProduct = OrderProduct(orderId=order.id, productId=product.id, quantity=quantity)
#                 database.session.add(orderProduct)
#                 database.session.flush()
#
#                 totalPrice = totalPrice + (product.price * quantity)
#
#             order.price = totalPrice
#
#     except ValueError as e:
#         database.session.rollback()
#         return jsonify({"message": str(e)}), 400
#
#     database.session.commit()
#
#     return jsonify({"id": order.id}), 200


@application.route("/status", methods=['GET'])
@jwt_required()
@roleCheck("customer")
def status():
    userEmail = get_jwt_identity()

    orders = Order.query.filter(Order.userEmail == userEmail).all()

    result = {
        "orders": [
            {
                "products": [
                    {
                        "categories": [category.name for category in product.categories],
                        "name": product.name,
                        "price": product.price,
                        "quantity": OrderProduct.query.filter(
                            and_(OrderProduct.productId == product.id, OrderProduct.orderId == order.id))
                            .first().quantity
                    }
                    for product in order.products
                ],
                "price": order.price,
                "status": order.status,
                "timestamp": order.time.strftime("%Y-%m-%dT%H:%M:%SZ"),
            }
            for order in orders
        ]
    }

    # result = {
    #     "orders": [
    #         OrderedDict([
    #             ("products", [
    #                 OrderedDict([
    #                     ("name", product.name),
    #                     ("categories", [category.name for category in product.categories]),
    #                     ("price", product.price),
    #                     ("quantity", OrderProduct.query.filter(OrderProduct.productId == product.id).first().quantity)
    #                 ])
    #                 for product in order.products
    #             ]),
    #             ("price", order.price),
    #             ("status", order.status),
    #             ("timestamp", order.time.strftime("%Y-%m-%dT%H:%M:%SZ")),
    #         ])
    #         for order in orders
    #     ]
    # }

    return jsonify(result), 200


@application.route("/delivered", methods=['POST'])
@jwt_required()
@roleCheck("customer")
def orderConfirm():
    if 'id' not in request.json:
        return jsonify({"message": "Missing order id."}), 400

    orderId = request.json["id"]

    if not isinstance(orderId, int) or orderId <= 0:
        return jsonify({"message": "Invalid order id."}), 400

    order = Order.query.filter(Order.id == orderId).first()

    if order is None:
        return jsonify({"message": "Invalid order id."}), 400

    if order.status != "PENDING":
        return jsonify({"message": "Invalid order id."}), 400

    order.status = "COMPLETE"
    database.session.commit()

    return Response(), 200

@application.route("/vezba", methods=['GET'])
def vezba():
    return str(Product.query.order_by(desc(Product.id)).all())



if (__name__ == "__main__"):
    database.init_app(application)
    application.run(debug=True, host="0.0.0.0", port=5002)
