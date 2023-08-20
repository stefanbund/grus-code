import csv
import cbpro
import numpy as np
import pandas as pd
from scipy.stats import skew
import sched, time
from datetime import date

RANGE = 0.0036
public_client = cbpro.PublicClient()

def sum_qty_asks(df):
    df['price'] = df['price'].astype(float)
    df['qty'] = df['qty'].astype(float)
    top_price = float(df['price'].min())
    threshold = top_price * RANGE
    return df[df['price'] >= top_price - threshold]['qty'].sum()
    
def sum_qty_bids(df):
    df['price'] = df['price'].astype(float)
    df['qty'] = df['qty'].astype(float)
    top_price = float(df['price'].max())
    threshold = top_price * RANGE
    return df[df['price'] >= top_price - threshold]['qty'].sum()

def sum_bids_cap(df):
    df['price'] = df['price'].astype(float)
    df['qty'] = df['qty'].astype(float)
    top_price = float(df['price'].max())
    threshold = top_price * RANGE
    df['sum']= df['price'] * df['qty']
    caps = df[df['price'] >= top_price - threshold]['sum'].sum()
    return caps

def sum_asks_cap(df):
    df['price'] = df['price'].astype(float)
    df['qty'] = df['qty'].astype(float)
    top_price = float(df['price'].min())
    threshold = top_price * RANGE
    df['sum']= df['price'] * df['qty']
    caps = df[df['price'] >= top_price - threshold]['sum'].sum()
    return caps
    
def generateSummaryonLOB(scheduler):
    scheduler.enter(3, 1, generateSummaryonLOB, (scheduler,))
    book = public_client.get_product_order_book('AVAX-USD', level=3)
    da = book['asks']
    df_asks = pd.DataFrame(da, columns=['price','qty','id'])
    db = book['bids']
    df_bids = pd.DataFrame(db, columns=['price','qty','id'])
    
    tav = round(sum_qty_asks(df_asks),3)
    tbv = round(sum_qty_bids(df_bids),3)
    bc = round(sum_bids_cap(df_bids),3)
    ac = round(sum_asks_cap(df_asks),3)
    mp = df_asks.iloc[0]['price']
    
    writer.writerow([mp, tav, tbv, bc, ac, int(time.time())]) #array of veriables, not a dictionary

# def do_something(scheduler):  
#     scheduler.enter(3, 1, do_something, (scheduler,))  
#     current_time = int(time.time())
#     stringa = 'this'
#     month = 'january'
#     writer.writerow([current_time, stringa, month])

today = date.today()
filename = today.strftime("%Y-%m-%d")+ ".csv"
with open(filename, mode='w', newline='') as csv_file:
    writer = csv.writer(csv_file)
    writer.writerow(['mp', 'tav', 'tbv', 'bc', 'ac', 'time'])   #init once with headers, mp, tav, tbv, bc, ac, time
    my_scheduler = sched.scheduler(time.time, time.sleep) 
    my_scheduler.enter(3, 1, generateSummaryonLOB, (my_scheduler,))   #generateSummary insert
    my_scheduler.run() 

# From https://stackoverflow.com/questions/474528/how-to-repeatedly-execute-a-function-every-x-seconds 
