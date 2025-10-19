-- diabetes_db.sql

CREATE DATABASE IF NOT EXISTS diabetes_db;
USE diabetes_db;

-- ตารางเก็บบัญชีผู้ใช้
CREATE TABLE Account (
    UserID INT AUTO_INCREMENT PRIMARY KEY,
    FirstName VARCHAR(100),
    LastName VARCHAR(100),
    Birthday DATE,
    Email VARCHAR(100) UNIQUE,
    Password VARCHAR(255),
    Role ENUM('User','Admin') DEFAULT 'User',
    ProfileImage VARCHAR(255) NULL,
    CreatedTime DATETIME DEFAULT CURRENT_TIMESTAMP,
    UpdatedTime DATETIME ON UPDATE CURRENT_TIMESTAMP
);

INSERT INTO Account (UserID, FirstName, LastName, Birthday, Email, Password, Role)
VALUES
    (1, "AdminFN", "AdminLN", STR_TO_DATE('02/12/2003', '%d/%m/%Y'), "AdminEmail@gmail.com", "$2y$10$GZnzKnkrerBHpGixhlDDEuKhZwJWOi7bKh.JUYg6i9yLR2YuZUtge", "Admin"),
    (2, "UserFN", "UserLN", STR_TO_DATE('03/12/2003', '%d/%m/%Y'), "user123@gmail.com", "$2y$10$WNmnosqqy1iqkkLYW2RBmepvdRd05pnF5LvBde3DkOsaIc7Gn/gpW", "User");

-- ตารางหมวดหมู่ความเสี่ยง
CREATE TABLE Category (
    CategoryID INT AUTO_INCREMENT PRIMARY KEY,
    RiskPercent_Lower FLOAT,
    RiskPercent_Upper FLOAT,
    Risk_Level VARCHAR(255),
    Risk_Color VARCHAR(255),
    Risk_Icon VARCHAR(255),
    Recommendation TEXT
);

INSERT INTO Category (CategoryID, RiskPercent_Lower, RiskPercent_Upper, Risk_Level, Risk_Color, Risk_Icon, Recommendation)
VALUES
    (1, 0.00, 49.99, "ความเสี่ยงต่ำที่สุด", "green-dark", "1_GenHlth_Black.png",
    "อาหาร: ปลูกผักกินเอง งดน้ำอัดลม รับประทานผลไม้รสไม่หวานจัด หลีกเลี่ยงหอยนางรม หมึก กุ้งตัวใหญ่ เนื้อสัตว์ติดมัน ลดการบริโภคผงชูรส ลดดื่มกาแฟสำเร็จรูป\n
    ออกกำลังกาย: ออกกำลังกายอย่างสม่ำเสมอ อย่างน้อยสัปดาห์ละ 3 วัน วันละ 30 นาที\n
    การติดตาม: ตรวจสุขภาพอย่างน้อยปีละ 1 ครั้ง
    "),
    (2, 50.00, 59.99, "ความเสี่ยงต่ำ", "green-light", "2_GenHlth_Black.png",
    "อาหาร: รับประทานข้าวไม่ขัดสี ผักวันละ 3 ทัพพี ผลไม้ที่ไม่หวานจัด ลดเนื้อสัตว์ที่ติดมัน\n
    ออกกำลังกาย: ออกกำลังกายอย่างสม่ำเสมอ อย่างน้อยสัปดาห์ละ 3 วัน วันละ 30 นาที\n
    การติดตาม: นัดพบแพทย์ทุก 3 เดือน
    "),
    (3, 60.00, 69.99, "ความเสี่ยงปานกลาง", "yellow", "3_GenHlth_Black.png",
    "อาหาร: รับประทานข้าวไม่ขัดสี ผักวันละ 3 ทัพพี ลดการบริโภคน้ำตาล ลดเนื้อสัตว์ที่ติดมัน\n
    ออกกำลังกาย: ออกกำลังกายอย่างสม่ำเสมอ อย่างน้อยสัปดาห์ละ 3 วัน\n
    การติดตาม: นัดพบแพทย์ทุก 1 เดือน
    "),
    (4, 70.00, 89.99, "ความเสี่ยงมาก", "orange", "4_GenHlth_Black.png",
    "อาหาร: รับประทานข้าวไม่ขัดสี ลดผลไม้เป็น 2-3 ส่วน/วัน ดื่มนมจืดพร่องมันเนย วันละ 3 แก้ว\n
    ออกกำลังกาย: ออกกำลังกายอย่างสม่ำเสมอ วัดความดันและตรวจระดับน้ำตาลทุก 1-3 เดือน\n
    การติดตาม: พบแพทย์ทุก 1 เดือนหรือเมื่อมีอาการผิดปกติ
    "),
    (5, 90.00, 100.00, "ความเสี่ยงมากที่สุด", "red", "5_GenHlth_Black.png",
    "อาหาร: รับประทานข้าวไม่ขัดสี ผักวันละ 3 ทัพพี ลดผลไม้เป็น 2-3 ส่วน/วัน ดื่มนมจืดพร่องมันเนย วันละ 1 แก้ว\n
    ออกกำลังกาย: ออกกำลังกายอย่างสม่ำเสมอ ควบคุมน้ำหนักตามคำแนะนำของแพทย์\n
    การติดตาม: พบแพทย์ทุก 2-4 สัปดาห์ และติดตามเยี่ยมบ้าน ตรวจภาวะแทรกซ้อน
    ");

-- ตารางเก็บผลประเมิน
CREATE TABLE PredictionRecord (
    PredictionID INT AUTO_INCREMENT PRIMARY KEY,
    UserID INT,
    HighBP INT,
    HighChol INT,
    BMI INT,
    HeartDiseaseorAttack INT,
    GenHlth INT,
    PhysHlth INT,
    DiffWalk INT,
    Age INT,
    BMI_cat_code INT,
    BMI_Age_interaction INT,
    CategoryID INT,
    Height INT,
    Weight INT,
    Model_Used VARCHAR(100),
    PredictDateTime DATETIME,
    Result_Binary INT,
    Result_Percentage FLOAT,
    UserNote TEXT,
    FOREIGN KEY (UserID) REFERENCES Account(UserID),
    FOREIGN KEY (CategoryID) REFERENCES Category(CategoryID)
);

-- ตารางบันทึกการกระทำของแอดมิน
CREATE TABLE AdminLog (
    LogID INT AUTO_INCREMENT PRIMARY KEY,
    UserID INT,
    Action VARCHAR(255),
    TargetType ENUM('Image','Model','Recommendation'),
    TargetID INT NULL,
    Timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (UserID) REFERENCES Account(UserID)
);

-- ตารางรูปภาพความรู้
-- CREATE TABLE HealthImage (
--     ImageID INT AUTO_INCREMENT PRIMARY KEY,
--     Title VARCHAR(255),
--     Description TEXT,
--     ImagePath VARCHAR(255),
--     UploadedBy INT,
--     UploadedTime DATETIME DEFAULT CURRENT_TIMESTAMP,
--     FOREIGN KEY (UploadedBy) REFERENCES Account(UserID)
-- );

-- ตารางเก็บไฟล์โมเดล
CREATE TABLE ModelFile (
    ModelID INT AUTO_INCREMENT PRIMARY KEY,
    FileName VARCHAR(255),
    FilePath VARCHAR(255),
    UploadedBy INT,
    UploadedTime DATETIME DEFAULT CURRENT_TIMESTAMP,
    Status ENUM('Active','Deprecated') DEFAULT 'Active',
    FOREIGN KEY (UploadedBy) REFERENCES Account(UserID)
);

-- ตารางเก็บกิจกรรมในปฏิทิน
CREATE TABLE calendar_events (
    id INTEGER PRIMARY KEY AUTO_INCREMENT,
    user_id INTEGER NOT NULL,
    event_date DATE NOT NULL,
    event_title VARCHAR(200) NOT NULL,
    event_description VARCHAR(500),
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);
