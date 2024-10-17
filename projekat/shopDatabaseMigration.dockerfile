FROM python:3

RUN mkdir -p /opt/src/shop
WORKDIR /opt/src/shop


COPY shop/migrate.py ./migrate.py
COPY shop/configuration.py ./configuration.py
COPY shop/models.py ./models.py
COPY shop/requirments.txt ./requirments.txt


RUN pip install -r ./requirments.txt


ENTRYPOINT ["python", "./migrate.py"]


