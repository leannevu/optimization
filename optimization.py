import numpy as np
import matplotlib
matplotlib.use('Agg')   # use non-GUI backend
import matplotlib.pyplot as plt
import pandas as pd
import scipy.optimize as spo
import os
import random
import io
import base64


class Optimize():

    #def __init__(self):
        #don't have anything for constructor  		

    ## generates 5 random stock names
    def generateRandomStocks(self, num_to_generate=5):
        list_rand = []
        for i in range(num_to_generate):
            rand_num = random.randint(1,1003) # use the random library
            list_rand.append(rand_num) # combine random numbers

        file_path = os.path.join(os.path.dirname(__file__), 'static', 'stock_names.csv') # get file path
        stock_names = pd.read_csv(file_path, header=None) # read stock file
        df_to_series = stock_names.iloc[list_rand,0] # filter stock file to 5 random rows
        return df_to_series # return 5 random stock names

    ## generate start and end dates
    def get_dates(self):
        start_date = '2009-12-31'
        end_date = '2010-12-07'

        idx = pd.date_range(start_date, end_date)
        return idx

    def symbol_to_path(self, symbol, dir='data'):
        file_path = os.path.join(os.path.dirname(__file__), 'static', dir, f'{symbol}')
        return file_path
    
    def getRandomPortfolio(self, symbols, dates):
        random_portfolio = self.getSPYPortfolio('SPY.csv', dates) #start with SPY for accurate dates
    
        for s in symbols:
            file_path = self.symbol_to_path(s)
            df_temp =  pd.read_csv(file_path, parse_dates=True, index_col='Date', usecols=['Date','Adj Close'], na_values=['nan'])
            df_temp = df_temp.rename(columns={'Adj Close':s})
            random_portfolio = random_portfolio.join(df_temp)

        random_portfolio.dropna(inplace=True)
        random_portfolio.drop('SPY.csv', axis=1, inplace=True)
        return random_portfolio
    
    def getSPYPortfolio(self, symbol, dates):
        portfolio = pd.DataFrame(index=dates)   

        file_path = self.symbol_to_path(symbol)
        df_temp =  pd.read_csv(file_path, parse_dates=True, index_col='Date', usecols=['Date','Adj Close'], na_values=['nan'])
        df_temp = df_temp.rename(columns={'Adj Close':symbol})
        portfolio = portfolio.join(df_temp)

        portfolio.dropna(inplace=True)
        return portfolio





    def optimize_portfolio(self):
        symbols = self.generateRandomStocks()
        dates = self.get_dates()
        random_porfolio = self.getRandomPortfolio(symbols, dates)

        while (len(random_porfolio) < 50): ## not necessary
            random_porfolio = self.getRandomPortfolio(symbols, dates)
        
        SPY_portfolio = self.getSPYPortfolio('SPY.csv', dates)
    
        num_allocs = len(random_porfolio.columns)
        allocGuess = np.ones(num_allocs)
        allocGuess = allocGuess * (1 / num_allocs)

        # Bounds: each allocation between 0 and 1
        bounds = [(0.0, 1.0)] * num_allocs #match args size
        result = spo.minimize(fun=lambda x, d: self.maximize_sharp_ratio(x, d), x0=allocGuess, args=(random_porfolio,), method = 'SLSQP', options={'disp': False},
                            bounds=bounds, constraints = ({'type': 'eq', 'fun': lambda x: 1 - np.sum(x)})) #change 50 to 1- constraint allocs to sum to 1

        optimal_allocs = result.x #get 'x' values the minimizer function returns


        # get statistics using the new optimal portfolio
        cr, adr, sddr, sr = self.compute_returns(random_porfolio, optimal_allocs)
        results = [cr, adr, sddr, sr]

        ## Compare daily optimal portfolio values and SPY values, using a normalized plot
        port_val = self.normalize_portfolio(random_porfolio, optimal_allocs)
        SPY_val = self.normalize_prices(SPY_portfolio)

        #make data ranges the same
        df_dateranges = pd.DataFrame(index=pd.date_range('2009-12-31', '2010-12-31'))
        port_val_all_dates = df_dateranges.join(port_val)
        SPY_val_all_dates = df_dateranges.join(SPY_val)

        #fill empty data
        port_val_all_dates.ffill(inplace=True)
        port_val_all_dates.bfill(inplace=True)
        SPY_val_all_dates.ffill(inplace=True)
        SPY_val_all_dates.bfill(inplace=True)

        plt.plot(port_val_all_dates, label='Portfolio')
        plt.plot(SPY_val_all_dates, label='SPY')
        plt.legend()
        # Naming the x-axis, y-axis and the whole graph
        plt.margins(x=0) #https://matplotlib.org/stable/gallery/subplots_axes_and_figures/axes_margins.html#sphx-glr-gallery-subplots-axes-and-figures-axes-margins-py
        plt.xlabel("Date")
        plt.ylabel("Price")
        plt.title("Optimized Daily Porfolio Value and SPY")

        # Save plot to a buffer
        buf = io.BytesIO() 
        plt.savefig(buf, format='png')
        plt.close()
        buf.seek(0)
        #Encode as base64
        encoded = base64.b64encode(buf.read()).decode('utf-8')
        buf.close()

        symbols = symbols.str.replace('.csv', '', regex=False).tolist()
        results = {
            'encoded_image' : f'data:image/png;base64,{encoded}',
            'allocs' : np.round(optimal_allocs, 6).tolist(),
            'computations' : [
                cr, 
                adr, 
                sddr, 
                round(sr, 6)
            ],
            'symbols' : symbols
        }

        return results
        
    def compute_returns(self, df, allocs):
        start_val = 1000000

        #rename df as prices for clarity; use for normed, alloced, pos_vals, and port_vals
        prices = df.astype('float64') # make sure data type is not issue

        # ensure is np array
        allocations = np.asarray(allocs).ravel()

        #normed, alloced, pos_vals, and port_vals
        normed = prices / prices.iloc[0] #normalize
        alloced = normed * allocations  #split allocations
        pos_vals = alloced * start_val #get values
        port_val = pos_vals.sum(axis=1) #get portfolio value

        #calculate daily returns; use for SR, using port_val
        daily_rets = (port_val[1:] / port_val[:-1].values) - 1 #already drops the first column

        #following used for portfolio statistics
        cum_ret = ((port_val.iloc[-1]/port_val.iloc[0]) - 1) 
        avg_daily_ret = daily_rets.mean(axis=0) 
        std_daily_ret = daily_rets.std(axis=0) #pandas defaults to standard deviation, whereas numpy defaults to population standard deviation
        
        k = 252
        SR = np.sqrt(k) * ((avg_daily_ret) / (std_daily_ret)) #removed the daily_rf, multiple by negative 1 for "minimum" aspect
        return round(cum_ret, 6), round(avg_daily_ret, 6), round(std_daily_ret, 6), round(SR, 6)	

    ## "error function" , SciPy minimize function will find allocations that contribute to the possible minimum sharp error
    def maximize_sharp_ratio(self, allocs, data): 
        start_val = 1000000

        #rename df as prices for clarity; use for normed, alloced, pos_vals, and port_vals
        prices = data.astype('float64') # make sure data type is not issue

        # ensure is np array
        allocations = np.asarray(allocs).ravel()

        #normed, alloced, pos_vals, and port_vals
        normed = prices / prices.iloc[0] #normalize
        alloced = normed * allocations  #split allocations
        pos_vals = alloced * start_val #get values
        port_val = pos_vals.sum(axis=1) #get portfolio value

        #calculate daily returns; use for SR, using port_val
        daily_rets = (port_val[1:] / port_val[:-1].values) - 1 #already drops the first column

        #following used for portfolio statistics
        cum_ret = ((port_val.iloc[-1]/port_val.iloc[0]) - 1) 
        avg_daily_ret = daily_rets.mean(axis=0) 
        std_daily_ret = daily_rets.std(axis=0) #pandas defaults to standard deviation, whereas numpy defaults to population standard deviation
        
        k = 252
        SR = np.sqrt(k) * ((avg_daily_ret) / (std_daily_ret)) * -1 #removed the daily_rf, multiple by negative 1 for "minimum" aspect
        return SR

    def normalize_prices(self, df):
        start_val = 1
        prices = df.astype('float64')  # make sure data type is not issue
        # normed, alloced, pos_vals, and port_vals
        normed = prices / prices.iloc[0]  # normalize
        normed = normed * start_val

        return normed

    def normalize_portfolio(self, df, allocs):
        #rename df as prices for clarity; use for normed, alloced, pos_vals, and port_vals
        start_val = 1
        prices = df.astype('float64') # make sure data type is not issue

        # ensure is np array
        allocations = np.asarray(allocs).ravel()

        #normed, alloced, pos_vals, and port_vals
        normed = prices / prices.iloc[0] #normalize
        alloced = normed * allocations  #split allocations
        pos_vals = alloced * start_val #get values
        port_val = pos_vals.sum(axis=1) #get portfolio value

        result = port_val
        result = result.rename('Normalized Portfolio')
        return result

