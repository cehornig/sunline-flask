from flask import Flask, render_template, request
import json
from markupsafe import escape
from convert import *
app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/about')
def about():
    base = request.base_url
    return render_template('about.html', base=base)

@app.route('/api/<lat>/<long>')
def api(lat, long):
    data = get_sun_coords(escape(lat), escape(long))
    return json.dumps(data)

@app.route('/api/date/<lat>/<long>/<date>')
def api_date(lat, long, date):
    data = get_sun_coords(escape(lat), escape(long), escape(date))
    return json.dumps(data)
