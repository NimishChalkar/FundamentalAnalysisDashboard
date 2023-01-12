import requests
import pandas as pd
import numpy as np
import collections
import yfinance as yf
from datetime import date
from dateutil.relativedelta import relativedelta


# global variables
metrics = ['PERatio', 'Earnings/Share', 'DividendYieldRatio', 'BookValue/Share', 'Revenue/Share', 'D/ERatio']

def getFundamentals(code):
    """Extract and store the data in a pandas dataframe"""
    url = f"https://eodhistoricaldata.com/api/fundamentals/{code}.US?api_token=6339e20e082090.50362094";
    req = requests.get(url);
    if req.status_code == 200:
        response = req.json();
        metrics = {};
        # create a list of the financials to slice through the periodic values
        try:
            #list_financials_cashflow = list(response["Financials"]["Cash_Flow"]["yearly"]);
            list_financials_balancesheet = list(response["Financials"]["Balance_Sheet"]["yearly"]);

            # getting the latest yearly financials
            current_total_liabilities = response["Financials"]["Balance_Sheet"]["yearly"][list_financials_balancesheet[0]]["totalCurrentLiabilities"];
            total_stockholder_equity = response["Financials"]["Balance_Sheet"]["yearly"][list_financials_balancesheet[0]]["totalStockholderEquity"];

            # extracting the desired metrics
            metrics["Code"] = response["General"]["Code"];
            metrics["Name"] = response["General"]["Name"];
            metrics["Sector"] = response["General"]["Sector"];
            metrics["MarketCapitalization"] = response["Highlights"]["MarketCapitalization"];
            metrics["PERatio"] = response["Highlights"]["PERatio"];
            metrics["Earnings/Share"] = response["Highlights"]["EarningsShare"];
            metrics["DividendYieldRatio"] = response["Highlights"]["DividendYield"];
            metrics["BookValue/Share"] = response["Highlights"]["BookValue"];
            metrics["Revenue/Share"] = response["Valuation"]["PriceBookMRQ"];
            metrics["D/ERatio"] = float(current_total_liabilities)/float(total_stockholder_equity);
        except Exception as e:
            print(code, e)
        return pd.DataFrame([metrics]);
    else:
        print(req.text)

def getStockData(tickers):
    # initialize an empty dataframe
    datadf = pd.DataFrame()
    # loop through every ticker in the list
    for ticker in tickers:
        datadf = pd.concat([datadf, getFundamentals(ticker)])
        print(datadf)
    return datadf


def cleanData(dataframe):
    # removing the first column and setting the index to ticker code
    data_clean = dataframe.drop(["Unnamed: 0"], axis=1)
    data_clean.set_index("Code")
    data_clean.dropna(axis=0, how="any", inplace=True)
    # "MarketCapitalization" is in scientific notation, we will have to convert it to Billions
    data_clean["MarketCapitalization"]=data_clean["MarketCapitalization"].astype(int).apply(lambda x: x/1000000000)
    return data_clean


def getSectorData(dataframe):
    """Get the different sectors and 
    the distribution of values per metric
    from a given dataframe"""
    
    sectors = dataframe["Sector"].unique() # get the list of sectors
    global metrics # get the list of metrics
    sector_data = collections.defaultdict(lambda : collections.defaultdict(dict))

    for sector in sectors:

        sector_stocks = dataframe[dataframe["Sector"] == sector] # get the stock data per sector

        for metric in metrics:
            sector_data[sector][metric]["10Pct"] = sector_stocks[metric].quantile(0.1) # get the 10th pc for the sector
            sector_data[sector][metric]["90Pct"] = sector_stocks[metric].quantile(0.9) # get the 90th pc
            sector_data[sector][metric]["Std"] = np.std(sector_stocks[metric], axis=0) / 5 # get the std
    
    return sector_data

def groupByMktCap(dataframe, exchange):
    """Group the stocks based on their Market Capitalization"""
    ind = ["BSE", "NSE"]
    if exchange in ind:
        lrgCap = dataframe[dataframe["MarketCapitalization"] >= 20000] # More than Rs. 20,000 cr. 
        midCap = dataframe[(dataframe["MarketCapitalization"] > 20000) | (dataframe["MarketCapitalization"] < 5000)] # Rs. 5,000 cr. to Rs. 20,000 cr.
        smlCap = dataframe[dataframe["MarketCapitalization"] < 5000] # Less than Rs. 5,000 cr.
    else:
        lrgCap = dataframe[dataframe["MarketCapitalization"] >= 10] # > $10B
        midCap = dataframe[(dataframe["MarketCapitalization"] > 2) | (dataframe["MarketCapitalization"] < 10)] # $2B – $10B
        smlCap = dataframe[dataframe["MarketCapitalization"] < 2] # less than $2B
    return smlCap, midCap, lrgCap

def get_metric_grade(dataframe, sector, metric_name, metric_val):
    """Grade the stock metric value for the given sector"""

    sector_data = getSectorData(dataframe)

    lowThan = metric_name in ["PERatio", "D/ERatio"]
        
    grade_basis = "10Pct" if lowThan else "90Pct" # 10th percentile as the basis for grading where a lower value is considered better
    
    start, change = sector_data[sector][metric_name][grade_basis], sector_data[sector][metric_name]["Std"]
    
    grade_map = {"A+": 0, "A": change, "A-" : change * 2, "B+" : change * 3, "B" : change * 4, 
                 "B-" : change * 5, "C+" : change * 6, "C" : change * 7, "C-" : change * 8, 
                 "D+" : change * 9, "D" : change * 10, "D-" : change * 11, "F" : change * 12}
    
    for grade, val in grade_map.items():
        comparison = start + val if lowThan else start - val
       
        if lowThan and metric_val < comparison:
            return grade
        
        elif lowThan == False and metric_val > comparison:
            return grade
            
    return "C"

def get_overall_grade(dataframe, ticker, sector):
    
    global metrics
    
    grade_scores = {'A+' : 4.3, 'A' : 4.0, 'A-' : 3.7, 'B+' : 3.3, 'B' : 3.0, 'B-' : 2.7, 
                    'C+' : 2.3, 'C' : 2.0, 'C-' : 1.7, 'D+' : 1.3, 'D' : 1.0, 'D-' : 0.7, 'F' : 0.0}
    
    metric_grades = []
    
    score = 0

    for metric in metrics:
        
        metric_grades.append(get_metric_grade(dataframe, sector, metric, dataframe.loc[dataframe["Code"] == ticker][metric].values[0]))
        
    for grade in metric_grades:

        score += grade_scores[grade]

    return round(score*3.5, 2)

def getStockRatings(dataframe):
    overall_ratings = []

    for row in dataframe.iterrows():
        ticker, sector = row[1]["Code"], row[1]["Sector"]
        overall_ratings.append(get_overall_grade(dataframe, ticker, sector))

    dataframe["Overall Rating"] = overall_ratings

    return dataframe

def getStockPrice(tickers):
    """ get the stock prices from yfinance for a list of tickers"""

    # from six months ago
    todaysdate = date.today()
    sixmonthago = todaysdate + relativedelta(months=-6)

    #initialize the prices dataframe
    main_df = pd.DataFrame(yf.download(tickers[0], sixmonthago, todaysdate)["Close"], columns=["Close"])
    main_df["Code"] = tickers[0]

    for ticker in tickers[1:]:
        temp_df = pd.DataFrame(yf.download(ticker, sixmonthago, todaysdate)["Close"], columns=["Close"])
        temp_df["Code"] = ticker
        main_df = pd.concat([main_df, temp_df])

    return main_df