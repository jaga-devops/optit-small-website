from flask import Flask, render_template, request, redirect, make_response
from flask_mysqldb import MySQL
import yaml
import pdfkit

app = Flask(__name__)

# Configure db
db = yaml.load(open('db.yaml'))
app.config['MYSQL_HOST'] = db['mysql_host']
app.config['MYSQL_USER'] = db['mysql_user']
app.config['MYSQL_PASSWORD'] = db['mysql_password']
app.config['MYSQL_DB'] = db['mysql_db']

mysql = MySQL(app)

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        # Fetch form data
        userDetails = request.form
        name = userDetails['name']
        dob = userDetails['dob']
        city = userDetails['city']
        cur = mysql.connection.cursor()
        cur.execute("INSERT INTO input(name, dob, city) VALUES(%s, %s, %s)",(name, dob, city))
        mysql.connection.commit()
        cur.close()
        return redirect('/current_user')
    return render_template('index.html')

@app.route('/current_user')
def currect_entry():
    cur = mysql.connection.cursor()
    get_current_user_details = cur.execute("select * from input ORDER BY id DESC LIMIT 1")
    if get_current_user_details > 0:
        currectUser = cur.fetchall()
        return render_template('current_user.html',currentUser=currectUser)

@app.route('/users')
def users():
    cur = mysql.connection.cursor()
    resultValue = cur.execute("SELECT * FROM input")
    if resultValue > 0:
        userDetails = cur.fetchall()
        return render_template('users.html',userDetails=userDetails)

@app.route('/<name>/<location>')
def print_current_user(name, location):
    rendered = render_template("print_to_pdf.html", name=name, location=location)
    pdf = pdfkit.from_string(rendered, False)
    response = make_response(pdf)
    response.headers['Content-Type'] = 'application/pdf'
    response.headers['Content-Disposition'] = 'inline; filename=output.pdf'
    return response

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=80)
