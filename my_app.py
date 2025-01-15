from dash import Dash, html, dcc, callback, Output, Input



app = Dash()

app.layout = [
    html.H1(children='Title of Dash App', style={'textAlign':'center'}),
    dcc.Dropdown(["Hello", "Canada"], 'Canada', id='dropdown-selection'),
    dcc.Graph(id='graph-content')
]

@callback(
    Output('graph-content', 'figure'),
    Input('dropdown-selection', 'value')
)
def update_graph(value):
    # dff = df[df.country==value]
    return None
if __name__ == '__main__':
    app.run(debug=True)