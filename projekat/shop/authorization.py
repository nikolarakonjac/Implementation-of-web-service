from functools import wraps
from flask_jwt_extended import verify_jwt_in_request, get_jwt
from flask import jsonify

def roleCheck(role):
    def innerRole(function):
        @wraps(function)
        def decorator(*arguments, **keywordArguments):
            verify_jwt_in_request() #ako nema tokena, fja baca izuzetak
            claims = get_jwt()  #dohvatimo payload deo
            if "roles" in claims and claims["roles"] == role:
                return function(*arguments, **keywordArguments) #pozivamo osnovnu fju koju dekorise roleCheck
            else:
                return jsonify({"msg": "Missing Authorization Header"}), 401
        return decorator
    return innerRole