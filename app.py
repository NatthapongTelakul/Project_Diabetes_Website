import os
import joblib
import pandas as pd
import numpy as np
from flask import Flask, render_template, request, redirect, url_for, flash, session

from forms import (
    HighBPForm, HighCholForm, HeartForm, DiffWalkForm,
    HeightAndWeightForm, GenHlthForm, PhyshlthForm,
    AgeForm, ModelChoiceForm
)

app = Flask(__name__)
app.config['SECRET_KEY'] = 'mykey'

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

# เริ่มต้นการทำงานที่ index.html
@app.route('/', methods=['GET', 'POST'])
def index():
    return render_template('index.html')

@app.route('/sign', methods=['GET', 'POST'])
def sign():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('pass')

        # ตัวอย่าง: ตรวจสอบ username/password แบบฮาร์ดโค้ด
        if email == 'user123@gmail.com' and password == '123456':
            session['isLoggedIn'] = True
            session['userEmail'] = email
            return redirect(url_for('home')) # เปลี่ยนเป็นหน้า home
        else:
            flash('Email หรือ Password ไม่ถูกต้อง', 'error')
            return render_template('sign.html')  # โหลดหน้าเดิมพร้อม error

    return render_template('sign.html')

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

@app.route('/admin-contact')
def profile():
    return render_template('admin.html')    

if __name__ == "__main__":
    app.run(debug=True) # เปิด debug mode (ต้องปิดเมื่อ deploy จริง)