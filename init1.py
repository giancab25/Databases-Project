#Import Flask Library
from flask import Flask, render_template, request, session, url_for, redirect
import pymysql.cursors
from datetime import date

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
@app.route('/flightsearch', methods=['GET', 'POST']) #at url directory flight search
def flightsearch():         #display flight search page
	return render_template('flightsearch.html')

#flight search execution with Depart city
@app.route('/searchresults', methods=['GET', 'POST'])
def searchresults():
	Depart_City = request.form['SC']
	Depart_port = request.form['SA'] 
	Arrival_City = request.form['DC']
	Arrival_port = request.form['DA']
	Depart_date = request.form['DD']
	Return_date = request.form['RD']
	cursor = conn.cursor(); #used to execute SQL commands
	view_query = 'CREATE VIEW city as SELECT Port_name as Depart_port,\
		 City as Depart_city FROM airport' #Query for data collection
	cursor.execute(view_query)
	view_query = 'CREATE VIEW city2 as SELECT Port_name as Arrival_port,\
		 City as Arrival_city FROM airport' 
	cursor.execute(view_query)
	data_query = 'SELECT Airline_name, Flight_num, Depart_date, Depart_time, \
		Depart_port, Arrival_port, Arrival_date, Arrival_time, Base_price, \
		ID_num, Flight_status FROM flights NATURAL JOIN city NATURAL JOIN \
		city2 WHERE Depart_city = %s AND Depart_port = %s AND Arrival_city = %s\
		AND Arrival_port = %s AND Depart_date >= %s' 
	roundDepart = 'SELECT Airline_name, Flight_num, Depart_date, Depart_time, \
		Depart_port, Arrival_port, Arrival_date, Arrival_time, Base_price, \
		ID_num, Flight_status FROM flights NATURAL JOIN city NATURAL JOIN \
		city2 WHERE Depart_city = %s AND Depart_port = %s AND Arrival_city = %s\
		AND Arrival_port = %s AND Depart_date >= %s AND Depart_date < %s \
		AND Arrival_date < %s' 
	if(Return_date == ''):
		data = cursor.execute(data_query, (Depart_City,Depart_port,Arrival_City, Arrival_port, Depart_date))
		if (data):
			flightData = cursor.fetchall()
			cursor.execute('DROP VIEW city')
			cursor.execute('DROP VIEW city2')
			cursor.close()
			return render_template('searchresults.html', flightData = flightData)
		else:
			cursor.execute('DROP VIEW city')
			cursor.execute('DROP VIEW city2')
			cursor.close()
			return render_template('searcherror.html')
	else:
		data = cursor.execute(roundDepart, (Depart_City,Depart_port,Arrival_City, Arrival_port, Depart_date, Return_date, Return_date))
		cursor2 = conn.cursor()
		data2 = cursor2.execute(data_query, (Arrival_City,Arrival_port,Depart_City, Depart_port, Return_date))
		if (data) and (data2):
			flightData = cursor.fetchall()
			returnData = cursor2.fetchall()
			cursor.execute('DROP VIEW city')
			cursor.execute('DROP VIEW city2')
			cursor.close()
			cursor2.close()
			return render_template('RTFinal.html', flightData = flightData, returnData = returnData)
		else:
			cursor.execute('DROP VIEW city')
			cursor.execute('DROP VIEW city2')
			cursor.close()
			cursor2.close()
			return render_template('searcherror.html')

#view flight status
@app.route('/viewflightstatus')
def status():
	return render_template('statInfo.html')

@app.route('/showstat', methods=['GET','POST'])
def showstat():
	Airline = request.form['AN']
	Flight = request.form['FN']
	Departure = request.form['DD']
	Arrival = request.form['AD']
	cursor = conn.cursor()
	query = 'SELECT Flight_status FROM flights WHERE Airline_name = %s \
		AND Flight_num = %s AND Depart_date = %s AND Arrival_date = %s'
	data = cursor.execute(query, (Airline, Flight, Departure, Arrival))
	if (data):
		stat = cursor.fetchall()
		cursor.close()
		return render_template('showstat.html', stat=stat)
	else:
		cursor.close()
		return render_template('searcherror.html')


@app.route('/loginAuth', methods=['GET', 'POST'])
def loginAuth():
	#grabs information from the forms
	username = request.form['email']
	password = request.form['password']

	#cursor used to send queries
	cursor_cus = conn.cursor()
	cursor_emp = conn.cursor()
	#executes customer query
	#query_cus = 'SELECT First_name FROM airline_staff WHERE Username = %s and PWD = %s'
	query_cus = 'SELECT * FROM customer WHERE Email_Address = %s and PWD = %s'
	query_emp = 'SELECT * FROM airline_staff WHERE Username = %s and PWD = %s'
	#executes and saves first (customer) query in 'data_cus'
	cursor_cus.execute(query_cus, (username,password))
	data_cus = cursor_cus.fetchone()
	#executes and saves second (employee) query in 'data_emp'
	cursor_emp.execute(query_emp,(username,password))
	data_emp = cursor_emp.fetchone()
	#use fetchall() if you are expecting more than 1 data row
	cursor_cus.close()
	cursor_emp.close()
	error = None
	if(data_cus):
		#creates a session for the the user
		#session is a built in
		#records the user name
		session['username'] = username
		#return redirect(url_for('home'))
		return redirect(url_for('home'))
	elif(data_emp):
		session['username'] = username
		return redirect(url_for('homestaff'))
	else:
		#returns an error message to the html page
		error = 'Invalid login or username'
		return render_template('login.html', error=error)
#Authenticates the register
@app.route('/registerAuth', methods=['GET', 'POST'])
def registerAuth():
	#grabs information from the forms
	name     = request.form['name']
	email    = request.form['email']
	password = request.form['password']
	phone_num= request.form['phone_num']
	passport_num = request.form['passport_num']
	passport_exp = request.form['passport_exp']
	passport_country = request.form['passport_country']
	dob      = request.form['date_of_birth']
	building_num = request.form['building_num']
	street   = request.form['cust_street']
	city     = request.form['cust_city']
	state    = request.form['cust_state']

	#cursor used to send queries
	cursor = conn.cursor()
	#executes query
	query = 'SELECT * FROM customer WHERE Email_Address = %s'
	cursor.execute(query, (email))
	#stores the results in a variable
	data = cursor.fetchone()
	#use fetchall() if you are expecting more than 1 data row
	error = None
	if(data):
		#If the previous query returns data, then user exists
		error = "This email is already registered"
		return render_template('register.html', error = error)
	else:
		#inserts the below values into the customer table
		ins = 'INSERT INTO customer VALUES(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)'
		cursor.execute(ins, (name,email,password, 
		               building_num,street,city,state,
					   phone_num,passport_num,passport_exp,
					   passport_country,dob))
		conn.commit()
		cursor.close()
		return render_template('index.html')
@app.route('/registerAuthStaff', methods=['GET','POST'])
def registerAuthStaff():
	#grabs and saves in variables info from forms
	username = request.form['staff_username']
	airline_name = request.form['airline_name']
	password = request.form['staff_password']
	first_name = request.form['first_name']
	last_name = request.form['last_name']
	dob =      request.form['staff_dob']\
	#cursor used to execute query
	cursor = conn.cursor()
	#defines and executes query
	query = 'SELECT * FROM airline_staff WHERE Username = %s'
	cursor.execute(query,(username))
	#saves queued data to "data"
	data = cursor.fetchone()
	error = None
	if(data): #checks if data exists
		error = 'This user is already registered'
		return render_template('register.html', error = error)
	else: #didnt exists so will be inserted into the database
		ins = 'INSERT INTO airline_staff VALUES(%s, %s, %s, %s, %s, %s)'
		cursor.execute(ins, (username, airline_name, password,
				       first_name, last_name, dob))
		conn.commit()
		cursor.close()
		return render_template('index.html')

@app.route('/home')
def home():
    
    username = session['username']
    #cursor = conn.cursor();
    #query = 'SELECT ts, blog_post FROM blog WHERE username = %s ORDER BY ts DESC'
    #cursor.execute(query, (username))
    #data1 = cursor.fetchall()
    #for each in data1:
        #print(each['blog_post'])
    #cursor.close()
    return render_template('home.html', username=username)#, username=username, posts=data1)

#Customer views their future flights
@app.route('/viewflights', methods=['GET','POST'])
def viewflights():
	username = session['username']
	dateToday = date.today()
	cursor = conn.cursor()
	query = 'CREATE VIEW CustTicket as SELECT Flight_num as Flight_Num, Cust_Email FROM ticket'
	cursor.execute(query)
	query = 'SELECT Airline_name, Flight_num, Depart_date, Depart_time, Depart_port,Arrival_port, Arrival_date,Arrival_time,Base_price,ID_num,FLight_status FROM flights NATURAL JOIN CustTicket WHERE Cust_Email = %s AND Depart_date > %s'
	cursor.execute(query, (username, dateToday))
	data = cursor.fetchall()
	query = 'DROP VIEW CustTicket'
	cursor.execute(query)
	if(data):
		cursor.close()
		return render_template('viewflights.html', username=username, data=data)
	else:
		return render_template('viewflights.html')

#Customer views their past flights
@app.route('/pastflights', methods=['GET','POST'])
def pastflights():
	username = session['username']
	dateToday = date.today()
	cursor = conn.cursor()
	query = 'CREATE VIEW CustTicket as SELECT Flight_num as Flight_Num, Cust_Email FROM ticket'
	cursor.execute(query)
	query = 'SELECT Airline_name, Flight_num, Depart_date, Depart_time, Depart_port,Arrival_port, Arrival_date,Arrival_time,Base_price,ID_num,FLight_status FROM flights NATURAL JOIN CustTicket WHERE Cust_Email = %s AND Depart_date < %s'
	cursor.execute(query, (username, dateToday))
	data = cursor.fetchall()
	query = 'DROP VIEW CustTicket'
	cursor.execute(query)
	if (data):
		cursor.close()
		return render_template('pastflights.html', username=username, data=data)
	else:
		return render_template('pastflights.html')	

@app.route('/homestaff')
def homestaff():
	username=session['username']
	return render_template('homestaff.html')

@app.route('/post', methods=['GET', 'POST'])
def post():
	username = session['username']
	#cursor = conn.cursor();
	# blog = request.form['blog']
	# query = 'INSERT INTO blog (blog_post, username) VALUES(%s, %s)'
	# cursor.execute(query, (blog, username))
	# conn.commit()
	# cursor.close()
	return redirect(url_for('home'))

@app.route('/poststaff',methods=['GET','POST'])
def poststaff():
	username=session['username']
	return render_template('homestaff.html')

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
