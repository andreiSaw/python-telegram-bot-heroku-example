FROM python:3.7-slim

COPY requirements.txt /tmp
RUN pip install --no-cache-dir -r /tmp/requirements.txt

RUN mkdir /app
ADD . /app
WORKDIR /app

CMD python /app/bot.py