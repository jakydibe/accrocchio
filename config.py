##############################################################
############################################################################
#Dati Immutabili
STRATEGIE = ["Fibo_harsi","Fibo_harsi_ema200","Rsi","Vwap_volume_profile","vwap_rsi",'order_blocks_strategy']
TIMEFRAMES = ['5m','1h','4h']#,'1h']#,'4h','1d','1w']
PERIOD_TIMEFRAMES = {'1m': 60*1000, '3m': 180*1000, '5m': 300*1000, '15m': 300*1000*5, '1h': 3600*1000, '4h': 4*3600*1000, '1d': 3600*24*1000,'1w':3600*24*1000*7} 
#PATH_TO_CONFIG
PATH_TO_CONFIG = ""

#APIKEY APISECRET JACOPO
#API_KEY='dQRhKwqbLhK1qeKx8jCDH9JgHcxyqROsbSd7Dgleyw08g26RFHMnsn8F6BhtjiBP'
#API_SECRET='7XBq5kHQZncvnVlcQ2ABPGQFoZWmNbi5WvMjTCqyN8qhuFBHJdSFH7Rmt6lYKEAR'

#APIKEY APISECRET GI
API_KEY='n4gyhV4S8DQtp1aLDHmNTCfkvWdFbEsLs3XOcPoJEHFImaEJOlcBVesua8kqr9Mn'
API_SECRET='oRjsCtDFDeQyl4uXuWAwimGKpw84lMYG1IZw2wX8wSHVtGIYI3EHZa0NHjaNm5Ik'

#CRYPTO SCANNER
CS_TRADING_PERIOD = 10
CS_TIME_FRAME = '5m'
CS_PAST_DATA = 500

#SETUP
TEST=True
SOLDI_MIEI = 30.0
EXCHANGE_TOKENS = ['USDT','BUSD']
TIME_FRAME = ['5m']
STRATEGIE_SCELTE = ["Rsi"]
NUM_CRYPTO = 20
MAX_TRADE = 2
MAX_DURATA = 60*60*24 #24 ore
REFRESH_SOCKET = 60*20
PAST_DATA=500

TAKE_PROFIT=0.015
STOP_LOSS=0.01

#STRATEGIE


#GRAFICO
KLINE_PERC = True
KLINE_WIDTH = 8
KLINE_SPACE = 4
LOAD_KLINE = 200
REFRESH_RATE=1000

#INDICATORI
#vwap
DEVIAZIONE_STD_VWAP = 2.13
#Fibonacci
FIBO_PERIOD=20
#HARSI
I_SMOOTHING=4

NUMERO_BARRE = 35

RSI_OVERBOUGH=70
RSI_OVERSOLD=30



############################################
#OBIETTIVI PER OGGI DEL BOT:
## 1- disegnare gli indicatori sul grafico, aggiustare il problema del grafico
## 2- provare trading automatizzato
## 3-
## 
## 8- grinding strategie e indicatori
## 9- trovare strategia trend following low win rate,, really gud risk/reward ratio (1:10-1:20)
##
##
