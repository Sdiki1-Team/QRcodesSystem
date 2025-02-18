FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt /app/

RUN pip install --no-cache-dir -r requirements.txt

COPY . /app/

RUN python manage.py migrate
EXPOSE 8000

CMD ["python", "manage.py", "runserver", "127.0.0.1:8000"]
