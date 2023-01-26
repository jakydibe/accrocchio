import json

def load_data():
    # Opening JSON file
    try:
        with open('database.json', 'r') as openfile:
            # Reading from json file
            return json.load(openfile)
    except:
        return {}

from fastapi import FastAPI
app = FastAPI()

@app.get("/")
async def root():
    return load_data()

@app.get("/to_buy")
def read_to_buy():
    return load_data()['to_buy']

@app.get("/{symbol}")
def read_symbol(symbol: str):
    s = symbol.replace('_','/')
    try:
        return load_data()[s]
    except:
        return "symbol not found"

@app.get("/{symbol}/{tf}")
def read_symbol_tf(symbol: str, tf: str):
    s = symbol.replace('_','/')
    try:
        return load_data()[s][tf]
    except:
        return "symbol/tf not found"

@app.get("/{symbol}/{tf}/{strat}")
def read_symbol_tf_strat(symbol: str, tf: str, strat: str):
    s = symbol.replace('_','/')
    try:
        return load_data()[s][tf][strat]
    except:
        return "symbol/tf not found"
