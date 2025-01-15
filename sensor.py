import dash
from dash import dcc, html
from dash.dependencies import Input, Output, State
import plotly.graph_objs as go
import pandas as pd
import time
import board
import busio
import adafruit_adxl34x
import threading

# Initialize I2C and ADXL345
i2c = busio.I2C(board.SCL, board.SDA)
accelerometer = adafruit_adxl34x.ADXL345(i2c)
accelerometer.range = adafruit_adxl34x.Range.RANGE_2_G

# Create a DataFrame to store acceleration data
data = pd.DataFrame(columns=["Timestamp", "X (g)", "Y (g)", "Z (g)"])

# Global flag for data acquisition
acquisition_running = False

# Function to continuously read data from ADXL345
def read_acceleration():
    global data, acquisition_running
    while True:
        if acquisition_running:
            x, y, z = accelerometer.acceleration
            timestamp = time.time()
            new_data = pd.DataFrame({"Timestamp": [timestamp], "X (g)": [x], "Y (g)": [y], "Z (g)": [z]})
            data = pd.concat([data, new_data], ignore_index=True)
            time.sleep(0.1)  # Sampling rate: 10 Hz

# Start the data collection thread
thread = threading.Thread(target=read_acceleration, daemon=True)
thread.start()

# Initialize Dash app
app = dash.Dash(__name__)

# Layout of the Dash app
app.layout = html.Div([
    html.H1("ADXL345 Acceleration Data", style={"textAlign": "center"}),

    # Buttons to start and stop acquisition
    html.Div([
        html.Button("Start Acquisition", id="start-button", n_clicks=0, style={"marginRight": "10px"}),
        html.Button("Stop Acquisition", id="stop-button", n_clicks=0),
    ], style={"textAlign": "center", "marginBottom": "20px"}),

    # Hidden div to store acquisition state
    dcc.Store(id="acquisition-state", data=False),

    # Graphs for acceleration data
    dcc.Graph(id="x-plot", style={"height": "300px"}),
    dcc.Graph(id="y-plot", style={"height": "300px"}),
    dcc.Graph(id="z-plot", style={"height": "300px"}),

    # Interval for periodic updates
    dcc.Interval(id="interval-component", interval=500, n_intervals=0)
])

# Callbacks to handle start/stop acquisition
@app.callback(
    Output("acquisition-state", "data"),
    [Input("start-button", "n_clicks"),
     Input("stop-button", "n_clicks")],
    [State("acquisition-state", "data")]
)
def update_acquisition_state(start_clicks, stop_clicks, current_state):
    global acquisition_running
    if start_clicks > stop_clicks:
        acquisition_running = True
        return True
    else:
        acquisition_running = False
        return False

# Callback to update graphs
@app.callback(
    [Output("x-plot", "figure"),
     Output("y-plot", "figure"),
     Output("z-plot", "figure")],
    [Input("interval-component", "n_intervals"),
     State("acquisition-state", "data")]
)
def update_graphs(n, is_running):
    global data

    # If acquisition is stopped, don't update graphs
    if not is_running:
        return dash.no_update, dash.no_update, dash.no_update

    # Keep only the latest 100 points for better performance
    if len(data) > 100:
        data = data.tail(100).reset_index(drop=True)

    # Create individual plots for X, Y, and Z
    x_fig = go.Figure(go.Scatter(x=data["Timestamp"], y=data["X (g)"], mode="lines", name="X-Axis"))
    x_fig.update_layout(title="X-Axis Acceleration", xaxis_title="Time", yaxis_title="Acceleration (g)")

    y_fig = go.Figure(go.Scatter(x=data["Timestamp"], y=data["Y (g)"], mode="lines", name="Y-Axis"))
    y_fig.update_layout(title="Y-Axis Acceleration", xaxis_title="Time", yaxis_title="Acceleration (g)")

    z_fig = go.Figure(go.Scatter(x=data["Timestamp"], y=data["Z (g)"], mode="lines", name="Z-Axis"))
    z_fig.update_layout(title="Z-Axis Acceleration", xaxis_title="Time", yaxis_title="Acceleration (g)")

    return x_fig, y_fig, z_fig

# Run the Dash app
if __name__ == "__main__":
    app.run_server(debug=True, host="0.0.0.0")