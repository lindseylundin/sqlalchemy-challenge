# Dependencies and Setup
import numpy as np
import datetime as dt
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func
from flask import Flask, jsonify


# Database Setup
engine = create_engine('sqlite:///Resources/hawaii.sqlite')

# Reflect existing database into new model
Base = automap_base()

# Reflect the tables
Base.prepare(engine, reflect=True)


# Save reference to the table
Measurement = Base.classes.measurement
Station = Base.classes.station

# Flask Setup
app = Flask(__name__)

# Flask Routes
@app.route("/")
def welcome():
    # List all available api routes.
    return (
        f"Available API Routes<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/choose_start_date <br/>"
        f"/api/v1.0/choose_start_date/choose_end_date"
    )



@app.route("/api/v1.0/precipitation")
def date_prcp():
    # Create our session (link) from Python to the Data Base (DB)
    session = Session(engine)
    
    # Query all dates and precipitation values
    results = session.query(Measurement.date, Measurement.prcp).all()
    
    session.close()
    
     # Convert the query results to a dictionary using date as the key and prcp as the value.
    all_date_prcp = []
    for date, prcp in results:
        date_prcp_dict = {date:prcp}
        all_date_prcp.append(date_prcp_dict)

    # Return the JSON representation of your dictionary.
    return jsonify(all_date_prcp)



@app.route('/api/v1.0/stations')
def stations():
    # Create session link from Python to DB
    session = Session(engine)
    
    # Query all station names
    results = session.query(Station.station, Station.name).all()
    
    session.close()
    
    # Create list of stations 
    all_stations = []
    for row in results:
        all_stations.append(row)

    # Return a JSON list of stations from the dataset.
    return jsonify(all_stations) 



@app.route('/api/v1.0/tobs')
def tobs():
    # Create session link from Python to DB
    session = Session(engine)

    # Find most recent date in measurement table
    last_date = session.query(Measurement.date).order_by(Measurement.date.desc()).first()
    last_date = dt.datetime.strptime(last_date[0], "%Y-%m-%d")
    last_date_format = last_date.date()
    last_date_format.isoformat()

    # Calculate the date one year from the last data in data set
    date_year_ago = last_date - dt.timedelta(days=365)
    date_year_ago_format = date_year_ago.date()
    date_year_ago_format.isoformat()

    # Find the most active station
    active_station = session.query(Station.station,Station.name,func.count(Measurement.station)).\
              filter(Measurement.station == Station.station).group_by(Station.station).\
                  order_by(func.count(Measurement.station).desc()).first()
    most_active = active_station[0]

    # Query the dates and temperature observations of the most active station for the last year of data.
    results = session.query(Measurement.date, Measurement.tobs).\
              filter(Measurement.date >= date_year_ago).\
                  filter(Measurement.station == most_active).all()
    
    session.close()

    # Create list of temperature observations 
    all_tobs = []
    for date,tobs in results:
        date_tobs_dict = {date:tobs}
        all_tobs.append(date_tobs_dict)
    
    # Return a JSON list of temperature observations (TOBS) for the previous year.
    return jsonify(all_tobs)  



@app.route('/api/v1.0/<start_date>')
def start_date(start_date):
    # Create session link from Python to DB
    session = Session(engine)

    # Query min, max, and avg temperatures from start date to most recent date
    min_temp = session.query(func.min(Measurement.tobs)).\
        filter(Measurement.date >= start_date).all()[0][0]
    max_temp = session.query(func.max(Measurement.tobs)).\
        filter(Measurement.date >= start_date).all()[0][0]
    avg_temp = round(session.query(func.avg(Measurement.tobs)).\
        filter(Measurement.date >= start_date).all()[0][0],2)

    session.close()

    # Create list with min, max, and avg temp for given range beginning with provided start date
    all_temp = [{'Min Temp':min_temp},{'Max Temp':max_temp},{'Avg Temp':avg_temp}]
  
    # Return a JSON list of temps we queried
    return jsonify(all_temp)



@app.route('/api/v1.0/<start_date>/<end_date>')
def start_end(start_date,end_date):
    
    # Create session link from Python to DB
    session = Session(engine)
 
    # Query min, max, and avg temperatures from start date to end date
    min_temp = session.query(func.min(Measurement.tobs)).\
        filter(Measurement.date >= start_date).\
            filter(Measurement.date <= end_date).all()[0][0]
    max_temp = session.query(func.max(Measurement.tobs)).\
        filter(Measurement.date >= start_date).\
            filter(Measurement.date <= end_date).all()[0][0]
    avg_temp = round(session.query(func.avg(Measurement.tobs)).\
        filter(Measurement.date >= start_date).\
            filter(Measurement.date <= end_date).all()[0][0],2)

    session.close()

    # Create list with min, max, and avg temp for given range beginning with provided start date and end date
    all_temp = [{'Min Temp':min_temp},{'Max Temp':max_temp},{'Avg Temp':avg_temp}]

    # Return a JSON list of the temps we queried
    return jsonify(all_temp)


if __name__ == '__main__':
    app.run(debug=True)