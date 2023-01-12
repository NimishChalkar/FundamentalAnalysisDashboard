from flask import Flask
from methods import *
import pandas as pd


app = Flask(__name__)

datasets = {}

@app.route("/")
def index():
    return "Welcome to SFA"

@app.before_first_request
def prepData():
    """ Perform preprocessing"""
    stock_df = pd.read_csv("sfa_data.csv")
    stocks_clean_df = cleanData(stock_df)
    smlCap, midCap, lrgCap = groupByMktCap(stocks_clean_df, "NYSE")
    datasets["smlCapRated"] = getStockRatings(smlCap)
    datasets["midCapRated"] = getStockRatings(midCap)
    datasets["lrgCapRated"] = getStockRatings(lrgCap)
    datasets["stockprices"] = getStockPrice(stocks_clean_df.Code.to_list())
    
########### apis to test #############

@app.route("/smlCapRated")
def smlCapStocks():
    return datasets["smlCapRated"].to_csv()

@app.route("/midCapRated")
def midCapStocks():
    return datasets["midCapRated"].to_csv()

@app.route("/lrgCapRated")
def lrgCapStocks():
    return datasets["lrgCapRated"].to_csv()

@app.route("/stockPrices")
def stockPrices():
    return datasets["stockprices"].to_csv()

#######################################

if __name__ == "__main__":
    app.run(debug=False, port=8001)