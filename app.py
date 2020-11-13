import numpy as np
import datetime as dt
import pandas as pd

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

from flask import Flask, jsonify

#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(engine, reflect=True)

# Save reference to the table
measurement = Base.classes.measurement
station = Base.classes.station

session = Session(engine)
#################################################
# Flask Setup
#################################################
app = Flask(__name__)


#################################################
# Flask Routes
#################################################
@app.route("/")
def home():
    return (
        f"Hawaii Climate Analysis Home Page<br/>"
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/temp/start/end"
     )

@app.route("/api/v1.0/precipitation")
def precip():
    """Return the precipitation data for the last year"""
    latest_date = session.query(measurement.date).order_by(measurement.date.desc()).first()[0]
    query_date = dt.datetime.strptime(latest_date , '%Y-%m-%d') - dt.timedelta(days=365)
    
    results = session.query(measurement.prcp, measurement.date).\
                filter(measurement.date >= query_date).all()


    # Create a dictionary from the row data and append to a list of all_passengers
    precip = {date: prcp for date, prcp in results}

    return jsonify(precip)


@app.route("/api/v1.0/stations")
def stations():
    """Return a list of stations."""
    results = session.query(station.station).all()

    stations = list(np.ravel(results))
    return jsonify(stations)


@app.route("/api/v1.0/tobs")
def tobs():
    """Return the temperature observations for the last year."""
    latest_date = session.query(measurement.date).order_by(measurement.date.desc()).first()[0]
    last_year = dt.datetime.strptime(latest_date , '%Y-%m-%d') - dt.timedelta(days=365)

    results = session.query(measurement.tobs).\
        filter(measurement.station == 'USC00519281').\
        filter(measurement.date >= last_year).all()

    temps = list(np.ravel(results))

    return jsonify(temps=temps)


@app.route("/api/v1.0/<start>")
@app.route("/api/v1.0/<start>/<end>")
def summary(start=None, end=None):
    """Return Temperature Min, Max, and Avg."""
    
    sel = [func.min(measurement.tobs), func.avg(measurement.tobs), func.max(measurement.tobs)]

    if not end:
        results = session.query(*sel).\
            filter(measurement.date >= start).all()

        temps = list(np.ravel(results))
        return jsonify(temps)

    results = results = session.query(*sel).\
            filter(measurement.date >= start).\
            filter(measurement.date <= end).all()

    temps = list(np.ravel(results))
    return jsonify(temps=temps)

if __name__ == "__main__":
    app.run()
