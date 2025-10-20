import os
import joblib
import pandas as pd
import numpy as np
from flask import Flask, request, render_template, redirect, url_for, flash, session, jsonify
import calendar as cal

from dotenv import load_dotenv
from flask_bcrypt import Bcrypt
from flask_mysqldb import MySQL
from werkzeug.utils import secure_filename # สำหรับจัดการชื่อไฟล์ที่อัปโหลด
from datetime import datetime
import json

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

# ตั้งค่า MySQL
app.config['MYSQL_HOST'] = os.getenv('MYSQL_HOST')
app.config['MYSQL_USER'] = os.getenv('MYSQL_USER')
app.config['MYSQL_PASSWORD'] = os.getenv('MYSQL_PASSWORD')
app.config['MYSQL_DB'] = os.getenv('MYSQL_DB')
app.config['MYSQL_CURSORCLASS'] = os.getenv('MYSQL_CURSORCLASS')

# เริ่มต้นใช้งานส่วนเสริม
mysql = MySQL(app)
bcrypt = Bcrypt(app)

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
UPLOAD_FOLDER_IMAGES = os.path.join(app.root_path, 'static', 'images', 'ProfileImage')
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
    profile_filename = None
    if 'profile_image' in request.files:
        file = request.files['profile_image']
        if file and file.filename != '' and allowed_file(file.filename, ALLOWED_IMAGE_EXT):
            filename = secure_filename(file.filename)
            # เพิ่ม timestamp เพื่อป้องกันชื่อไฟล์ซ้ำ
            import time
            timestamp = str(int(time.time()))
            name, ext = os.path.splitext(filename)
            unique_filename = f"{name}_{timestamp}{ext}"
            
            # บันทึกไฟล์ลงโฟลเดอร์ static/images/ProfileImage
            upload_path = os.path.join(app.root_path, 'static', 'images', 'ProfileImage')
            if not os.path.exists(upload_path):
                os.makedirs(upload_path)
            
            file.save(os.path.join(upload_path, unique_filename))
            
            # เก็บเฉพาะชื่อไฟล์ไว้ใน database
            profile_filename = unique_filename

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

    # Insert พร้อมชื่อไฟล์ ProfileImage (ไม่รวม path)
    if profile_filename:
        sql = """INSERT INTO Account (FirstName, LastName, Birthday, Email, Password, Role, ProfileImage)
                 VALUES (%s, %s, %s, %s, %s, %s, %s)"""
        cur.execute(sql, (first, last, birthday, email, hashed, 'User', profile_filename))
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
    return render_template('home.html', current_page='home')











# ========== CALENDAR ROUTES ==========

@app.route('/calendar')
def calendar():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    return render_template('calendar.html', current_page='calendar')


@app.route('/calendar/events', methods=['GET'])
def get_events():
    """ดึงกิจกรรมทั้งหมดของผู้ใช้"""
    if 'user_id' not in session:
        return jsonify({'error': 'Unauthorized'}), 401

    user_id = session.get('user_id')
    
    try:
        cur = mysql.connection.cursor()
        cur.execute(
            "SELECT EventID, EventDate, EventText FROM CalendarEvent WHERE UserID = %s ORDER BY EventDate",
            (user_id,)
        )
        rows = cur.fetchall()
        cur.close()

        events = []
        for row in rows:
            events.append({
                'id': row['EventID'],
                'title': row['EventText'],
                'start': row['EventDate'].isoformat() if hasattr(row['EventDate'], 'isoformat') else str(row['EventDate']),
                'allDay': True
            })
        
        return jsonify(events)
    
    except Exception as e:
        print(f"Error fetching events: {str(e)}")
        return jsonify({'error': str(e)}), 500


@app.route('/calendar/add', methods=['POST'])
def add_event():
    """เพิ่มกิจกรรมใหม่"""
    if 'user_id' not in session:
        return jsonify({'success': False, 'message': 'ไม่ได้รับการยืนยัน'}), 401

    user_id = session.get('user_id')
    data = request.get_json()
    event_date = data.get('date')
    event_text = data.get('text', '').strip()

    # ตรวจสอบความถูกต้อง
    if not event_date:
        return jsonify({'success': False, 'message': 'วันที่ไม่ถูกต้อง'})
    
    if not event_text or len(event_text) > 255:
        return jsonify({'success': False, 'message': 'กรุณากรอกชื่อกิจกรรม (สูงสุด 255 ตัวอักษร)'})

    try:
        # ตรวจสอบวันที่
        datetime.strptime(event_date, '%Y-%m-%d')
    except ValueError:
        return jsonify({'success': False, 'message': 'รูปแบบวันที่ไม่ถูกต้อง'})

    try:
        cur = mysql.connection.cursor()

        # ตรวจสอบจำนวนกิจกรรมในวันนั้น
        cur.execute(
            "SELECT COUNT(*) AS count FROM CalendarEvent WHERE UserID = %s AND EventDate = %s",
            (user_id, event_date)
        )
        result = cur.fetchone()
        count = result['count']

        if count >= 5:
            cur.close()
            return jsonify({'success': False, 'message': 'เพิ่มกิจกรรมได้สูงสุด 5 รายการต่อวัน'})

        # เพิ่มกิจกรรม
        cur.execute(
            "INSERT INTO CalendarEvent (UserID, EventDate, EventText) VALUES (%s, %s, %s)",
            (user_id, event_date, event_text)
        )
        mysql.connection.commit()
        
        event_id = cur.lastrowid
        cur.close()

        return jsonify({
            'success': True,
            'message': 'บันทึกกิจกรรมเรียบร้อยแล้ว',
            'eventID': event_id
        })

    except Exception as e:
        print(f"Error adding event: {str(e)}")
        return jsonify({'success': False, 'message': f'เกิดข้อผิดพลาด: {str(e)}'}), 500


@app.route('/calendar/delete/<int:event_id>', methods=['DELETE'])
def delete_event(event_id):
    """ลบกิจกรรม"""
    if 'user_id' not in session:
        return jsonify({'success': False, 'message': 'ไม่ได้รับการยืนยัน'}), 401

    user_id = session.get('user_id')

    try:
        cur = mysql.connection.cursor()

        # ตรวจสอบว่ากิจกรรมนี้เป็นของผู้ใช้คนนี้
        cur.execute(
            "SELECT UserID FROM CalendarEvent WHERE EventID = %s",
            (event_id,)
        )
        event = cur.fetchone()

        if not event or event['UserID'] != user_id:
            cur.close()
            return jsonify({'success': False, 'message': 'ไม่พบกิจกรรม'}), 404

        # ลบกิจกรรม
        cur.execute(
            "DELETE FROM CalendarEvent WHERE EventID = %s AND UserID = %s",
            (event_id, user_id)
        )
        mysql.connection.commit()
        cur.close()

        return jsonify({'success': True, 'message': 'ลบกิจกรรมเรียบร้อยแล้ว'})

    except Exception as e:
        print(f"Error deleting event: {str(e)}")
        return jsonify({'success': False, 'message': f'เกิดข้อผิดพลาด: {str(e)}'}), 500


@app.route('/calendar/update/<int:event_id>', methods=['PUT'])
def update_event(event_id):
    """แก้ไขกิจกรรม"""
    if 'user_id' not in session:
        return jsonify({'success': False, 'message': 'ไม่ได้รับการยืนยัน'}), 401

    user_id = session.get('user_id')
    data = request.get_json()
    event_text = data.get('text', '').strip()

    if not event_text or len(event_text) > 255:
        return jsonify({'success': False, 'message': 'กรุณากรอกชื่อกิจกรรม (สูงสุด 255 ตัวอักษร)'})

    try:
        cur = mysql.connection.cursor()

        # ตรวจสอบว่ากิจกรรมนี้เป็นของผู้ใช้คนนี้
        cur.execute(
            "SELECT UserID FROM CalendarEvent WHERE EventID = %s",
            (event_id,)
        )
        event = cur.fetchone()

        if not event or event['UserID'] != user_id:
            cur.close()
            return jsonify({'success': False, 'message': 'ไม่พบกิจกรรม'}), 404

        # แก้ไขกิจกรรม
        cur.execute(
            "UPDATE CalendarEvent SET EventText = %s WHERE EventID = %s AND UserID = %s",
            (event_text, event_id, user_id)
        )
        mysql.connection.commit()
        cur.close()

        return jsonify({'success': True, 'message': 'แก้ไขกิจกรรมเรียบร้อยแล้ว'})

    except Exception as e:
        print(f"Error updating event: {str(e)}")
        return jsonify({'success': False, 'message': f'เกิดข้อผิดพลาด: {str(e)}'}), 500










@app.route('/profile')
def profile():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    user_id = session['user_id']
    cur = mysql.connection.cursor()

    # ดึงข้อมูล User
    cur.execute("SELECT FirstName, LastName, Email, ProfileImage FROM Account WHERE UserID = %s", (user_id,))
    user = cur.fetchone()

    # ดึงประวัติการประเมินทั้งหมด
    cur.execute("""
        SELECT PredictionID, PredictDateTime, Result_Percentage, Result_Binary, Model_Used, UserNote
        FROM PredictionRecord
        WHERE UserID = %s
        ORDER BY PredictDateTime ASC
    """, (user_id,))
    records = cur.fetchall()

    cur.close()

    return render_template('profile.html', user=user, records=records, current_page='profile')
















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
    return render_template('step.html', form=form, step=step, total=total_steps, image=image, current_page='home')

    





















@app.route('/predict/result', methods=['GET', 'POST'])
def result():
    # เอาข้อมูลจาก session มาจัด features
    # แปลง String เป็น int ก่อนใช้
    try:
        highbp = int(session.get('highbp', 0))
        highchol = int(session.get('highchol', 0))
        heart = int(session.get('heart', 0))
        diffwalk = int(session.get('diffwalk', 0))
        genhlth = int(session.get('genhlth', 3))
        physhlth = int(session.get('physhlth', 0))
        age_choice = session.get('age', "1")
        age = int(age_choice)
        
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

        bmi_cat = 0
        if bmi < 18.5:
            bmi_cat = 0
        elif bmi < 25:
            bmi_cat = 1
        elif bmi < 30:
            bmi_cat = 2
        else:
            bmi_cat = 3

        bmi_age_interaction = int(round(bmi * age))

        # สร้าง DataFrame ตาม feature ที่โมเดลต้องการ
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

        # เลือกโมเดลจาก session (random_forest เป็นค่า default)
        model_name = session.get('model_choice', 'random_forest')
        model_path = os.path.join('models', f"{model_name}.joblib")
        
        if os.path.exists(model_path):
            model = joblib.load(model_path)
            y_pred = model.predict(features)[0]
            try:
                y_prob = model.predict_proba(features)[0][1] * 100
            except Exception:
                y_prob = None
            prediction_result = int(y_pred)
            probability = round(y_prob, 2) if y_prob is not None else None
        else:
            prediction_result = 0
            probability = None

        # ส่งข้อมูลไปแสดง
        data = {
            'highbp': session.get('highbp'),
            'highchol': session.get('highchol'),
            'heart': session.get('heart'),
            'diffwalk': session.get('diffwalk'),
            'genhlth': session.get('genhlth'),
            'physhlth': session.get('physhlth'),
            'age': session.get('age'),
            'height': session.get('height'),
            'weight': session.get('weight'),
            'bmi': bmi,
            'bmi_cat_code': bmi_cat,
            'bmi_age_interaction': bmi_age_interaction,
            'model_choice': session.get('model_choice')
        }

        # ========== ตรวจสอบข้อมูลจาก MySQL Category ==========
        risk_data = {
            'category_id': None,
            'risk_level': 'ไม่สามารถประเมินได้',
            'risk_color': 'gray',
            'risk_icon': 'unknown.png',
            'recommendation': 'ไม่มีคำแนะนำ'
        }

        # ตรวจสอบและดึงข้อมูล Category ตามระดับความเสี่ยง
        if probability is not None:
            cur = mysql.connection.cursor()

            # ใช้ <= เพื่อให้ครอบคลุมค่าที่เท่ากับ RiskPercent_Upper (เช่น 100.0)
            query = """
                SELECT CategoryID, RiskPercent_Lower, RiskPercent_Upper,
                    Risk_Level, Risk_Color, Risk_Icon, Recommendation
                FROM Category
                WHERE %s >= RiskPercent_Lower AND %s <= RiskPercent_Upper
                LIMIT 1
            """
            cur.execute(query, (probability, probability))
            category = cur.fetchone()
            cur.close()

            # ตรวจสอบว่าเจอข้อมูลหรือไม่
            if category:
                # ถ้ามีข้อมูลในตาราง Category
                risk_data = {
                    'category_id': category['CategoryID'],
                    'risk_level': category['Risk_Level'],
                    'risk_color': category['Risk_Color'],
                    'risk_icon': category['Risk_Icon'],
                    'recommendation': category['Recommendation']
                }
                print(f"[DEBUG] Category matched: {risk_data}")  # สำหรับตรวจสอบ
            else:
                # ถ้าไม่พบหมวดหมู่ที่ตรงกับค่า probability
                print(f"[DEBUG] No category found for probability = {probability}")

                risk_data = {
                    'category_id': None,
                    'risk_level': 'ไม่พบหมวดหมู่ที่ตรงกับความเสี่ยงนี้',
                    'risk_color': 'gray',
                    'risk_icon': 'unknown.png',
                    'recommendation': 'ไม่มีคำแนะนำสำหรับค่าความเสี่ยงนี้'
                }
        else:
            # กรณี probability ไม่มีค่า (probability เป็น None)
            print("[DEBUG] Probability is None")
            risk_data = {
                'category_id': None,
                'risk_level': 'ไม่สามารถประเมินความเสี่ยงได้',
                'risk_color': 'gray',
                'risk_icon': 'unknown.png',
                'recommendation': 'กรุณาลองประเมินใหม่อีกครั้ง'
            }

        return render_template('result.html',
                               prediction=prediction_result,
                               probability=probability,
                               data=data,
                               risk_data=risk_data,
                               prediction_datetime=datetime.now(),
                               current_page='home')
    except Exception as e:
        return f"Error preparing result: {e}", 500































@app.route('/predict/save_result', methods=['POST'])
def save_result():
    """
    Save prediction result to database (MySQL version)
    """
    try:
        # Check if user is logged in
        user_id = session.get('user_id')
        if not user_id:
            return jsonify({'success': False, 'message': 'User not logged in'}), 401

        # Get data from session and form
        prediction = int(request.form.get('prediction', 0))
        probability = float(request.form.get('probability', 0))
        bmi = float(request.form.get('bmi', 0))
        user_note = request.form.get('userNote', '').strip()
        model_used = request.form.get('model_used', 'random_forest')

        # Get health data from session
        highbp = int(session.get('highbp', 0))
        highchol = int(session.get('highchol', 0))
        heart = int(session.get('heart', 0))
        diffwalk = int(session.get('diffwalk', 0))
        genhlth = int(session.get('genhlth', 3))
        physhlth = int(session.get('physhlth', 0))
        age = int(session.get('age', 1))
        height = int(session.get('height', 0)) if session.get('height') else 0
        weight = int(session.get('weight', 0)) if session.get('weight') else 0

        # Calculate BMI category
        if bmi < 18.5:
            bmi_cat_code = 0
        elif bmi < 25:
            bmi_cat_code = 1
        elif bmi < 30:
            bmi_cat_code = 2
        else:
            bmi_cat_code = 3

        # Calculate BMI-Age interaction
        bmi_age_interaction = int(round(bmi * age))

        # Determine risk category based on probability
        if probability < 50:
            category_id = 1
        elif probability < 60:
            category_id = 2
        elif probability < 70:
            category_id = 3
        elif probability < 90:
            category_id = 4
        else:
            category_id = 5

        # Insert into MySQL
        cur = mysql.connection.cursor()

        insert_query = """
            INSERT INTO PredictionRecord (
                UserID, HighBP, HighChol, BMI, HeartDiseaseorAttack,
                GenHlth, PhysHlth, DiffWalk, Age, BMI_cat_code, 
                BMI_Age_interaction, CategoryID, Height, Weight, 
                Model_Used, PredictDateTime, Result_Binary, 
                Result_Percentage, UserNote
            )
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """

        values = (
            user_id, highbp, highchol, bmi, heart,
            genhlth, physhlth, diffwalk, age, bmi_cat_code,
            bmi_age_interaction, category_id, height, weight,
            model_used, datetime.now(), prediction,
            probability, user_note if user_note else None
        )

        cur.execute(insert_query, values)
        mysql.connection.commit()

        prediction_id = cur.lastrowid
        cur.close()

        # Clear session data after saving
        session_keys_to_clear = [
            'highbp', 'highchol', 'heart', 'diffwalk',
            'height', 'weight', 'genhlth', 'physhlth',
            'age', 'model_choice'
        ]
        for key in session_keys_to_clear:
            session.pop(key, None)

        return jsonify({
            'success': True,
            'message': 'บันทึกผลการประเมินเรียบร้อยแล้ว',
            'prediction_id': prediction_id
        }), 200

    except ValueError as e:
        return jsonify({'success': False, 'message': f'ข้อมูลไม่ถูกต้อง: {str(e)}'}), 400
    except Exception as e:
        mysql.connection.rollback()
        return jsonify({'success': False, 'message': f'เกิดข้อผิดพลาด: {str(e)}'}), 500






















@app.route('/menu')
def menu():
    return render_template('menu.html', current_page='menu')







@app.route('/account')
def account():
    # ตรวจสอบว่า user login แล้วหรือไม่
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    # ดึงข้อมูล user จาก database
    cur = mysql.connection.cursor()
    cur.execute("""
                SELECT UserID, FirstName, LastName, Email, ProfileImage
                FROM Account 
                WHERE UserID=%s""", (session['user_id'],))
    user = cur.fetchone()
    cur.close()
    
    if user is None:
        flash("User not found.", "danger")
        return redirect(url_for('login'))
    
    return render_template('account.html', 
                         current_page='menu',
                         first_name=user['FirstName'],
                         last_name=user['LastName'],
                         email=user['Email'],
                         profile_image=user['ProfileImage'] or 'default-avatar.png')
















@app.route('/update_account', methods=['POST'])
def update_account():
    # ตรวจสอบว่า user login แล้วหรือไม่
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    # รับข้อมูลจาก form
    first_name = request.form.get('first_name', '').strip()
    last_name = request.form.get('last_name', '').strip()
    current_password = request.form.get('current_password', '').strip()
    new_password = request.form.get('new_password', '').strip()
    confirm_password = request.form.get('confirm_password', '').strip()
    
    # ตรวจสอบว่ากรอก FirstName และ LastName ครบไหม
    if not first_name or not last_name:
        flash("Please fill in both first name and last name.", "warning")
        return redirect(url_for('account'))
    
    # ตรวจสอบว่าถ้ากรอก confirm_password แต่ไม่กรอก new_password
    if confirm_password and not new_password:
        flash("Cannot fill confirm password without new password.", "danger")
        return redirect(url_for('account'))
    
    # ดึงข้อมูล user จาก database
    cur = mysql.connection.cursor()
    cur.execute("SELECT UserID, FirstName, LastName, Email, Password FROM Account WHERE UserID=%s", (session['user_id'],))
    user = cur.fetchone()
    cur.close()
    
    if user is None:
        flash("User not found.", "danger")
        return redirect(url_for('login'))
    
    # ตัวแปรเก็บ password ใหม่
    password_to_update = None
    
    # ถ้า user กรอก password ใหม่
    if new_password:
        # ตรวจสอบว่า current_password ว่างไหม
        if not current_password:
            flash("Please enter your current password to change password.", "warning")
            return redirect(url_for('account'))
        
        # ตรวจสอบว่า new_password กับ confirm_password ตรงกันไหม
        if new_password != confirm_password:
            flash("New password and confirm password do not match.", "danger")
            return redirect(url_for('account'))
        
        # ตรวจสอบว่า confirm_password ไม่ว่าง
        if not confirm_password:
            flash("Please confirm your new password.", "warning")
            return redirect(url_for('account'))
        
        # ตรวจสอบว่า current_password ถูกต้องไหม
        if not bcrypt.check_password_hash(user['Password'], current_password):
            flash("Current password is incorrect.", "danger")
            return redirect(url_for('account'))
        
        # ตรวจสอบความยาวของ password
        if len(new_password) < 6:
            flash("New password must be at least 6 characters long.", "warning")
            return redirect(url_for('account'))
        
        # Hash password ใหม่
        password_to_update = bcrypt.generate_password_hash(new_password).decode('utf-8')
    
    # อัปเดตข้อมูลใน database
    try:
        cur = mysql.connection.cursor()
        
        if password_to_update:
            # อัปเดต FirstName, LastName, และ Password
            cur.execute(
                "UPDATE Account SET FirstName=%s, LastName=%s, Password=%s WHERE UserID=%s",
                (first_name, last_name, password_to_update, session['user_id'])
            )
        else:
            # อัปเดต FirstName และ LastName เท่านั้น
            cur.execute(
                "UPDATE Account SET FirstName=%s, LastName=%s WHERE UserID=%s",
                (first_name, last_name, session['user_id'])
            )
        
        mysql.connection.commit()
        cur.close()
        
        # อัปเดต session ใหม่
        session['first_name'] = first_name
        
        flash("Account updated successfully.", "success")
        return redirect(url_for('account'))
    
    except Exception as e:
        mysql.connection.rollback()
        flash(f"Error updating account: {str(e)}", "danger")
        return redirect(url_for('account'))











    

@app.route('/feedback', methods=['GET', 'POST'])
def feedback():
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        message = request.form.get('message')

        # ตรวจว่ากรอกครบไหม
        if not name or not email or not message:
            flash("กรุณากรอกข้อมูลให้ครบทุกช่อง", "danger")
        else:
            try:
                cur = mysql.connection.cursor()
                cur.execute("""
                    INSERT INTO feedback (Name, Email, Message)
                    VALUES (%s, %s, %s)
                """, (name, email, message))
                mysql.connection.commit()
                cur.close()
                flash("ส่งข้อเสนอแนะเรียบร้อยแล้ว", "success")
                return redirect(url_for('feedback'))
            except Exception as e:
                print("Feedback Error:", e)
                flash("เกิดข้อผิดพลาดในการบันทึกข้อมูล", "danger")

    # ถ้าเป็น GET (แค่เปิดหน้าเฉย ๆ)
    return render_template('feedback.html', current_page='menu')



# เมื่อผู้ใช้ logout แล้วให้ลบข้อมูลใน session ด้วย
@app.route('/logout')
def logout():
    session.clear()  # ลบข้อมูลทั้งหมดใน session
    flash("You have been logged out.", "success")
    return redirect(url_for('sign'))



# @app.route('/admin/dashboard')
# def admin_dashboard():
#     if 'user_id' not in session or session.get('role') != 'Admin':
#         flash("Unauthorized access", "danger")
#         return redirect(url_for('login'))
#     return render_template('admin_dashboard.html', name=session['first_name'])


# @app.route('/admin_contact')
# def admin_contact():
#     return render_template('admin_contact.html')    

if __name__ == "__main__":
    app.run(debug=True, # เปิด debug mode (ต้องปิดเมื่อ deploy จริง)
            port=5000,
            use_reloader=True) 