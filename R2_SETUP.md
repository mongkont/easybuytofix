# Cloudflare R2 Setup Guide

## การตั้งค่า Cloudflare R2 สำหรับ Django

### 1. ข้อมูล R2 ที่คุณให้มา:
- **Account ID**: `e5b7120932431231170883ebc727d3e1`
- **Bucket Name**: `easybuytofix`
- **S3 API**: `https://e5b7120932431231170883ebc727d3e1.r2.cloudflarestorage.com/easybuytofix`
- **Public URL**: `https://pub-e4286a7e2c854dd2b75a10748857903a.r2.dev`

### 2. การตั้งค่า Access Keys:

1. เข้าไปที่ [Cloudflare Dashboard](https://dash.cloudflare.com/)
2. ไปที่ **R2 Object Storage** > **Manage R2 API tokens**
3. สร้าง API token ใหม่:
   - **Permissions**: Object Read & Write
   - **Bucket**: easybuytofix
4. คัดลอก **Access Key ID** และ **Secret Access Key**

### 3. อัปเดตไฟล์ .env:

```bash
# Cloudflare R2 Settings
R2_ENABLED=True
R2_ACCOUNT_ID=e5b7120932431231170883ebc727d3e1
R2_ACCESS_KEY_ID=your_access_key_here
R2_SECRET_ACCESS_KEY=your_secret_key_here
R2_BUCKET_NAME=easybuytofix
R2_CUSTOM_DOMAIN=https://pub-e4286a7e2c854dd2b75a10748857903a.r2.dev
R2_ENDPOINT_URL=https://e5b7120932431231170883ebc727d3e1.r2.cloudflarestorage.com
```

### 4. ทดสอบการเชื่อมต่อ:

```bash
# เปิดใช้งาน virtual environment
source venv/bin/activate

# ทดสอบ R2 connection
python r2_test.py
```

### 5. การใช้งาน:

เมื่อ R2 ถูกเปิดใช้งาน ไฟล์ media ทั้งหมดจะถูกอัปโหลดไปยัง Cloudflare R2 โดยอัตโนมัติ

- **Local Storage**: เมื่อ `R2_ENABLED=False`
- **R2 Storage**: เมื่อ `R2_ENABLED=True`

### 6. ตัวอย่างการใช้งานใน Django:

```python
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile

# อัปโหลดไฟล์
file_content = ContentFile(b"Hello World")
saved_path = default_storage.save('test/hello.txt', file_content)

# ดึง URL ของไฟล์
file_url = default_storage.url(saved_path)
print(file_url)  # https://pub-e4286a7e2c854dd2b75a10748857903a.r2.dev/test/hello.txt
```

### 7. การตั้งค่า CORS (ถ้าจำเป็น):

หากต้องการให้ frontend เข้าถึงไฟล์ได้โดยตรง ให้ตั้งค่า CORS ใน Cloudflare R2:

```json
[
  {
    "AllowedOrigins": ["*"],
    "AllowedMethods": ["GET", "HEAD"],
    "AllowedHeaders": ["*"],
    "MaxAgeSeconds": 3000
  }
]
```

### 8. การจัดการไฟล์:

- ไฟล์ทั้งหมดจะถูกเก็บใน bucket `easybuytofix`
- URL ของไฟล์จะใช้ custom domain: `https://pub-e4286a7e2c854dd2b75a10748857903a.r2.dev/`
- ไฟล์จะถูก cache เป็นเวลา 24 ชั่วโมง (86400 วินาที)
