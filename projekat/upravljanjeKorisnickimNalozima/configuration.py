from datetime import timedelta
import os

# databaseAddress = os.environ["DATABASE_ADDRESS"]
class Configuration():
    # SQLALCHEMY_DATABASE_URI = f"mysql+pymysql://root:root@{databaseAddress}/korisnickiNalozi"
    SQLALCHEMY_DATABASE_URI = f"mysql+pymysql://root:root@localhost:3307/korisnickiNalozi"

    JWT_SECRET_KEY = "JWT_SECRET_DEV_KEY"
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=1)
    JWT_REFRESH_TOKEN_EXPIRES = timedelta(days=30)




