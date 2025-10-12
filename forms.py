from flask_wtf import FlaskForm
from wtforms import RadioField, IntegerField, SelectField, SubmitField
from wtforms.validators import DataRequired, InputRequired, NumberRange

class HighBPForm(FlaskForm):
    highbp = RadioField("คุณมีความดันโลหิตสูงหรือไม่?",
                        choices=[("0","ไม่"), ("1","ใช่")],
                        validators=[DataRequired()])
    submit = SubmitField("Next")

class HighCholForm(FlaskForm):
    highchol = RadioField("คุณมีคอเลสเตอรอลสูงหรือไม่?",
                          choices=[("0","ไม่"), ("1","ใช่")],
                          validators=[DataRequired()])
    submit = SubmitField("Next")

class HeartForm(FlaskForm):
    heart = RadioField("คุณเคยมีโรคหัวใจหรือไม่?",
                       choices=[("0","ไม่"), ("1","ใช่")],
                       validators=[DataRequired()])
    submit = SubmitField("Next")

class DiffWalkForm(FlaskForm):
    diffwalk = RadioField("คุณมีปัญหาในการเดินหรือไม่?",
                          choices=[("0","ไม่"), ("1","ใช่")],
                          validators=[DataRequired()])
    submit = SubmitField("Next")

class HeightAndWeightForm(FlaskForm):
    height = IntegerField("ส่วนสูง (cm)",
                          validators=[DataRequired(), NumberRange(min=100, max=250)])
    weight = IntegerField("น้ำหนัก (kg)",
                          validators=[DataRequired(), NumberRange(min=20, max=300)])
    submit = SubmitField("Next")

class GenHlthForm(FlaskForm):
    genhlth = SelectField("สุขภาพโดยรวมของคุณ",
                          choices=[("1","ยอดเยี่ยม"),("2","ดี"),("3","ปานกลาง"),("4","แย่"),("5","แย่มาก")],
                          validators=[DataRequired()])
    submit = SubmitField("Next")

class PhyshlthForm(FlaskForm):
    physhlth = IntegerField("จำนวนวันในเดือนที่แล้วที่สุขภาพกายไม่ดี (0-30)",
                            validators=[
                                InputRequired(message="กรุณากรอกจำนวนวัน"),
                                NumberRange(min=0, max=30, message="กรุณากรอกตัวเลขระหว่าง 0 ถึง 30")
                            ])
    submit = SubmitField("Next")

class AgeForm(FlaskForm):
    age = SelectField("อายุ",
                      choices=[("1","18-24"),("2","25-29"),("3","30-34"),("4","35-39"),
                               ("5","40-44"),("6","45-49"),("7","50-54"),
                               ("8","55-59"),("9","60-64"),("10","65-69"),
                               ("11","70-74"),("12","75-79"),("13","80+")],
                      validators=[DataRequired()])
    submit = SubmitField("Next")

class ModelChoiceForm(FlaskForm):
    model_choice = SelectField("เลือกโมเดลที่ใช้ทำนาย",
                               choices=[("decision_tree","DecisionTree"),("knn","KNN"),("naive_bayes","Naive Bayes"),("random_forest","Random Forest")],
                               validators=[DataRequired()])
    submit = SubmitField("Submit")
