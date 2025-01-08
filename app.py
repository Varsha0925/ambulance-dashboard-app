import requests
from flask import Flask, request, jsonify
import networkx as nx
import os

# Initialize Flask App
app = Flask(__name__)

# API Keys
TRAFFIC_API_KEY = os.getenv('TRAFFIC_API_KEY', 'AIzaSyBfgFUm0h-tpdRKfGkbhXIDhJih6ixfSJM')
WEATHER_API_KEY = os.getenv('WEATHER_API_KEY', '48e41d4567a6897feb0096632fdc91c8')
GEOCODING_API_KEY = os.getenv('GEOCODING_API_KEY', 'AIzaSyBfgFUm0h-tpdRKfGkbhXIDhJih6ixfSJM')

# API Endpoints
TRAFFIC_API_URL = 'https://maps.googleapis.com/maps/api/directions/json'
WEATHER_API_URL = 'https://api.openweathermap.org/data/2.5/weather'
GEOCODING_API_URL = 'https://maps.googleapis.com/maps/api/geocode/json'

# Define Hospital Locations (Latitude, Longitude)
HOSPITALS = {
    'Government General Hospital': (16.5062, 80.6480),
    'Andhra Hospital': (16.5101, 80.6350),
    'Manipal Hospital': (16.5211, 80.6450),
    'Ramesh Hospitals': (16.4990, 80.6570),
    'Vijaya Super Speciality Hospital': (16.5050, 80.6440)
}


# 📍 1️⃣ Geocode Accident Location
def get_coordinates_from_location(location_name):
    try:
        response = requests.get(
            GEOCODING_API_URL,
            params={
                'address': location_name,
                'key': GEOCODING_API_KEY
            }
        )
        if response.status_code == 200:
            data = response.json()
            if 'results' in data and len(data['results']) > 0:
                location = data['results'][0]['geometry']['location']
                return location['lat'], location['lng']
    except Exception as e:
        print("Geocoding API Error:", e)
    return None, None


# 🚦 2️⃣ Real-Time Traffic Data Fetching
def get_realtime_traffic_data(origin, destination):
    try:
        response = requests.get(
            TRAFFIC_API_URL,
            params={
                'origin': origin,
                'destination': destination,
                'key': TRAFFIC_API_KEY
            }
        )
        if response.status_code == 200:
            data = response.json()
            routes = data.get('routes', [])
            if routes:
                return routes[0]['legs'][0]['duration_in_traffic']['value'] / 60  # Return in minutes
    except Exception as e:
        print("Traffic API Error:", e)
    return 10


# 🌦️ 3️⃣ Real-Time Weather Data Fetching
def get_realtime_weather_data(city):
    try:
        response = requests.get(
            WEATHER_API_URL,
            params={
                'q': city,
                'appid': WEATHER_API_KEY,
                'units': 'metric'
            }
        )
        if response.status_code == 200:
            data = response.json()
            return data['weather'][0]['main']
    except Exception as e:
        print("Weather API Error:", e)
    return 'Clear'


# 🏥 4️⃣ Find Nearest Hospital
def find_nearest_hospital(accident_lat, accident_lon):
    nearest_hospital = None
    shortest_distance = float('inf')
    
    for hospital, (lat, lon) in HOSPITALS.items():
        distance = ((accident_lat - lat)**2 + (accident_lon - lon)**2)**0.5
        if distance < shortest_distance:
            shortest_distance = distance
            nearest_hospital = hospital
            
    return nearest_hospital, HOSPITALS[nearest_hospital]


# 🚑 5️⃣ Optimize Route
def get_optimized_route(source, destination):
    try:
        response = requests.get(
            TRAFFIC_API_URL,
            params={
                'origin': source,
                'destination': destination,
                'key': TRAFFIC_API_KEY
            }
        )
        if response.status_code == 200:
            data = response.json()
            routes = data.get('routes', [])
            if routes:
                return routes[0]['overview_polyline']['points']
    except Exception as e:
        print("Route Optimization Error:", e)
    return None


# 🚦 6️⃣ API Endpoint for Route Optimization
@app.route('/optimize', methods=['GET'])
def optimize_route():
    accident_location = request.args.get('location')
    city = request.args.get('city', 'Vijayawada')

    # Get Coordinates from Accident Location
    accident_lat, accident_lon = get_coordinates_from_location(accident_location)
    if accident_lat is None or accident_lon is None:
        return jsonify({'error': 'Invalid accident location'}), 400

    # Find Nearest Hospital
    nearest_hospital, (hospital_lat, hospital_lon) = find_nearest_hospital(accident_lat, accident_lon)

    # Get Real-time Weather
    weather = get_realtime_weather_data(city)

    # Get Optimized Route
    source = f"{accident_lat},{accident_lon}"
    destination = f"{hospital_lat},{hospital_lon}"
    route = get_optimized_route(source, destination)

    return jsonify({
        'nearest_hospital': nearest_hospital,
        'weather': weather,
        'route_polyline': route
    })


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
