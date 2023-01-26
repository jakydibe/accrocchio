import statistics, numpy,time
from datetime import datetime
import pandas as pd

import config, indicatori_func

def buy_zones(dict,canali):
    lista_volume_totale = []
    for k in canali.keys():
        lista_volume_totale.append(canali[k][0]+canali[k][1])
    media_volumi_prezzo = statistics.mean(lista_volume_totale)
    canale_close = 0
    lista_canali = list(canali.keys())
    
    canale_close = lista_canali[-1]
    for x in range(1,len(lista_canali)):
        if dict['close'][-1] < lista_canali[x]:
            canale_close = lista_canali[x-1]
            break
    
    if (canali[canale_close][0] + canali[canale_close][1]) > media_volumi_prezzo:
        if canali[canale_close][0] > canali[canale_close][1]:
            return True

    
    return False




def buy_vwap_volume(dict,canali):

    if dict['close'][-1] >= dict['open'][-1]:
        
        if dict['close'][-1] < dict['vwap'][-1] - dict['vwap_stdev'][-1]*config.DEVIAZIONE_STD_VWAP:
            canale_close = 0

            if buy_zones(dict,canali) == True:
                return True

def ha_buy(dict):
    try:
        if dict['ha_close'][-2] < dict['ha_open'][-2]:
            if dict['ha_close'][-1] > dict['ha_open'][-1]:
                return True
        return False
    except Exception as e:
        print("DIOCA NCENNO ABBASTANZA CANDELE, MAGNA NPO' DE MERDA E ARTORNA TUQUI QUANDO E' PRONTO...{}".format(e))
        return False



def rintraccia_fibo_ultima(dict):
    numero_rintraccia = 4 #il numero di candele che vuoi controllare prima - 1
    for i in range(1,numero_rintraccia):
        if dict['low'][-i] < dict['fibo'][-i] - dict['fibo_r3'][-i]:
            return True

    return False

def rintraccia_ultra_high_volume(dict):
    for i in range(1,6):        
        if dict['volume'][-i] > dict['volume_ma_std30'][-i]:
            return True
    
    return False

def rintraccia_fibo_penultima(dict):
    numero_rintraccia = 4 #il numero di candele che vuoi controllare prima - 1
    for i in range(1,numero_rintraccia):
        if dict['low'][-i] < dict['fibo'][-i] - dict['fibo_r2'][-i]:
            return True

    return False


#############################################################################
#FUNZIONI STRATEGIE##########################################################
#############################################################################

def Fibo_harsi_ema200(dict,prezzo):
    risk_reward = 1/1.2
    atr_tp = dict['atr'][-1] 
    atr_tp *= 1.4

    if (dict['low'][-1] < dict['fibo'][-1] - dict['fibo_r3'][-1]  or dict['fibo'][-2] - dict['fibo_r3'][-2]) and  dict['fibo'][-1] + dict['fibo_r3'][-1] < dict['ema200'][-1] or (ha_buy(dict) == True and rintraccia_fibo_ultima(dict) == True):
        #print("[DEBUG]BUY CON EMA")
        dict['stop_loss'] = prezzo - atr_tp
        dict['take_profit'] = prezzo + atr_tp/risk_reward
        return True
    return False

def Fibo_harsi(dict,prezzo):
    risk_reward = 1/1.2
    atr_tp = dict['atr'][-1] 
    atr_tp *= 1.4

    if ha_buy(dict) == True and rintraccia_fibo_ultima(dict) == True:
        print('[DEBUG]BUY CON RSI ultima')
        dict['stop_loss'] = prezzo - atr_tp
        dict['take_profit'] = prezzo + atr_tp/risk_reward
        return True
    return False

def Vwap_volume_profile(dict,prezzo):
    risk_reward = 1/1.2
    atr_tp = dict['atr'][-1] 
    atr_tp *= 1.4

    now = datetime.now()
    dt_string = now.strftime("%H:%M:%S")
    ora = int(dt_string[:2] + dt_string[3:5])
    if ora > 420:
        if buy_vwap_volume(dict,dict['canali_volume']) == True:
            dict['stop_loss'] = prezzo - atr_tp
            dict['take_profit'] = prezzo + atr_tp/risk_reward
            return True
    else:
        print("FAGIANO NON E' ORA DI TRADARE TORNA A DORMIRE COGLIONAZZO!")
        return False



def vwap_3(dict,prezzo):
    try:
        risk_reward = 1/1.2
        #df = pd.DataFrame({'close':dict['close'][-250:],'low':dict['low'][-250:],'high':dict['high'][-250:],'volume':dict['volume'][-250:]})
        atr_tp = dict['atr'][-1] 
        atr_tp *= 1.4
        now = datetime.now()
        dt_string = now.strftime("%H:%M:%S")
        ora = int(dt_string[:2] + dt_string[3:5])
        if ora > 420:
            if (dict['high'][-1] >= dict['vwap_3_p'][-1]) or (dict['low'][-1] <= dict['vwap_3_m'][-1]) :
                    return True
        return False
    except:
        return False


def supertrend_strat(dict,prezzo):
    risk_reward = 1/1.2
    #df = pd.DataFrame({'close':dict['close'][-250:],'low':dict['low'][-250:],'high':dict['high'][-250:],'volume':dict['volume'][-250:]})
    atr_tp = dict['atr'][-1] 
    atr_tp *= 1.4


    if (dict['close'][-2] >= dict['supertrend'][-2] and dict['close'][-1] <=dict['supertrend'][-1]) or (dict['close'][-2] <= dict['supertrend'][-2] and dict['close'][-1] >=dict['supertrend'][-1]):
            return True
    return False

#def market_cipher_A(dict,prezzo)\\\\:
#    ema_1 = 
def Rsi(dict,prezzo):
    #df = pd.DataFrame({'close':dict['close'][-250:],'low':dict['low'][-250:],'high':dict['high'][-250:],'volume':dict['volume'][-250:]})
    atr_tp = dict['atr'][-1] 
    risk_reward = 1/1.2

    atr_tp *= 1.4

    rsi = dict['rsi']

    if rsi[-1] > config.RSI_OVERSOLD and rsi[-2] < config.RSI_OVERSOLD:
        dict['stop_loss'] = prezzo - atr_tp
        dict['take_profit'] = prezzo + atr_tp/risk_reward
        return True
    return False

def vwap_rsi(dict,prezzo):
    risk_reward = 1/1.2
    #df = pd.DataFrame({'close':dict['close'][-250:],'low':dict['low'][-250:],'high':dict['high'][-250:],'volume':dict['volume'][-250:]})
    atr_tp = dict['atr'][-1] 
    atr_tp *= 1.4

    if dict['close'][-1] < dict['vwap'][-1]:
        if Rsi(dict,prezzo) == True:
            return True
    return False

def order_blocks_strategy(dict,prezzo):
    risk_reward = 1/2
    for i in reversed(dict['lbox']):
        if dict['low'][-1] < i[1]:
            dict['stop_loss'] = prezzo - (i[1] - i[2])
            dict['take_profit'] = prezzo + 1/risk_reward*(i[1]-i[2])
            return True
    return False


def pazzo_totale(dict,prezzo,strategie):
    #print("#############################################################")
    # print("INDICATORI ATTUALI\n ")
    # print("RSI: {}".format(dict['rsi'][-10:]))
    # print("ATR: {}".format(dict['atr'][-10:]))
    # print("EMA200: {}".format(dict['ema200'][-10:]))


    for x in strategie:
        if eval("{}(dict,prezzo)".format(x)) == True:
            return True

    #if dict['low'][-1] < dict['vwap'][-1]:    
    #    if ha_buy(dict) == True and rintraccia_fibo_ultima(dict) == True:
    #        print('[DEBUG]BUY CON RSI ultima')
    #        return True
    
    return False
