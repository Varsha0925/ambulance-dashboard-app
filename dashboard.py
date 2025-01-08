import dash
from dash import dcc, html, Input, Output, State
import requests
import os

app = dash.Dash(__name__)
app.title = "🚑 Real-Time Ambulance Optimization"
server = app.server

API_URL = os.getenv('API_URL', 'http://127.0.0.1:5000/optimize')

# Layout
app.layout = html.Div([
    html.H1("🚑 Real-Time Ambulance Route Optimization", style={'textAlign': 'center'}),
    html.Div([
        html.Label("Accident Location Name:"),
        dcc.Input(id='location-input', type='text', placeholder='Enter Accident Location'),
        html.Label("City:"),
        dcc.Input(id='city-input', type='text', placeholder='Enter City', value='Vijayawada'),
        html.Button('Find Route', id='optimize-button', n_clicks=0)
    ]),
    html.Div(id='output-info', style={'marginTop': '20px'}),
    dcc.Graph(id='route-graph', style={'height': '500px'})
])


@app.callback(
    [Output('output-info', 'children'), Output('route-graph', 'figure')],
    Input('optimize-button', 'n_clicks'),
    [State('location-input', 'value'), State('city-input', 'value')]
)
def fetch_route(n_clicks, location, city):
    try:
        response = requests.get(API_URL, params={'location': location, 'city': city})
        if response.status_code == 200:
            data = response.json()
            hospital = data['nearest_hospital']
            weather = data['weather']
            return (
                f"Nearest Hospital: {hospital} | Weather: {weather}",
                {'layout': {'title': 'Optimized Route'}}
            )
    except Exception as e:
        return f"❌ Error: {str(e)}", {}


if __name__ == '__main__':
    app.run_server(debug=False, host='0.0.0.0', port=int(os.environ.get('PORT', 8050)))
