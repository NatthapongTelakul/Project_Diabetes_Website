# Project Diabetes Website (Python + Flask)

โปรเจกต์นี้เป็น Web Application ที่พัฒนาด้วย **Python** และ **Flask**  
จัดทำโดย  
1.นาย นัทธพงศ์ เตละกุล รหัสนักศึกษา 6510210155  
2.นางสาว นลินทิพย์ สุวรรณลอยล่อง รหัสนักศึกษา 6510210143  

## ขั้นตอนการติดตั้ง

### 1. ติดตั้ง Python
ดาวน์โหลดและติดตั้ง Python ได้ที่:  
[Python Downloads](https://www.python.org/downloads/)

ตรวจสอบเวอร์ชัน Python ใน CMD:
```bash
python --version
```

### 2. ติดตั้ง Flask และ Library ที่จำเป็น
ติดตั้ง Flask:
```bash
pip install Flask
```

ตรวจสอบว่า Flask ถูกติดตั้งแล้ว:
```bash
pip freeze
```

ติดตั้ง flask-mysqldb ใช้เชื่อม MySQL
```bash
pip install flask-mysqldb
```
  
ติดตั้ง flask-jwt-extended หรือ PyJWT เพื่อ สร้าง/ตรวจ JWT  
```bash  
pip install flask-jwt-extended
```  

ติดตั้ง flask-bcrypt เพื่อ hash รหัสผ่าน  
```bash  
pip install flask-bcrypt
```  
ติดตั้ง PyJWT เพื่อสร้าง/ถอด JWT  
```bash  
pip install PyJWT
```  
ติดตั้ง python-dotenv เพื่อเก็บ config แบบปลอดภัยใน .env
```bash
pip install python-dotenv
```  

ติดตั้ง library อื่น ๆ ที่จำเป็น:
```bash
pip install joblib
pip install pandas
pip install -U Flask-WTF
```

## วิธีใช้ไฟล์ SQL  
วิธีที่ 1: ผ่าน phpMyAdmin  
1. เข้า http://localhost/phpmyadmin  
2. สร้างฐานข้อมูลชื่อ diabetes_db  
3. ไปที่แท็บ “Import”  
4. เลือกไฟล์ diabetes_db.sql  
5. คลิก “Go”  
วิธีที่ 2: ผ่าน Terminal  
```bash
mysql -u root -p < database/diabetes_db.sql
```

---

## วิธีรัน Project

ไปที่โฟลเดอร์โปรเจกต์ของคุณ (เช่น `Project_Diabetes_Website`)  
และรันด้วยคำสั่ง:

```bash
Your directory>python -u "Your directory\app.py"
```

**ตัวอย่าง**:  
```bash
D:\Project_Diabetes_Website>python -u "d:\Project_Diabetes_Website\app.py"
```

จากนั้นเปิดเว็บเบราว์เซอร์แล้วเข้าไปที่:  
`http://127.0.0.1:5000/`  

---

