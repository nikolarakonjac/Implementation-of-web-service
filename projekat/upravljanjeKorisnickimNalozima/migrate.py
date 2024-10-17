import os
import shutil
from flask import Flask
from configuration import Configuration
from models import *
from flask_migrate import Migrate, init, migrate, upgrade
from sqlalchemy_utils import database_exists, create_database

application = Flask(__name__)
application.config.from_object(Configuration)

migrateObject = Migrate(application, database)

if (not database_exists(application.config["SQLALCHEMY_DATABASE_URI"])):
    create_database(application.config["SQLALCHEMY_DATABASE_URI"])

database.init_app(application)

if os.path.exists("migrations"):
    shutil.rmtree("migrations")

with application.app_context() as context:
    init()
    migrate(message="pocetno popunjavanje baze rolama i jednim vlasnikom")
    upgrade()

    kupacRole = Role(name="customer")
    kurirRole = Role(name="courier")
    vlasnikRole = Role(name="owner")

    database.session.add(kupacRole)
    database.session.add(kurirRole)
    database.session.add(vlasnikRole)
    database.session.commit()

    user = User(
        forename="Scrooge",
        surname="McDuck",
        email="onlymoney@gmail.com",
        password="evenmoremoney",
        roleId=vlasnikRole.id
    )

    database.session.add(user)
    database.session.commit()
