FROM python:3.7-slim

ENV MODE=$MODE
COPY requirements.txt .
RUN pip install -r requirements.txt && rm -rf /root/.cache

ADD . /app
CMD python3 /app/bot.py