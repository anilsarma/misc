import requests
import pandas as pd
import numpy as np
from bs4 import BeautifulSoup as bs
import re
import html
import datetime

import io

class YahooFinance:

    url_base = "https://finance.yahoo.com/quote/{}"
    # start_epoch, end_epoch, event, crumb, interval
    url_hist_base = "https://query1.finance.yahoo.com/v7/finance/download/{symbol}?period1={start_epoch}&period2={end_epoch}&interval={interval}&events={event}&crumb={crumb}"
    def __init__(self):
        self.url_symbol = None
        #elf.symbol = None
        self.cookies = None
        self.crumb = None

    def init(self, symbol):
        #self.start_date = pd.to_datetime(start_date)#.replace(hour=0, minute=0, second=0)

        self.url_symbol = YahooFinance.url_base.format(symbol)
        #self.symbol = symbol
        #print(self.url_symbol," startdate=", YahooFinance.get_epoch(self.start_date), self.symbol)
        with  requests.get(self.url_symbol) as response:
            print(response.cookies)
            for x in response.cookies:
                print("Entries", x.name, x.value)
            self.cookies = response.cookies
            text = response.text

            # find this pattern "CrumbStore": {"crumb": "DCtHapvvNjt"}, "
            pat = re.compile('CrumbStore":{"crumb":"(.+?)"},')
            matcher = pat.findall(text)
            if matcher is None:
                raise Exception("cannot find crumb in the stream")
            self.crumb = html.unescape(matcher[0])
            self.crumb = self.crumb.replace(u"\\u002F", "/")


        print (self.crumb, self.cookies)

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
        #print(url)
        cookies = { x.name: x.value for x in self.cookies }
        response = requests.get(url, cookies=cookies)
        df = pd.read_csv(io.StringIO(response.text))
        df.loc[:, 'Symbol']=symbol
        return df

    def get_historical(self, symbol, start_date, end_date=None, interval="1d"):
        return self.get_hist_data(symbol, start_date, end_date, event="history", interval=interval)

    def get_historical_div(self, symbol, start_date, end_date=None):
        return self.get_hist_data(symbol, start_date, end_date, event="div", interval="1d")

    def get_historical_split(self, symbol, start_date, end_date=None):
        return self.get_hist_data(symbol, start_date, end_date, event="split    ", interval="1d")

    def get_details(self, symbol):
        if self.crumb is None:
            self.init(symbol)
        url_symbol = YahooFinance.url_base.format(symbol)
        cookies = {x.name: x.value for x in self.cookies}
        response = requests.get(url_symbol, cookies=cookies)
        parser = bs(response.text, 'html.parser')

        tags = ["PREV_CLOSE-value", "OPEN-value", "BID-value", "ASK-value", "TD_VOLUME-value", "AVERAGE_VOLUME_3MONTH-value"]
        for t in tags:
            td = parser.find("td", { "data-test": t})
            print (t, "=", td.find("span").string)

        tags = ["DAYS_RANGE-value", "FIFTY_TWO_WK_RANGE-value"]
        for t in tags:
            td = parser.find("td", { "data-test": t})
            print (t, "=", td.string)

if __name__ == "__main__":
    y = YahooFinance()
    #df = y.get_historical("2012.02.28", "2020.02.28")
    #print(df)
    y.get_details("AAPL")
    df = y.get_historical("AAPL","1970.02.28")