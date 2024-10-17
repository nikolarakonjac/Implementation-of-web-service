from flask import Flask, request, Response, jsonify
from configuration import Configuration
from models import *
from email.utils import parseaddr
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, create_refresh_token, get_jwt, get_jwt_identity
from sqlalchemy import and_
import re

application = Flask( __name__ )
application.config.from_object(Configuration)


@application.route("/register_customer", methods=['POST'])
def registerCustomer():
    data = request.get_json(force=True)

    forename = data.get("forename", "")
    surname = data.get("surname", "")
    email = data.get("email", "")
    password = data.get("password", "")

    forenameEmpty = len(forename) == 0
    surnameEmpty = len(surname) == 0
    emailEmpty = len(email) == 0
    passwordEmpty = len(password) == 0



    if forenameEmpty:
        return jsonify({"message": "Field forename is missing."}), 400
    elif surnameEmpty:
        return jsonify({"message": "Field surname is missing."}), 400
    elif emailEmpty:
        return jsonify({"message": "Field email is missing."}), 400
    elif passwordEmpty:
        return jsonify({"message": "Field password is missing."}), 400

    #provera da li je email u dobrom formatu
    email_pattern = re.compile(r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}")

    if( not (re.match(email_pattern, email))):
        return jsonify({"message": "Invalid email."}), 400

    if len(password) < 8:
        return jsonify({"message": "Invalid password."}), 400


    #provera da li zadati email vec postoji u bazi
    if User.query.filter_by(email=email).first():
        return jsonify({"message": "Email already exists."}), 400

    consumer_role = Role.query.filter_by(name="customer").first()

    if consumer_role is None:
        return jsonify({"message": "Role 'customer' not found."}), 200

    new_user = User(email=email, password=password, forename=forename, surname=surname, roleId=consumer_role.id)
    database.session.add(new_user)
    database.session.commit()

    return Response(), 200


@application.route("/register_courier", methods=['POST'])
def registerCourier():
    data = request.get_json(force=True)

    forename = data.get("forename", "")
    surname = data.get("surname", "")
    email = data.get("email", "")
    password = data.get("password", "")

    forenameEmpty = len(forename) == 0
    surnameEmpty = len(surname) == 0
    emailEmpty = len(email) == 0
    passwordEmpty = len(password) == 0

    if forenameEmpty:
        return jsonify({"message": "Field forename is missing."}), 400
    elif surnameEmpty:
        return jsonify({"message": "Field surname is missing."}), 400
    elif emailEmpty:
        return jsonify({"message": "Field email is missing."}), 400
    elif passwordEmpty:
        return jsonify({"message": "Field password is missing."}), 400

    #provera da li email dobrog formata
    emailPattern = re.compile(r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}")

    if (not (re.match(emailPattern, email))):
        return jsonify({"message": "Invalid email."}), 400

    if len(password) < 8:
        return jsonify({"message": "Invalid password."}), 400

    # provera da li zadati email vec postoji u bazi
    if User.query.filter_by(email=email).first():
        return jsonify({"message": "Email already exists."}), 400


    courierRole = Role.query.filter_by(name="courier").first()

    if courierRole is None:
        return jsonify({"message": "Role 'courier' not found."}), 200

    newUser = User(email=email, password=password, forename=forename, surname=surname, roleId=courierRole.id)
    database.session.add(newUser)
    database.session.commit()

    return Response(), 200


jwt = JWTManager( application )

@application.route("/login", methods=['POST'])
def loginUser():
    data = request.get_json(force=True)
    email = data.get("email", "")
    password = data.get("password", "")

    emailEmpty = len(email) == 0
    passwordEmpty = len(password) == 0

    if emailEmpty:
        return jsonify({"message": "Field email is missing."}), 400
    elif passwordEmpty:
        return jsonify({"message": "Field password is missing."}), 400

    # provera da li email dobrog formata
    emailPattern = re.compile(r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}")

    if (not (re.match(emailPattern, email))):
        return jsonify({"message": "Invalid email."}), 400

    if len(password) < 8:
        return jsonify({"message": "Invalid credentials."}), 400

    user = User.query.filter(and_(User.email == email, User.password == password)).first()
    if user is None:
        return jsonify({"message": "Invalid credentials."}), 400

    additionalClaims = {
        "forename": user.forename,
        "surname": user.surname,
        "roles": "customer" if user.roleId == 1 else "courier" if user.roleId == 2 else "owner"
    }

    accessToken = create_access_token(identity=user.email, additional_claims=additionalClaims)

    return jsonify({"accessToken": accessToken}), 200



#korisnik zeli da obrise svoj nalog
@application.route("/delete", methods=['POST'])
@jwt_required()
def deleteUser():
    email = get_jwt_identity()

    user = User.query.filter(User.email == email).first()

    if user is None:
        return jsonify({"message": "Unknown user."}), 400

    database.session.delete(user)
    database.session.commit()

    return Response(), 200


if(__name__ == "__main__"):
    database.init_app(application)
    application.run(debug=True, host="0.0.0.0", port=5000)









