from pykrx import stock
import yfinance as yf
from sqlalchemy import create_engine, or_
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, String
from sqlalchemy.orm import sessionmaker
from tqdm import tqdm
import multiprocessing as mp


engine = create_engine('sqlite:///static/db/stock.db?check_same_thread=False', echo=True)
print('stock DB created')
Session = sessionmaker(bind=engine)
session = Session()
Base = declarative_base()

class StockInfo(Base):
    __tablename__ = 'info'
    symbol = Column(String, primary_key=True)
    sector = Column(String)
    website = Column(String)
    industry = Column(String)
    shortName = Column(String)
    longName = Column(String)
    logo_url = Column(String)
    market = Column(String)
    
    def __init__(self, **kwargs):
        self.__dict__.update(kwargs)
    
    def __repr__(self):
        return "<Stock Information('%s')>" % (self.symbol)
Base.metadata.create_all(engine)    
    
    
def ticker2yahoo(symbol, market):
    if market == 'KOSPI':
        return symbol + '.KS'
    elif market == 'KOSDAQ':
        return symbol + '.KQ'
    

def addStockInfo(ticker, market):
    key_lists = ['symbol', 'sector', 'website', 'industry', 'shortName', 'longName', 'logo_url']
    try:
        s = yf.Ticker(ticker)
        info = {k: v for k, v in s.info.items() if k in key_lists}
        info['market'] = market
        if info['shortName']:
            session.add(StockInfo(**info))
        else:
            print(ticker)
    except Exception as e:
        print(f'{ticker}: {e}')
        
    
def addStocksInfo(market):
    symbols = stock.get_market_ticker_list(market=market)
    markets = [market for _ in range(len(symbols))]
    symbols = list(map(ticker2yahoo, symbols, markets))

    for i, symbol in enumerate(tqdm(symbols)):
        addStockInfo(symbol, market)
    session.commit()


def searchStock(sub: str):
    sub = sub.lower()
    search = session.query(StockInfo.symbol, StockInfo.longName).\
        filter(or_(StockInfo.symbol.contains(sub), StockInfo.longName.contains(sub)))
    ret = [[row.symbol, row.longName] for row in search]
    return ret


def allStockInfo():
    allStocks = session.query(StockInfo.symbol, StockInfo.longName)
    ret = [[row.symbol, row.longName] for row in allStocks]
    return ret


if __name__ == '__main__':
    session.add
    manager = mp.Manager()
    markets = ['KOSPI', 'KOSDAQ']
    jobs = []
    for market in markets:
        p = mp.Process(target=addStocksInfo, args=(market, ))
        jobs.append(p)
        p.start()
        
    for proc in jobs:
        proc.join()