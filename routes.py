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
        'SELECT model, spz, rok_vyroby, id FROM vozidla WHERE vlastnik = ?', (session['user_id'],)
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
    con = sqlite3.connect('vwa.db')
    cur = con.cursor()

    cur.execute(
        """
            SELECT v.id, v.model, v.spz, v.rok_vyroby, st.stav 
            FROM vozidla v 
            INNER JOIN servis s ON v.id = s.vozidlo 
            INNER JOIN stav_servisu st ON s.id = st.id_servisu
            WHERE v.vlastnik = ?
        """,(session['user_id'],)
    )
    data = cur.fetchall()
    con.close()

    return render_template("client_orderlist.html", data=data);

@app.route("/client/create_order", methods=['GET', 'POST'])
@client_authorization
def client_make_order():
    if request.method == 'GET':
        return redirect('/'+session['user_role'])
    if request.method == 'POST':
        vehicle_id = request.form['vehicle_id']

        con = sqlite3.connect("vwa.db")
        cur = con.cursor()

        cur.execute(
            'SELECT id, model FROM vozidla WHERE id = ?',(vehicle_id,)
        )

        data = cur.fetchall()

        con.close()

        vehicle = data[0]

        return render_template("client_make_order.html", data=vehicle)

@app.route("/client/place_order", methods=['POST'])
@client_authorization
def client_place_order():
    if request.method == 'POST':
        vehicle_id = request.form['id']
        problem = request.form['problem']

        con = sqlite3.connect("vwa.db")
        cur = con.cursor()

        cur.execute(
            'INSERT INTO servis(vozidlo, problem) VALUES(?,?)',(vehicle_id, problem)
        )
        cur.execute(
            'INSERT INTO stav_servisu(id_servisu, stav) VALUES(last_insert_rowid(), ?)', ('objednano',)
        )
        con.commit()

        con.close()

        return redirect('/client')
    

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
    con = sqlite3.connect("vwa.db")
    cur = con.cursor()

    cur.execute(
        'SELECT v.id, v.model, v.spz, v.rok_vyroby, u.primeni, u.jmeno FROM vozidla v INNER JOIN uzivately u ON v.vlastnik = u.id'
    )
    data = cur.fetchall()

    con.close()
    return render_template("admin_carlist.html", data=data)

@app.route('/admin/add_car', methods=['GET', 'POST'])
@admin_authorization
def admin_add_car():
    if request.method == 'GET':
        return render_template("admin_add_car.html")
    if request.method == 'POST':
        owner_login = request.form['owner']
        model = request.form['car_model']
        license_plate = request.form['spz']
        year = request.form['year']

        con = sqlite3.connect("vwa.db")
        cur = con.cursor()

        cur.execute(
            'SELECT * FROM uzivately WHERE login = ?',(owner_login,)
        )
        owner = cur.fetchone();

        con.close();

        if owner:
            con = sqlite3.connect("vwa.db")
            cur = con.cursor()

            cur.execute(
                'INSERT INTO vozidla (spz, model, rok_vyroby, vlastnik) VALUES(?,?,?,?)', (license_plate, model, year, owner[0])
            )
            con.commit()
            
            con.close()

            return redirect("/admin/car_list")
        else:
            return render_template("admin_add_car.html", error="Uzivatel s tymto loginem neexistuje!")

@app.route("/admin/car_edit", methods=['GET','POST'])
@admin_authorization        
def admin_car_edit():
    if request.method == 'GET':
        id = request.args.get('vehicle_id')

        con = sqlite3.connect('vwa.db')
        cur = con.cursor()
        
        cur.execute(
            'SELECT id, model, spz, rok_vyroby FROM vozidla WHERE id = ?',(id,)
        )
        data = cur.fetchone()

        con.close()

        return render_template('admin_car_edit.html', data=data)

    if request.method == 'POST':
        id = request.form['id']
        model = request.form['model']
        license = request.form['license']
        year = request.form['year']

        con = sqlite3.connect('vwa.db')
        cur = con.cursor()

        cur.execute(
            'UPDATE vozidla SET model = ?, spz = ?, rok_vyroby = ? WHERE id = ?',(model, license, year, id)
        )

        con.commit()

        con.close()

        return redirect("/admin/car_list")



@app.route("/admin/delete_car", methods = ['POST'])
@admin_authorization
def admin_delete_car():
    id = request.form['vehicle_id']

    con = sqlite3.connect("vwa.db")
    cur = con.cursor()

    cur.execute(
        'DELETE FROM vozidla WHERE id = ?', (id,)
    )

    con.commit()

    con.close()

    return redirect("/admin/car_list")

@app.route("/admin/service_list")
@admin_authorization
def admin_service_list():
    return render_template("admin_servicelist.html")

@app.route("/admin/order_list")
@admin_authorization
def admin_order_list():
    con = sqlite3.connect("vwa.db")
    cur = con.cursor()

    cur.execute(
        """
        SELECT v.id, v.model, v.spz, v.rok_vyroby, v.vlastnik, s.problem FROM vozidla v
        INNER JOIN servis s ON v.id = s.vozidlo
        """
    )
    data = cur.fetchall()

    con.close()

    return render_template("admin_orderlist.html", data=data);

@app.route("/admin/order_confirmation", methods=['GET','POST'])
def admin_order_confirmation():
    if request.method == 'GET':
        id = request.args.get('id')

        return render_template("admin_order_confirmation.html")

@app.route("/admin/user_list", methods=['GET', 'POST'])
@admin_authorization
def admin_user_lsit():
    if request.method == 'GET':
        con = sqlite3.connect("vwa.db")
        cur = con.cursor()

        cur.execute(
            """
            SELECT u.id, u.jmeno, u.primeni, u.login ,ur.nazev
            FROM uzivately u
            INNER JOIN role_uzivately ur
            ON u.id = ur.id_uzivatele
            """
        )
        users = cur.fetchall()

        con.close()

        return render_template("admin_userlist.html", users=users)

@app.route("/admin/user_add", methods=['GET','POST'])
@admin_authorization
def admin_user_add():
    if request.method == 'GET':
        con = sqlite3.connect("vwa.db")
        cur = con.cursor()

        cur.execute(
            'SELECT nazev FROM role'
        )
        roles = cur.fetchall()

        con.close()

        return render_template("admin_user_add.html", roles=roles)

    if request.method == 'POST':
        fname = request.form['fname']
        lname = request.form['lname']
        login = request.form['login']
        role = request.form['role']

        con = sqlite3.connect("vwa.db")
        cur = con.cursor()

        cur.execute(
            'INSERT INTO uzivately(jmeno, primeni, login, heslo, vkladan) VALUES(?,?,?,?,?)',(fname, lname, login, login, session['user_id'])
        )
        cur.execute(
            'INSERT INTO role_uzivately (platnost, nazev, id_uzivatele) VALUES(1, ?, last_insert_rowid())',(role,)
        )
        con.commit()

        con.close()

        return redirect("/admin/user_list")

@app.route("/admin/user_edit", methods=['GET','POST'])
@admin_authorization
def admin_user_edit():
    if request.method == 'GET':
        id = request.args.get('id')

        con = sqlite3.connect("vwa.db")
        cur = con.cursor()

        cur.execute(
            """
            SELECT u.id, u.jmeno, u.primeni, u.login ,ur.nazev
            FROM uzivately u
            INNER JOIN role_uzivately ur
            ON u.id = ur.id_uzivatele
            WHERE u.id = ?
            """,(id,)
        )
        user = cur.fetchone()

        cur.execute(
            'SELECT nazev FROM role'
        )
        roles = cur.fetchall()

        con.close()

        return render_template("admin_user_edit.html", user=user, roles=roles)

    if request.method == 'POST':
        id = request.form['id']
        fname = request.form['fname']
        lname = request.form['lname']
        login = request.form['login']
        role = request.form['role']

        con = sqlite3.connect("vwa.db")
        cur = con.cursor()

        cur.execute(
            'UPDATE role_uzivately SET platnost = 0 WHERE id_uzivatele = ? AND platnost = 1',(id,)
        )
        cur.execute(
            'UPDATE uzivately SET jmeno = ?, primeni = ?, login = ? WHERE id = ?',(fname, lname, login, id)
        )
        cur.execute(
            'INSERT INTO role_uzivately(platnost, nazev, id_uzivatele, pridelil) VALUES(1,?,?,?)',(role, id, session['user_id'])
        )

        con.commit()

        con.close()

        return redirect("/admin/user_list")