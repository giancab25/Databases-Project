#Import Flask Library
from asyncio.windows_events import NULL
from flask import Flask, render_template, request, session, url_for, redirect
import pymysql.cursors

#Initialize the app from Flask
app = Flask(__name__)

#Configure MySQL
conn = pymysql.connect(host='localhost',
					   port = 3306,
                       user='root',
                       password='',
                       db='airticketreservation',
                       charset='utf8mb4',
                       cursorclass=pymysql.cursors.DictCursor)

#Define a route to hello function
@app.route('/')
def hello():
	return render_template('index.html')

#Define route for login
@app.route('/login')
def login():
	return render_template('login.html')

#Define route for register
@app.route('/register')
def register():
	return render_template('register.html')

#flight search feature page
@app.route('/flightsearch') #at url directory flight search
def flightsearch():         #display flight search page
	return render_template('flightsearch.html')

#flight search execution with Depart city
@app.route('/SCsearchresults', methods=['GET', 'POST'])
def SCsearchresults():
	Depart_City = request.form['SC'] #request input DA
	cursor = conn.cursor(); #used to execute SQL commands
	view_query = 'CREATE VIEW city as SELECT Port_name as Depart_port, City FROM airport' #Query for data collection
	cursor.execute(view_query)
	data_query = 'SELECT Airline_name, Flight_num, Depart_date, Depart_time, Depart_port, Arrival_port, Arrival_date, Arrival_time, Base_price, ID_num, Flight_status FROM flights NATURAL JOIN city WHERE City = %s'
	data = cursor.execute(data_query, (Depart_City))
	close_view = 'DROP VIEW city'
	if data != NULL:
		flightData = cursor.fetchall()
		cursor.execute(close_view)
		return render_template('searchresults.html', flightData = flightData)
	else:
		cursor.execute(close_view)
		return render_template('searcherror.html')
#flight search execution with Depart port
@app.route('/SAsearchresults', methods=['GET', 'POST'])
def SAsearchresults():
	Depart_port = request.form['SA'] #request input DA
	cursor = conn.cursor(); #used to execute SQL commands
	query = 'SELECT * FROM flights WHERE Depart_port = %s' #Query for data collection
	data = cursor.execute(query, (Depart_port))
	if data != NULL:
		flightData = cursor.fetchall()
		return render_template('searchresults.html', flightData = flightData)
	else:
		return render_template('searcherror.html')
#flight search execution with Arrival city
@app.route('/DCsearchresults', methods=['GET', 'POST'])
def DCsearchresults():
	Arrival_City = request.form['DC'] #request input DA
	cursor = conn.cursor(); #used to execute SQL commands
	view_query = 'CREATE VIEW city as SELECT Port_name as Arrival_port, City FROM airport' #Query for data collection
	cursor.execute(view_query)
	data_query = 'SELECT Airline_name, Flight_num, Depart_date, Depart_time, Depart_port, Arrival_port, Arrival_date, Arrival_time, Base_price, ID_num, Flight_status FROM flights NATURAL JOIN city WHERE City = %s'
	data = cursor.execute(data_query, (Arrival_City))
	close_view = 'DROP VIEW city'
	if data != NULL:
		flightData = cursor.fetchall()
		cursor.execute(close_view)
		return render_template('searchresults.html', flightData = flightData)
	else:
		cursor.execute(close_view)
		return render_template('searcherror.html')
#flight search execution with Arrival port
@app.route('/DAsearchresults', methods=['GET', 'POST'])
def DAsearchresults():
	Arrival_port = request.form['DA'] #request input DA
	cursor = conn.cursor(); #used to execute SQL commands
	query = 'SELECT * FROM flights WHERE Arrival_port = %s' #Query for data collection
	data = cursor.execute(query, (Arrival_port))
	if data != NULL:
		flightData = cursor.fetchall()
		return render_template('searchresults.html', flightData = flightData)
	else:
		return render_template('searcherror.html')
#flight search execution with Depart date
@app.route('/DDsearchresults', methods=['GET', 'POST'])
def DDsearchresults():
	Depart_date = request.form['DD'] #request input DA
	cursor = conn.cursor(); #used to execute SQL commands
	query = 'SELECT * FROM flights WHERE Depart_date = %s' #Query for data collection
	data = cursor.execute(query, (Depart_date))
	if data !=  NULL:
		flightData = cursor.fetchall()
		return render_template('searchresults.html', flightData = flightData)
	else:
		return render_template('searcherror.html')

#flight search execution for Round Trip
@app.route('/RTsearchresults', methods=['GET', 'POST'])
def RTsearchresults():
	Depart_date = request.form['DD'] #request input
	cursor = conn.cursor(); #used to execute SQL commands
	query = 'SELECT * FROM flights WHERE Depart_date = %s' #Query 
	data = cursor.execute(query, (Depart_date))
	if data != NULL:
		DepartData = cursor.fetchall()
		return render_template('RTresults.html', DepartData = DepartData)
	else:
		return render_template('searcherror.html')

#for possible return flights
@app.route('/RTresults', methods=['GET', 'POST'])
def RTresults():
	Flight_num = request.form['FN'] 
	Depart_date = request.form['DD'] 
	Depart_time = request.form['DT'] 
	Airline_name = request.form['AN'] 
	Arrival_port = request.form['AP'] 
	Arrival_date = request.form['AD']
	cursor1 = conn.cursor(); #used to execute SQL commands
	query1 = 'SELECT * FROM flights WHERE Flight_num = %s and Depart_date = %s and Depart_time = %s and Airline_name = %s and Arrival_port = %s' #Query 
	data1 = cursor1.execute(query1, (Flight_num,Depart_date,Depart_time,Airline_name, Arrival_port))
	cursor2 = conn.cursor(); #used to execute SQL commands
	query2 = 'SELECT * FROM flights WHERE Depart_port = %s and Depart_date > %s' #Query 
	data2 = cursor2.execute(query2, (Arrival_port, Arrival_date))	
	if data1 != NULL and data2 != NULL:
		DepartData = cursor1.fetchall()
		ReturnData = cursor2.fetchall()
		return render_template('RTFinal.html', DepartData = DepartData, ReturnData = ReturnData)
	else:
		return render_template('searcherror.html')

#Authenticates the login
@app.route('/loginAuth', methods=['GET', 'POST'])
def loginAuth():
	#grabs information from the forms
	username = request.form['username']
	password = request.form['password']

	#cursor used to send queries
	cursor = conn.cursor()
	#executes query
	query = 'SELECT * FROM user WHERE username = %s and password = %s'
	cursor.execute(query, (username, password))
	#stores the results in a variable
	data = cursor.fetchone()
	#use fetchall() if you are expecting more than 1 data row
	cursor.close()
	error = None
	if(data):
		#creates a session for the the user
		#session is a built in
		session['username'] = username
		return redirect(url_for('home'))
	else:
		#returns an error message to the html page
		error = 'Invalid login or username'
		return render_template('login.html', error=error)

#Authenticates the register
@app.route('/registerAuth', methods=['GET', 'POST'])
def registerAuth():
	#grabs information from the forms
	username = request.form['username']
	password = request.form['password']

	#cursor used to send queries
	cursor = conn.cursor()
	#executes query
	query = 'SELECT * FROM user WHERE username = %s'
	cursor.execute(query, (username))
	#stores the results in a variable
	data = cursor.fetchone()
	#use fetchall() if you are expecting more than 1 data row
	error = None
	if(data):
		#If the previous query returns data, then user exists
		error = "This user already exists"
		return render_template('register.html', error = error)
	else:
		ins = 'INSERT INTO user VALUES(%s, %s)'
		cursor.execute(ins, (username, password))
		conn.commit()
		cursor.close()
		return render_template('index.html')

@app.route('/home')
def home():
    
    username = session['username']
    cursor = conn.cursor();
    query = 'SELECT ts, blog_post FROM blog WHERE username = %s ORDER BY ts DESC'
    cursor.execute(query, (username))
    data1 = cursor.fetchall() 
    for each in data1:
        print(each['blog_post'])
    cursor.close()
    return render_template('home.html', username=username, posts=data1)

@app.route('/home_staff')
def home_staff():
    
    username = session['username']
    cursor = conn.cursor();
    query = 'SELECT ts, blog_post FROM blog WHERE username = %s ORDER BY ts DESC'
    cursor.execute(query, (username))
    data1 = cursor.fetchall() 
    for each in data1:
        print(each['blog_post'])
    cursor.close()
    return render_template('home_staff.html', username=username, posts=data1)

		
@app.route('/post', methods=['GET', 'POST'])
def post():
	username = session['username']
	cursor = conn.cursor();
	blog = request.form['blog']
	query = 'INSERT INTO blog (blog_post, username) VALUES(%s, %s)'
	cursor.execute(query, (blog, username))
	conn.commit()
	cursor.close()
	return redirect(url_for('home'))

@app.route('/logout')
def logout():
	session.pop('username')
	return redirect('/')
		
app.secret_key = 'some key that you will never guess'
#Run the app on localhost port 5000
#debug = True -> you don't have to restart flask
#for changes to go through, TURN OFF FOR PRODUCTION
if __name__ == "__main__":
	app.run('127.0.0.1', 5000, debug = True)
