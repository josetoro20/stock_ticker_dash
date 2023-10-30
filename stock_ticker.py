import dash
from dash import html, dcc
from dash.dependencies import Input, Output, State
import yfinance as yf  # Importing yfinance library for stock data retrieval from Yahoo Finance
from datetime import datetime
import pandas as pd
import dash_auth

USER_NAME_PAIRS = [['username','password'], ['pepet16','1234']]
mydataset = "https://raw.githubusercontent.com/josetoro20/stock_ticker_dash/main/NASDAQcompanylist.csv"
nsdq = pd.read_csv(mydataset)
app = dash.Dash()

server = app.server
auth = dash_auth.BasicAuth(app, USER_NAME_PAIRS)

# reading in a company list

nsdq.set_index('Symbol',inplace=True) # company sysmbols now set as index, inplace = true appends the df

options = [] #empty options list for loop to append to

for tic in nsdq.index:  # for every ticker in that index we contruct a dictionary
    mydict = {} # create dict
    mydict['label'] = nsdq.loc[tic]['Name'] + ' ' + tic # grab location of name (using loc of symbol), add space and add tic symbol
    mydict['value'] = tic #now in dict Value: tic
    options.append(mydict) # append both label and value to build dict

app.layout = html.Div([
    html.H1('Stock Ticker Dashboard'),  # Header for the dashboard
    html.Div([
        html.H3('Enter a stock symbol:', style={'paddingRight':'30px'}),  # Title above the dropdown
        dcc.Dropdown(
            id='my_stock_picker',  # ID used for callbacks
            options = options, # list at the top, create by tic for loop
            value=['TSLA'],# Initial value set for the dropdown
            multi=True #allows the user to choose multiple options
        ),
    ],style={'display':'inline-block', 'verticalAligh': 'top', 'width': '30%'}),
    html.Div([html.H3('Select a start and end date'),
              dcc.DatePickerRange(id='my_date_picker',
                                  min_date_allowed=datetime(2015,1,1),
                                  max_date_allowed=datetime.today(),
                                  start_date=datetime(2021,1,1),
                                  end_date=datetime.today()
    )],style={'display':'inline-block'}
             ),
    html.Div([
        html.Button(id='submit-button',
                    n_clicks=0,
                    children='Submit',
                    style={'fontSize': 24, 'marginLeft': '30px'})
    ], style={'display':'inline-block'}), # button is next to date picker

    dcc.Graph(
        id='my_graph',  # ID of the graph component
        figure={
            'data': [
                {'x': [1, 2], 'y': [3, 1]}  # Placeholder data for the graph
            ],
            'layout': {'title': 'Default Title'}  # Default title for the graph
        }
    )
])


@app.callback(Output('my_graph', 'figure'),
              [Input('submit-button', 'n_clicks')],
              [State('my_stock_picker', 'value'),
                    State('my_date_picker', 'start_date'),
                    State('my_date_picker','end_date')
               ])
def update_graph(n_clicks,stock_ticker,start_date,end_date):
    start = datetime.strptime(start_date[:10], '%Y-%m-%d')  #the string comes in this format, convert the str format into datetime object called start so we can pass into data reader
    end = datetime.strptime(end_date[:10], '%Y-%m-%d')

    traces = []
    for tic in stock_ticker:
        df = yf.download(tic, start=start, end=end)  # Fetch stock data using yfinance
        traces.append({'x': df.index, 'y': df['Close'], 'name': tic})
    fig = {
        'data': traces,  # x-axis: dates, y-axis: closing prices
        'layout': {'title': stock_ticker}  # Set the stock ticker as the title
    }
    return fig


if __name__ == '__main__':
    app.run_server()
