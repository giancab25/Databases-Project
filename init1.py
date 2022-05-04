#Import Flask Library
from asyncio.windows_events import NULL
from datetime import datetime, date, timedelta
from flask import Flask, render_template, request, session, url_for, redirect
import pymysql.cursors

#Initialize the app from Flask
app = Flask(__name__)

#Configure MySQL
conn = pymysql.connect(host='localhost',
					   port = 3306,
                       user='root',
                       password='',
                       db='project',
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
	if (data):
		flightData = cursor.fetchall()
		cursor.execute(close_view)
		cursor.close()
		return render_template('searchresults.html', flightData = flightData)
	else:
		cursor.execute(close_view)
		cursor.close()
		return render_template('searcherror.html')
#flight search execution with Depart port
@app.route('/SAsearchresults', methods=['GET', 'POST'])
def SAsearchresults():
	Depart_port = request.form['SA'] #request input DA
	cursor = conn.cursor(); #used to execute SQL commands
	query = 'SELECT * FROM flights WHERE Depart_port = %s' #Query for data collection
	data = cursor.execute(query, (Depart_port))
	if (data):
		flightData = cursor.fetchall()
		cursor.close()
		return render_template('searchresults.html', flightData = flightData)
	else:
		cursor.close()
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
	if (data):
		flightData = cursor.fetchall()
		cursor.execute(close_view)
		cursor.close()
		return render_template('searchresults.html', flightData = flightData)
	else:
		cursor.execute(close_view)
		cursor.close()
		return render_template('searcherror.html')
#flight search execution with Arrival port
@app.route('/DAsearchresults', methods=['GET', 'POST'])
def DAsearchresults():
	Arrival_port = request.form['DA'] #request input DA
	cursor = conn.cursor(); #used to execute SQL commands
	query = 'SELECT * FROM flights WHERE Arrival_port = %s' #Query for data collection
	data = cursor.execute(query, (Arrival_port))
	if (data):
		flightData = cursor.fetchall()
		cursor.close()
		return render_template('searchresults.html', flightData = flightData)
	else:
		cursor.close()
		return render_template('searcherror.html')
#flight search execution with Depart date
@app.route('/DDsearchresults', methods=['GET', 'POST'])
def DDsearchresults():
	Depart_date = request.form['DD'] #request input DA
	cursor = conn.cursor(); #used to execute SQL commands
	query = 'SELECT * FROM flights WHERE Depart_date = %s' #Query for data collection
	data = cursor.execute(query, (Depart_date))
	if (data):
		flightData = cursor.fetchall()
		cursor.close()
		return render_template('searchresults.html', flightData = flightData)
	else:
		cursor.close()
		return render_template('searcherror.html')

#flight search execution for Round Trip
@app.route('/RTsearchresults', methods=['GET', 'POST'])
def RTsearchresults():
	Depart_date = request.form['DD'] #request input
	cursor = conn.cursor(); #used to execute SQL commands
	query = 'SELECT * FROM flights WHERE Depart_date = %s' #Query 
	data = cursor.execute(query, (Depart_date))
	if (data) :
		DepartData = cursor.fetchall()
		cursor.close()
		return render_template('RTresults.html', DepartData = DepartData)
	else:
		cursor.close()
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
	if (data1)  and (data2) :
		DepartData = cursor1.fetchall()
		ReturnData = cursor2.fetchall()
		cursor1.close()
		cursor2.close()
		return render_template('RTFinal.html', DepartData = DepartData, ReturnData = ReturnData)
	else:
		cursor1.close()
		cursor2.close()
		return render_template('searcherror.html')

#flight search execution for Round Trip

@app.route('/critique_sub', methods=['GET', 'POST'])
def critique_sub():
	#grabs information from the forms
	username = session['username']
	f_num = request.form['f_num']
	rating = request.form['rating']
	comment = request.form['comment']
	
	
	#cursor used to send queries
	cursor = conn.cursor()

	query = 'SELECT * FROM flights, ticket WHERE ticket.Flight_num = %s and Cust_Email = %s'
	cursor.execute(query, (f_num, username))
	data = cursor.fetchone()
	query = 'SELECT * FROM critiques WHERE Cust_addy = %s'
	cursor.execute(query, (username))
	spam = cursor.fetchone()
	message = None
	if (spam) and (data):
		cursor.close()
		message = "You've already left a review for this flight, please select another and click the 'Refresh' button to reload the table."
		return render_template('pastflights.html', message=message)
	elif (spam) and not (data):
		cursor.close()
		message = "You've not taken this flight, please select another and click the 'Refresh' button to reload the table."
		return render_template('pastflights.html', message=message)
	elif not (data) and not (spam):
		cursor.close()
		message = "We couldn't find a flight with this Flight Number, please try again"
		return render_template('pastflights.html', message=message)
	else:
		
		ins = 'INSERT INTO critiques VALUES (%s, %s, %s, %s)'
		cursor.execute(ins, (username, f_num, rating, comment))
		conn.commit()
		cursor.close()
		message = 'Your review has been submitted and will be reviewed as soon as possible. Thank you!'
		return render_template('home.html', message=message)


@app.route('/reloadCrit', methods=['GET', 'POST'])
def refreshCrit():
	return redirect(url_for('pastflights'))


#Authenticates the login
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
	cursor.close()
	if (data):
		return render_template('pastflights.html', username=username, data=data)
	else:
		return render_template('pastflights.html')

#Customer views up coming flights for purchase
@app.route('/available', methods=['GET','POST'])
def available():
	curr_date = date.today()
	cursor = conn.cursor(); #used to execute SQL commands
	query = 'SELECT * FROM flights WHERE Depart_date > %s' #Query for data collection
	data = cursor.execute(query, (curr_date))
	if (data):
		data = cursor.fetchall()
		cursor.close()
		return render_template('available.html', data = data)
	else:
		cursor.close()
		return render_template('available.html')

@app.route('/yearPurchases', methods=['GET', 'POST'])
def yearPurchases():
	username = session['username']
	curr_date = date.today()
	yr_date = date.today() - timedelta(days = 365)
	cursor = conn.cursor()
	query = 'SELECT ROUND(AVG(Sold_Price),2) FROM ticket, flights WHERE Cust_Email = %s AND Depart_date > %s AND Depart_date < %s'
	cursor.execute(query, (username, yr_date, curr_date))
	data = cursor.fetchone()
	cursor.close()
	if (data):
		return render_template('yearPurchases.html', username=username, data=data)
	else:
		return render_template('yearPurchases.html', username=username)

@app.route('/fixedTable', methods=['GET', 'POST'])
def fixedTable():
	username = session['username']
	curr_date = date.today()
	hyear_date = date.today() - timedelta(days = 182)
	cursor = conn.cursor()
	query = 'SELECT Sold_Price FROM ticket NATURAL JOIN flights WHERE Cust_Email = %s AND Depart_date > %s AND Depart_date < %s'
	cursor.execute(query, (username, hyear_date, curr_date))
	data = cursor.fetchall()
	if (data):
		cursor.close()
		return render_template('fixedTable.html', username=username, data=data)
	else:
		return render_template('fixedTable.html', username=username)

@app.route('/pickRangeP', methods=['GET', 'POST'])
def pickRangeP():
	return render_template('rangedPurchases.html', username=session['username'])

@app.route('/rangedPurchases', methods=['GET', 'POST'])
def rangedPurchases():
	username = session['username']
	hyr_date = request.form['hyr_date']
	yr_date = request.form['yr_date']
	cursor = conn.cursor()
	query = 'SELECT ROUND(AVG(Sold_Price),2) FROM ticket, flights WHERE Cust_Email = %s AND Depart_date > %s AND Depart_date < %s'
	data = cursor.execute(query, (username, hyr_date, yr_date))
	cursor.close()
	if (data != NULL):
		return render_template('rangedResults.html', username=username, data=data, yr_date=yr_date, hyr_date=hyr_date)
	else:
		return render_template('rangedResults.html', username=username, yr_date = yr_date, hyr_date = hyr_date)


@app.route('/homestaff')
def homestaff():
	username=session['username']
	return render_template('homestaff.html', username=username)

		
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


@app.route('/logout')
def logout():
	session.pop('username')
	return redirect('/')
		
app.secret_key = 'some key that you will never guess'
#Run the app on localhost port 5000
#debug = True -> you don't have to restart flask
#for changes to go through, TURN OFseaF FOR PRODUCTION
if __name__ == "__main__":
	app.run('127.0.0.1', 5000, debug = True)