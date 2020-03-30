# Import libraries
import pandas_datareader
import datetime
import argparse
import pandas as pd
import plotly.graph_objects as go

# Parse command line arguments
parser = argparse.ArgumentParser()
parser.add_argument("--ticker", help="Enter corporation ticker symbol", default = 'TEF.MC')
parser.add_argument("--startDate", help="Enter start date of interval YY-MM-DD", default =  str(datetime.date.today()-datetime.timedelta(days = 365)))
parser.add_argument("--endDate", help="Enter end date of interval YY-MM-DD", default = str(datetime.date.today()))
args = parser.parse_args()

# Variables
ticker = args.ticker
startDate = datetime.datetime.strptime(str(args.startDate), "%Y-%m-%d")
endDate = datetime.datetime.strptime(str(args.endDate),"%Y-%m-%d")

# Read data from yahoo
df = pandas_datareader.DataReader(ticker, 'yahoo', startDate, endDate)

# Get Date into a column value
df.reset_index(inplace=True,drop=False)

# Print dataframe head
print(df.head)

# Export dataframe to csv
df.to_csv(ticker + '.csv')

# This code is adapted from https://plot.ly/python/ohlc-charts/
# OHLC Chart without Rangeslider
fig = go.Figure(data=go.Ohlc(x=df['Date'],
                open=df['Open'],
                high=df['High'],
                low=df['Low'],
                close=df['Close']))
fig.update(layout_xaxis_rangeslider_visible=False)

# Adding customized text
fig.update_layout(
    title=ticker,
    yaxis_title='Cotización')

# Show OHLC Chart
fig.show()

# Save OHLC Chart html
fig.write_html("file.html")
