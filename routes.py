import sqlite3
from flask import Flask, render_template, redirect, request, session

app = Flask(__name__)
app.config['SECRET_KEY'] = '8d7778f920ce5ca8d70b40eee907a06d'

with open("init_db.py") as init:
    exec(init.read())

@app.route("/")
def hello():
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
            return redirect('/client')## TODO: make redirect to a role page, based on what role the user is
        else:
            return render_template("authorization.html", error="Špatné údaje!")

@app.route("/logout", methods=['GET'])
def logout():
    session.pop('user_id', None)
    return redirect('/')


@app.route("/client")
def client_screen():
    return redirect("/client/order_list")

@app.route("/client/car_list")
def client_car_list():
    return render_template("client_carlist.html");

@app.route("/client/order_list")
def client_order_list():
    return render_template("client_orderlist.html");

@app.route("/mechanic")
def mechanic_screen():
    return render_template("base_mechanic_page.html")

@app.route("/manager")
def manager_screen():
    return render_template("base_manager_page.html")

@app.route("/admin")
def admin():
    return redirect("/admin_car_list")

@app.route("/admin/car_list")
def admin_car_list():
    return render_template("admin_carlist.html")

@app.route("/admin/service_list")
def admin_service_list():
    return render_template("admin_servicelist.html")

@app.route("/admin/order_list")
def admin_order_list():
    return render_template("admin_orderlist.html");

@app.route("/admin/user_list")
def admin_user_lsit():
    return render_template("admin_userlist.html")

