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




class masslist_data():
    def __init__(self, path):
        super().__init__()
        self.path = path
        self.filename= str(os.path.split(self.path)[0])



    def __repr__(self):
        return "name of file is " +"  "+ str(os.path.split(self.path)[-1])


    def add_objects(self):
        workers = []
        if os.path.isfile(self.path):
            xx= str(os.path.split(self.path)[-1])

            if xx == ".mzXML":
                tree = ET.parse(self.path)
                root = tree.getroot()
                first= root.findall('.//{http://sashimi.sourceforge.net/schema_revision/mzXML_3.2}scan')
                second= root.findall('.//{http://sashimi.sourceforge.net/schema_revision/mzXML_3.2}peaks')
                for x, y in zip(first, second):
                    x= x.attrib
                    k= y.text
                    z= y.attrib
                    obj= Worker(x, k, z)
                    workers.append(obj)
        return worker



    def find_data(self):
        workers= self.add_objects()
        mlist= []
        scanlist= []
        rtlist= []
        size = []
        intensitylist= []


        for x in workers:
            a, b = x.tag_text()
            scan, _, _, retentiontime= x.tag_dict()
            mlist.extend(a)
            scanlist.extend([scan]* len(a))
            size.append(len(a))
            rtlist.extend([retentiontime] * len(a))
            intensitylist.extend(b)
        return mlist, rtlist, scanlist, intensitylist, size



    def make_dataframe(self):
        a, b, c, d, e = self.find_data()
        df1= pd.DataFrame({'mz': a, self.filename: d, 'scan': c, 'rt': b})
        return df1


    def peaklist_full(self):
        df1= self.make_dataframe()
        obj_peak= Peaklist_data(df1)
        peaks= obj_peak.find_peak()
        return peaks




class Worker():
    def __init__(self, x, y, z):
        super().__init__()
        self.tag = x
        self.text = y
        self.peaktag= z

    def tag_dict(self):
        data= self.tag
        scan= int(data['num'])
        basePeakMz= data['basePeakMz']
        basePeakIntensity= data['basePeakIntensity']
        basePeakIntensity= basePeakIntensity.strip()
        basePeakIntensity= re.sub('e0', 'e+0', basePeakIntensity)
        basePeakIntensity= round(float(basePeakIntensity), 4)
        retentionTime= data['retentionTime']
        retentionTime= re.sub('[^0-9.]+', '', retentionTime)
        return scan, basePeakMz, basePeakIntensity, retentionTime



    def tag_text(self):
        mz_list, intensity_list= [], []
        dd= self.peaktag
        coded= self.text
        mz_list= []
        precision = 'f'
        if dd['precision'] == 64:
            precision = 'd'

        # get endian
        endian = '!'
        if dd['byteOrder'] == 'little':
            endian = '<'
        elif dd['byteOrder'] == 'big':
            endian = '>'
        compression=None


        data = coded.encode("ascii")
        data = base64.decodebytes(data)

        mz_list= []

        if dd['compressionType'] == 'zlib':
            data = zlib.decompress(data)


        # convert from binary
        count = len(data) // struct.calcsize(endian + precision)
        data = struct.unpack(endian + precision * count, data[0:len(data)])
        points = map(list, zip(data[::2], data[1::2]))

        for x in points:

            mz_list.append(round(x[0], 4))
            intensity_list.append(round(x[-1], 4))

        return mz_list, intensity_list




class Peaklist_data():

    def __init__(self, obj):
        super().__init__()
        self.mass = obj



    def find_peak(self):
        df1= self.mass
        df1= df1[df1['intensity'] > 1000]
        minimum= df1['rt'].min()
        maximum= df1['rt'].max()
        minimum1= df1['mz'].min()
        maximum1= df1['mz'].max()
        thresold= 0.5
        thresold1= 0.005
        from numpy import arange
        ranges= arange(minimum, maximum, thresold)
        bins = pd.cut(df1['rt'], ranges)
        ranges1= arange(minimum1, maximum1, thresold1)
        bins1 = pd.cut(df1['mz'], ranges)
        grouped= df1.groupby(bins)
        dfm= pd.DataFrame()
        for i, k in grouped:
            groupx= k.groupby(bins1)
            for y, w in groupx:
                dfx= final(w)
                dfm= dfm.append(dfx, ignore_index= True)
        return dfm






if __name__ == "__main__":
