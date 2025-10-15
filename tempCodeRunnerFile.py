# Login โดยใช้ JSONWebToken (JWT) เข้ารหัสแบบ bcrypt
@app.route('/login', methods=['GET', 'POST'])
def login():
    # ถ้าเป็นการเข้าหน้า login แบบ GET ให้แสดงหน้าเว็บ sign.html
    if request.method == 'GET':
        return render_template('sign.html')

    # ถ้าเป็นการส่งข้อมูล login แบบ POST
    email = request.form['email']
    password = request.form['password']

    print(f"Login attempt: {email} / {password}")

    # ตรวจสอบว่ากรอกครบไหม
    if not (email and password):
        flash("Please fill in both email and password.", "warning")
        return redirect(url_for('login'))

    # สร้าง cursor เพื่อ query ข้อมูลจากฐานข้อมูล
    cur = mysql.connection.cursor()
    cur.execute("SELECT UserID, FirstName, LastName, Email, Password, Role FROM Account WHERE Email=%s", (email,))
    user = cur.fetchone()
    cur.close()

    print(f"User from DB: {user}")

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