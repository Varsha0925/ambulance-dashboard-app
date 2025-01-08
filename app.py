import requests
import networkx as nx
from flask import Flask, request, jsonify

# Initialize Flask App
app = Flask(__name__)

# API Keys
TRAFFIC_API_KEY = 'AIzaSyBfgFUm0h-tpdRKfGkbhXIDhJih6ixfSJM'
WEATHER_API_KEY = '48e41d4567a6897feb0096632fdc91c8'
GEOCODING_API_KEY = 'AIzaSyBfgFUm0h-tpdRKfGkbhXIDhJih6ixfSJM'

# API Endpoints
TRAFFIC_API_URL = 'https://maps.googleapis.com/maps/api/directions/json'
WEATHER_API_URL = 'https://api.openweathermap.org/data/2.5/weather'
GEOCODING_API_URL = 'https://maps.googleapis.com/maps/api/geocode/json'

# Sample Graph for Vijayawada Map with Hospitals
G = nx.Graph()
locations = {
    'Accident Site': (16.5062, 80.6480),
    'Hospital 1': (16.5101, 80.6350),
    'Hospital 2': (16.5211, 80.6450),
    'Hospital 3': (16.4990, 80.6570)
}

# Add edges with default weights
G.add_edge('Accident Site', 'Hospital 1', weight=1)
G.add_edge('Accident Site', 'Hospital 2', weight=2)
G.add_edge('Accident Site', 'Hospital 3', weight=1.5)
G.add_edge('Hospital 1', 'Hospital 2', weight=1)
G.add_edge('Hospital 2', 'Hospital 3', weight=1.2)


# 📍 Real-Time Traffic Data
def get_realtime_traffic_data(origin, destination):
    try:
        response = requests.get(
            TRAFFIC_API_URL,
            params={'origin': origin, 'destination': destination, 'key': TRAFFIC_API_KEY}
        )
        if response.status_code == 200:
            data = response.json()
            routes = data.get('routes', [])
            if routes:
                return routes[0]['legs'][0]['duration_in_traffic']['value'] / 60  # Return in minutes
        return 10
    except Exception as e:
        print("Traffic API Exception:", e)
        return 10


# 🌦️ Real-Time Weather Data
def get_realtime_weather_data(city):
    try:
        response = requests.get(
            WEATHER_API_URL,
            params={'q': city, 'appid': WEATHER_API_KEY, 'units': 'metric'}
        )
        if response.status_code == 200:
            data = response.json()
            return data['weather'][0]['main']
    except Exception as e:
        print("Weather API Exception:", e)
    return 'Clear'


# 🗺️ Optimize Route
def optimize_route(accident_site, city):
    weather = get_realtime_weather_data(city)
    routes = {}

    for hospital in ['Hospital 1', 'Hospital 2', 'Hospital 3']:
        traffic_penalty = get_realtime_traffic_data(accident_site, hospital)
        weather_penalty = 1.5 if weather != 'Clear' else 1.0
        G[accident_site][hospital]['weight'] *= traffic_penalty * weather_penalty

        path = nx.shortest_path(G, source=accident_site, target=hospital, weight='weight')
        routes[hospital] = path

    best_hospital = min(routes, key=lambda h: nx.shortest_path_length(G, accident_site, h, weight='weight'))
    return routes[best_hospital]


# 🚑 API Endpoint
@app.route('/optimize', methods=['GET'])
def get_route():
    accident_location = request.args.get('source', 'Accident Site')
    city = request.args.get('city', 'Vijayawada')

    route = optimize_route(accident_location, city)
    return jsonify({'route': route})


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
