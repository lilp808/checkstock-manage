FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Railway จะส่ง PORT มาให้ทาง Environment Variable
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000"]