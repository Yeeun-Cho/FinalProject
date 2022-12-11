from datetime import datetime
from time import mktime  
from flask import Flask, render_template, jsonify, request
import requests
# import exchange_calendars as xcals
from datetime import datetime
from stock import searchStock, allStockInfo

app = Flask(__name__)
# app.config['SQLALCHEMY_DATABASE_URL'] = 'sqlite:///static/db/stock.db' # db path
# db = SQLAlchemy(app)


def _get_crumbs_and_cookies(ticker):
    """
    get crumb and cookies for historical data csv download from yahoo finance
    parameters: stock - short-handle identifier of the company 
    returns a tuple of header, crumb and cookie
    """
    
    url = 'https://finance.yahoo.com/quote/{}/history'.format(ticker)
    with requests.session():
        header = {'Connection': 'keep-alive',
                   'Expires': '-1',
                   'Upgrade-Insecure-Requests': '1',
                   'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) \
                   AppleWebKit/537.36 (KHTML, like Gecko) Chrome/54.0.2840.99 Safari/537.36'
                   }
        
        website = requests.get(url, headers=header)

        return (header, website.cookies)


def convert_to_unix(date):
    """
    converts date to unix timestamp
    
    parameters: date - in format (dd-mm-yyyy)
    
    returns integer unix timestamp
    """
    datum = datetime.strptime(date, '%Y-%m-%d')
    
    return int(mktime(datum.timetuple()))

  

def load_csv_data(ticker, interval='1d', period1='1990-01-01', period2=datetime.today().strftime('%Y-%m-%d')):
    """
    queries yahoo finance api to receive historical data in csv file format
    
    parameters: 
        stock - short-handle identifier of the company
        
        interval - 1d, 1wk, 1mo - daily, weekly monthly data
        
        day_begin - starting date for the historical data (format: dd-mm-yyyy)
        
        day_end - final date of the data (format: dd-mm-yyyy)
    
    returns a list of comma seperated value lines
    """
    
    header, cookies = _get_crumbs_and_cookies(ticker)
    
    period1 = convert_to_unix(period1)
    period2 = convert_to_unix(period2)
    
    with requests.session():
        url = 'https://query1.finance.yahoo.com/v7/finance/download/' \
              '{ticker}?period1={period1}&period2={period2}&interval={interval}' \
              .format(ticker=ticker, period1=period1, period2=period2, interval=interval)
                
        website = requests.get(url, headers=header, cookies=cookies)
        return website.text.split('\n')[1:-1]  # not include 0: Date,Open,High,Low,Close,AdjClose,Volume

def modifyStock(string):
    date, open, high, low, close, _, volume = string.split(',')
    try:
        open = int(float(open))
    except ValueError:
        print(string)
        exit()
        
    high = int(float(high))
    low = int(float(low))
    close = int(float(close))
    volume = int(float(volume))
    return {'time': date, 'open': open, 'high': high, 'low': low, 'close': close, 'value': volume}


def nullCheck(string):
    data = string.split(',')
    if 'null' in data:
        return False
    elif float(data[-1]) == 0:
        return False
    else:
        return True
    

## HTML 화면 보여주기
@app.route('/')
def home():
    return render_template('home.html')

# @app.route('/chart')
# def homework():
#     return render_template('chart.html')

@app.route('/chart')
def chart():
    return render_template('chart.html')

@app.route('/stock', methods=['post'])
def stockData():
    ticker = request.form.get('ticker')
    timeframe = request.form.get('timeframe')
    stock = load_csv_data(ticker, interval=timeframe)
    print(stock, timeframe)
    # df = stock.get_market_ohlcv(ticker, fromdate='1990-01-01', todate=today)
    stock = list(filter(nullCheck, stock))
    stock = list(map(modifyStock, stock))
    doc = {'stock': stock}
    return jsonify(doc)

@app.route('/search', methods=['post'])
def search():
    sub = request.form.get('sub')
    search = searchStock(sub)
    doc = {'search': search}
    return jsonify(doc)

@app.route('/info', methods=['post'])
def info():
    allStocks = allStockInfo()
    doc = {'allStocks': allStocks}
    return jsonify(doc)
    
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080, debug=True, threaded=True)