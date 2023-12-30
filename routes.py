import sqlite3
from flask import Flask, render_template, redirect, request

app = Flask(__name__)

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
        

@app.route("/login")
def authorization():
    return render_template("authorization.html")

@app.route("/car")
def car_list():
    return render_template("car_list.html")

@app.route("/servis")
def servis_list():
    return render_template("servis_list.html")

@app.route("/client")
def client_screen():
    return render_template("base_client_page.html")

@app.route("/mechanic")
def mechanic_screen():
    return render_template("base_mechanic_page.html")

@app.route("/manager")
def manager_screen():
    return render_template("base_manager_page.html")

@app.route("/admin")
def admin():
    return redirect("/admin_car_list")

@app.route("/admin_car_list")
def admin_car_list():
    return render_template("admin_carlist.html")

@app.route("/admin_service_list")
def admin_service_list():
    return render_template("admin_servicelist.html")

@app.route("/admin_order_list")
def admin_order_list():
    return render_template("admin_orderlist.html");

@app.route("/admin_user_list")
def admin_user_lsit():
    return render_template("admin_userlist.html")

