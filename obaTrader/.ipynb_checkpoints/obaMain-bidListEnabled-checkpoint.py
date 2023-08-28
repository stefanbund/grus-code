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

surges = []
precursors = []
globalList = []
def buildDecision(mp, tav, tbv, bc, ac, int(time.time()) ) :
    # integrate average change threshold, determine whether surge or precursor
    caps_df = capsFrame   
    lookback_period = 10 # in rows
    caps_df['change'] = caps_df['mp'].pct_change(periods=lookback_period)
    # caps_df.sample
    print(caps_df.shape[0], caps_df.columns)# Calculate the returns of your asset over a fixed lookback period
    meanChange = round(caps_df['change'].mean(),8)
    # identify units of 10 rows where the percent change is greater or less than the threshold
    threshold = meanChange
    # surges = []
    # precursors = []
    #populate surge and / or precursors
    for i in range(0,len(caps_df),10):
        if caps_df.iloc[i:i+10]['change'].mean() >= threshold:
            surges.append({'time': caps_df.iloc[i]['time'],
                           's_MP': caps_df.iloc[i]['mp'],
                           'change': caps_df.iloc[i:i+10]['change'].mean(),
                           'type':'surge'})  #['bc', 'ac', 'tbv', 'tav', 'time', 'mp', 'minBid', 'change']
        else:
            precursors.append({'time': caps_df.iloc[i]['time'],
                               'p_MP': caps_df.iloc[i]['mp'],
                               'change': caps_df.iloc[i:i+10]['change'].mean(),
                                'type':'precursor',
                                'p_buyCap':caps_df.iloc[i]['bc'], 
                                'p_askCap':caps_df.iloc[i]['ac'],
                                'p_totalBidVol':caps_df.iloc[i]['tbv'],
                                'p_totalAskVol':caps_df.iloc[i]['tav']})
    # grouping, sequentials
    surges_df = pd.DataFrame(surges)
    precursors_df = pd.DataFrame(precursors)
    sequence_df = pd.concat([surges_df, precursors_df]).sort_values(by=['time'], ascending=True)
    sequence_df['group'] = (sequence_df['type'] != sequence_df['type'].shift(1)).cumsum()
    sequence_df['length'] = sequence_df.groupby(['type', 'group'])['group'].transform('count')
    print(sequence_df.shape[0])
    sequence_df['sum_change'] = sequence_df.groupby(['type', 'group'])['change'].transform('sum')
    print(sequence_df.shape[0])
    
    sequence_df['area']  = sequence_df.apply(lambda row: row['length'] * row['sum_change'], axis=1)
    sequence_df.loc[sequence_df['type'] == 'surge', 'surge_area'] = sequence_df.loc[sequence_df['type'] == 'surge', 'area']
    sequence_df.columns
    unique_df = sequence_df.groupby('group').first().reset_index()
    print(unique_df)
    even_df = unique_df.iloc[::2].reset_index(drop=True)
    odd_df = unique_df.iloc[1::2].reset_index(drop=True)
    merged_df = pd.concat([even_df, odd_df], axis=1)
    print(merged_df)
    nan_cols = merged_df.dropna(axis=1, how='all')
    nan_cols.head() #normally, cluster here
    #drop cluster information
    clustered.drop(['group', 'time', 's_MP', 'change', 'type', 'length', 'sum_change', 's_area', 'surge_area' ] , axis=1, inplace=True) 
s

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
    buildDecision( mp, tav, tbv, bc, ac, int(time.time()) )
    
today = date.today()
filename = today.strftime("%Y-%m-%d")+ ".csv"
with open(filename, mode='w', newline='') as csv_file:
    writer = csv.writer(csv_file)
    writer.writerow(['mp', 'tav', 'tbv', 'bc', 'ac', 'time'])   #init once with headers, mp, tav, tbv, bc, ac, time
    my_scheduler = sched.scheduler(time.time, time.sleep) 
    my_scheduler.enter(3, 1, generateSummaryonLOB, (my_scheduler,))   #generateSummary insert
    my_scheduler.run() 

# From https://stackoverflow.com/questions/474528/how-to-repeatedly-execute-a-function-every-x-seconds 
