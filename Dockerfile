FROM python:3.6
WORKDIR /code
COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt
COPY . .
ENV DATABASE_HOST=db
ENV DATABASE_PORT=5432
ENV DATABASE_USER=postgres
ENV DATABASE_PASSW=postgres
ENV DATABASE_NAME=avito_test
ENV BROKER_HOST=broker
ENV BROKER_PORT=5672
ENV API_KEY=