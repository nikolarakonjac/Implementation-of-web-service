from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import ForeignKey

database = SQLAlchemy() #nasa baza

class User(database.Model):
    __tablename__ = "users"

    id = database.Column(database.Integer, primary_key=True)
    email = database.Column(database.String(256), nullable=False, unique=True)
    password = database.Column(database.String(256), nullable=False)
    forename = database.Column(database.String(256), nullable=False)
    surname = database.Column(database.String(256), nullable=False)

    #strani kljuc -> veza sa Role tableom
    roleId = database.Column(database.Integer, ForeignKey('roles.id'), nullable=False)
    role = database.relationship('Role', back_populates='users')



class Role(database.Model):
    __tablename__ = "roles"

    id = database.Column(database.Integer, primary_key=True)
    name = database.Column(database.String(256), nullable=False)

    users = database.relationship('User', back_populates='role', uselist=True)


    def __repr__(self):
        return self.name