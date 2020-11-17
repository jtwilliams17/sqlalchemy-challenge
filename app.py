import numpy as np
import datetime as dt
import pandas as pd

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

from flask import Flask, jsonify


engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()
# reflect tables
Base.prepare(engine, reflect=True)

# Table references
Measurement = Base.classes.measurement
Station = Base.classes.station

session = Session(engine)

app = Flask(__name__)

# Flask routes
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
    latest_date = session.query(Measurement.date).order_by(Measurement.date.desc()).first()[0]
    query_date = dt.datetime.strptime(latest_date , '%Y-%m-%d') - dt.timedelta(days=365)
    
    results = session.query(Measurement.prcp, Measurement.date).\
                filter(Measurement.date >= query_date).all()


    # Create a dictionary from the row data and append to a list of all_passengers
    precip = {date: prcp for date, prcp in results}

    return jsonify(precip)


@app.route("/api/v1.0/stations")
def stations():
    """Return a list of stations."""
    results = session.query(Station.station).all()

    stations = list(np.ravel(results))
    return jsonify(stations)


@app.route("/api/v1.0/tobs")
def tobs():
    """Return the temperature observations for the last year."""
    latest_date = session.query(Measurement.date).order_by(Measurement.date.desc()).first()[0]
    last_year = dt.datetime.strptime(latest_date , '%Y-%m-%d') - dt.timedelta(days=365)

    results = session.query(Measurement.tobs).\
        filter(Measurement.station == 'USC00519281').\
        filter(Measurement.date >= last_year).all()

    temps = list(np.ravel(results))

    return jsonify(temps=temps)


@app.route("/api/v1.0/<start>")
@app.route("/api/v1.0/<start>/<end>")
def summary(start=None, end=None):
    """Return Temperature Min, Max, and Avg."""
    
    sel = [func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)]

    if not end:
        results = session.query(*sel).\
            filter(Measurement.date >= start).all()

        temps = list(np.ravel(results))
        return jsonify(temps)

    results = results = session.query(*sel).\
            filter(Measurement.date >= start).\
            filter(Measurement.date <= end).all()

    temps = list(np.ravel(results))
    return jsonify(temps=temps)

if __name__ == "__main__":
    app.run()
