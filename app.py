import os
import joblib
import pandas as pd
import numpy as np
from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_wtf import FlaskForm
from wtforms import RadioField, SelectField, SubmitField, IntegerField
from wtforms.validators import DataRequired, NumberRange

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

class MyForm(FlaskForm):
    # Features
    highbp = RadioField('HighBP', choices=[('0','No'), ('1','Yes')], validators=[DataRequired()])
    highchol = RadioField('HighChol', choices=[('0','No'), ('1','Yes')], validators=[DataRequired()])
    heart = RadioField('Heart Disease or Attack?', choices=[('0','No'), ('1','Yes')], validators=[DataRequired()])
    diffwalk = RadioField('Difficulty walking?', choices=[('0','No'), ('1','Yes')], validators=[DataRequired()])

    height = IntegerField('Height (cm)', validators=[DataRequired(), NumberRange(min=50, max=250)])
    weight = IntegerField('Weight (kg)', validators=[DataRequired(), NumberRange(min=20, max=300)])

    genhlth = SelectField('General Health (1=Excellent → 5=Poor)', 
                          choices=[('1','Excellent'), ('2','Very good'), ('3','Good'), ('4','Fair'), ('5','Poor')])
    physhlth = IntegerField('Physical health not good (0-30 days)', validators=[NumberRange(min=0, max=30)])

    age = SelectField('Age Group', choices=[
        ('1','18-24'), ('2','25-29'), ('3','30-34'), ('4','35-39'),
        ('5','40-44'), ('6','45-49'), ('7','50-54'), ('8','55-59'),
        ('9','60-64'), ('10','65-69'), ('11','70-74'), ('12','75-79'), ('13','80+')
    ])

    # เลือกโมเดล
    model_choice = SelectField('เลือกโมเดลประเมินเบาหวาน', choices=[
        ('decision_tree', 'Decision Tree'),
        ('knn', 'KNN'),
        ('naive_bayes', 'Naive Bayes'),
        ('random_forest', 'Random Forest')
    ])

    submit = SubmitField('ประเมิน')


















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

@app.route('/predict', methods=['GET', 'POST'])
def predict():
    # user_id = session.get('user_id')
    # username = session.get('username')
    form = MyForm()
    
    prediction_result = None
    probability = None

    if form.validate_on_submit():
        # ดึงค่าจากฟอร์ม
        highbp = int(form.highbp.data)
        highchol = int(form.highchol.data)
        heart = int(form.heart.data)
        diffwalk = int(form.diffwalk.data)
        genhlth = int(form.genhlth.data)
        physhlth = int(form.physhlth.data)
        age = int(form.age.data)

        # คำนวณ BMI
        height_m = form.height.data / 100
        bmi = int(form.weight.data / (height_m ** 2))

        # BMI Category
        bmi_cat = bmi_category_code(bmi)

        # BMI x Age interaction
        bmi_age_interaction = int(bmi * age)

        # เก็บใน session
        session['highbp'] = highbp
        session['highchol'] = highchol
        session['heart'] = heart
        session['diffwalk'] = diffwalk
        session['genhlth'] = genhlth
        session['physhlth'] = physhlth
        session['age'] = age
        session['bmi'] = bmi
        session['bmi_cat'] = bmi_cat
        session['bmi_age_interaction'] = bmi_age_interaction

        # เตรียม feature vector ตามลำดับที่ใช้ตอนเทรน
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


        # โหลดโมเดล
        model_name = form.model_choice.data
        model_path = os.path.join("models", f"{model_name}.joblib")
        model = joblib.load(model_path)

        # ทำการพยากรณ์
        y_pred = model.predict(features)[0]
        y_prob = model.predict_proba(features)[0][1] * 100  # ความน่าจะเป็น class 1 (%)

        prediction_result = int(y_pred)
        probability = round(y_prob, 2)

        # เก็บผลใน session
        session['prediction'] = prediction_result
        session['probability'] = probability

        # เก็บค่าลง database พร้อมผลการพยากรณ์
        # save_to_db(user_id, username, prediction_result, probability)
    return render_template('predict.html', form=form,
                           prediction=session.get('prediction'),
                           probability=session.get('probability'))

@app.route('/admin')
def profile():
    # ชื่อ อายุ
    username = "natthapong"
    return render_template('admin.html', username = username)    

if __name__ == "__main__":
    app.run(debug=True) # เปิด debug mode (ต้องปิดเมื่อ deploy จริง)