FROM python:3.12

ADD ./discord /discord
ADD ./common /common

WORKDIR /discord

RUN pip install -r req.txt

CMD ["python", "main.py"]