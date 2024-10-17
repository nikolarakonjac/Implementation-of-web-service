
from flask import Flask, request, Response, jsonify
from sqlalchemy import and_

from configuration import Configuration
from models import *
from flask_jwt_extended import jwt_required, JWTManager, get_jwt_identity
from authorization import roleCheck


application = Flask( __name__ )
application.config.from_object(Configuration)

jwt = JWTManager(application)



@application.route("/orders_to_deliver", methods=['GET'])
@jwt_required()
@roleCheck("courier")
def getNotDeliveredOrders():
    #narudzbine koje nisu preuzete

    # orders = Order.query.filter(Order.status != "COMPLETE").all()
    orders = Order.query.filter(Order.status == "CREATED").all()

    result = {
        "orders": [
            {
                "id": order.id,
                "email": order.userEmail
            }
            for order in orders
        ]
    }

    return jsonify(result), 200


@application.route("/pick_up_order", methods=['POST'])
@jwt_required()
@roleCheck("courier")
def pickUpOrder():

    if "id" not in request.json:
        return jsonify({"message": "Missing order id."}), 400

    orderId = request.json["id"]

    if not isinstance(orderId, int) or orderId <= 0:
        return jsonify({"message": "Invalid order id."}), 400

    order = Order.query.filter(Order.id == orderId).first()

    if order is None:
        return jsonify({"message": "Invalid order id."}), 400

    if order.status == "PENDING" or order.status == "COMPLETE":
        return jsonify({"message": "Invalid order id."}), 400

    order.status = "PENDING"
    database.session.commit()
    # status = pending; znaci da je neki kurir pokupio narudzbinu

    return Response(), 200

if(__name__ == "__main__"):
    database.init_app(application)
    application.run(debug=True, host="0.0.0.0", port=5003)