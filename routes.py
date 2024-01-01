import sqlite3
from flask import Flask, render_template, redirect, request, session
from functools import wraps

app = Flask(__name__)
app.config['SECRET_KEY'] = '8d7778f920ce5ca8d70b40eee907a06d'

with open("init_db.py") as init:
    exec(init.read())

@app.route("/")
def index_page():
    return render_template("index.html")

@app.route("/reg", methods = ['GET', 'POST'])
def registration():
    if request.method == 'GET':
        return render_template("registration.html")
    
    if request.method == 'POST':
        con = sqlite3.connect("vwa.db")
        cur = con.cursor()
        cur.execute(
            'INSERT INTO uzivately (jmeno, primeni, login, heslo) VALUES(?,?,?,?)',
            (
                request.form['fname'],
                request.form['lname'],
                request.form['login'],
                request.form['password']
            )
        )
        cur.execute(
            "INSERT INTO role_uzivately (platnost, nazev, id_uzivatele) VALUES(1, 'user', last_insert_rowid())"
        )
        con.commit()
        con.close()
        return redirect("/client")

@app.route("/login", methods=['GET', 'POST'])
def authorization():
    if request.method == 'GET':
        return render_template("authorization.html")

    if request.method == 'POST':
        login = request.form['login']
        password = request.form['password']

        con = sqlite3.connect("vwa.db")
        cur = con.cursor()

        cur.execute("SELECT * FROM uzivately WHERE login = ? AND heslo = ?",(login, password))
        user = cur.fetchone()

        con.close()

        if user:
            session['user_id'] = user[0]

            con = sqlite3.connect("vwa.db")
            cur = con.cursor()

            cur.execute(
                'SELECT nazev FROM role_uzivately WHERE id_uzivatele = ?', (session['user_id'],)
                )
            role = cur.fetchone()

            con.close()

            if role:
                session['user_role'] = role[0]

                return redirect('/'+session['user_role'])
                
            else:
                return render_template("authorization.html", error="Role nebyla nalezena!")

        else:
            return render_template("authorization.html", error="Špatné údaje!")

@app.route("/logout", methods=['GET'])
def logout():
    session.pop('user_id', None)
    return redirect('/')

def admin_authorization(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        if 'user_role' in session and session['user_role'] == 'admin':
            return func(*args, **kwargs)
        else:
            return redirect('/'+session['user_role'])
    return wrapper

def manager_authorization(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        if 'user_role' in session and session['user_role'] == 'manager':
            return func(*args, **kwargs)
        else:
            return redirect('/'+session['user_role'])
    return wrapper

def mechanic_authorization(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        if 'user_role' in session and session['user_role'] == 'mechanic':
            return func(*args, **kwargs)
        else:
            return redirect('/'+session['user_role'])
    return wrapper

def client_authorization(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        if 'user_role' in session and session['user_role'] == 'client':
            return func(*args, **kwargs)
        else:
            return redirect('/'+session['user_role'])
    return wrapper

@app.route("/client")
@client_authorization
def client_screen():
    return redirect("/client/order_list")

@app.route("/client/car_list")
@client_authorization
def client_car_list():
    con = sqlite3.connect("vwa.db")
    cur = con.cursor()

    cur.execute(
        'SELECT model, spz, rok_vyroby FROM vozidla WHERE vlastnik = ?', (session['user_id'],)
    )
    data = cur.fetchall()

    con.close()

    return render_template("client_carlist.html", data=data);

@app.route("/client/add_car", methods=['GET','POST'])
@client_authorization
def client_add_car():
    if request.method == 'GET':
        return render_template("client_add_car.html")

    if request.method == 'POST':
        model = request.form['car_model']
        license_plate = request.form['spz']
        year = request.form['year']

        con = sqlite3.connect("vwa.db")
        cur = con.cursor()

        cur.execute(
            'INSERT INTO vozidla (spz, model, rok_vyroby, vlastnik) VALUES(?,?,?,?)',(license_plate, model, year, session['user_id'])
        )        

        con.commit()
        con.close()

        return redirect('/client/car_list')

@app.route("/client/order_list")
@client_authorization
def client_order_list():
    return render_template("client_orderlist.html");

@app.route("/mechanic")
@mechanic_authorization
def mechanic_screen():
    return redirect("/mechanic/car_list")

@app.route("/mechanic/car_list")
@mechanic_authorization
def mechanic_car_list():
    return render_template("mechanic_car_list.html")

@app.route("/manager")
@manager_authorization
def manager_screen():
    return render_template("base_manager_page.html")

@app.route("/admin")
@admin_authorization
def admin():
    return redirect("/admin/car_list")

@app.route("/admin/car_list")
@admin_authorization
def admin_car_list():
    return render_template("admin_carlist.html")

@app.route("/admin/service_list")
@admin_authorization
def admin_service_list():
    return render_template("admin_servicelist.html")

@app.route("/admin/order_list")
@admin_authorization
def admin_order_list():
    return render_template("admin_orderlist.html");

@app.route("/admin/user_list")
@admin_authorization
def admin_user_lsit():
    return render_template("admin_userlist.html")

