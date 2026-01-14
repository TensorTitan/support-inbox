FROM python:3.11-slim

COPY main.py main.py

RUN pip install pika requests

CMD ["python", "-u", "main.py"]