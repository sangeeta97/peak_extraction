import pandas as pd
import logging
import zipfile
import argparse
import re
import sys
import warnings
import pywt
import numpy as np
import matplotlib.pyplot as plt
import matplotlib
import sys
import base64
import zlib
import struct
import pandas as pd


import matplotlib.pyplot as plt
from scipy.misc import electrocardiogram
from scipy.signal import find_peaks
import numpy as np
import scipy
# #
#Utility Functions
# #
def peaks_find(x):

    peak, _= scipy.signal.find_peaks(x)

    return peak


def smoothing(data):
    for ii in range(3):
        (data, coeff_d) = pywt.dwt(data, 'sym5')
    return data

def peak_loc(xx):
    data= smoothing(xx)
    peak_indexes = scipy.signal.argrelextrema(data, np.greater)
    peak_indexes = peak_indexes[0]
    return peak_indexes

def peaks_property_left(x, y):
    _, left_bases, _ = scipy.signal.peak_prominences(x, y)
    return left_bases
#
#
def peaks_property_right(x, y):
    _, _, right = scipy.signal.peak_prominences(x, y)
    return right
#

def peak_range(x,y,z):
    dd=[]
    for e,r in zip(x,y):
        kk= z[e:r]
        dd.append(kk)
    return dd
#

def peak_area(scan_array, intensity_array, start, stop):
    area = 0

    for i in range(start + 1, stop):
        x1 = scan_array[i - 1]
        y1 = intensity_array[i - 1]
        x2 = scan_array[i]
        y2 = intensity_array[i]
        area += (y1 * (x2 - x1)) + ((y2 - y1) * (x2 - x1) / 2.)
    return area



def row_area(row):
    cc = row['intensity_range']
    ck = row['intensity_range']
    cm = row['points']
    return peak_area(list(range(row['points'])), ck[0], 0, cm)




##function to integrate utility Functions

def final(df):
    try:
        x= np.array(df['intensity'].tolist())
        y= np.array(df['mz'].tolist())
        z= np.array(df['scan'].tolist())
        w= np.array(df['rt'].tolist())
        peak= peaks_find(x)
        if len(peak) >= 1:
            from scipy.signal import chirp, find_peaks, peak_widths
            result_half = peak_widths(x, peak, rel_height=0.5)
            result_half= result_half[0]
            result_half= np.array(result_half)
            result_bol= (result_half > 2) & (result_half < 20)
            peak= peak[result_bol]
            peak_mz= y[peak]
            peak_intensity= x[peak]
            peak_rt= w[peak]
            left_index= peaks_property_left(x, peak)
            right_index= peaks_property_right(x, peak)
            scan_range= peak_range(left_index, right_index, z)
            mz_range= peak_range(left_index, right_index, y)
            intensity_range= peak_range(left_index, right_index, x)
            master_dict= {'peak_mz': peak_mz, 'peak_intensity': peak_intensity, 'peak_rt': peak_rt, 'mz_range': mz_range, 'intensity_range': intensity_range, 'scan_range': scan_range}
            df9= pd.DataFrame(master_dict)
            return df9

    except Exception as e:
        print(e)

# putting all together


df1= pd.read_csv('masslist.csv')
df1= df1[df1['intensity'] > 1000]

minimum= df1['mz'].min()
maximum= df1['mz'].max()
thresold= 0.005
from numpy import arange
ranges= arange(minimum, maximum, thresold)
bins = pd.cut(df1['mz'], ranges)

grouped= df1.groupby(bins)

dfm= pd.DataFrame()

for i, k in grouped:
    dfx= final(k)
    dfm= dfm.append(dfx, ignore_index= True)

dfm.to_csv('peaksn1.csv')






#
# df1= pd.read_csv('masslist.csv')
# df1= df1[df1['intensity'] > 1000]
#
# minimum= df1['rt'].min()
# maximum= df1['rt'].max()
# thresold= 10
#
# from numpy import arange
#
#
#
# ranges= arange(minimum, maximum, thresold)
# bins = pd.cut(df1['rt'], ranges)
# print(bins)
#
#
# grouped= df1.groupby(bins)
#
#
# for x, i in grouped:
#     print(i)
#     print(i['rt'])
#     dfx= final(i)
#     dfm= dfm.append(dfx, ignore_index= True)
#
#
# df1.to_csv('peakselected.csv')
