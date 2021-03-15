from flask import Flask,render_template,redirect,request,url_for,flash,session
import sqlite3
from wtforms import Form,StringField,PasswordField,validators
from passlib.hash import sha256_crypt
import os
from werkzeug.utils import secure_filename
from functools import wraps
UPLOAD_FOLDER = 'D:/NewCssHtml/static/resimler/Games'
app = Flask(__name__)
app.secret_key = b'_5#y2L"F4Q8z\n\xec]/'
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if "logged_in" in session:
            return f(*args, **kwargs)

        else:
            flash("Unattainable Page,Please Login")
            return redirect(url_for("login"))
        
    return decorated_function


connection = sqlite3.connect("newsql.db")
cursor = connection.cursor()
connection.commit()
connection.close()


@app.route("/")
def index():
    connection = sqlite3.connect("newsql.db")
    cursor = connection.cursor()
    sql = "SELECT * FROM games"
    cursor.execute(sql)
    result = cursor.fetchall()
    if len(result) == 0:
        return render_template("home.html")
    
    else:
        return render_template("home.html",result = result)


    return render_template("home.html")

@app.route("/register",methods =["GET","POST"])
def register():
    if request.method == "POST":

        namesurname = request.form.get("namesurname")
        username = request.form.get("username")
        email = request.form.get("email")
        password = request.form.get("password")
        password = sha256_crypt.encrypt(password)
        connection = sqlite3.connect("newsql.db")
        cursor = connection.cursor()
        sql = "CREATE TABLE IF NOT EXISTS users(namesurname TEXT,username TEXT,email TEXT,password TEXT)"
        cursor.execute(sql)
        connection.commit()
        
        if username and password:

            sqlselectsorgu = "SELECT * FROM users WHERE username = ?"
            cursor.execute(sqlselectsorgu,(username,))
            result = cursor.fetchmany()
            username_kontrol = result[0][1]

            if username != username_kontrol:
                namesurname = request.form.get("namesurname")
                username = request.form.get("username")
                email = request.form.get("email")
                password = request.form.get("password")
                password = sha256_crypt.encrypt(password)
                sql2 = "INSERT INTO users(namesurname,username,email,password) VALUES(?,?,?,?)"
                cursor.execute(sql2,(namesurname,username,email,password))
                connection.commit()
                connection.close()
                flash("Congratulations Register.","success")
                return redirect(url_for("index"))
            else:
                flash("This Username Already Use","warning") 
                return redirect(url_for("register"))
        else:
            flash("Try Again.","success")
            return redirect(url_for("register"))

    else:
        return render_template("register.html")


@app.route("/log_in",methods = ["GET","POST"])
def login():

    if request.method == "POST":

        username = request.form.get("username")
        password = request.form.get("password")

        if username and password:
            connection = sqlite3.connect("newsql.db")
            cursor = connection.cursor()
            sql = "SELECT * FROM users WHERE username= ?"
            cursor.execute(sql,(username,))
            result = cursor.fetchone()

            if result:
                username_real = result[1]
                pass_real = result[3]

                if username == username_real:

                    verify_pass = sha256_crypt.verify(password,pass_real)

                    if verify_pass:

                        flash("Congratulations, Logged In","success")
                        session["logged_in"] = True
                        session["username"] = username
                        return redirect(url_for("index"))
                    
                    else:
                        flash("Wrong Password, Try Again","warning")
                        return redirect(url_for("login"))

                else:

                    flash("Wrong User, Try Again","warning")
                    return redirect(url_for("login"))

            else:

                flash("Wrong User Login, Try Again","warning")
                return redirect(url_for("login"))
        else:

            flash("Please Fill in the Fields","warning")
            return redirect(url_for("login"))


    else:
        return render_template("login.html")

@app.route("/log_out")
def logout():

    session.clear()
    flash("we are will miss you")
    return redirect(url_for("index"))


@app.route("/addgames",methods = ["POST","GET"])
@login_required
def addgames():

    connection = sqlite3.connect("newsql.db")
    cursor = connection.cursor()
    sql = "CREATE TABLE IF NOT EXISTS games(GameName TEXT, GameYear INT,GameDirection TEXT ,GameCompany TEXT,GameContent, GamePhotoName TEXT)"
    cursor.execute(sql)
    connection.commit()

    

    if request.method == "POST":
        gamename = request.form.get("gamename")
        gameyear = request.form.get("gameyear")
        gamedirection = request.form.get("gamedirection")
        gamecompany = request.form.get("gamecompany")
        gamecontent = request.form.get("gamecontent")

        if gamename and gameyear and gamedirection and gamecompany:
            file = request.files['gamephoto']
            if file.filename == "":
                flash("No Selected File, Please Select File")
                return redirect(url_for("addgames"))
            gamephotoname = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'],gamephotoname))
            sql2 = "INSERT INTO games(GameName,GameYear,GameDirection,GameCompany,GameContent,GamePhotoName) VALUES(?,?,?,?,?,?)"
            cursor.execute(sql2,(gamename,gameyear,gamedirection,gamecompany,gamecontent,gamephotoname))
            connection.commit()
            connection.close()
            flash("Congratulations.The Game Saved.")
            return redirect(url_for("addgames"))



        else:

            flash("Do Not Have Inputs,Please Fill The Inputs")
            return redirect(url_for("addgames"))

    else:

        return render_template("addgames.html")

@app.route("/games/<name>")
@login_required
def games(name):
    connection = sqlite3.connect("newsql.db")
    cursor = connection.cursor()
    sql = "SELECT * FROM games WHERE GameName = ? "
    cursor.execute(sql,(name,))
    data = cursor.fetchone()
    return render_template("games.html",data=data)

@app.route("/games/<name>")
@app.route("/buygames")
def buygames():

    connection = sqlite3.connect("newsql.db")
    cursor = connection.cursor()
    sql = "SELECT * FROM games"
    cursor.execute(sql)
    data = cursor.fetchall()
    if len(data) == 0:
        return render_template("buygames.html")
    
    else:
        return render_template("buygames.html",data = data)




@app.route("/games/<name>")
@app.route("/gamesdelete/<name>")
def gamesdelete(name):
    
    connection = sqlite3.connect("newsql.db")
    cursor = connection.cursor()
    sql = "DELETE FROM games WHERE GameName = ?"
    cursor.execute(sql,(name,))
    connection.commit()
    connection.close()
    flash("Cong.Your Games Deleted")
    return redirect(url_for("index"))

@app.route("/games/<name>")
@app.route("/gamesupdate/<name>",methods = ["GET","POST"])
def gamesupdate(name):
    connection = sqlite3.connect("newsql.db")
    cursor = connection.cursor()
    sql = "CREATE TABLE IF NOT EXISTS games(GameName TEXT, GameYear INT,GameDirection TEXT ,GameCompany TEXT,GameContent, GamePhotoName TEXT)"
    cursor.execute(sql)
    connection.commit()

    

    if request.method == "POST":
        gamename = request.form.get("gamename")
        gameyear = request.form.get("gameyear")
        gamedirection = request.form.get("gamedirection")
        gamecompany = request.form.get("gamecompany")
        gamecontent = request.form.get("gamecontent")
        if gamename and gameyear and gamedirection and gamecompany and gamecontent:
            file = request.files['gamephoto']
            if file.filename == "":
                sql2 = "Update games  SET GameName = ? , GameYear = ? , GameDirection = ? , GameCompany = ? , GameContent = ? WHERE GameName = ?"
                cursor.execute(sql2,(gamename,gameyear,gamedirection,gamecompany,gamecontent,name))
                connection.commit()
                connection.close()
                flash("Congratulations.The Game Update.")
                return redirect(url_for("index"))
            else:
                
                gamephotoname = secure_filename(file.filename)
                file.save(os.path.join(app.config['UPLOAD_FOLDER'],gamephotoname))
                sql2 = "Update games  SET GameName = ? , GameYear = ? , GameDirection = ? , GameCompany = ? , GameContent = ? , GamePhoto = ? WHERE GameName = ?"
                cursor.execute(sql2,(gamename,gameyear,gamedirection,gamecompany,gamecontent,gamephotoname,name))
                connection.commit()
                connection.close()
                flash("Congratulations.The Game Saved.")
                return redirect(url_for("index"))



        else:

            flash("Do Not Have Inputs,Please Fill The Inputs")
            return redirect(url_for("updategames"))

    else:
        connection = sqlite3.connect("newsql.db")
        cursor = connection.cursor()
        sql = "SELECT * FROM games WHERE GameName = ? "
        cursor.execute(sql,(name,))
        data = cursor.fetchone()

        return render_template("updategames.html",data = data)
    



if __name__ == "__main__":

    app.run(debug=True)

