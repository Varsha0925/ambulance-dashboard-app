import dash
from dash import dcc, html, Input, Output, State
import requests
import json

# Initialize the Dash app
app = dash.Dash(__name__)
app.title = "Ambulance Route Optimization Dashboard"

# Backend API URL
API_URL = "http://127.0.0.1:5000/optimize"

# App Layout
app.layout = html.Div([
    html.H1("🚑 Ambulance Route Optimization Dashboard", style={'textAlign': 'center'}),
    html.Div([
        html.Label("Source Location:"),
        dcc.Input(id='source-input', type='text', placeholder='Enter Source', debounce=True),
        
        html.Label("Destination Location:"),
        dcc.Input(id='destination-input', type='text', placeholder='Enter Destination', debounce=True),
        
        html.Label("City:"),
        dcc.Input(id='city-input', type='text', placeholder='Enter City', value='Vijayawada', debounce=True),
        
        html.Button('Optimize Route', id='optimize-button', n_clicks=0, style={'marginTop': '10px'})
    ], style={'margin': '20px'}),
    
    html.Hr(),
    html.Div(id='output-route', style={'marginTop': '20px', 'fontSize': '18px', 'fontWeight': 'bold'}),
    
    dcc.Graph(id='route-graph', style={'height': '500px'})
])

# Callback to fetch route data from backend
@app.callback(
    [Output('output-route', 'children'),
     Output('route-graph', 'figure')],
    Input('optimize-button', 'n_clicks'),
    [State('source-input', 'value'),
     State('destination-input', 'value'),
     State('city-input', 'value')]
)
def optimize_route(n_clicks, source, destination, city):
    if not source or not destination:
        return "❌ Please provide both Source and Destination locations.", {}

    try:
        # Call Backend API
        response = requests.get(
            API_URL,
            params={
                'source': source,
                'destination': destination,
                'city': city
            }
        )
        
        if response.status_code == 200:
            data = response.json()
            route = data.get('route', [])
            
            if not route:
                return "⚠️ No valid route found. Please check your input.", {}
            
            # Generate a sample graph visualization
            nodes = {node: index for index, node in enumerate(route)}
            edges = [(route[i], route[i+1]) for i in range(len(route) - 1)]
            
            fig = {
                'data': [
                    {'x': [nodes[edge[0]], nodes[edge[1]]], 
                     'y': [0, 1], 
                     'mode': 'lines+markers+text',
                     'text': [edge[0], edge[1]],
                     'textposition': 'top center',
                     'line': {'width': 2}}
                    for edge in edges
                ],
                'layout': {
                    'title': 'Optimized Route Visualization',
                    'xaxis': {'title': 'Nodes'},
                    'yaxis': {'visible': False},
                    'showlegend': False
                }
            }
            
            return f"✅ Optimized Route: {' → '.join(route)}", fig
        
        else:
            return f"❌ API Error: {response.status_code}", {}
    
    except Exception as e:
        return f"❌ An error occurred: {str(e)}", {}

# Run the Dash app
if __name__ == '__main__':
    import os
    app.run_server(debug=False, host='0.0.0.0', port=int(os.environ.get('PORT', 8050)))


