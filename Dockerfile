FROM python:3.7

RUN pip install -r requirements.txt --no-cache-dir

RUN mkdir /app
ADD . /app
WORKDIR /app

CMD python /app/bot.py