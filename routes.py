from flask import Flask, render_template

app = Flask(__name__)

@app.route("/")
def hello():
    return render_template("index.html")

@app.route("/reg")
def registration():
    return render_template("registration.html")

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