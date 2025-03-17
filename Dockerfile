FROM python:3.12

WORKDIR /app
COPY . /app

RUN pip install poetry==2.1.1 poetry-plugin-export
RUN poetry export -f requirements.txt --output requirements.txt


RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt


CMD ["sh", "-c", "alembic upgrade head && python add_data.py && python main.py"]

