# Utilities for retrieving altitude and azimuth from longitude and latitude

from pysolar.solar import *
import datetime
import requests
import math
try:
    import pytz
except:
    pytz = None

from timezonefinder import TimezoneFinder
from pytz import timezone

# For optional datetime
# https://stackoverflow.com/questions/9539921/how-do-i-create-a-python-function-with-optional-arguments#:~:text=After%20the%20required%20positional%20arguments,specific%20optional%20arguments%20by%20name.&text=Just%20use%20the%20*args%20parameter,a%20%22way%22%20of%20overloading.
def get_sun_coords(lat, long, *args):
    lat = float(lat)
    long = float(long)

    if lat > 90 or lat < -90 or long > 180 or long < -180:
        return {"error": "Invalid coordinates"}

    if len(args) > 0:
        dateStr = args[0]
        date = datetime.datetime.strptime(dateStr, '%Y-%m-%d')
    else:
        date = datetime.date.today()

    months = ['January',
              'February',
              'March',
              'April',
              'May',
              'June',
              'July',
              'August',
              'September',
              'October',
              'November',
              'December']

    data = {}
    all_minutes = get_all_minutes_for_date(date)
    counter = 0

    for minute in all_minutes:
        coords = get_sun_coords_for_time(lat, long, minute)
        if "error" in coords:
            return {"error": coords["error"]}

        convertedCoords = convert_coords_to_xyz(coords)
        data[counter] = convertedCoords
        counter += 1

    data["date"] = f"{months[date.month - 1]} {date.day}, {date.year}"
    data["lat"] = str(lat)
    data["long"] = str(long)

    riseSet = get_sunrise_sunset(lat, long, date)

    data['sunrise'] = riseSet['sunrise']
    data['sunset'] = riseSet['sunset']

    day_len_hour = math.floor(riseSet['day_length'])
    day_len_minute = math.floor((riseSet['day_length'] - day_len_hour) * 60)

    day_len_str = str(day_len_hour) + ' hours, ' + str(day_len_minute) + ' minutes'

    data['day_length'] = day_len_str
    return data

def convert_coords_to_xyz(coords):
    azimuth = coords['azimuth']
    altitude = coords['altitude']

    # 3D "globe" radius for trig calculations is an arbitrary constant
    threeDRadius = 100
    alt_in_radians = math.radians(altitude)
    az_in_radians = math.radians(azimuth)
    is_negative = alt_in_radians < 0

    # Trigonometry reminder
    # https://owlcation.com/stem/Everything-About-Triangles-and-More-Isosceles-Equilateral-Scalene-Pythagoras-Sine-and-Cosine
    twoDRadius = threeDRadius * math.cos(alt_in_radians)

    # For 3d
    x = twoDRadius * math.cos(az_in_radians)
    y = twoDRadius * math.sin(az_in_radians)
    z = threeDRadius * math.sin(alt_in_radians)
    return {"x": x,
            "y": y,
            "z": z,
            "timestring": coords['timestring'],
            "isNegative": str(is_negative)}

def get_sun_coords_for_time(lat, long, date):
    tf = TimezoneFinder()

    lat = float(lat)
    long = float(long)

    localTzStr = tf.timezone_at(lng=long, lat=lat)

    if localTzStr == None:
        localTzStr = tf.closest_timezone_at(lng=long, lat=lat, delta_degree=3)

    if localTzStr == None:
        return {"error": "No timezone"}

    localTzObj = pytz.timezone(localTzStr)

    date = localTzObj.localize(date)

    altitude = get_altitude(lat, long, date)
    azimuth = get_azimuth(lat, long, date)

    ampm = "AM" if date.hour < 12 else "PM"
    hour = date.hour if date.hour < 13 else date.hour - 12

    if hour == 0:
        hour = 12

    minute = '00' if date.minute == 0 else date.minute

    timestring = f"{hour}:{minute} {ampm}"
    return { "altitude" : altitude, "azimuth" : azimuth, "timestring":  timestring}

def get_all_minutes_for_date(date):
    all_minutes = []

    #todayDay = todayDay.replace(month=3)
    iterateDate = datetime.datetime(year=date.year,
                              month=date.month,
                              day=date.day,
                              hour=0,
                              minute=0)

    # Using timedelta
    # https://www.geeksforgeeks.org/python-datetime-timedelta-function/
    td = datetime.timedelta(minutes=10)

    while iterateDate.day == date.day:
        all_minutes.append(iterateDate)
        iterateDate = iterateDate + td
    return all_minutes

def get_sunrise_sunset(lat, long, date):
    tf = TimezoneFinder()
    date = str(date)

    # Don't pass pure 0 to SunriseSunset.com
    # It causes an error
    if float(lat) == 0:
        lat = "0.000001"

    if float(long) == 0:
        long = "0.000001"

    apiString = 'https://api.sunrise-sunset.org/json?lat=' + str(lat) + '&lng=' + str(long) + '&date=' + str(date) + '&formatted=0'
    apiData = requests.get(apiString).json()

    localTzStr = tf.timezone_at(lng=float(long), lat=float(lat))

    if localTzStr == None:
        localTzStr = tf.closest_timezone_at(lng=float(long), lat=float(lat), delta_degree=3)

    if localTzStr == None:
        return {"error": "No timezone"}

    localTzObj = pytz.timezone(localTzStr)
    utcTzObj =  pytz.timezone('UTC')

    sunriseStr = apiData['results']['sunrise']
    sunsetStr = apiData['results']['sunset']

    utcSunrise = datetime.datetime.strptime(sunriseStr, '%Y-%m-%dT%H:%M:%S+00:00').replace(tzinfo=utcTzObj)
    utcSunset = datetime.datetime.strptime(sunsetStr, '%Y-%m-%dT%H:%M:%S+00:00').replace(tzinfo=utcTzObj)

    # Convert to local timezone
    # https://stackoverflow.com/questions/10997577/python-timezone-conversion
    sunrise = utcSunrise.astimezone(localTzObj)
    sunset = utcSunset.astimezone(localTzObj)

    sunrise = get_nice_datestring(sunrise)
    sunset = get_nice_datestring(sunset)

    day_length = float(apiData['results']['day_length']) / (60 * 60)
    return {"sunrise": sunrise, "sunset": sunset, "day_length": day_length}

def get_nice_datestring(date):
    ampm = "AM" if date.hour < 12 else "PM"
    hour = date.hour if date.hour < 13 else date.hour - 12

    if hour == 0:
        hour = 12

    minute = '00' if date.minute == 0 else date.minute

    if date.minute < 10:
        minute = '0' + str(date.minute)

    timestring = f"{hour}:{minute} {ampm}"
    return timestring
