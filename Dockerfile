FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY src/ src/
COPY Procfile .
COPY railway.json .

EXPOSE 8000

CMD ["python", "src/api.py"]
