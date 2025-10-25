# Django Admin Display Rules

## การตั้งค่าการแสดงผลใน Django Admin

### 1. Avatar Display Rules
- **ListView**: รูป avatar ต้องเป็นวงกลม (circular) ขนาด 40px
- **Object-fit**: ใช้ `object-fit: cover` เสมอ
- **CSS Class**: `#result_list .field-avatar_preview img`

```css
#result_list .field-avatar_preview img {
    width: 40px !important;
    height: 40px !important;
    object-fit: cover !important;
    border-radius: 50% !important;
    border: 1px solid #ddd !important;
    display: block !important;
    margin: 0 auto !important;
}
```

### 2. Date Display Rules
- **ปี**: ต้องแสดงเป็น พ.ศ. (Buddhist Era) เสมอ
- **เดือน**: ใช้ชื่อเดือนภาษาไทย
- **รูปแบบ**: "25 ตุลาคม 2568, 19:22"

```python
def created_at_thai(self, obj):
    if obj.created_at:
        import pytz
        thai_tz = pytz.timezone('Asia/Bangkok')
        thai_time = obj.created_at.astimezone(thai_tz)
        buddhist_year = thai_time.year + 543
        
        thai_months = [
            'มกราคม', 'กุมภาพันธ์', 'มีนาคม', 'เมษายน', 'พฤษภาคม', 'มิถุนายน',
            'กรกฎาคม', 'สิงหาคม', 'กันยายน', 'ตุลาคม', 'พฤศจิกายน', 'ธันวาคม'
        ]
        
        month_name = thai_months[thai_time.month - 1]
        formatted_date = f"{thai_time.day} {month_name} {buddhist_year}, {thai_time.strftime('%H:%M')}"
        return formatted_date
    return "-"
```

### 3. Creator/Editor Display Rules
- **รูปแบบ**: "ชื่อ นามสกุล (username)"
- **ตัวอย่าง**: "มงคล ตั้งใจพิทักษ์ (mongkont)"
- **ถ้าไม่มีชื่อ**: แสดงแค่ username

```python
def created_by_display(self, obj):
    if obj.created_by:
        full_name = obj.created_by.get_full_name()
        if full_name:
            return f"{full_name} ({obj.created_by.username})"
        return obj.created_by.username
    return "-"
```

### 4. ListView Columns
- **User**: username
- **ชื่อ-นามสกุล**: full name
- **เบอร์โทรศัพท์**: phone number
- **รูปโปรไฟล์**: circular avatar
- **ผู้สร้าง**: creator name with username
- **ผู้แก้ไข**: editor name with username
- **วันที่สร้าง**: Thai Buddhist Era date

### 5. Required Packages
```txt
pytz==2024.1  # For timezone handling
Pillow==10.4.0  # For image processing
```

### 6. CSS File Location
- **File**: `static/css/admin.css`
- **Collect**: `python manage.py collectstatic --noinput`

---

**หมายเหตุ**: กฎเหล่านี้ต้องใช้กับทุก Django admin listview ในโปรเจ็กต์
