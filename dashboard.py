import dash
from dash import dcc, html, Input, Output, State
import requests
import os

app = dash.Dash(__name__)
app.title = "🚑 Ambulance Route Optimization"
server = app.server

API_URL = os.getenv('API_URL', 'http://127.0.0.1:5000/optimize')

app.layout = html.Div([
    html.H1("🚑 Ambulance Route Optimization", style={'textAlign': 'center'}),
    html.Div([
        html.Label("Accident Location:"),
        dcc.Input(id='source-input', type='text', placeholder='Enter Accident Location', debounce=True),
        html.Label("City:"),
        dcc.Input(id='city-input', type='text', placeholder='Enter City', value='Vijayawada', debounce=True),
        html.Button('Find Nearest Hospital', id='optimize-button', n_clicks=0, style={'marginTop': '10px'})
    ]),
    html.Div(id='output-route', style={'marginTop': '20px'}),
    dcc.Graph(id='route-graph', style={'height': '500px'})
])


@app.callback(
    [Output('output-route', 'children'), Output('route-graph', 'figure')],
    Input('optimize-button', 'n_clicks'),
    [State('source-input', 'value'), State('city-input', 'value')]
)
def optimize_route(n_clicks, source, city):
    try:
        response = requests.get(
            API_URL,
            params={'source': source, 'city': city}
        )
        if response.status_code == 200:
            data = response.json()
            route = data.get('route', [])
            return f"Optimized Route: {' → '.join(route)}", {}
    except Exception as e:
        return f"❌ Error: {str(e)}", {}


if __name__ == '__main__':
    app.run_server(debug=False, host='0.0.0.0', port=int(os.environ.get('PORT', 8050)))
