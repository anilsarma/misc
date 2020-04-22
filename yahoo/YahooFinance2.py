import datetime
import html
import io
import re
import numpy as np
import pandas as pd
import requests
from bs4 import BeautifulSoup as bs
import json

class YahooFinance:

    #url_base = "https://finance.yahoo.com/quote/{}"
    # start_epoch, end_epoch, event, crumb, interval
    url_hist_base = "https://query1.finance.yahoo.com/v7/finance/download/{symbol}?period1={start_epoch}&period2={end_epoch}&interval={interval}&events={event}&crumb={crumb}"
    url_base = "https://query1.finance.yahoo.com//v8/finance/chart/{symbol}?symbol={symbol}&interval={interval}"
    def __init__(self, **kwargs):
        self.url_symbol = None
        #elf.symbol = None
        self.cookies = None
        self.crumb = None
        self.summary = {}
        self.kwargs = kwargs
        self.query_time = None
        self.meta = None
        self.df = {}
        self.close = None
        self.last_price = None

    def clear(self):
        self.crumb = None
        self.cookies = None

    def init(self, symbol, interval="1h", args=None, **kwargs):
        self.kwargs = {}
        #self.start_date = pd.to_datetime(start_date)#.replace(hour=0, minute=0, second=0)

        self.url_symbol = YahooFinance.url_base.format(symbol=symbol, interval=interval, **kwargs)
        if args is not None:
            self.url_symbol = self.url_symbol + args
        #self.symbol = symbol
        #print(self.url_symbol," startdate=", YahooFinance.get_epoch(self.start_date), self.symbol)
        if not kwargs :
            kwargs = self.kwargs
        with  requests.get(self.url_symbol, **kwargs) as response:
            #print(response.cookies)
            #for x in response.cookies:
            #    print("Entries", x.name, x.value)
            self.cookies = response.cookies
            text = response.text

            # find this pattern "CrumbStore": {"crumb": "DCtHapvvNjt"}, "
            pat = re.compile('CrumbStore":{"crumb":"(.+?)"},')
            matcher = pat.findall(text)
            if matcher is None:
                raise Exception("cannot find crumb in the stream")

            print(matcher)
            print(text)
            self.crumb = None
            if len(matcher) >0:
                self.crumb = html.unescape(matcher[0])
                self.crumb = self.crumb.replace(u"\\u002F", "/")

            #high, low, volume, open, close
            chart =  json.loads(text)
            data = chart['chart']['result'][0]['indicators']['quote'][0]
            timestamp = chart['chart']['result'][0]['timestamp']
            meta = chart['chart']['result'][0]['meta']

            self.close = meta['previousClose']
            self.last_price = meta['regularMarketPrice']
            print(self.close, self.last_price)

            ts = pd.to_datetime(timestamp, unit='s').tz_localize("utc").tz_convert("US/Eastern").tz_localize(None)
            ts.name = "date"
            df = pd.DataFrame(data)
            df.index = ts
            self.df = df
            self.meta = meta
            # chart previousClose regularMarketPrice
            #json.loads(text)['chart']['result'][0]

        print (datetime.datetime.now(), self.crumb, self.cookies)

    @staticmethod
    def get_epoch(datetime):
        return int((pd.to_datetime(datetime)- pd.Timestamp("1970-01-01")).total_seconds())




    def get_hist_data(self, symbol, start_date, end_date = None, event="history", interval="1d"):
        if self.crumb is None:
            self.init(symbol)
        start_date = pd.to_datetime(start_date)
        if end_date is None:
            end_date = pd.to_datetime(datetime.datetime.now())
            end_date = pd.to_datetime(end_date)
        url = YahooFinance.url_hist_base.format(start_epoch=YahooFinance.get_epoch(start_date),
                                                end_epoch=YahooFinance.get_epoch(end_date),
                                                symbol=symbol,
                                                event=event, crumb=self.crumb, interval=interval)

        cookies = { x.name: x.value for x in self.cookies }
        response = requests.get(url, cookies=cookies, *self.kwargs)
        df = pd.read_csv(io.StringIO(response.text))
        df.loc[:, 'Symbol']=symbol
        return df

    def get_historical(self, symbol, start_date, end_date=None, interval="1d"):
        return self.get_hist_data(symbol, start_date, end_date, event="history", interval=interval)

    def get_historical_div(self, symbol, start_date, end_date=None):
        return self.get_hist_data(symbol, start_date, end_date, event="div", interval="1d")

    def get_historical_split(self, symbol, start_date, end_date=None):
        return self.get_hist_data(symbol, start_date, end_date, event="split    ", interval="1d")

    def get_details(self, symbol, timedelta=None):
        if self.meta is None : #or self.cookies.is_expired():
            self.init(symbol)

        if timedelta is not None and self.query_time is not None:
            diff = pd.to_datetime(datetime.datetime.now()) - self.query_time
            if diff < timedelta:
                return

        self.init(symbol)
        return self.meta

    def get_query_time(self):
        return self.query_time

    def get_tuple_value(self, symbol, key, token=None):
        if not self.meta:
            self.init(symbol)
        return self.meta[key]

    def to_float(self, v):
        try:
            if isinstance(v, str):
                v = v.replace(",", "")
            return float(v)
        except:
            pass
        return np.nan

    def to_int(self, v):
        try:
            if isinstance(v, str):
                v = v.replace(",", "")
            if isinstance(v, float):
                return v
            return int(v)
        except:
            pass
        return 0

    def get_last_price(self, symbol):
        return self.to_float(self.get_tuple_value(symbol, "regularMarketPrice"))

    def get_bid(self, symbol):
        return self.get_tuple_value(symbol, "regularMarketPrice", "x")

    def get_ask(self, symbol):
        return self.get_tuple_value(symbol, "regularMarketPrice", "x")

    def get_open_price(self, symbol):
        if not self.meta:
            self.init(symbol)
        return self.df.iloc[0]['open']

    def get_prev_close(self, symbol):
        if not self.meta:
            self.init(symbol)
        return self.meta["previousClose"]

    def get_thirty_day_volume(self, symbol):
        return self.to_float(self.get_tuple_value(symbol, "TD_VOLUME-value").replace(",", ""))

    def get_close_status(self, symbol):
        if self.crumb is None:
            self.init(symbol)
        if not self.summary:
            self.get_details(symbol)
        return self.summary['CLOSED']

if __name__ == "__main__":
    #https://query1.finance.yahoo.com//v8/finance/chart/AAPL?interval=1m&period1=1583283028&period2=1583887828
    y = YahooFinance( )
    y.init("AAPL",interval="1m", args="&period1=1583283028&period2=1583887828&includePrePost=true")

    y.df.to_csv("AAPL.csv")

    #https://stackoverflow.com/questions/44030983/yahoo-finance-url-not-working
    #https://query1.finance.yahoo.com/v10/finance/quoteSummary/AAPL?modules=assetProfile%2CearningsHistory
    #df = y.get_historical("2012.02.28", "2020.02.28")
    #print(df)
    y.get_details("AAPL")
    #df = y.get_historical("AAPL","1970.01.01")
    #df.loc[:, "30D"] = df.Volume.rolling(window=30).mean().fillna(0).astype(int)

    #print(df.head(60))

    print(y.get_bid("AAPL"), y.get_ask("AAPL"))
    print("CLOSE", y.get_prev_close("AAPL"))
    print("OPEN", y.get_open_price("AAPL"))
    print("LAST", y.get_last_price("AAPL"))
    #print(y.get_thirty_day_volume("AAPL"))