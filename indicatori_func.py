import numpy, statistics,time, config,math

from datetime import datetime
import pandas as pd
import pandas_ta as ta


def CalcoloSMA(df,period):
    try:
        sma = list(df.rolling(period).mean())
        #print("SMA: {}".format(sma[-15:]))

        return sma[-15:]
    except Exception as e:
        print('erorre in CalcoloSMA() : {}'.format(e))

def supertrend(df, period=7, atr_multiplier=3):
    try:
        stringa_accesso = f"SUPERT_{period}_{atr_multiplier}.0"
        sti = ta.supertrend(df['high'], df['low'], df['close'], length=period, multiplier=atr_multiplier)[stringa_accesso]
        return sti
    except Exception as e:
        print(f"errore in supertrend(): {e}")
        return None



def CalcoloEMA(df,period):  #passare almeno 10 valori in piu' rispetto al periodo

    try:
        array_ema = list(df.ewm(com=period).mean())
        #print("EMA: {}".format(array_ema[-15:]))
        return array_ema[-15:]
       
    except Exception as e:
        print('erorre in CalcoloEMA() : {}'.format(e))
        return 



#def STC(df,cycle_length,fast_length,slow_length):
#    fast_ema = CalcoloEma(df,fast_length)
#    slow_ema = CalcoloEma(df,slow_length)

#    macd = fast_ema[-30:]-slow_ema[-30:]

#    low_strano = min(macd,cycle_length)
#    high_strano = max(macd,cycke_length) - low_strano

#    var_strana_C = None
#    if high_strano > 0:
#        var_strana_C = (macd-low_strano)/(high_strano*100)
#    else:
#        if var_strana_C = None
#            var_strana_C = 0

#    pass


def CalcoloATR(df,period): #passare almeno 1 valore piu' rispetto al periodo
    try: #  https://technical-analysis-library-in-python.readthedocs.io/en/latest/index.html
    
    
        atr = list(ta.atr(df['high'],df['low'],df['close'],length=period))
        #print("atr: {}".format(atr[-15:]))

        return atr

    except Exception as e:
        print('erorre in CalcoloATR() : {}'.format(e))
        return None

def CalcoloRSI(df,period): #passare come minimo un valore in piu' del perio
    try:
        rsi = list(ta.rsi(df,length=period))
        #print("RSI: {}".format(rsi[-5:]))
        return rsi[-15:]
    except Exception as e:
        print('erorre in CalcoloRSI() : {}'.format(e))




def ha_rsi_oscillator(dict,rsiOpen,rsiHigh,rsiLow,rsiClose):
    try:
        dict['ha_close'].append(float((rsiOpen + rsiClose + rsiLow + rsiHigh)/4.0))
        
        #print("RSI OPEN {} RSI CLOSE {}".format(rsiOpen,rsiClose))
        if(len(dict['ha_open']) == 0):
            dict['ha_open'].append(float((rsiOpen + rsiClose)/2))
        else:
            dict['ha_open'].append(float(((dict['ha_open'][-1]*config.I_SMOOTHING) + dict['ha_close'][-1])/(config.I_SMOOTHING+1)))
            
        dict['ha_high'].append(float(max(rsiHigh,max(dict['ha_close'][-1],dict['ha_open'][-1]))))    
        dict['ha_low'].append(float(min(rsiLow,min(dict['ha_close'][-1],dict['ha_open'][-1]))))
    except Exception as e:
        print("ERRORE DIOCRISTO SEI SCEMO FAGIANO {}".format(e))


def fibo_bands(df):
    try:
        middleband = CalcoloSMA(df['close'],config.FIBO_PERIOD)
        avg = numpy.array(CalcoloATR(df, config.FIBO_PERIOD))
        #print("------------ATR: {}=------------".format(avg))
        
        fibratio1 = 1.618
        fibratio2 = 2.618
        fibratio3 = 4.236
        r1 = avg*fibratio1
        r2 = avg*fibratio2
        r3 = avg*fibratio3

        return middleband, r1, r2, r3
    except Exception as e:
        print("errore in fibo_bands(): {}".format(e))
        return None

def vwap_func(high, low, close, volume):
    try:
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

    except Exception as e:
        print("errore in vwap_func(): {}".format(e))
    return myvwap,vwap_stdev


def order_blocks(dict):
    try:
        sens = 28
        sens /= 100

        ob_created_bear = False
        ob_created_bull = False
        cross_index = 0


        bar_index = float(len(dict['pc']))

        if bar_index > 1:
            if dict['pc'][-2] > (-sens) and dict['pc'][-1] < (-sens):
                ob_created_bear = True
                cross_index = bar_index

            if dict['pc'][-2] < sens and dict['pc'][-1] > sens:
                ob_created_bull = True
                cross_index = bar_index

    
            if ob_created_bear and (len(dict['cross_index']) == 0 or cross_index - dict['cross_index'][-1] > 5 ):
                dict['cross_index'].append(cross_index)
                last_green = 0.0
                #trova la prima candela verde ne
                for i in range(4,15):
                    if dict['close'][-i] > dict['open'][-i]:
                        last_green = i
                        break

                #CREAZIONE DELL ARRAY CON [0] CANDELA DI INZIO, [1] TOP e [2] BOTTOM
                box = []
                box.extend([bar_index-last_green,dict['high'][int(bar_index-last_green)],dict['low'][int(bar_index-last_green)]])
                dict['sbox'].append(box)

            if ob_created_bull and (len(dict['cross_index']) == 0 or cross_index -  dict['cross_index'][-1] > 5):
                dict['cross_index'].append(cross_index)
                last_red = 0.0

                for i in range(4,15):
                    if dict['close'][-i] < dict['open'][-i]:
                        last_red = i
                        break
                box = []
                box.extend([bar_index-last_red,dict['high'][int(bar_index-last_red)],dict['low'][int(bar_index-last_red)]])
                dict['lbox'].append(box)

            if len(dict['sbox']) > 0:
                x = 0
                for i in range(len(dict['sbox'])):
                    sbox = dict['sbox'][i-x]
                    top = sbox[1]
                    if dict['close'][-1] > top and dict['close'][-2] > top:
                        dict['sbox'].pop(i-x)
                        x+=1

            if len(dict['lbox']) > 0:
                x = 0
                for i in range(len(dict['lbox'])):
                    lbox = dict['lbox'][i-x]
                    bot = lbox[2]
                    if dict['close'][-1] < bot and dict['close'][-2] < bot:
                        dict['lbox'].pop(i-x)
                        x+=1
    except Exception as e:
        print("eccezione in order_blocks() : {}".format(e))


def volume_profile(openC,high,low,close,volume,righe):
    try:
        highest = max(high)
        lowest = min(low)

        prezzi_medi = []
        incremento = float((highest-lowest)/righe)

        for i in range(righe+1):
            prezzi_medi.append(lowest + i*incremento)

        canali = {prezzo_medio:[.0,.0] for prezzo_medio in prezzi_medi} #il primo el dell array e' il volume positivo, l' altro il negativo
        del canali[prezzi_medi[-1]]
       # print('[DEBUG] prima del primo ciclo; tutto ok')
        for i in range(len(high)):
            canale_low = 0
            canale_high = 0
            for x in range(len(prezzi_medi)-1):
                if low[i] > prezzi_medi[x] and low[i] < prezzi_medi[x+1]:
                    canale_low = x
                if high[i] > prezzi_medi[x] and high[i] < prezzi_medi[x+1]:
                    canale_high = x

            diff_canali = canale_high-canale_low
            
            rapporto_corpo_candela = 0
            if high[i] - low[i] != 0:
                rapporto_corpo_candela = (float(close[i]-openC[i]))/(high[i]-low[i])
            
            if diff_canali == 0:
                if rapporto_corpo_candela < 0:
                    canali[prezzi_medi[canale_low]][0] += volume[i]/(2.0+rapporto_corpo_candela)
                    canali[prezzi_medi[canale_low]][1] += volume[i]/(2.0-rapporto_corpo_candela)
                else:
                    canali[prezzi_medi[canale_low]][0] += volume[i]/(2.0-rapporto_corpo_candela)
                    canali[prezzi_medi[canale_low]][1] += volume[i]/(2.0+rapporto_corpo_candela)
            else:
                #print('[DEBUG] prima del secondo ciclo; tutto ok')
                #print("DIFF_CANALI: {}".format(diff_canali))
                
                for x in range(diff_canali):
                    #print("CANALE_LOW: {}".format(canale_low))
                    #print(canali)
                    #print(prezzi_medi)
                    if rapporto_corpo_candela < 0:
                        canali[prezzi_medi[canale_low + x]][0] += volume[i]/(diff_canali +1.0)/(2.0+rapporto_corpo_candela)
                        canali[prezzi_medi[canale_low + x]][1] += volume[i]/(diff_canali +1.0)/(2.0-rapporto_corpo_candela)
                    else:
                        canali[prezzi_medi[canale_low + x]][0] += volume[i]/(diff_canali +1.0)/(2.0-rapporto_corpo_candela)
                        canali[prezzi_medi[canale_low + x]][1] += volume[i]/(diff_canali +1.0)/(2.0+rapporto_corpo_candela)
                        
                    #print('[DEBUG] fine del secondo ciclo; tutto ok')

    except Exception as e:
        print("eccezione in volume profile coglionazzo merdaccia {}".format(e))
    return canali

def calcolo_indicatori(dict,is_candle_open):
    
    try:
        #print('vwap')
        now = int(datetime.timestamp(datetime.now()))
        today = (now - now%(60*60*24))*1000

        time_elapsed = dict['time'][-1] - today
        limit_candele = 0
        if time_elapsed>0:
            limit_candele = int(time_elapsed/(int(config.TIME_FRAME[0][-2])*60000))
            if limit_candele <= len(dict['close']):
                vwap, vwap_stdev = vwap_func(dict['high'][-limit_candele:],dict['low'][-limit_candele:],dict['close'][-limit_candele:],dict['volume'][-limit_candele:])

                if is_candle_open == True:
                    dict['vwap'].append(vwap)
                    dict['vwap_stdev'].append(vwap_stdev)
                    dict['vwap_1_p'].append(vwap+1*vwap_stdev)
                    dict['vwap_1_m'].append(vwap-1*vwap_stdev)
                    dict['vwap_3_p'].append(vwap+2.95*vwap_stdev)
                    dict['vwap_3_m'].append(vwap-2.95*vwap_stdev)
                else:
                    dict['vwap'][-1] = vwap
                    dict['vwap_stdev'][-1] = vwap_stdev
                    dict['vwap_1_p'][-1] = vwap+1*vwap_stdev
                    dict['vwap_1_m'][-1] = vwap-1*vwap_stdev
                    dict['vwap_3_p'][-1] = vwap+2.95*vwap_stdev
                    dict['vwap_3_m'][-1] = vwap-2.95*vwap_stdev


                #dict['canali_volume'] = volume_profile(dict['open'][-limit_candele:],dict['high'][-limit_candele:],dict['low'][-limit_candele:],dict['close'][-limit_candele:],dict['volume'][-limit_candele:],config.NUMERO_BARRE)
        #print('fine vwap')

        if len(dict['close'])>300:
            df = pd.DataFrame({'close':dict['close'][-250:],'low':dict['low'][-250:],'high':dict['high'][-250:],'volume':dict['volume'][-250:]})

            volume_medio = statistics.mean(dict['volume'][-250:])

            volume_medio30 = CalcoloSMA(df['volume'],period=30)
            linea_std_volume = volume_medio30[-1] *3
            ema200 = CalcoloEMA(df['close'],200)

            #print("###############################################################################\nema200: {}".format(ema200))
            pc = (dict['open'][-1] - dict['open'][-4])/dict['open'][-4]*100
            dict['pc'].append(pc)
            #order_blocks(dict)

            ema5 = CalcoloEMA(df['close'],5)
            ema11 = CalcoloEMA(df['close'],11)
            ema15 = CalcoloEMA(df['close'],15)
            ema18 = CalcoloEMA(df['close'],18)
            ema21 = CalcoloEMA(df['close'],21)
            ema24 = CalcoloEMA(df['close'],24)
            ema28 = CalcoloEMA(df['close'],28)
            ema34 = CalcoloEMA(df['close'],34)


            rsiHigh = CalcoloRSI(df['high'],period=14)
            rsiLow = CalcoloRSI(df['low'],period=14)
            rsiClose = CalcoloRSI(df['close'],period=14)
            #print("###############################################################################\nrsiClose : {}".format(rsiClose))
            
            #print("[debug] dopo calcolo ema5 e rsi appsot")
            #print("ema200: {}".format(ema200))

            prezzo_attuale = (dict['low'][-1] + dict['close'][-1])/2.0
            distanza_perc_ema = (prezzo_attuale - ema200[-1])/ema200[-1] #errore qui dioca

            ha_rsi_oscillator(dict,rsiClose[-2]-50.0,rsiHigh[-1]-50.0,rsiLow[-1]-50.0,rsiClose[-1]-50.0)
            #print('[debug] prima fibo_bands appost')
            fibo, fibo_r1, fibo_r2, fibo_r3  = fibo_bands(df)
            #print("##############################")
            #print("ema200: {}".format(ema200))
            atr = CalcoloATR(df,14)
            st=supertrend(df)[-20:]
            st=st.values.tolist()

            #time.sleep(10)
            #print("RSI: {}".format(rsiClose))
            #print('[debug] fine calcolo-indicatori prima degli append')

            if is_candle_open == True:
                dict['supertrend'] = st
                dict['fibo'].append(fibo[-1])
                dict['fibo_r1'].append(fibo_r1[-1])
                dict['fibo_r2'].append(fibo_r2[-1])
                dict['fibo_r3'].append(fibo_r3[-1])
                dict['distanza_perc_ema200'].append(distanza_perc_ema)
                dict['volume_medio'].append(volume_medio)
                dict['ema200'].append(ema200[-1])
                dict['ema5'].append(ema5[-1])
                dict['ema11'].append(ema11[-1])
                dict['ema15'].append(ema15[-1])
                dict['ema18'].append(ema18[-1])
                dict['ema21'].append(ema21[-1])
                dict['ema24'].append(ema24[-1])
                dict['ema28'].append(ema28[-1])
                dict['ema34'].append(ema34[-1])

                dict['rsi'].append(rsiClose[-1])
                dict['atr']=atr
                dict['volume_ma_std30'].append(linea_std_volume)

            else:
                dict['supertrend'][-1] = st[-1]

                dict['fibo'][-1] = fibo[-1]
                dict['fibo_r1'][-1] = fibo_r1[-1]
                dict['fibo_r2'][-1] = fibo_r2[-1]
                dict['fibo_r3'][-1] = fibo_r3[-1]
                dict['distanza_perc_ema200'][-1] = distanza_perc_ema
                dict['volume_medio'][-1] = volume_medio
                dict['ema200'][-1] = ema200[-1]
                dict['ema5'][-1] = ema5[-1]
                dict['ema11'][-1] = ema11[-1]
                dict['ema15'][-1] = ema15[-1]
                dict['ema18'][-1] = ema18[-1]
                dict['ema21'][-1] = ema21[-1]
                dict['ema24'][-1] = ema24[-1]
                dict['ema28'][-1] = ema28[-1]
                dict['ema34'][-1] = ema34[-1]
                

                dict['rsi'][-1] = rsiClose[-1]
                dict['atr'][-1] = atr[-1]
                dict['volume_ma_std30'][-1] = linea_std_volume
            #dict['df']
        
    except Exception as e:
        print('Sei un coglione {}'.format(e))
