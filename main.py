import io
import tkinter
from typing import TypedDict, List
import requests
from dotenv import dotenv_values
from datetime import datetime
from PIL import Image, ImageTk
import urllib.request


# I used TypeDict to allow the type of location,
# current weather and forecast to be represented precisely.
class Location( TypedDict ):
    lat: int
    lon: int


class CurrentWeather( TypedDict ):
    temperature: float
    feels_like: float
    humidity: float
    wind_speed: float
    clouds: float
    weather_icon: str
    weather_description: str


class Forecast( TypedDict ):
    main: CurrentWeather
    dt_txt: str


def get_location( config, zip_code, country_code ) -> Location:
    r1 = requests.get( 'http://api.openweathermap.org/geo/1.0/zip', params={
        "zip": f"{zip_code},{country_code}",
        "appid": config[ "API_KEY" ],
    } )
    return r1.json()  # Our API response in JSON format.

def get_icon( cod_icon ):
    img_url = f'http://openweathermap.org/img/wn/{ cod_icon }@2x.png'
    raw_data = urllib.request.urlopen( img_url ).read()
    data_stream = io.BytesIO( raw_data )
    icon = Image.open( data_stream )
    return icon


def get_current_weather( config, location: Location ) -> CurrentWeather:
    # Requesting the current weather data in OpenWeather API.
    # Store the latitude and longitude for the next request.
    weather = requests.get( 'https://api.openweathermap.org/data/2.5/weather', params={
        "lat": location[ 'lat' ],
        "lon": location[ 'lon' ],
        "appid": config[ "API_KEY" ],
        "units": "imperial"  # We use the Fahrenheit scale to measure degrees (units=imperial).
    } ).json()

    icon = get_icon( weather[ 'weather' ][ 0 ][ 'icon' ] )
    return {
        'Weather description': weather[ 'weather' ][ 0 ][ 'description' ].capitalize(),
        'Temperature': f"{ weather[ 'main' ][ 'temp' ] } °F", # In °F
        'Feels like': f"{ weather[ 'main' ][ 'feels_like' ] } °F", # In °F
        'Humidity': f"{ weather[ 'main' ][ 'humidity' ] } %", # In percentage
        'Wind speed': f"{ weather[ 'wind' ][ 'speed' ] } miles/hour", # In miles per hour
        'Clouds': f"{ weather[ 'clouds' ][ 'all' ] } %", # Cloudiness in percentage
        'Icon': icon,
    }


def get_forecast( config, location: Location ) -> List[ Forecast ]:
    lat = location[ 'lat' ]  # Store the latitude for the next request.
    lon = location[ 'lon' ]  # Store the longitude for the next request.
    forecast = requests.get( f'https://api.openweathermap.org/data/2.5/forecast', params={
        "lat": lat,
        "lon": lon,
        "appid": config[ "API_KEY" ],
        "units": "imperial"  # We use the Fahrenheit scale to measure degrees (units=imperial).
    } ).json()
    # I made this dict to summarize the forecasts in the next days at 09:00 AM
    raw_infos = { x[ 'dt_txt' ][ :10 ]: x[ 'main' ] for x in forecast[ 'list' ] if '09:00' in x[ 'dt_txt' ] }
    parsed_infos = {
        k: {
            'Temperature': f"{ v[ 'temp' ] } °F",
            'Feels like': f"{ v[ 'feels_like' ] } °F",
            'Min temperature': f"{ v[ 'temp_min' ] } °F",
            'Max temperature': f"{ v[ 'temp_max' ] } °F"
         } for k, v in raw_infos.items()
        }
    return parsed_infos

def create_tkinter( name ):
    main_window = tkinter.Tk()  # We start the GUI.
    main_window.title( name )  # The main title.
    return main_window

def write_date(app):
    label_frame = tkinter.LabelFrame( app, text=f'Current Time and Date' )
    label_frame.pack( fill='both', expand='yes' )
    current_date = datetime.now().strftime( "%d/%m/%Y" )
    current_time = datetime.now().strftime( "%H:%M:%S" )
    tkinter.Label( label_frame, text= current_time ).grid( column= 1, row= 1, ipadx= 10, ipady= 10 )
    tkinter.Label( label_frame, text= current_date ).grid( column= 2, row= 1, ipadx= 10, ipady= 10 )

def write_current_weather( app, weather ):
    label_frame = tkinter.LabelFrame( app, text=f'Current Weather in Rio de Janeiro' )
    label_frame.pack( fill='both', expand='yes' )
    keys = [ x for x in weather.keys() ]
    values = [ x for x in weather.values() ]

    for i in range( len( weather ) ):
        key = keys[i]
        value = values[i]
        if keys[i] == 'Icon':
            tkinter.Label( label_frame, text= key ).grid( row= i + 1, ipadx= 10, ipady= 10 )
            tkinter.Label( label_frame, image= ( ImageTk.PhotoImage( value ) ) ).grid( column= 1, row= i + 1, ipadx= 10, ipady= 10 )
        else:
            tkinter.Label( label_frame, text= key ).grid( row= i + 1, ipadx= 10, ipady= 10 )
            tkinter.Label( label_frame, text= value ).grid( column= 1, row= i + 1, ipadx= 10, ipady= 10 )

def write_forecasts( app, forecast ):
    label_frame = tkinter.LabelFrame( app, text='Forecast Weather in Rio de Janeiro' )
    label_frame.pack( fill='both', expand='yes' )
    keys = [ x for x in forecast.keys() ]
    values = [ x for x in forecast.values() ]
    label_values = [ x for x in values[0].keys() ]
    for i in range( len( forecast ) ):
        tkinter.Label( label_frame, text= keys[i] ).grid( column= i + 1, row= 0, ipadx= 10, ipady= 10 )
        for j in range( len( label_values )):
            tkinter.Label( label_frame, text= values[i][label_values[j]] ).grid( column= i + 1, row= j + 1, ipadx= 10, ipady= 10 )
    for i in range( len( label_values ) ):
        tkinter.Label( label_frame, text= label_values[i] ).grid( column= 0, row= i + 1, ipadx= 10, ipady= 10 )


def create_button( app, text, function ):
    return tkinter.Button( app, text= text, command= function ).pack( pady= 20 )

if __name__ == '__main__':
    # An aplication to call the current weather in Rio de Janeiro (RJ) - Brazil.
    env_config = dotenv_values(".env") # This will return a dict with our keys in .env.
    zip_code = '20000-000'  # RJ zip code. Neighborhood São Cristovão.
    country_code = 'BR'  # Brazil country code in ISO 3166.

    # Firstly, we request the Geocoding API to discover the latitude and longitude.
    location = get_location( env_config, zip_code, country_code )
    weather = get_current_weather( env_config, location )
    forecast = get_forecast( env_config, location )

    app = create_tkinter( 'Rio de Janeiro Weather - Henrique Silva Costa Júnior' )
    write_date( app )
    write_current_weather( app, weather )
    create_button( app, 'Show Forecasts', lambda: write_forecasts( app, forecast ) )
    app.mainloop()

