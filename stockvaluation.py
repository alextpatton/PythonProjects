from bs4 import BeautifulSoup
from html.parser import HTMLParser
import csv, re, urllib.parse, urllib.request, os.path

class stockvaluation(object):
    ticker = ''
    tickers = ''
    buylist = []
    #guru
    GURU = ''
    BVG_5 = 0
    #yahoo
    YAHOO_CSV = 'http://finance.yahoo.com/d/quotes.csv'
    YAHOO_SYMBOLS = [{'ask':'a'},{'bookvalue':'b4'},{'open':'o'},{'EPS':'e'},{'EPS Current':'e7'},{'Last Trade':'l1'},{'P/E':'r'},{'Name':'n'}]
    YAHOO_f = ''
    YAHOO_V = ''
    EPS = 0
    PRICE = 0
    PE = 0
    NAME = 0
    
    #msn
    MSN = ''
    EPSG_5 = 0
    #calculations
    F_PE = 0
    lowest_growth = 0
    def enterTicker(self, arg=False):
        if arg:
            self.ticker = ticker = arg
        else:    
            self.ticker = ticker = input('Enter a Ticker: ')
        self.GURU = 'http://www.gurufocus.com/financials/'+ticker
        self.MSN = 'http://investing.money.msn.com/investments/key-ratios?symbol='+ticker
        for s in self.YAHOO_SYMBOLS:
            for key in s:
                self.YAHOO_f+=s[key]
        self.YAHOO_V = {'s':ticker,'f':self.YAHOO_f}
    #Load tickers from txt file: tickers.txt
    def loadTickerFile(self):
        file = open('tickers.txt','r', encoding='utf-8')
        read = file.read()
        self.tickers = sorted(read.split(','))
        file.close()
    #look up tickers one by one    
    def batchProcessTickers(self):
        #create new file
        inc = 0
        filename = 'results.txt'
        while(os.path.isfile(filename)):
            inc+=1
            filename = 'results'+str(inc)+'.txt'
        file = open(filename,'a')
        #get count of number of tickers being processed
        count = len(self.tickers)
        it = 0
        for ticker in self.tickers:
            it+=1
            print('CHECKING: '+ticker+' ('+str(it)+'/'+str(count)+')')
            self.enterTicker(ticker)
            stats = self.runCalculations()
            if str(stats[1]['Price']) == '0.00':
                print('TICKER ERROR FOR '+ticker)
            file.write("\n")
            file.write(ticker)
            file.write("\n")
            for i in stats:
                for k, v in i.items():
                    file.write(k +': '+str(v)+"\n")
                    if v == 'BUY - GOOD VALUE':
                        self.buylist.append(ticker)
            file.write('-----------------------------------\n')
        file.write('\nBuy List: ')    
        for item in self.buylist:
            file.write(item+', ')
        print('Saved to File: '+filename)    
        file.close()        
            
    #return the response from Guru
    def guruRead(self):
        req = urllib.request.Request(self.GURU)
        response = urllib.request.urlopen(req)
        return response.read().decode('utf-8')
    
    #return the response from Yahoo
    def yahooCSV(self):
        url = self.YAHOO_CSV+'?s='+self.ticker+'&f='+self.YAHOO_V['f']
        req = urllib.request.Request(url)
        response=urllib.request.urlopen(req)
        rr = response.read().decode('utf-8')
        sp = rr.split(',')
        try:
            self.EPS = float(sp[3])
        except:
            self.EPS = 0 
        self.PRICE = sp[5]
        self.PE = sp[6]
        self.NAME = sp[7]
        return sp
    
    #return MSN data
    def MSNRead(self):
        req = urllib.request.Request(self.MSN)
        response = urllib.request.urlopen(req)
        return response.read().decode('utf-8')
    
    #return the Growth Book Value Per Share
    def GBVPS(self):
        rr = self.guruRead()
        soup = BeautifulSoup(rr)
        tables = soup.findChildren('table')
        try:
            soup = BeautifulSoup(str(tables[1]))
            td = soup.findChildren('td')
            data = str(td[19])
            oneyear = re.sub('<[^<]+?>', '', data)
            data = str(td[18])
            fiveyear = self.BVG_5 = re.sub('<[^<]+?>', '', data)
            data = str(td[17])
            tenyear = re.sub('<[^<]+?>', '', data)
            return [tenyear,fiveyear,oneyear]
        except:
            return ['ERROR',0,'ERROR']
    
    #return Net income Growth
    def EPSGrowth(self):
        rr = self.MSNRead()
        soup = BeautifulSoup(rr)
        tables = soup.findChildren('table')
        try:
            soup = BeautifulSoup(str(tables[0]))
            td = soup.findChildren('td')
            #netincome td[14]
            data = str(td[14])
            net = re.sub('<[^<]+?>', '', data)
            net = self.EPSG_5 = net.strip()
            return net
        except:
            return 0
    
    #return lowest growth metric
    def lowestGrowth(self):
        try:
            BVG = float(self.BVG_5)
            EPSG = float(self.EPSG_5)
            return [['Book Value Growth',BVG],['Net Income Growth',EPSG]]
        except:
            return [['Book Value Growth',0],['Net Income Growth',0]]

    #return future pe
    def futurePrice(self):
        lglist = self.lowestGrowth()
        one = lglist[0][1]
        two = lglist[1][1]
        pe = 2*float(one)
        futureeps = float(self.EPS) * (1+float(one)/100)**10
        pe2 = 2*float(two)
        future2 = float(self.EPS) * (1+float(two)/100)**10
        futureprice = pe*futureeps
        futureprice2 = pe2*future2
        return [futureprice,futureprice2]
    #make all queries and calculations together
    def runCalculations(self):
        eps = self.yahooCSV()
        gbvps = self.GBVPS()
        epsg = self.EPSGrowth()
        lowest = self.lowestGrowth()
        fp = self.futurePrice()
        fp1 = fp[0]
        fp2 = fp[1]
        rating = ''
        if fp1/8>float(self.PRICE) or fp2/8>float(self.PRICE):
            rating = 'BUY - GOOD VALUE'
        else:
            rating = "DON'T BUY - OVER PRICED"
        return [{'Name':self.NAME},{'Price':self.PRICE},{'EPS':self.EPS},{'P/E':self.PE},{'GBVPS_5':gbvps[1]},{'Growth Metrics':lowest},{'Future Price': fp},{'Buy Price': [fp1/8,fp2/8]},{'Rating':rating}]  
    #print all returned values
    def printall(self):
        eps = self.yahooCSV()
        gbvps = self.GBVPS()
        epsg = self.EPSGrowth()
        lowest = self.lowestGrowth()
        fp = self.futurePrice()
        fp1 = fp[0]
        fp2 = fp[1]
        rating = ''
        if fp1/8>float(self.PRICE) or fp2/8>float(self.PRICE):
            rating = 'BUY - GOOD VALUE'
        else:
            rating = "DON'T BUY - OVER PRICED"
        print(self.NAME)
        print('Price: {} EPS: {} P/E: {}'.format(self.PRICE,self.EPS,self.PE))
        print('Book Value (%)Growth')
        print('10year 5year 1year')
        print(str(gbvps[0])+'% '+str(gbvps[1])+'% '+str(gbvps[2])+'%')
        print('Net Income Growth (%) 5 year avg')
        print(str(self.EPSG_5)+'%')
        print('Growth Metrics')
        print(str(lowest[0])+': '+str(lowest[1]))
        print('10 Year Future Price')
        print(str(fp1) +' Or '+str(fp2))
        print('15% return (Future Price/4)')
        print(str(fp1/4)+' Or '+str(fp2/4))
        print('Buy Price')
        print(str(fp1/8)+' Or '+str(fp2/8))
        print(self.ticker +' - '+ rating)
        print('--------------------')
#MAIN        
test = stockvaluation()
iput = input('SINGLE or BATCH? ')
if iput == 'BATCH':
    test.loadTickerFile()
    test.batchProcessTickers()
else:    
    while(True):
        test.enterTicker()
        test.printall()


        
        

        
        
        
