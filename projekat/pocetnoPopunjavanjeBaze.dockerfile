FROM python:3

RUN mkdir -p /opt/src/upravljanjeKorisnickimNalozima
WORKDIR /opt/src/upravljanjeKorisnickimNalozima


COPY upravljanjeKorisnickimNalozima/migrate.py ./migrate.py
COPY upravljanjeKorisnickimNalozima/configuration.py ./configuration.py
COPY upravljanjeKorisnickimNalozima/models.py ./models.py
COPY upravljanjeKorisnickimNalozima/requirments.txt ./requirments.txt


RUN pip install -r ./requirments.txt


ENTRYPOINT ["python", "./migrate.py"]


