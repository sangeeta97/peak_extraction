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
import xml.etree.ElementTree as ET
plt.style.use('seaborn-pastel')
from spectrum_peak import *
from sklearn.cluster import DBSCAN
from sklearn import mixture
from scipy.optimize import linear_sum_assignment




class correspondance():
    def __init__(self, path):
        super().__init__()
        self.path = path
        self.mz_tolerance= 0.001
        self.rt_tolerance= 0.05


    def result(self):
        obj1= masslist_data(self.path)
        data= obj1.peaklist_full()
        return data


class combine():
    def __init__(self, dir):
        self.dir= dir
        self.mz_tolerance= 0.001
        self.rt_tolerance= 0.05


    def read_values(self):
        listdataframe= pd.DataFrame()
        for x in os.path.list():
            obj= correspondance(x)
            dd= obj.result()
            listdataframe= pd.concat([listdataframe, dd])

        return listdataframe



    def clusters(self):
        dataframes= self.read_values()
        min_samples= dataframes['initial'].nunique()
        ft_points = dataframes.loc[:, ["mz", "rt"]].copy()
        ft_points["rt"] = ft_points["rt"] * self.mz_tolerance / self.rt_tolerance
        dbscan = DBSCAN(eps=self.mz_tolerance, min_samples= min_samples,
                        metric="chebyshev")
        dbscan.fit(ft_points)
        cluster = pd.Series(data=dbscan.labels_, index=dataframes.index)
        full= dataframes.merge(cluster, how= 'inner', left_index= True, right_index= True)
        return full



    def dataframe_map(self):
        
