import os
import joblib
import pandas as pd
import numpy as np
from flask import Flask, request, render_template, redirect, url_for, flash, session, jsonify

from db_config import init_db
from dotenv import load_dotenv
from flask_bcrypt import Bcrypt
from flask_mysqldb import MySQL
from werkzeug.utils import secure_filename # สำหรับจัดการชื่อไฟล์ที่อัปโหลด

from forms import (
    HighBPForm, HighCholForm, HeartForm, DiffWalkForm,
    HeightAndWeightForm, GenHlthForm, PhyshlthForm,
    AgeForm, ModelChoiceForm
)

# โหลดค่าจากไฟล์ .env
load_dotenv()

app = Flask(__name__)

# ตั้งค่าจาก .env
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')
app.config['JWT_SECRET_KEY'] = os.getenv('JWT_SECRET_KEY')  # flask-jwt-extended

# ตั้งค่า MySQL
app.config['MYSQL_HOST'] = os.getenv('MYSQL_HOST')
app.config['MYSQL_USER'] = os.getenv('MYSQL_USER')
app.config['MYSQL_PASSWORD'] = os.getenv('MYSQL_PASSWORD')
app.config['MYSQL_DB'] = os.getenv('MYSQL_DB')

# เริ่มต้นใช้งานส่วนเสริม
mysql = MySQL(app)
bcrypt = Bcrypt(app)

# เรียกใช้การเชื่อมต่อ DB
mysql = init_db(app)

# ฟังก์ชันคำนวณ BMI Category
def bmi_category_code(bmi):
    if bmi < 18.5:
        return 0   # Underweight
    elif bmi < 25:
        return 1   # Normal
    elif bmi < 30:
        return 2   # Overweight
    else:
        return 3   # Obese

# Step configuration: name, form class, image file (optional)
steps = [
    {"name": "highbp", "form": HighBPForm, "image": "highbp.png"},
    {"name": "highchol", "form": HighCholForm, "image": "highchol.png"},
    {"name": "heart", "form": HeartForm, "image": "heart.png"},
    {"name": "diffwalk", "form": DiffWalkForm, "image": "diffwalk.png"},
    {"name": "height_weight", "form": HeightAndWeightForm, "image": "height_weight.png"},
    {"name": "genhlth", "form": GenHlthForm, "image": "genhlth.png"},
    {"name": "physhlth", "form": PhyshlthForm, "image": "physhlth.png"},
    {"name": "age", "form": AgeForm, "image": "age.png"},
    {"name": "model_choice", "form": ModelChoiceForm, "image": "model_choice.png"},
]

ALLOWED_IMAGE_EXT = {'png','jpg','jpeg'}
UPLOAD_FOLDER_IMAGES = '/static/images/ProfileImage'
UPLOAD_FOLDER_MODELS = '/models'
app.config['UPLOAD_FOLDER_IMAGES'] = UPLOAD_FOLDER_IMAGES
app.config['UPLOAD_FOLDER_MODELS'] = UPLOAD_FOLDER_MODELS

def allowed_file(filename, allowed_set):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in allowed_set

# เริ่มต้นการทำงานที่ index.html
@app.route('/', methods=['GET', 'POST'])
def index():
    return render_template('index.html')

@app.route('/sign')
def sign():
    return render_template('sign.html')

# ลงทะเบียน account ใหม่
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'GET':
        return render_template('sign.html')

    data = request.form
    first = data.get('firstname')
    last = data.get('lastname')
    email = data.get('email')
    password = data.get('password')
    birthday = data.get('birthday')  # format YYYY-MM-DD

    # จัดการไฟล์รูปภาพโปรไฟล์
    profile_image_path = None
    if 'profile_image' in request.files:
        file = request.files['profile_image']
        if file and file.filename != '' and allowed_file(file.filename, ALLOWED_IMAGE_EXT):
            filename = secure_filename(file.filename)
            # เพิ่ม timestamp เพื่อป้องกันชื่อไฟล์ซ้ำ
            import time
            timestamp = str(int(time.time()))
            name, ext = os.path.splitext(filename)
            unique_filename = f"{name}_{timestamp}{ext}"
            
            # บันทึกไฟล์
            upload_path = os.path.join(app.root_path, 'static', 'images', 'ProfileImage')
            if not os.path.exists(upload_path):
                os.makedirs(upload_path)
            
            file.save(os.path.join(upload_path, unique_filename))
            # เก็บ path สำหรับใช้ใน database
            profile_image_path = f"/static/images/ProfileImage/{unique_filename}"

    if not (email and password):
        flash("Email and password required", "danger")
        return redirect(url_for('register'))

    # Check existing email
    cur = mysql.connection.cursor()
    cur.execute("SELECT UserID FROM Account WHERE Email=%s", (email,))
    if cur.fetchone():
        flash("Email already registered", "warning")
        cur.close()
        return redirect(url_for('register'))

    # ใช้ flask_bcrypt เข้ารหัส
    hashed = bcrypt.generate_password_hash(password).decode('utf-8')

    # Insert พร้อม ProfileImage
    if profile_image_path:
        sql = """INSERT INTO Account (FirstName, LastName, Birthday, Email, Password, Role, ProfileImage)
                 VALUES (%s, %s, %s, %s, %s, %s, %s)"""
        cur.execute(sql, (first, last, birthday, email, hashed, 'User', profile_image_path))
    else:
        sql = """INSERT INTO Account (FirstName, LastName, Birthday, Email, Password, Role)
                 VALUES (%s, %s, %s, %s, %s, %s)"""
        cur.execute(sql, (first, last, birthday, email, hashed, 'User'))
    
    mysql.connection.commit()
    cur.close()
    flash("Registered successfully. Please login.", "success")
    return redirect(url_for('login'))














# Login เข้ารหัส Password แบบ bcrypt
@app.route('/login', methods=['GET', 'POST'])
def login():
    # ถ้าเป็นการเข้าหน้า login แบบ GET ให้แสดงหน้าเว็บ sign.html
    if request.method == 'GET':
        return render_template('sign.html')

    # ถ้าเป็นการส่งข้อมูล login แบบ POST
    email = request.form['email']
    password = request.form['password']

    # ตรวจสอบว่ากรอกครบไหม
    if not (email and password):
        flash("Please fill in both email and password.", "warning")
        return redirect(url_for('login'))

    # สร้าง cursor เพื่อ query ข้อมูลจากฐานข้อมูล
    cur = mysql.connection.cursor()
    cur.execute("SELECT UserID, FirstName, LastName, Email, Password, Role FROM Account WHERE Email=%s", (email,))
    user = cur.fetchone()
    cur.close()

    # ตรวจสอบว่ามี email นี้ในระบบไหม
    if user is None:
        flash("Email not found. Please register first.", "danger")
        return redirect(url_for('login'))


    # ตรวจสอบรหัสผ่านที่ผู้ใช้กรอก กับรหัสผ่านที่ hash เก็บไว้ใน DB
    # bcrypt.check_password_hash(รหัสที่เก็บใน DB, รหัสที่ผู้ใช้กรอก)
    if bcrypt.check_password_hash(user['Password'], password):
        # ถ้ารหัสผ่านถูกต้อง
        session['user_id'] = user['UserID']
        session['email'] = user['Email']
        session['role'] = user['Role']
        session['first_name'] = user['FirstName']

        # แยกหน้าแสดงผลตาม Role
        if user['Role'] == 'Admin':
            return redirect(url_for('admin_dashboard'))  # ไปหน้า admin
        else:
            return redirect(url_for('home'))   # ไปหน้า user
    else:
        # ถ้ารหัสผ่านไม่ตรง
        flash("Invalid password. Please try again.", "danger")
        return redirect(url_for('login'))
























































@app.route('/home')
def home():
    return render_template('home.html')



















# redirect /predict -> /predict/1
@app.route('/predict')
def predict_root():
    return redirect(url_for('predict_step', step=1))

@app.route('/predict/<int:step>', methods=['GET', 'POST'])
def predict_step(step):
    total_steps = len(steps)
    if step < 1 or step > total_steps:
        return redirect(url_for('predict_step', step=1))

    step_cfg = steps[step - 1]
    FormClass = step_cfg['form']
    form = FormClass()

    if form.validate_on_submit():
        # เก็บทุก field ในฟอร์มลง session (ยกเว้น csrf & submit)
        for fname, ffield in form._fields.items():
            if fname in ('csrf_token', 'submit'):
                continue
            session[fname] = ffield.data
        # ถ้าเป็น step สุดท้าย ให้ไปหน้า result
        if step == total_steps:
            return redirect(url_for('result'))
        # นอกจากนั้น step ถัดไป
        return redirect(url_for('predict_step', step=step + 1))

    image = step_cfg.get('image')
    return render_template('step.html', form=form, step=step, total=total_steps, image=image)

@app.route('/predict/result')
def result():
    # เอาข้อมูลจาก session มาจัด features
    # ระวังค่าสตริง -> แปลงเป็น int ก่อนใช้
    try:
        highbp = int(session.get('highbp', 0))
        highchol = int(session.get('highchol', 0))
        heart = int(session.get('heart', 0))
        diffwalk = int(session.get('diffwalk', 0))
        genhlth = int(session.get('genhlth', 3))
        physhlth = int(session.get('physhlth', 0))
        # age stored as choice string like "1","2"... convert to index or numeric representation you used in training
        age_choice = session.get('age', "1")
        age = int(age_choice)
        # height & weight
        height = session.get('height')
        weight = session.get('weight')
        if height is not None and weight is not None:
            height = float(height)
            weight = float(weight)
            height_m = height / 100.0
            bmi = weight / (height_m ** 2)
            bmi = round(bmi, 2)
        else:
            bmi = 0.0

        bmi_cat = bmi_category_code(bmi)
        bmi_age_interaction = int(round(bmi * age))

        # สร้าง DataFrame ตาม feature ที่โมเดลคาดหวัง
        features = pd.DataFrame([{
            'HighBP': highbp,
            'HighChol': highchol,
            'BMI': bmi,
            'HeartDiseaseorAttack': heart,
            'GenHlth': genhlth,
            'PhysHlth': physhlth,
            'DiffWalk': diffwalk,
            'Age': age,
            'BMI_cat_code': bmi_cat,
            'BMI_Age_interaction': bmi_age_interaction
        }])

        # เลือกโมเดลจาก session (value เช่น 'random_forest', 'knn' ...)
        model_name = session.get('model_choice', 'random_forest')
        model_path = os.path.join('models', f"{model_name}.joblib")
        if os.path.exists(model_path):
            model = joblib.load(model_path)
            y_pred = model.predict(features)[0]
            # ถ้าโมเดลมี predict_proba
            try:
                y_prob = model.predict_proba(features)[0][1] * 100
            except Exception:
                y_prob = None
            prediction_result = int(y_pred)
            probability = round(y_prob, 2) if y_prob is not None else None
        else:
            # หากไม่มีโมเดล ให้ mock ผลลัพธ์ (หรือแจ้ง error)
            prediction_result = 0
            probability = None

        # ส่งข้อมูลไปแสดง
        data = {cfg['name']: session.get(cfg['name']) for cfg in steps}
        return render_template('result.html',
                               prediction=prediction_result,
                               probability=probability,
                               data=data,
                               bmi=bmi)
    except Exception as e:
        # แสดง error ง่ายๆ (คุณอาจอยากบันทึก/แจ้งอย่างดีกว่านี้)
        return f"Error preparing result: {e}", 500

# @app.route('/predict', methods=['GET', 'POST'])
# def predict():
#     # user_id = session.get('user_id')
#     # username = session.get('username')
#     form = MyForm()
    
#     prediction_result = None
#     probability = None

#     if form.validate_on_submit():
#         # ดึงค่าจากฟอร์ม
#         highbp = int(form.highbp.data)
#         highchol = int(form.highchol.data)
#         heart = int(form.heart.data)
#         diffwalk = int(form.diffwalk.data)
#         genhlth = int(form.genhlth.data)
#         physhlth = int(form.physhlth.data)
#         age = int(form.age.data)

#         # คำนวณ BMI
#         height_m = form.height.data / 100
#         bmi = int(form.weight.data / (height_m ** 2))

#         # BMI Category
#         bmi_cat = bmi_category_code(bmi)

#         # BMI x Age interaction
#         bmi_age_interaction = int(bmi * age)

#         # เก็บใน session
#         session['highbp'] = highbp
#         session['highchol'] = highchol
#         session['heart'] = heart
#         session['diffwalk'] = diffwalk
#         session['genhlth'] = genhlth
#         session['physhlth'] = physhlth
#         session['age'] = age
#         session['bmi'] = bmi
#         session['bmi_cat'] = bmi_cat
#         session['bmi_age_interaction'] = bmi_age_interaction

#         # เตรียม feature vector ตามลำดับที่ใช้ตอนเทรน
#         features = pd.DataFrame([{
#             'HighBP': highbp,
#             'HighChol': highchol,
#             'BMI': bmi,
#             'HeartDiseaseorAttack': heart,
#             'GenHlth': genhlth,
#             'PhysHlth': physhlth,
#             'DiffWalk': diffwalk,
#             'Age': age,
#             'BMI_cat_code': bmi_cat,
#             'BMI_Age_interaction': bmi_age_interaction
#         }])


#         # โหลดโมเดล
#         model_name = form.model_choice.data
#         model_path = os.path.join("models", f"{model_name}.joblib")
#         model = joblib.load(model_path)

#         # ทำการพยากรณ์
#         y_pred = model.predict(features)[0]
#         y_prob = model.predict_proba(features)[0][1] * 100  # ความน่าจะเป็น class 1 (%)

#         prediction_result = int(y_pred)
#         probability = round(y_prob, 2)

#         # เก็บผลใน session
#         session['prediction'] = prediction_result
#         session['probability'] = probability

#         # เก็บค่าลง database พร้อมผลการพยากรณ์
#         # save_to_db(user_id, username, prediction_result, probability)
#     return render_template('predict.html', form=form,
#                            prediction=session.get('prediction'),
#                            probability=session.get('probability'))

@app.route('/admin/dashboard')
def admin_dashboard():
    if 'user_id' not in session or session.get('role') != 'Admin':
        flash("Unauthorized access", "danger")
        return redirect(url_for('login'))
    return render_template('admin_dashboard.html', name=session['first_name'])


@app.route('/admin-contact')
def profile():
    return render_template('admin.html')    

if __name__ == "__main__":
    app.run(debug=True, # เปิด debug mode (ต้องปิดเมื่อ deploy จริง)
            port=5000,
            use_reloader=True) 