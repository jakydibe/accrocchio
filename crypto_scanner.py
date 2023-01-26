import aiohttp, asyncio
import numpy, statistics, math, time
import pandas as pd
import pandas_ta as ta
from datetime import datetime

TRADING_PERIOD = 10
TIME_FRAME_VOL = '5m'
PAST_DATA = 500



#funzione che fa una richiesta alla pagina web del simbolo per controllare se effettivamente e' up  e disponibile al trading questa valuta 
async def check_crypto(session: aiohttp.ClientSession,s: dict, exchange_tokens: list) -> str:  
        if not('DOWN' in s['symbol']) and not('UP' in s['symbol']):
            #if 'LIMIT' in s['orderTypes'] and 'MARKET' in s['orderTypes'] and 'STOP_LOSS_LIMIT' in s['orderTypes']:
                for token in exchange_tokens:
                    if s['symbol'][-len(token):] == token:
                        url="https://www.binance.com/it/trade/{}_{}?theme=dark&type=spot".format(s['symbol'][0:-4],token) #molto hardcodata
                        richiesta = await session.request('GET', url=url)
                        if richiesta.status == 200:
                            return s['symbol']
                            #return simboli_accettati



def calcola_vwap(high,low,close,volume):
    vwapsum = 0.0
    sum_vol = 0.0
    v2sum = 0.0
    for i in range(len(high)):
        vwapsum += (high[i]+low[i]+close[i])/3.0*volume[i]
        v2sum += ((high[i] + low[i]+close[i])/3.0)*((high[i] + low[i]+close[i])/3.0) * volume[i]
        sum_vol += volume[i]

    myvwap = vwapsum/sum_vol
    #dev = numpy.std(myvwap)
    #print("v2smu/sum_vol: {}\nmyvwap^2: {}".format(v2sum/sum_vol,myvwap*myvwap))
    #print("DEV: {}".format(dev))
    vwap_stdev = math.sqrt(max(v2sum/sum_vol - myvwap*myvwap, 0))

    return myvwap,vwap_stdev

#funzione che calcola la volatilita' di un asset e ne calcola anche alcuni parametri come il volume, cosi' che possiamo scegliere solo asset validi e non asset con pochissima/troppa volatilita' e/o bassa liquidita'
async def calc_volatility(session,symbol,time_frame,past_data):
    try:
        url="https://api.binance.com/api/v3/klines"

        params = {
        'symbol': symbol,
        'interval': time_frame,
        'limit': past_data
        }

        response = await session.request('GET', url=url, params=params) #richieste asincrone per risparmiare moltissimo tempo
        conn_weight = response.headers['x-mbx-used-weight'] #connection weight da tenere d'occhio altrimenti si rischia il ban del proprio ip 
        klines=await response.json() 

        open = []
        high = []
        low = []
        close = []    
        volume = []
        time = []

        ritorno = []
        for kline in klines:
            time.append(int(kline[0]))
            open.append(float(kline[1]))
            high.append(float(kline[2]))
            low.append(float(kline[3]))
            close.append(float(kline[4]))
            volume.append(float(kline[5]))
        
            if len(close) > 1:
                ritorno.append(numpy.log(close[-1]/close[-2])) 

        df = pd.DataFrame({'close':close,'volume':volume,'low':low,'high':high,'open':open,'time':time})

        #np_close = numpy.array(close)
        rsi = list(ta.rsi(df['close'],length=14))
        rsi = rsi[-1]
        ##############calcolo VWAP############################################
        now = int(datetime.timestamp(datetime.now()))                       ##
        today = (now - now%(60*60*24))*1000                                 ##
                                                                            ##
        time_elapsed = time[-1] - today                                     ##
        limit_candele = 0                                                   ##
        if time_elapsed>0:                                                  ##
            limit_candele = int(time_elapsed/(int(TIME_FRAME_VOL[0])*60000))##
                                                                            ##
        df.index = pd.to_datetime(df.index)                                 ##
        vwap,vwap_stdev = calcola_vwap(high,low,close,volume)               ##
        banda_2_m = vwap - 2*vwap_stdev
        banda_2_p = vwap + 2*vwap_stdev

        oversold_vwap = 0
        if low[-1] < banda_2_m or high[-1] > banda_2_p: 
            oversold_vwap = 1                                               ##

        volatility = numpy.std(numpy.array(ritorno)) * math.sqrt(TRADING_PERIOD) #calcolo della volatilita' con deviazione standard ##
        #########################fine CALCOLO VWAP############################
                                                                        
        #######################CALCOLO VOLUME##################################
        prezzo_medio = statistics.mean(close)                                ##   
        volume_medio = statistics.mean(volume)                               ##
                                                                             ##
        volume_dollari=prezzo_medio*volume_medio                             ##
        ###########################fine VOLUME#################################
    
        return [symbol,[volatility,rsi,oversold_vwap,volume_dollari]],conn_weight
    except Exception as e:
        print("errore in calc_volatility: {}".format(e))


#funzione asincrona che sceglie le cryptovalute migliori da tradare in un preciso momento, in base a volume, volatilita'
async def crypto_finder(bot, update_progress, exchange_tokens, num_crypto,scan_type):  
    try:
        # Asynchronous context manager.  Prefer this rather
        # than using a different session for each GET request
        async with aiohttp.ClientSession() as session:
            response= await session.request('GET', url= "https://api.binance.com/api/v3/exchangeInfo", params= {'permissions': 'SPOT'})
            conn_weight = response.headers['x-mbx-used-weight']
            exchange_info = await response.json()

            #print(conn_weight)

            tasks = []
            for s in exchange_info['symbols']:
                tasks.append(check_crypto(session=session, s=s, exchange_tokens=exchange_tokens))
            # asyncio.gather() will wait on the entire task set to be
            # completed.  If you want to process results greedily as they come in,
            # loop over asyncio.as_completed()
            result = await asyncio.gather(*tasks, return_exceptions=True) #awaitiamo la lista di tutti i simboli disponibili al trading

            update_progress(0.1)

            symbols=[]
            for r in result:
                if r!=None and not('BTTC' in r): #eliminiamo i doppioni (es. BTC/USDT e BTC/BUSD, e preferiamo la coppia con USDT )
                    trovata = False
                    s_remove = None
                    for s in symbols:
                        if s[:-4]==r[:-4]:
                            if 'USDT' in s:
                                trovata=True
                            else:
                                s_remove=s
                            break
                    
                    if s_remove!=None:
                        symbols.remove(s_remove)
                    if trovata==False:
                        symbols.append(r)   

            print('\nTrovati {} Simboli\n'.format(len(symbols)))

            tasks2 = [[]] #array che contiene 
            result2=[]
            for i in range(len(symbols)):
                tasks2[-1].append(calc_volatility(session=session, symbol=symbols[i],time_frame=TIME_FRAME_VOL,past_data=PAST_DATA))

                if i%30==0 or i==len(symbols)-1:
                    result2.append(await asyncio.gather(*tasks2[-1], return_exceptions=True))
                    tasks2.append([])
                    conn_weight=int(result2[-1][-1][1])

                    if conn_weight>350 and i!=len(symbols)-1:
                        print('\nRequested {} symbols'.format(i))
                        print('Connection Weight: {}'.format(conn_weight))
                        print('Waiting 30 Seconds...')
                        time.sleep(30)

                    update_progress(0.2 + i/(len(symbols)-1)*0.75) #20 - 95

        print('\nvolatilita calcolata\n')

        lista=[]
        for arr in result2:
            for el in arr:
                lista.append(el[0])

        for i in range(len(lista)):
            if 'USDT' in lista[i][0]:
                lista[i][0] = lista[i][0].replace('USDT', '/USDT')
            elif 'BUSD' in lista[i][0]:
                lista[i][0] = lista[i][0].replace('BUSD', '/BUSD') 

        print("SORT BY: {}".format(scan_type))

        #sort per volume 
        sort_volume=sorted(dict(lista).items(), key=lambda x:x[1][3])
        lista_2=[]

        if len(sort_volume)/2>50:
            lista_2 = sort_volume[-50:]
        else:
            lista_2 = sort_volume[-int(len(sort_volume)/2):]

        update_progress(0.96)

        if scan_type == 'Volatility/Volume':
            
            #sort per volatilita
            sort_volatilita = sorted(dict(lista_2).items(), key=lambda x:x[1][0])
            if len(sort_volatilita)>10:
                lista_3 = sort_volatilita[-8-num_crypto:-8]
            else:

                lista_3 = sort_volatilita

            update_progress(0.97)

            invertito_volatilita=[]
            l=len(lista_3)
            for i in range(l):
                invertito_volatilita.append(lista_3[l-1-i])

            update_progress(0.98)

            vol_data=[]
            for el in invertito_volatilita:
                vol_data.append(el[1][0])

            update_progress(0.99)

            lista_return = []
            for vr in invertito_volatilita:
                lista_return.append(vr[0])

            print(lista_return)

            bot.symbols.extend(lista_return)

        elif scan_type == 'Rsi/volume':
            
            sorted_rsi = sorted(dict(lista_2).items(), key=lambda x:x[1][1])

            sorted_swag_supremo = []

            update_progress(0.97)

            for i in range(len(sorted_rsi)):
                sorted_swag_supremo.append(sorted_rsi[i][0])
            
            update_progress(0.98)

    #        print(sorted_swag_supremo)  SE CON RSI UNCOMMENTA IL REVERSED!!!!
            #sorted_swag_supremo_inv = list(reversed(sorted_swag_supremo))
            #print(sorted_swag_supremo_inv)

            bot.symbols.extend(sorted_swag_supremo[:num_crypto+1])
            update_progress(0.99)
        
        elif scan_type == 'Vwap/Volume':
            
            lista_vwap_over_bought_oversold = []

            for i in lista_2:
                print(i)
                if i[1][2] == 1:
                    lista_vwap_over_bought_oversold.append(i)
            update_progress(0.97)
            print("[DEBUG] PRIMA DEL SORT APPOST")

            sorted_vwap = sorted(dict(lista_vwap_over_bought_oversold).items(),key=lambda x:x[1][2])

            sorted_swag_supremo = []

            for i in range(len(sorted_vwap)):
                sorted_swag_supremo.append(sorted_vwap[i][0])
            
            update_progress(0.98)
            

            

            update_progress(0.99)
            if len(sorted_swag_supremo) > num_crypto:
                bot.symbols.extend(sorted_swag_supremo[-num_crypto:])
            else:
                bot.symbols.extend(sorted_swag_supremo[-len(sorted_swag_supremo):])

        update_progress(1)
        return 


    except Exception as e:
        print('Errore in trova_crypto: {}'.format(e))
        print('Errore in trova_crypto: {}'.format(e))
