import requests
import networkx as nx
from flask import Flask, request, jsonify

# Initialize Flask App
app = Flask(__name__)

# API Keys
TRAFFIC_API_KEY = 'AIzaSyBfgFUm0h-tpdRKfGkbhXIDhJih6ixfSJM'
WEATHER_API_KEY = '48e41d4567a6897feb0096632fdc91c8'

# API Endpoints
TRAFFIC_API_URL = 'https://maps.googleapis.com/maps/api/directions/json'
WEATHER_API_URL = 'https://api.openweathermap.org/data/2.5/weather'

# Sample Graph for Routing
G = nx.Graph()
G.add_edge('A', 'B', weight=1)
G.add_edge('B', 'C', weight=2)
G.add_edge('A', 'D', weight=4)
G.add_edge('C', 'D', weight=1)


# 1️⃣ Real-Time Traffic Data Fetching
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
                traffic_duration = routes[0]['legs'][0]['duration_in_traffic']['value']
                return traffic_duration / 60  # Return minutes
            else:
                print("No route found.")
                return 10  # Default weight
        else:
            print("Traffic API Error:", response.status_code)
            return 10  # Default weight
    except Exception as e:
        print("Traffic API Exception:", e)
        return 10


# 2️⃣ Real-Time Weather Data Fetching
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
            weather_condition = data['weather'][0]['main']
            return weather_condition
        else:
            print("Weather API Error:", response.status_code)
            return 'Clear'
    except Exception as e:
        print("Weather API Exception:", e)
        return 'Clear'


# 3️⃣ Dynamic Route Optimization
def optimize_route(source, destination, city):
    weather_condition = get_realtime_weather_data(city)
    traffic_penalty = get_realtime_traffic_data(source, destination)

    # Adjust graph weights dynamically based on traffic and weather
    for edge in G.edges:
        base_weight = 1.0  # Default weight
        weather_penalty = 1.5 if weather_condition != 'Clear' else 1.0
        G[edge[0]][edge[1]]['weight'] = base_weight * traffic_penalty * weather_penalty

    try:
        path = nx.shortest_path(G, source=source, target=destination, weight='weight')
        return path
    except nx.NetworkXNoPath:
        return []


# 4️⃣ API Endpoint for Route Optimization
@app.route('/optimize', methods=['GET'])
def get_route():
    source = request.args.get('source')
    destination = request.args.get('destination')
    city = request.args.get('city', 'Vijayawada')

    if not source or not destination:
        return jsonify({'error': 'Source and Destination are required'}), 400

    route = optimize_route(source, destination, city)
    return jsonify({'route': route})


# 5️⃣ Run the Flask App
if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
