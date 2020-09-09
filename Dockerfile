FROM python:2-alpine

WORKDIR /app

COPY requirements.txt ./
RUN pip install -r requirements.txt

COPY config.py llcd.py ./
RUN ls -la

CMD ["python", "./llcd.py"]