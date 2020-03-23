# Import libraries
import pandas_datareader
import datetime
import argparse

#Parse command line arguments
parser = argparse.ArgumentParser()
parser.add_argument("--ticker", help="Enter corporation ticker symbol")
parser.add_argument("--startDate", help="Enter start date of interval YY-MM-DD")
parser.add_argument("--endDate", help="Enter end date of interval YY-MM-DD")
args = parser.parse_args()

# Variables
ticker=args.ticker
startDate = datetime.datetime.strptime(args.startDate, "%Y-%m-%d")
endDate = datetime.datetime.strptime(args.endDate,"%Y-%m-%d")

# Read data from yahoo
df = pandas_datareader.DataReader(ticker, 'yahoo', startDate, endDate)

# Print dataframe
print(df)
