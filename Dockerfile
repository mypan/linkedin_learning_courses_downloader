FROM python:3-alpine

WORKDIR /app

COPY Pipfile Pipfile.lock ./
RUN pipenv install

COPY config.py lld.py ./
RUN ls -la

CMD ["pipenv", "run download"]