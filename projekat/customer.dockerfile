FROM python:3

RUN mkdir -p /opt/src/shop
WORKDIR /opt/src/shop


COPY shop/customerApplication.py ./customerApplication.py
COPY shop/configuration.py ./configuration.py
COPY shop/models.py ./models.py
COPY shop/requirments.txt ./requirments.txt
COPY shop/authorization.py ./authorization.py

RUN pip install -r ./requirments.txt

ENV PYTHONPATH="/opt/src/shop"

ENTRYPOINT ["python", "./customerApplication.py"]


