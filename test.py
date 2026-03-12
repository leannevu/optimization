import random
import pandas as pd
import numpy as np
import optimization as op
import os

'''
number_list = []
for n in range(5):
    num = random.randint(0,1003)
    number_list.append(num)


print(f'number_list is {number_list}')
stock_names = pd.read_csv('static/stocks_names.csv', header=None)
print(stock_names)
huh = stock_names.iloc[number_list, 0] 
print(huh)

'''
#op_object = op.Optimize()
#ad = op_object.optimize_portfolio()

## generates 5 random stock names
def generateRandomStocks(num_to_generate=5):
    list_rand = []
    for i in range(num_to_generate):
        rand_num = random.randint(1,1003) # use the random library
        list_rand.append(rand_num) # combine random numbers

    file_path = os.path.join(os.path.dirname(__file__), 'static', 'stock_names.csv') # get file path
    stock_names = pd.read_csv(file_path, header=None) # read stock file
    df_to_series = stock_names.iloc[list_rand,0] # filter stock file to 5 random rows
    return df_to_series # return 5 random stock names

def getRandomPortfolio(symbols, dates):
    random_portfolio = getSPYPortfolio('SPY.csv', dates) #start with SPY for accurate dates

    for s in symbols:
        file_path = symbol_to_path(s)
        df_temp =  pd.read_csv(file_path, parse_dates=True, index_col='Date', usecols=['Date','Adj Close'], na_values=['nan'])
        df_temp = df_temp.rename(columns={'Adj Close':s})
        random_portfolio = random_portfolio.join(df_temp)

    random_portfolio.dropna(inplace=True)
    random_portfolio.drop('SPY.csv', axis=1, inplace=True)
    return random_portfolio

def symbol_to_path(symbol, dir='data'):
        file_path = os.path.join(os.path.dirname(__file__), 'static', dir, f'{symbol}')
        return file_path

def getSPYPortfolio(symbol, dates):
    portfolio = pd.DataFrame(index=dates)   

    file_path = symbol_to_path(symbol)
    df_temp =  pd.read_csv(file_path, parse_dates=True, index_col='Date', usecols=['Date','Adj Close'], na_values=['nan'])
    df_temp = df_temp.rename(columns={'Adj Close':symbol})
    portfolio = portfolio.join(df_temp)

    portfolio.dropna(inplace=True)
    return portfolio

    ## generate start and end dates
def get_dates():
    start_date = '2009-12-31'
    end_date = '2010-12-31'

    idx = pd.date_range(start_date, end_date)
    return idx

symbols = generateRandomStocks()
dates = get_dates()

random_porfolio = getRandomPortfolio(symbols, dates)
spy = getSPYPortfolio('SPY.csv', dates)
print(len(random_porfolio))
print('random_porfolio sum: ', random_porfolio.isna().sum())



#print(f'Image: {type(image)} \nAllocs: {type(allocs)} \nComputation: {type(computations)} \nSymbols: {type(symbols)}')
