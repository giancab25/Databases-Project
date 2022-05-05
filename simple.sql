CREATE TABLE Airport(
	Port_code		int,
	Port_name		varchar(20),
	City			varchar(20),
	Country			varchar(20),
	Airport_Type	varchar(15),
	PRIMARY KEY(Port_code)
);

CREATE TABLE Customer(
	Cust_name 		 varchar(20),
	Email_Address 	 varchar(40),
	PWD 			 varchar(50),
	Building_Num 	 int,
	Cust_street 	 varchar(20),
	Cust_city 		 varchar(20),
	Cust_state 		 varchar(20),
	Phone_Num 		 char(11),
	Passport_Num	 varchar(9),
	Passport_exp 	 date,
	Passport_Country varchar(20),
	Date_of_birth 	 date,
	PRIMARY KEY (Email_Address)
);

CREATE TABLE Airline(
	Airline_name	varchar(20),
	Port_code		int,
	PRIMARY KEY (Airline_name, Port_code),
	FOREIGN KEY (Port_code) references Airport (Port_code)
);

CREATE TABLE Flights(
	Airline_name	varchar(20),
	Flight_num		int,
	Depart_date		date,
	Depart_time		time,
	Depart_port		varchar(20),
	Arrival_port	varchar(20),
	Arrival_date	date,
	Arrival_time	time,
	Base_price		numeric(5,2),
	ID_num			int,
	Flight_status	varchar(7),
	Avg_rating		int,
	PRIMARY KEY (Airline_name, Flight_num, Depart_date, Depart_time),
	FOREIGN KEY (Airline_name) references Airline (Airline_name)
	INDEX{Flight_num)
);

CREATE TABLE Airline_Staff(
	Username		varchar(20),
	Airline_name	varchar(20),
	PWD				varchar(50),
	First_name		varchar(12),
	Last_name		varchar(12),
	Date_of_Birth 	date,
	PRIMARY KEY (Username, Airline_name),
	FOREIGN KEY (Airline_name) references Airline (Airline_name)
);

CREATE TABLE Staff_Phone_Number(
	Staff_username	varchar(20),
	Phone_Num		char(11),
	PRIMARY KEY (Staff_username, Phone_Num),
	FOREIGN KEY (Staff_username) references  Airline_Staff (Username)
);

CREATE TABLE Airplanes(
	Airline_name		varchar(20),
	ID					varchar(10),
	Seat_amount			int,
	Manufactor_Company	varchar(20),
	Age					int,
	PRIMARY KEY (Airline_name, ID),
	FOREIGN KEY (Airline_name) references Airline (Airline_name)
);

CREATE TABLE Ticket(
	Flight_Num           int,
	Ticket_ID            int,
	Cust_Email           varchar(40),
	Class                varchar(15),
	Airline_Name         varchar(20),
	Sold_Price           numeric(6,2),
	Card_Type            varchar(6),
	Name_on_Card         varchar(36),
	Card_Expiration_Date date,
	PRIMARY KEY (Ticket_ID),
	FOREIGN KEY (Cust_Email) references Customer (Email_Address),
	FOREIGN KEY (Airline_Name) references Airline (Airline_name),
	FOREIGN KEY (Flight_Num) references Flights (Flight_num)
);

/*		Junction table for many-to-many relationship		*/
CREATE TABLE Critiques(
	Cust_addy			varchar(40),
	Flight_num			int,
	Rating				int,
	Comments			varchar(250),
	FOREIGN KEY (Cust_addy) references Customer (Email_Address),
	FOREIGN KEY (Flight_Num) references Flights (Flight_num)
);
