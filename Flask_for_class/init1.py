#Import Flask Library

from flask import Flask, render_template, request, session, url_for, redirect
from pymysql import NULL
from datetime import datetime, timedelta, date
import pymysql.cursors
# CHANGE
import random

#Initialize the app from Flask
app = Flask(__name__,template_folder='templates')

#Configure MySQL                                                        
conn = pymysql.connect(host='localhost',
					   port=3306,
                       user='root',
                       password='letmein',
                       db='flight_reservation',
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

#CHANGE
@app.route('/reloadPS')
def reloadPS():
	return redirect(url_for('purchase_search'))

# CHANGES BELOW 
@app.route('/home')
def home():
	username = session['username']
	#pulls user's name for display
	cursor = conn.cursor()
	query = 'SELECT Cust_name FROM customer WHERE Email_Address=%s'
	cursor.execute(query,(username))
	user_name = cursor.fetchone()['Cust_name']
	return render_template('home.html',username=user_name)

@app.route('/homestaff')
def homestaff():
	username=session['username']
	return render_template('homestaff.html')

#flight search feature page
@app.route('/flightsearch') #at url directory flight search
def flightsearch():         #display flight search page
	return render_template('flightsearch.html')

#CHANGE: Link to Purchase Feature Page
@app.route('/purchase_page')
def purchase_page():
	username = session['username']
	return render_template('purchase_page.html')

#CHANGE: Link to Search for Flight to Purchase a Ticket
@app.route('/purchase_search')
def purchase_search():
	username = session['username']
	#pulls available airport info
	cursor_port = conn.cursor()
	query_port = 'SELECT * FROM airport'
	cursor_port.execute(query_port)
	airport = cursor_port.fetchall()
	return render_template('purchase_search.html',airport=airport)
#CHANGE: Link to Cancel Page
@app.route('/cancel_page')
def cancel_page():
	username = session['username']
	cursor=conn.cursor()
	query = 'SELECT * FROM ticket NATURAL JOIN flights WHERE Cust_Email=%s AND Depart_date>CURDATE()'
	cursor.execute(query,(username))
	ticket_list = cursor.fetchall()
	cursor.close()
	return render_template('cancel_page.html',ticket_list=ticket_list)
#CHANGE: STAFF -> Link to View Flights Page
@app.route('/viewflights')
def viewflights():
	username = session['username']
	#pulls available airport info
	cursor_port = conn.cursor()
	query_port = 'SELECT * FROM airport'
	cursor_port.execute(query_port)
	airport = cursor_port.fetchall()
	conn.commit()
	#gets airline name of staff
	cursor = conn.cursor()
	query_airname = 'SELECT Airline_name FROM airline_staff WHERE Username=%s'
	cursor.execute(query_airname,(username))
	airline = cursor.fetchone()["Airline_name"]
	conn.commit()
	#default
	query_allflights = 'SELECT * FROM flights WHERE Airline_name=%s AND Depart_date BETWEEN CURDATE() AND DATE_ADD(CURDATE(),INTERVAL 30 DAY)'
	cursor.execute(query_allflights,(airline))
	flightData = cursor.fetchall()
	return render_template('viewflights.html',airport=airport,flightData=flightData)

#CHANGE: STAFF -> Links to Date Range
@app.route('/specify_flights')
def specify_flights():
	username = session['username']
	#pulls available airport info
	cursor_port = conn.cursor()
	query_port = 'SELECT * FROM airport'
	cursor_port.execute(query_port)
	airport = cursor_port.fetchall()
	conn.commit()
	#gets airline name of staff
	cursor = conn.cursor()
	query_airname = 'SELECT Airline_name FROM airline_staff WHERE Username=%s'
	cursor.execute(query_airname,(username))
	airline = cursor.fetchone()["Airline_name"]
	conn.commit()
	#find qualifying source airports
	cursor = conn.cursor()
	Scity_airport = request.form.get('Scity_port')
	query_port = 'SELECT Port_name FROM airport WHERE Port_name=%s or City=%s'
	cursor.execute(query_port,(Scity_airport,Scity_airport))
	Sairport = cursor.fetchall()
	conn.commit()
	#find qualifying destination airports
	Dcity_airport = request.form.get('Dcity_port')
	cursor.execute(query_port,(Dcity_airport,Dcity_airport))
	Dairport = cursor.fetchall()
	conn.commit()
	#recover from & to date
	ddate = request.form['ddate']
	rdate = request.form['rdate']
	#create view with all possible depart airports (this is for a natural join with flights)
	query_sourceair = 'CREATE VIEW source_air AS SELECT Port_name as Depart_port FROM airport WHERE Port_name=%s or City=%s'
	query_destair = 'CREATE VIEW dest_air AS SELECT Port_name as Arrival_port FROM airport WHERE Port_name=%s or City=%s'
	cursor.execute(query_sourceair,(Scity_airport,Scity_airport))
	conn.commit()
	cursor.execute(query_destair,(Dcity_airport,Dcity_airport))
	conn.commit()
	if(rdate):
		b = datetime.strptime(rdate,"%Y-%m-%d")
		query_outflights = 'SELECT * FROM flights NATURAL JOIN source_air NATURAL JOIN dest_air WHERE Depart_date BETWEEN %s AND %s' #>=%s and Depart_date<=%s'
		cursor.execute(query_outflights,(ddate,rdate))
		outflights = cursor.fetchall()
		conn.commit()
		#fetches possible returning flights
		query_Rsourceair = 'ALTER VIEW source_air AS SELECT Port_name as Arrival_port FROM airport WHERE Port_name=%s or City=%s'
		query_Rdestair = 'ALTER VIEW dest_air AS SELECT Port_name as Depart_port FROM airport WHERE Port_name=%s or City=%s'
		query_inflights = 'SELECT * FROM flights NATURAL JOIN source_air NATURAL JOIN dest_air WHERE Depart_date>=%s'
		cursor.execute(query_Rsourceair,(Scity_airport,Scity_airport))
		conn.commit()
		cursor.execute(query_Rdestair,(Dcity_airport,Dcity_airport))
		conn.commit()
		cursor.execute(query_inflights,(rdate))
		inflights = cursor.fetchall()
		conn.commit()
		#drops views
		query_dropS = 'DROP VIEW source_air'
		cursor.execute(query_dropS)
		conn.commit()
		query_dropD = 'DROP VIEW dest_air'
		cursor.execute(query_dropD)
		conn.commit()
		#error cases
		error=None
		#checks the depart date for correct input
		if(a<datetime.today()):
			error='Please try another depart date. Hit Reload and try again'
			return render_template('purchase_search.html',error=error)
		#checks the return date for correct input
		elif(b<=datetime.today() or b<a):
			error='Please try another return date. Hit Reload and try again'
			return render_template('purchase_search.html',error=error)
		elif(len(outflights)==0):
			error='There are no available outgoing flights for the date(s). Please hit Reload and try again'
			return render_template('purchase_search.html',error=error)
		elif(len(inflights)==0):
			error='There are no available return flights for these dates. Please hit Reload and try again'
			return render_template('purchase_search.html',error=error)
		return render_template('purchase_page.html',outflights=outflights,inflights=inflights)
	return render_template('daterange_flights.html')

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
#Edge Cases for registration (cust and staff):
    # If entered foreign key doesnt exists, output error 
	# preventing page crash with error
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
	dob =      request.form['staff_dob']
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
		
@app.route('/post', methods=['GET', 'POST'])
def post():
	username = session['username']
	# cursor = conn.cursor();
	# blog = request.form['blog']
	# query = 'INSERT INTO blog (blog_post, username) VALUES(%s, %s)'
	# cursor.execute(query, (blog, username))
	# conn.commit()
	# cursor.close()
	return redirect(url_for('home'))
#CHANGE returns flights that match user's input 
@app.route('/search_purchase', methods=['GET','POST'])
def search_purchase():
	username = session['username']
	#find qualifying source airports
	cursor = conn.cursor()
	Scity_airport = request.form.get('Scity_port')
	query_port = 'SELECT Port_name FROM airport WHERE Port_name=%s or City=%s'
	cursor.execute(query_port,(Scity_airport,Scity_airport))
	Sairport = cursor.fetchall()
	conn.commit()
	#find qualifying destination airports
	Dcity_airport = request.form.get('Dcity_port')
	cursor.execute(query_port,(Dcity_airport,Dcity_airport))
	Dairport = cursor.fetchall()
	conn.commit()
	#recover depart & return date
	ddate = request.form['ddate']
	rdate = request.form['rdate']
	a = datetime.strptime(ddate,"%Y-%m-%d")
	#uses aquired data to find available flights
	#create view with all possible depart airports (this is for a natural join with flights)
	query_sourceair = 'CREATE VIEW source_air AS SELECT Port_name as Depart_port FROM airport WHERE Port_name=%s or City=%s'
	query_destair = 'CREATE VIEW dest_air AS SELECT Port_name as Arrival_port FROM airport WHERE Port_name=%s or City=%s'
	cursor.execute(query_sourceair,(Scity_airport,Scity_airport))
	conn.commit()
	cursor.execute(query_destair,(Dcity_airport,Dcity_airport))
	conn.commit()
	#if round trip
	if(rdate):
		b = datetime.strptime(rdate,"%Y-%m-%d")
		query_outflights = 'SELECT * FROM flights NATURAL JOIN source_air NATURAL JOIN dest_air WHERE Depart_date BETWEEN %s AND %s' #>=%s and Depart_date<=%s'
		cursor.execute(query_outflights,(ddate,rdate))
		outflights = cursor.fetchall()
		conn.commit()
		#fetches possible returning flights
		query_Rsourceair = 'ALTER VIEW source_air AS SELECT Port_name as Arrival_port FROM airport WHERE Port_name=%s or City=%s'
		query_Rdestair = 'ALTER VIEW dest_air AS SELECT Port_name as Depart_port FROM airport WHERE Port_name=%s or City=%s'
		query_inflights = 'SELECT * FROM flights NATURAL JOIN source_air NATURAL JOIN dest_air WHERE Depart_date>=%s'
		cursor.execute(query_Rsourceair,(Scity_airport,Scity_airport))
		conn.commit()
		cursor.execute(query_Rdestair,(Dcity_airport,Dcity_airport))
		conn.commit()
		cursor.execute(query_inflights,(rdate))
		inflights = cursor.fetchall()
		conn.commit()
		#drops views
		query_dropS = 'DROP VIEW source_air'
		cursor.execute(query_dropS)
		conn.commit()
		query_dropD = 'DROP VIEW dest_air'
		cursor.execute(query_dropD)
		conn.commit()
		#error cases
		error=None
		#checks the depart date for correct input
		if(a<datetime.today()):
			error='Please try another depart date. Hit Reload and try again'
			return render_template('purchase_search.html',error=error)
		#checks the return date for correct input
		elif(b<=datetime.today() or b<a):
			error='Please try another return date. Hit Reload and try again'
			return render_template('purchase_search.html',error=error)
		elif(len(outflights)==0):
			error='There are no available outgoing flights for the date(s). Please hit Reload and try again'
			return render_template('purchase_search.html',error=error)
		elif(len(inflights)==0):
			error='There are no available return flights for these dates. Please hit Reload and try again'
			return render_template('purchase_search.html',error=error)
		return render_template('purchase_page.html',outflights=outflights,inflights=inflights)
	else: #one way trip
		query_outflights = 'SELECT * FROM flights NATURAL JOIN source_air NATURAL JOIN dest_air WHERE Depart_date>=%s'
		cursor.execute(query_outflights,(ddate))
		outflights = cursor.fetchall()
		conn.commit()
		#drops views
		query_dropS = 'DROP VIEW source_air'
		cursor.execute(query_dropS)
		conn.commit()
		query_dropD = 'DROP VIEW dest_air'
		cursor.execute(query_dropD)
		conn.commit()
		#error cases
		error=None
		#checks the depart date for correct input
		if(a<datetime.today()):
			error='Please try another depart date. Hit Reload and try again'
			return render_template('purchase_search.html',error=error)
		elif(len(outflights)==0):
			error='There are no available outgoing flights for the date(s). Please hit Reload and try again'
			return render_template('purchase_search.html',error=error)
	return render_template('purchase_page.html',outflights=outflights)

# CHANGE: checks list of tuples (returned from fetchall()) & returns
#         non existant #
def generate_tickID(flightID_results):
	flag=True
	i=0
	while(flag):
		id=random.randrange(10000,100000)
		for x in flightID_results:
			if(x==id):
				i+=1
		if(i==0):
			flag=False
	return id

#CHANGE
# tell them flight ID_num doesnt match any of the tickets
# can improve by having it remove flight from being available to select
@app.route('/purchase', methods=['GET','POST'])
def purchase():
	username = session['username']
	#gets date from database call
	cursor=conn.cursor()
	cursor_seats=conn.cursor()
	cursor_tseats=conn.cursor()
	cursor_airline=conn.cursor()
	#grabs data for outgoing flight
	flight_str = str(request.form.get('outflights'))
	flight=flight_str.split(',')
	flight_num = flight[0]
	ID_num = flight[1]
	price = flight[2]
	flight_ddate = flight[3]
	flight_dtime = flight[4]
	
	#queries (except for taken seats)
	query='SELECT Ticket_ID FROM ticket'
	query_seat='SELECT Seat_Amount FROM airplanes WHERE ID=%s'
	query_airline='SELECT Airline_name FROM flights WHERE Flight_num=%s and Depart_date=%s and Depart_time=%s'
	#execution
	cursor.execute(query)
	cursor_seats.execute(query_seat,(ID_num))
	cursor_airline.execute(query_airline,(flight_num,flight_ddate,flight_dtime))
	#grab data & save into var (these return dictionaires)
	data_IDs = cursor.fetchall() 
	data_seat=cursor_seats.fetchone()
	data_airline=cursor_airline.fetchone()
	airline_name = data_airline['Airline_name']
	#grabs taken seats now that airline is known
	query_tseats='SELECT COUNT(*) FROM ticket WHERE Flight_num=%s and Airline_Name=%s'
	cursor_tseats.execute(query_tseats,(flight_num,airline_name))
	data_tseats=cursor_tseats.fetchone()
	#checks if there are any spots available
	error=None
	if(data_seat==data_tseats):
		error = 'There are no longer any available seats on this flight. Please select another flight'
		return render_template('home.html', username=username,error = error)
	# gets data from form filled out by user
	ticket_id=generate_tickID(data_IDs)
	ticket_class = request.form['ticket_class']
	card_type = request.form['card_type']
	card_name = request.form['card_name']
	card_exp = request.form['exp_date']
	card_num = request.form['card_number']
	#recalculates price of ticket
	price = float(price)
	if(ticket_class=='First'):
		price+=432
	elif(ticket_class=='Business'):
		price+=201
	#insertions
	ins = 'INSERT INTO ticket VALUES(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)'
	cursor.execute(ins, (flight_num, ticket_id, username,    
				       ticket_class, airline_name, price,
					   card_type, card_name, card_exp, card_num))
	conn.commit()
	#if round trip (returning flight)
	inflight_str = request.form.get('inflights')
	if(inflight_str!=None):
		#captures data on inflight
		inflight_str = str(inflight_str)
		inflight = inflight_str.split(',')
		inflight_num = inflight[0]
		inflightID_num = inflight[1]
		inflightprice = inflight[2]
		inflight_ddate = inflight[3]
		inflight_dtime = inflight[4]
		#fetchs airline name
		cursor.execute(query_airline,(inflight_num,inflight_ddate,inflight_dtime))
		inflight_airline = cursor.fetchone()['Airline_name']
		#provides another ticket id for returning flight
		flag = True
		while(flag):
			inticket_id = generate_tickID(data_IDs)
			if(inticket_id!=ticket_id):
				flag=False
		#recalculates price of ticket
		inflightprice = float(inflightprice)
		if(ticket_class=='First'):
			inflightprice+=432
		elif(ticket_class=='Business'):
			inflightprice+=201
		#insertion
		ins = 'INSERT INTO ticket VALUES(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)'
		cursor.execute(ins, (inflight_num, inticket_id, username,    
				       ticket_class, inflight_airline, inflightprice,
					   card_type, card_name, card_exp, card_num))
		conn.commit()
	cursor.close()
	cursor_seats.close()
	cursor_tseats.close()
	cursor_airline.close()
	return redirect(url_for('home'))
#CHANGE
@app.route('/cancel', methods=['GET','POST'])
def cancel():
	username = session['username']
	#gets date from database call
	cursor=conn.cursor()
	#gets data from select
	tikID = str(request.form.get('tickets'))
	query = 'DELETE FROM ticket WHERE Ticket_ID=%s'
	cursor.execute(query,(tikID))
	conn.commit()
	cursor.close()	
	return redirect(url_for('home'))

#CHANGE: STAFF -> Conducts flight search within an airline
@app.route('/staff_view', methods=['GET','POST'])
def staff_view():
	username = session['username']
	#gets airline name of staff
	cursor = conn.cursor()
	query_airname = 'SELECT Airline_name FROM airline_staff WHERE Username=%s'
	cursor.execute(query_airname,(username))
	airline = cursor.fetchone()
	conn.commit()
	#default
	query_allflights = 'SELECT * FROM flights WHERE Airline_name=%s AND Depart_date BETWEEN CURDATE() AND DATE_ADD(CURDATE(),INTERVAL 30 DAY)'
	
	cursor.execute(query_allflights,(airline))
	#find qualifying source airports
	cursor = conn.cursor()
	Scity_airport = request.form.get('Scity_port')
	query_port = 'SELECT Port_name FROM airport WHERE Port_name=%s or City=%s'
	cursor.execute(query_port,(Scity_airport,Scity_airport))
	Sairport = cursor.fetchall()
	conn.commit()


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
