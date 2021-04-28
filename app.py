# Test commit
from flask import Flask
from flask import render_template
import json
from markupsafe import escape
from convert import *
app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/api/<lat>/<long>')
def api(lat, long):
    data = get_sun_coords(escape(lat), escape(long))
    return json.dumps(data)

@app.route('/api/<lat>/<long>/<date>')
def api_date(lat, long, date):
    data = get_sun_coords(escape(lat), escape(long), escape(date))
    return json.dumps(data)
