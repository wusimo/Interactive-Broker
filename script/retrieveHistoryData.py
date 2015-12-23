import urllib

base_url = "http://ichart.finace.yahoo.com/table/scv?s="
def make_url(ticker_symbol):
    return base_url + ticker_symbol

output_path = "./"
def maek_filename(ticker_symbol,directory = "S&P")
    return output_path + directory + "/" +ticker_symbol +".csv"

def pull_historical_data(ticker_symbol,directory = "S&P"):
    try:
        urllib.retrieve(make_url(ticker_symbol),make_filename(ticker_symbol,directory))
    except urllib.ContentTooShorError as e:
        outfile = open(make_filename(ticker_symbol,directory),"w")
        outfile.write(e.content)
        outfile.close()
