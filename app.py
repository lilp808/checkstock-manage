from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.responses import StreamingResponse
import pandas as pd
import io
import os

app = FastAPI()

@app.get("/")
def read_root():
    return {"message": "CSV Processor API is running. Use /process-csv-to-csv to upload files."}

@app.post("/process-csv-to-csv")
async def process_csv_to_csv(file: UploadFile = File(...)):
    # 1. อ่านข้อมูลจากไฟล์ที่ส่งมา
    try:
        contents = await file.read()
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Cannot read file: {str(e)}")

    # 2. ตรวจสอบและอ่านไฟล์ด้วย Encoding ที่เหมาะสมกับภาษาไทย
    try:
        # ลอง UTF-8 ก่อน
        df_raw = pd.read_csv(io.BytesIO(contents), header=None, encoding='utf-8')
    except:
        try:
            # ถ้าไม่ได้ให้ใช้ Windows-874 (ภาษาไทย)
            df_raw = pd.read_csv(io.BytesIO(contents), header=None, encoding='cp874')
        except Exception as e:
            raise HTTPException(status_code=422, detail="Unsupported encoding. Please use UTF-8 or CP874.")

    processed_data = []

    # 3. วนลูปจัดการข้อมูลตามโครงสร้างที่ต้องการ
    for _, row in df_raw.iterrows():
        # ลบช่องว่างส่วนเกินในแต่ละช่อง
        cols = [str(val).strip() if pd.notna(val) else "" for val in row.values]
        
        # คัดกรองเฉพาะแถวที่มีเลขลำดับในคอลัมน์ที่ 2 (index 1)
        row_id = cols[1] if len(cols) > 1 else ""
        
        if row_id.isdigit():
            processed_data.append({
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
            })

    if not processed_data:
        raise HTTPException(status_code=404, detail="No valid data rows found in the CSV.")

    # 4. สร้าง DataFrame ใหม่และแปลงกลับเป็น CSV Stream
    df_result = pd.DataFrame(processed_data)
    
    # ใช้ utf-8-sig เพื่อให้ Excel เปิดภาษาไทยได้ถูกต้อง
    stream = io.StringIO()
    df_result.to_csv(stream, index=False, encoding='utf-8-sig')
    
    # เตรียมข้อมูลส่งกลับ
    response_bytes = io.BytesIO(stream.getvalue().encode('utf-8-sig'))
    response_bytes.seek(0)

    return StreamingResponse(
        response_bytes,
        media_type="text/csv",
        headers={
            "Content-Disposition": "attachment; filename=cleaned_inventory.csv"
        }
    )

if __name__ == "__main__":
    import uvicorn
    # ดึงค่า PORT จาก Railway environment
    port = int(os.environ.get("PORT", 8080))
    uvicorn.run(app, host="0.0.0.0", port=port)