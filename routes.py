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
                'SELECT nazev FROM role_uzivately WHERE id_uzivatele = ? AND platnost = 1', (session['user_id'],)
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
            SELECT st.id, v.model, v.spz, v.rok_vyroby, st.stav
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

@app.route('/client/notification', methods=['POST'])
@client_authorization
def client_get_notifications():
    id = request.form['stav_id']

    con = sqlite3.connect("vwa.db")
    cur = con.cursor()

    cur.execute(
        """
        SELECT v.model FROM vozidla v
        INNER JOIN servis s ON v.id = s.vozidlo
        INNER JOIN stav_servisu st ON st.id_servisu = s.id
        WHERE st.id = ?
        """,(id,)
    )
    car = cur.fetchone()

    cur.execute(
        """
        SELECT n.datum, n.zprava FROM notifikace n
        INNER JOIN stav_servisu st ON st.id = n.id_stav
        WHERE st.id = ?
        ORDER BY n.datum ASC
        """,(id,)
    )

    notifications = cur.fetchall()

    con.close()

    return render_template("client_notification.html", car=car, notifications=notifications)
    

@app.route("/mechanic")
@mechanic_authorization
def mechanic_screen():
    return redirect("/mechanic/car_list")

@app.route("/mechanic/car_list")
@mechanic_authorization
def mechanic_car_list():
    con = sqlite3.connect('vwa.db')
    cur = con.cursor()

    cur.execute(
        """
        select v.id, v.model, v.spz, v.rok_vyroby, o.datum
        FROM vozidla v
        INNER JOIN servis s
        ON v.id = s.vozidlo
        INNER JOIN operace o
        ON o.soucast_servisu = s.id
        INNER JOIN stav_servisu st
        ON st.id_servisu = s.id
        WHERE o.provadi = ? AND st.stav IS NOT 'dokonceno';
        """,(session['user_id'],)
    )
    data = cur.fetchall()

    con.close()

    return render_template("mechanic_car_list.html", data=data)

@app.route("/mechanic/notification", methods=['GET','POST'])
@mechanic_authorization
def mechanic_notification():
    if request.method == 'GET':
        id = request.args.get('id')

        con = sqlite3.connect("vwa.db")
        cur = con.cursor()

        cur.execute(
            """
            select s.id, v.model, v.spz, o.typ
            FROM vozidla v
            INNER JOIN servis s
            ON v.id = s.vozidlo
            INNER JOIN operace o
            ON o.soucast_servisu = s.id
            WHERE o.provadi = ? AND v.id = ?;
            """,(session['user_id'], id)
        )
        data = cur.fetchone()

        con.close()
        return render_template('mechanic_notification.html', data=data)

    if request.method == 'POST':
        servis_id = request.form['servis_id']
        notification = request.form['notification']
        service_end = request.form.getlist('service_end')[0]
        print(service_end)

        con = sqlite3.connect('vwa.db')
        cur = con.cursor()

        cur.execute(
            'SELECT st.id FROM stav_servisu st INNER JOIN servis s ON st.id_servisu = s.id'
        )
        stav_servisu = cur.fetchone()
        stav_servisu_id = stav_servisu[0]

        cur.execute(
            'INSERT INTO notifikace(id_stav, zprava) VALUES(?,?)',(stav_servisu_id, notification)
        )

        if service_end == 'on':
            cur.execute(
                'UPDATE stav_servisu SET stav = "dokonceno" WHERE id = ?',(stav_servisu_id,)
            )
            cur.execute(
                "UPDATE stav_servisu SET dokonceni = DATETIME('now')"
            )
        
        con.commit()

        con.close()

        return redirect('/mechanic')



@app.route("/manager")
@manager_authorization
def manager_screen():
    return redirect('/manager/car_list')

@app.route('/manager/car_list')
@manager_authorization
def manager_car_list():
    con = sqlite3.connect("vwa.db")
    cur = con.cursor()

    cur.execute(
        'SELECT v.id, v.model, v.spz, v.rok_vyroby, u.primeni, u.jmeno FROM vozidla v INNER JOIN uzivately u ON v.vlastnik = u.id'
    )
    data = cur.fetchall()

    con.close()

    return render_template('manager_car_list.html', data=data)

@app.route('/manager/notification', methods=['POST'])
@manager_authorization
def manager_notification():
    id = request.form['stav_id']

    con = sqlite3.connect("vwa.db")
    cur = con.cursor()

    cur.execute(
        """
        SELECT v.model FROM vozidla v
        INNER JOIN servis s ON v.id = s.vozidlo
        INNER JOIN stav_servisu st ON st.id_servisu = s.id
        WHERE st.id = ?
        """,(id,)
    )
    car = cur.fetchone()

    cur.execute(
        """
        SELECT n.datum, n.zprava FROM notifikace n
        INNER JOIN stav_servisu st ON st.id = n.id_stav
        WHERE st.id = ?
        ORDER BY n.datum ASC
        """,(id,)
    )

    notifications = cur.fetchall()

    print(id)

    con.close()

    return render_template("manager_notifications.html", car=car, notifications=notifications)


@app.route('/manager/car_edit', methods=['GET','POST'])
@manager_authorization
def manager_car_edit():
    if request.method == 'GET':
        id = request.args.get('vehicle_id')

        if id:
            con = sqlite3.connect('vwa.db')
            cur = con.cursor()
            
            cur.execute(
                'SELECT id, model, spz, rok_vyroby FROM vozidla WHERE id = ?',(id,)
            )
            data = cur.fetchone()

            con.close()

            return render_template('manager_car_edit.html', data=data)
        else:
            return redirect('/manager/car_list')

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

        return redirect("/manager/car_list")

@app.route('/manager/service_list')
@manager_authorization
def manager_service_list():
    con = sqlite3.connect("vwa.db")
    cur = con.cursor()

    cur.execute(
        """
        SELECT ss.id, v.model, v.spz, v.rok_vyroby, u.jmeno, u.primeni, ss.stav FROM vozidla v
        INNER JOIN servis s ON v.id = s.vozidlo
        INNER JOIN operace o ON s.id = o.soucast_servisu
        INNER JOIN uzivately u ON u.id = o.provadi
        INNER JOIN stav_servisu ss ON ss.id_servisu = s.id
        WHERE ss.stav IS NOT 'dokonceno'
        """
    )

    data = cur.fetchall()

    con.close()

    return render_template("manager_servicelist.html", data=data)

@app.route('/manager/orders')
@manager_authorization
def manager_order_list():
    con = sqlite3.connect("vwa.db")
    cur = con.cursor()

    cur.execute(
        """
        SELECT v.id, v.model, v.spz, v.rok_vyroby, v.vlastnik, s.problem FROM vozidla v
        INNER JOIN servis s ON v.id = s.vozidlo
        LEFT JOIN operace o ON s.id = o.soucast_servisu
        WHERE o.id IS NULL
        """
    )
    data = cur.fetchall()

    con.close()

    return render_template("manager_orderlist.html", data=data);

@app.route("/manager/order_confirmation", methods=['GET','POST'])
@manager_authorization
def manager_order_confirmation():
    if request.method == 'GET':
        id = request.args.get('id')

        if id:
            con = sqlite3.connect("vwa.db")
            cur = con.cursor()

            cur.execute(
                """
                SELECT u.id, u.jmeno, u.primeni
                FROM uzivately u
                INNER JOIN role_uzivately r
                ON u.id = r.id_uzivatele
                WHERE r.nazev = 'mechanic'
                """
            )
            thechnicians = cur.fetchall()

            cur.execute(
                'SELECT id, model, spz FROM vozidla WHERE id = ?',(id,)
            )
            vehicle = cur.fetchone()

            cur.execute(
                'SELECT nazev FROM typ_operace'
            )
            repair = cur.fetchall()

            con.close()

            repair = [item for sublist in repair for item in sublist]

            return render_template("manager_order_confirm.html", thechnicians=thechnicians, vehicle=vehicle, repair=repair)
        else:
            return redirect("/manager/orders")
    
    if request.method == 'POST':
        vehicle_id = request.form['id']
        mechanic = request.form['mechanic']
        date = request.form['date']
        time = request.form['time']
        repair_type = request.form['repair_type']

        date = date + ' ' + time+':00:00'

        con = sqlite3.connect("vwa.db")
        cur = con.cursor()

        cur.execute(
            """
            SELECT s.id FROM vozidla v
            INNER JOIN servis s ON v.id = s.vozidlo
            WHERE v.id = ?
            """,(vehicle_id,)
        )

        servis = cur.fetchone()

        cur.execute(
            'INSERT INTO operace(cena, soucastky, typ, provadi, soucast_servisu, datum) VALUES(0, " ", ?,?,?,?)',(repair_type, mechanic, servis[0], date)
        )

        cur.execute(
            'UPDATE stav_servisu SET stav = "Termin rezervovan" WHERE id_servisu = ?',(servis[0],)
        )

        con.commit()

        con.close()

        return redirect('/manager/orders')

@app.route('/manager/statistics')
@manager_authorization
def manager_statistics():
    con = sqlite3.connect('vwa.db')
    cur = con.cursor()
    
    cur.execute(
        'SELECT t.nazev, COUNT(o.typ)  FROM typ_operace t LEFT JOIN operace o ON t.nazev = o.typ GROUP BY t.nazev'
    )
    total = cur.fetchall()

    con.close()

    return render_template('manager_statistics.html', total=total)

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

        if id:
            con = sqlite3.connect('vwa.db')
            cur = con.cursor()
            
            cur.execute(
                'SELECT id, model, spz, rok_vyroby FROM vozidla WHERE id = ?',(id,)
            )
            data = cur.fetchone()

            con.close()

            return render_template('admin_car_edit.html', data=data)
        else:
            return redirect('/admin/car_list')

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

    con = sqlite3.connect("vwa.db")
    cur = con.cursor()

    cur.execute(
        """
        SELECT v.id, v.model, v.spz, v.rok_vyroby, u.jmeno, u.primeni, ss.stav FROM vozidla v
        INNER JOIN servis s ON v.id = s.vozidlo
        INNER JOIN operace o ON s.id = o.soucast_servisu
        INNER JOIN uzivately u ON u.id = o.provadi
        INNER JOIN stav_servisu ss ON ss.id_servisu = s.id
        WHERE ss.stav IS NOT 'dokonceno'
        """
    )

    data = cur.fetchall()

    con.close()

    return render_template("admin_servicelist.html", data=data)

@app.route("/admin/order_list")
@admin_authorization
def admin_order_list():
    con = sqlite3.connect("vwa.db")
    cur = con.cursor()

    cur.execute(
        """
        SELECT v.id, v.model, v.spz, v.rok_vyroby, v.vlastnik, s.problem FROM vozidla v
        INNER JOIN servis s ON v.id = s.vozidlo
        LEFT JOIN operace o ON s.id = o.soucast_servisu
        WHERE o.id IS NULL
        """
    )
    data = cur.fetchall()

    con.close()

    return render_template("admin_orderlist.html", data=data);

@app.route("/admin/order_confirmation", methods=['GET','POST'])
@admin_authorization
def admin_order_confirmation():
    if request.method == 'GET':
        id = request.args.get('id')

        if id:
            con = sqlite3.connect("vwa.db")
            cur = con.cursor()

            cur.execute(
                """
                SELECT u.id, u.jmeno, u.primeni
                FROM uzivately u
                INNER JOIN role_uzivately r
                ON u.id = r.id_uzivatele
                WHERE r.nazev = 'mechanic'
                """
            )
            thechnicians = cur.fetchall()

            cur.execute(
                'SELECT id, model, spz FROM vozidla WHERE id = ?',(id,)
            )
            vehicle = cur.fetchone()

            cur.execute(
                'SELECT nazev FROM typ_operace'
            )
            repair = cur.fetchall()

            con.close()

            repair = [item for sublist in repair for item in sublist]

            return render_template("admin_order_confirmation.html", thechnicians=thechnicians, vehicle=vehicle, repair=repair)
        else:
            return redirect("/admin/order_list")
    
    if request.method == 'POST':
        vehicle_id = request.form['id']
        mechanic = request.form['mechanic']
        date = request.form['date']
        time = request.form['time']
        repair_type = request.form['repair_type']

        date = date + ' ' + time+':00:00'

        con = sqlite3.connect("vwa.db")
        cur = con.cursor()

        cur.execute(
            """
            SELECT s.id FROM vozidla v
            INNER JOIN servis s ON v.id = s.vozidlo
            WHERE v.id = ?
            """,(vehicle_id,)
        )

        servis = cur.fetchone()

        cur.execute(
            'INSERT INTO operace(cena, soucastky, typ, provadi, soucast_servisu, datum) VALUES(0, " ", ?,?,?,?)',(repair_type, mechanic, servis[0], date)
        )

        cur.execute(
            'UPDATE stav_servisu SET stav = "Termin rezervovan" WHERE id_servisu = ?',(servis[0],)
        )

        con.commit()

        con.close()

        return redirect('/admin/order_list')

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
            WHERE ur.platnost = 1
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

@app.route("/admin/delete_user", methods=['POST'])
@admin_authorization
def admin_delete_user():
    if request.method == 'POST':
        id = request.form['id']

        con = sqlite3.connect("vwa.db")
        cur = con.cursor()

        cur.execute(
            'DELETE FROM vozidla WHERE vlastnik = ?',(id,)
        )

        cur.execute(
            'DELETE FROM role_uzivately WHERE id_uzivatele = ?',(id,)
        )

        cur.execute(
            'DELETE FROM uzivately WHERE id = ?', (id,)
        )

        con.commit()

        con.close()

        return redirect('/admin/user_list')

@app.route('/admin/statistics')
@admin_authorization
def admin_statistics():
    con = sqlite3.connect('vwa.db')
    cur = con.cursor()
    
    cur.execute(
        'SELECT t.nazev, COUNT(o.typ)  FROM typ_operace t LEFT JOIN operace o ON t.nazev = o.typ GROUP BY t.nazev'
    )
    total = cur.fetchall()

    con.close()

    return render_template('admin_statistics.html', total=total)

