    # Import the dependencies.
from flask import Flask, jsonify
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func
import datetime as dt
import pandas as pd
import numpy as np

#################################################
# Database Setup
#################################################

    # Create an engine to connect to the SQLite database
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

    # reflect an existing database into a new model
Base = automap_base()

    # reflect the tables
Base.prepare(autoload_with=engine)

    # Save references to each table
Measurement = Base.classes.measurement
Station = Base.classes.station

    # Create our session (link) from Python to the DB
session = Session(engine)

#################################################
# Flask Setup
#################################################

app = Flask(__name__)

    # Create our session (link) from Python to the DB
session = Session(engine)

#################################################
# Flask Routes
#################################################

    # Define the homepage route
@app.route("/")
def welcome():
    """List all available API routes."""
    return (
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/<start><br/>"
        f"/api/v1.0/<start>/<end><br/>"
    )

    # Define the precipitation route
@app.route("/api/v1.0/precipitation")
def precipitation():
    """Return a JSON representation of precipitation data for the last 12 months."""
    try:
        # Calculate the date 1 year ago from the last data point in the database
        most_recent_date = session.query(func.max(Measurement.date)).scalar()
        one_year_ago = (pd.to_datetime(most_recent_date) - pd.DateOffset(years=1)).strftime('%Y-%m-%d')

        # Query for the last 12 months of precipitation data
        precipitation_data = session.query(Measurement.date, Measurement.prcp).filter(Measurement.date >= one_year_ago).all()

        # Convert query results to a dictionary
        precipitation_dict = {date: prcp for date, prcp in precipitation_data}

        # Return the JSON representation of the dictionary
        return jsonify(precipitation_dict)

    except Exception as e:
        return jsonify({"error": str(e)}), 500

    # Define the stations route
@app.route("/api/v1.0/stations")
def stations():
    """Return a JSON list of stations."""
    try:
        # Query all stations
        results = session.query(Station.station, Station.name, Station.latitude, Station.longitude, Station.elevation).all()

        # Convert list of tuples into list of dictionaries
        stations_list = [{"station": station, "name": name, "latitude": lat, "longitude": lon, "elevation": elev}
                         for station, name, lat, lon, elev in results]

        # Return the JSON list of stations
        return jsonify(stations_list)

    except Exception as e:
        return jsonify({"error": str(e)}), 500

    # Define the temperature observations route
@app.route("/api/v1.0/tobs")
def tobs():
    """Return a JSON list of temperature observations for the last year of the most active station."""
    try:
        # Calculate the date 1 year ago from the last data point in the database
        most_recent_date = session.query(func.max(Measurement.date)).scalar()
        one_year_ago = (pd.to_datetime(most_recent_date) - pd.DateOffset(years=1)).strftime('%Y-%m-%d')

        # Query the dates and temperature observations of the most active station for the last year of data
        most_active_station_id = 'USC00519281'  # Replace with the actual most active station ID if known
        results = session.query(Measurement.date, Measurement.tobs).filter(
            Measurement.station == most_active_station_id).filter(
            Measurement.date >= one_year_ago).all()

        # Convert list of tuples into list of dictionaries
        tobs_list = [{"date": date, "temperature": tobs} for date, tobs in results]

        # Return the JSON list of temperature observations
        return jsonify(tobs_list)

    except Exception as e:
        return jsonify({"error": str(e)}), 500

    # Define the temperature range routes
@app.route("/api/v1.0/<start>")
@app.route("/api/v1.0/<start>/<end>")
def temperature_range(start, end=None):
    """Return TMIN, TAVG, TMAX for all dates >= start date or between start and end date inclusive."""
    try:
        # Variables for reference to temperature calculations
        sel = [func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)]

        if end:
            # If an end date is provided
            results = session.query(*sel).filter(Measurement.date >= start).filter(Measurement.date <= end).all()
        else:
            # If no end date is provided
            results = session.query(*sel).filter(Measurement.date >= start).all()

        # Convert list of tuples into list of dictionaries
        temps = [{"TMIN": tmin, "TAVG": round(tavg, 2), "TMAX": tmax} for tmin, tavg, tmax in results]

        # Return the JSON list of temperature statistics
        return jsonify(temps)

    except Exception as e:
        return jsonify({"error": str(e)}), 500
                      
    # Run the Flask app
if __name__ == '__main__':
    app.run(debug=False)

    # Close the session when the script terminates
@app.teardown_appcontext
def shutdown_session(exception=None):
    session.close()