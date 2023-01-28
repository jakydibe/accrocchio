import ccxt.pro as ccxtpro
from datetime import datetime
from joblib import Parallel, delayed
import asyncio, json, time, os

from indicatori_func import calcolo_indicatori
from crypto_scanner import crypto_finder
import config, strategie

STRATEGIE= ["vwap_3","supertrend_strat"]

def create_dict(symbol, klines):
    try:
        swag_dict = {}
        for tf in config.TIMEFRAMES:
            dict = {'time':[], 'open':[], 'high':[], 'low':[],'close':[], 'volume':[],
                'comprato_passato':10, 'pc':[], 'cross_index':[],
                'take_profit':0.0, 'stop_loss':0.0,
            
                'volume_medio':[], 'ema5':[],'ema11':[],'ema15':[],'ema18':[],'ema21':[],'ema24':[],'ema28':[],'ema34':[],
                'ema200':[], 'distanza_perc_ema200':[],
                'fibo':[], 'fibo_r1':[], 'fibo_r2':[], 'fibo_r3':[],
                'vwap':[], 'vwap_stdev':[],'vwap_1_p':[],'vwap_1_m':[],'vwap_3_p':[],'vwap_3_m':[], 'volume_ma_std30':[], 'canali_volume':{},
                'ha_open':[], 'ha_close':[], 'ha_high':[], 'ha_low':[],
                'lbox':[],'sbox':[],'rsi':[],'atr':[],'supertrend':[],} 
        
            for kline in klines[tf]:
                dict['time'].append(int(kline[0]))
                dict['open'].append(float(kline[1]))
                dict['high'].append(float(kline[2]))
                dict['low'].append(float(kline[3]))
                dict['close'].append(float(kline[4]))
                dict['volume'].append(float(kline[5]))

                calcolo_indicatori(dict, True) 

            swag_dict[tf] = dict
    except Exception as e:
        print("Errore in create_dict(): {}".format(e))
    
    return symbol, swag_dict

class Bot():
    def __init__(self) -> None:
        self.core_dict = {}

        self.exchange = ccxtpro.binanceus()
        self.exchange.enableRateLimit = True

        self.symbols = ['BTCUSDT','ETHUSDT']
        #self.symbols = ['ETHUSDT']
        #asyncio.run(crypto_finder(self, print, config.EXCHANGE_TOKENS, config.NUM_CRYPTO, 'Rsi/volume'))

        self.strat_dict = {symbol: {tf: {strat: False for strat in STRATEGIE} for tf in config.TIMEFRAMES} for symbol in self.symbols}
        # for symbol in self.symbols:
        #     self.strat_dict[symbol] = {}
        #     for tf in config.TIMEFRAMES:
        #         self.strat_dict[symbol][tf] = {}

        self.strat_dict['to_buy'] = []


    async def fetch_klines(self, symbol, timeframe, limit):
        candles = await self.exchange.fetch_ohlcv(symbol=symbol, timeframe=timeframe, limit=limit)
        return timeframe, candles

    def clear_dict(self,dict):

        for s in self.symbols:
            for tf in config.TIMEFRAMES:
                for i in dict[s][tf].keys():
                    dict[s][tf][i] = []

    async def open_trading_session(self):
        try:
            self.core_dict = {}

            print("NUM_CRYPTO: {}".format(config.NUM_CRYPTO))

            print(f'\nTrading Symbols: {self.symbols}\n\n')

            start = datetime.now()
            print('start time {}'.format(start))    
            
            print('Loading Symbols 10%')
            pb=0.1
            pb_inc = 1/len(self.symbols) * 0.5

            klines = {}

            for symbol in self.symbols:
                klines[symbol] = dict(await asyncio.gather(*[self.fetch_klines(symbol, tf, config.PAST_DATA) for tf in config.TIMEFRAMES]))
                pb += pb_inc
                print(f'Loading Symbols {pb*100}%')   
                
            end = datetime.now()
            print('end time klines {}'.format(end))
            print(f'elapsed = {end-start}\n')

            #print(klines[self.symbols[-1]]['1m'])

            lista_tuple = Parallel(n_jobs=-1)(delayed(create_dict)(symbol, klines[symbol]) for symbol in self.symbols)
            self.core_dict = dict(lista_tuple)
            #print(core_dict)

            print('Loading Symbols 90%')

            end = datetime.now()
            print('THE END {}'.format(end))
            print(f'ELAPSED = {end-start}\n')
            
            print('Loading Symbols 100%\nAll Symbols Loaded')

            start_time=datetime.now()
            self.ts_start_time=int(datetime.timestamp(start_time))

            print('Bot operativo: {}'.format(start_time))
            while True:
                for symbol in self.symbols:
                    for tf in config.TIMEFRAMES:
                        await asyncio.gather(*[self.trading(symbol, tf)])
                self.clear_dict(self.core_dict)
                await self.exchange.close()

        except Exception as e:
            print(f'Errore in open_trading_session: {e}')


    async def trading(self, symbol, timeframe):
        try:
            #trades = await self.exchange.watch_trades(symbol)
            #candles = self.exchange.build_ohlcvc(trades, timeframe)
            #candles = await self.exchange.watch_ohlcv(symbol,timeframe)
            #self.core_dict = {}
            candles = await self.exchange.fetch_ohlcv(symbol=symbol, timeframe=timeframe, limit=config.PAST_DATA)
            for candle in candles:
                open_time = candle[0]

                #if open_time < self.core_dict[symbol][timeframe]['time'][-1]:
                    #  continue

                open_price = candle[1]
                high_price = candle[2]
                low_price = candle[3]
                close_price= candle[4]
                volume = candle[5]

                self.core_dict[symbol][timeframe]['time'].append(open_time)
                self.core_dict[symbol][timeframe]['open'].append(open_price)
                self.core_dict[symbol][timeframe]['high'].append(high_price)
                self.core_dict[symbol][timeframe]['low'].append(low_price)
                self.core_dict[symbol][timeframe]['close'].append(close_price)
                self.core_dict[symbol][timeframe]['volume'].append(volume)

                #calcolo indicatori
            calcolo_indicatori(self.core_dict[symbol][timeframe],True)

            self.check_buy(timeframe, symbol)
            return
        
        except Exception as e:
            print("errore in async trading: {}".format(str(e)))
            # raise e  # uncomment to break all loops in case of an error in any one of them
            # break  # you can also break just this one loop if it fails

    def check_buy(self, tf, symbol):
        try:
            prezzo =  self.core_dict[symbol][tf]['close'][-1]
            dict = self.core_dict[symbol][tf]

            changed = True
            os.system('cls||clear')
            if tf =='5m':
                print(f"simbolo: {symbol} vwap_3_m: {self.core_dict[symbol][tf]['vwap_3_m'][-1]}")
            else:
                print(f"simbolo: {symbol} st {tf}: {self.core_dict[symbol][tf]['supertrend'][-1]}")

            for strat in STRATEGIE:


                buy = eval("strategie.{}(dict,prezzo)".format(strat))
                if self.strat_dict[symbol][tf][strat] != buy:
                    self.strat_dict[symbol][tf][strat] = buy
                    changed = True

                    if buy == True:
                        print(f'BUY!! {symbol} {tf}')
                        self.strat_dict['to_buy'].append((symbol,tf,strat))
                    else:
                        print(f'NOT BUY!! {symbol} {tf}')
                        self.strat_dict['to_buy'].remove((symbol,tf,strat))


            # strategies_dict = {"Fibo_harsi":False,"Fibo_harsi_ema200":False,"Rsi":False,"vwap_rsi":False}
            # for strat in strategies_dict.keys():
            #     if eval("strategie.{}(dict,prezzo)".format(strat)) == True:
            #         print(f'{symbol} {tf} BUY!!')
            #         strategies_dict[strat] = True

            # self.strat_dict[symbol][tf] = strategies_dict

            if changed==True:
                with open("database.json", "w") as outfile:
                    json.dump(self.strat_dict, outfile)
                    #json.dump(self.core_dict['ETHUSDT']['5m']['supertrend'][-20:],outfile)
        except Exception as e:
            print(f"errore in check_buy(): {e}")

if __name__ == '__main__':
    print('Starting bot...')
    bot = Bot()
    print('bot_creato')
    asyncio.run(bot.open_trading_session())
