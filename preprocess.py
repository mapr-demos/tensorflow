#!/usr/bin/env python

import pandas as pd
import datetime as dt
import numpy as np
import re

INPUTFILE = "/mapr/demo.mapr.com/user/mapr/claims_2002_2006.csv"
OUT_TRAIN = "/mapr/demo.mapr.com/user/mapr/claims_train.csv"
OUT_TEST = "/mapr/demo.mapr.com/user/mapr/claims_test.csv"
SPLIT = 0.8

INPUTCOLS = ['Date Received', 'Airport Code', 'Airport Name', \
    'Claim Site', 'Item', 'Claim Amount', 'Status', 'Claim Site' ]
TARGETMAP = { 'Approved' : 1, 'Settled' : 1, 'Denied' : 0,
    'Canceled' : 0, re.compile('Insufficient.*') : 0,
    re.compile('Closed.*') : 0, re.compile('In litigation.*') : 0,
    re.compile('In review.*') : 0 }

print "reading input file: %s" % INPUTFILE
df = pd.read_csv(INPUTFILE, usecols=INPUTCOLS, dtype=str)
rawlen = len(df.index)
df.dropna(inplace=True)
newlen = len(df.index)
print "raw data len: %d" % rawlen
print "dropped %d rows with invalid values" % (rawlen - newlen)

# get dummy columns for categorical variables
airport_d = pd.get_dummies(df['Airport Name'])
site_d = pd.get_dummies(df['Claim Site'])

# use only the first word of the item category, i.e. "Luggage", etc.
item_d = pd.get_dummies(df['Item'].map(lambda x: str(x).split(' ', 1)[0]))

# map the date to a day of the week
dayofweek_d = pd.get_dummies(df['Date Received'].map(lambda x: \
    dt.datetime.strptime(str(x), '%d-%b-%y').weekday()))

# bring it all together
newdf = pd.concat([airport_d, site_d, item_d, \
    df['Claim Amount'], dayofweek_d, df['Status']], axis=1)

# clean and normalize the amount column, dropping excessively large values
newdf['Claim Amount'] = newdf['Claim Amount'].replace('[\$,\,]','', regex=True).astype(float)
newlen = len(df.index)
newdf = newdf[newdf['Claim Amount'] < 5000]
print "dropped %d very large claims" % (newlen - len(newdf.index))
newdf['Claim Amount'] = (newdf['Claim Amount'] - newdf['Claim Amount'].mean()) / newdf['Claim Amount'].std()

# map the final status to a target class (1: approved or settled, 0: other)
newdf = newdf.replace({'Status': TARGETMAP })

# clean any remaining unmapped/transformed rows
newlen = len(newdf.index)
newdf.dropna(inplace=True)
print "dropped %d remaining rows with invalid values" % (newlen - len(newdf.index))

randmask = np.random.rand(len(newdf)) < SPLIT

train = newdf[randmask]
test =  newdf[~randmask]
print "classes: accepted/total: train: %d/%d test: %d/%d" % \
    (len(train[train['Status'] == 1].index), len(train.index), \
    len(test[test['Status'] == 1].index), len(test.index))

# write the result to a new .csv file with the header line
# expected by load_csv_with_header() 
print "writing training file: %s" % OUT_TRAIN
with open(OUT_TRAIN, 'w') as of:
    of.write('%d,%d,Accepted,Other\n' % (len(train.index), len(train.columns) - 1))
    train.to_csv(of, index=False, header=False)
of.close()

print "writing test file: %s" % OUT_TEST
with open(OUT_TEST, 'w') as of:
    of.write('%d,%d,Accepted,Other\n' % (len(test.index), len(test.columns) - 1))
    test.to_csv(of, index=False, header=False)
of.close()

print "done"
