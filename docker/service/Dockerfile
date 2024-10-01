FROM python:3.9

WORKDIR /app

COPY ../../requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

RUN apt-get update && apt-get install -y netcat-openbsd postgresql-client

COPY ../.. .

RUN pip install pre-commit

RUN pre-commit install

RUN pre-commit run --all-files

CMD ["bash", "./start.sh"]

