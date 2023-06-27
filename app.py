from flask import Flask, render_template, request,url_for,flash,redirect,session;
from flask_session import Session
import ibm_db

app=Flask(__name__)

app.config["SESSION_PERMANENT"]=False 
app.config["SESSION_TYPE"]="filesystem"
Session(app)
app.secret_key = "789764532"

conn=ibm_db.connect("DATABASE=bludb;HOSTNAME=19af6446-6171-4641-8aba-9dcff8e1b6ff.c1ogj3sd0tgtu0lqde00.databases.appdomain.cloud;PORT=30699;SECURITY=SSL;SSLServerCertificate=DigiCertGlobalRootCA.crt;UID=prr47494;PWD=ggtIQb5SN8tno7qc",'','')


def insertsql(tablename, fields, values):
    query="Insert into "+tablename+"("

    for i in fields:
        query+=str(i)+","
    query=query[:-1]+") Values ("
    for i in range(len(fields)):
        query+="?,"
    query=query[:-1]+")"

    print(query)

    prep_stmt=ibm_db.prepare(conn,query)

    for i in range(len(values)):
        ibm_db.bind_param(prep_stmt,i+1,values[i])

    ibm_db.execute(prep_stmt)



@app.route("/",methods=('GET','POST'))
def signin():
    if request.method=='POST':
        email=request.form["email"]
        password=request.form["password"]

        query= ibm_db.exec_immediate(conn,"select * from userauth")

        userdetails=ibm_db.fetch_assoc(query)

        
        flag=0
        while userdetails!=False:
            print(userdetails['EMAIL'],email,userdetails['PASSWORD']==password)
            if userdetails['EMAIL']==email and userdetails["PASSWORD"]==password.strip():
                flag=2;session["email"]=userdetails["EMAIL"];break
            elif userdetails["EMAIL"]==email and userdetails["PASSWORD"]!=password.strip():
                flag=1;break
            userdetails=ibm_db.fetch_assoc(query)
        if flag==0:
            flash("User doesn't exist")
        elif flag==1:
            flash("Password is incorrect")
        else:
            return redirect(url_for("home")) 

    return render_template("signin.html")

@app.route("/signup")
def signup():
    return render_template('signup.html')  
    
@app.route('/create/',methods=('GET','POST'))
def create():
    if request.method=="POST":
        email=request.form['email']
        password=request.form['password']
        repassword=request.form['repassword']

        if not email:
            flash('Email required')

        elif not password:
            flash('Password is required')
        
        elif not repassword:
            flash('Password is required')

        elif password!=repassword:
            flash('Password did not match')

        else:
            session['email']=email
            fields=["email","password"]
            values=[email,password]
            insertsql("userauth",fields,values)
            return redirect(url_for("profile"))
            
    return  redirect(url_for("signup"))

@app.route("/profile",methods=('POST','GET'))
def profile():
    email=session['email']
    if request.method=="POST":
        name=request.form['name']
        age=request.form['age']
        gender=request.form['gender']
        weight=request.form['weight']
        height=request.form['height']
        allergies=request.form['allergies']
        healthissues=request.form['healthissues']

        fields=["email","name","age","gender","weight","height","allergies","healthissues"]
        values=[email,name,age,gender,weight,height,allergies,healthissues]
        insertsql("userdetails",fields,values)

        
        return redirect(url_for('home'))

    return render_template('profile.html')
    

@app.route("/home")
def home():
    try:
        if session["email"]:
            return render_template("home.html",email=session["email"])
    except:
        return redirect(url_for("login"))
    return redirect(url_for("login"))

@app.route("/get",methods=('POST','GET'))
def get():
    if request.method=="POST":
        foodname=request.form['foodname']
        image=request.form['image']
        return redirect(url_for("display",foodname=foodname,image=image))

@app.route("/display/<foodname>&<image>")
def display(foodname,image):
    if foodname=="Pasta":
        return render_template("display.html",foodname=foodname,image=image,nutri="pastanutri.png")
    elif foodname=="Pizza":
        return render_template("display.html",foodname=foodname,image=image,nutri="pizzanutri.png")
    else:
        return render_template("display.html",foodname=foodname,image=image,nutri="nutri.png")

@app.route("/logout",methods=('POST','GET'))
def logout():
    session['userid']=None 
    return redirect(url_for("signin"))

@app.route("/search")
def search():
    return render_template("search.html",email=session['email'])


if __name__ == "__main__":
    app.run(debug=True)


