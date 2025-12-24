from fastapi import FastAPI, UploadFile, File
import pandas as pd
import io
import re

app = FastAPI()

@app.get("/")
def read_root():
    return {"status": "API is running"}

@app.post("/process-csv")
async def process_csv(file: UploadFile = File(...)):
    # 1. อ่านไฟล์ที่ส่งมา
    contents = await file.read()
    
    # 2. แปลงข้อความและจัดการบรรทัดที่ไม่เกี่ยวข้อง
    # ใช้ engine='python' เพื่อให้รองรับไฟล์ที่โครงสร้างไม่สมบูรณ์ได้ดีขึ้น
    df = pd.read_csv(io.BytesIO(contents), skiprows=0, header=None)

    result = []
    
    for index, row in df.iterrows():
        # แปลงข้อมูลในแต่ละแถวเป็น List ของ String
        cols = [str(val).strip() for val in row.values]
        
        # เงื่อนไข: คอลัมน์ที่ 2 (index 1) ต้องเป็นตัวเลขลำดับ
        # และมีความยาวคอลัมน์ที่เหมาะสม
        row_id = cols[1] if len(cols) > 1 else ""
        
        if row_id.isdigit():
            data = {
                "ลำดับ": row_id,
                "วันที่รับเข้า": cols[2] if len(cols) > 2 else "",
                "รายการสินค้า": cols[3] if len(cols) > 3 else "",
                "ทะเบียนเก่า": cols[4] if len(cols) > 4 else "",
                "ทะเบียนใหม่": cols[5] if len(cols) > 5 else "",
                "ปี": cols[6] if len(cols) > 6 else "",
                "CC": cols[7] if len(cols) > 7 else "",
                "สี": cols[8] if len(cols) > 8 else "",
                "วันที่ภาษีหมดอายุ": cols[9] if len(cols) > 9 else "",
                "ผู้จำหน่าย": cols[10] if len(cols) > 10 else "",
                "ประเภท": cols[11] if len(cols) > 11 else "",
                "มีเล่ม": cols[12] if len(cols) > 12 else "",
                "ราคา": cols[14] if len(cols) > 14 else ""
            }
            result.append(data)

    return {"count": len(result), "data": result}

if __name__ == "__main__":
    import uvicorn
    import os
    # พยายามดึงค่า PORT จากระบบ ถ้าไม่มีให้ใช้ 8080
    port = int(os.environ.get("PORT", 8080))
    uvicorn.run(app, host="0.0.0.0", port=port)