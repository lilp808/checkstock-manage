FROM python:3.9-slim

WORKDIR /app

# คัดลอกเฉพาะไฟล์ที่จำเป็นเพื่อทำ caching
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# คัดลอกโค้ดทั้งหมด
COPY . .

# Railway จะส่งตัวแปร PORT มาให้ เราสั่งรันผ่าน uvicorn โดยตรง
CMD uvicorn app:app --host 0.0.0.0 --port $PORT