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
plt.style.use('seaborn-pastel')
#matplotlib.use('Agg')


import xml.etree.ElementTree as ET
tree = ET.parse('699_PH1_WH1.mzXML')
root = tree.getroot()

import re

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



def create_workers():
    mlist=[]
    rtlist=[]
    scanlist=[]
    intensitylist=[]
    size= []


    workers = []
    first= root.findall('.//{http://sashimi.sourceforge.net/schema_revision/mzXML_3.2}scan')
    second= root.findall('.//{http://sashimi.sourceforge.net/schema_revision/mzXML_3.2}peaks')
    for x, y in zip(first, second):
        x= x.attrib
        k= y.text
        z= y.attrib
        obj= Worker(x, k, z)
        workers.append(obj)


    for x in workers:
        a, b = x.tag_text()
        scan, _, _, retentiontime= x.tag_dict()
        mlist.extend(a)
        scanlist.extend([scan]* len(a))
        size.append(len(a))
        rtlist.extend([retentiontime] * len(a))
        intensitylist.extend(b)

    df1= pd.DataFrame({'mz': a, 'intensity': d, 'scan': c, 'rt': b})


    return mlist, rtlist, scanlist, intensitylist, size, df1






if __name__ == "__main__":
    a, b, c, d, e, _ = create_workers()
    print(len(a))
    print(len(b))
    print(len(c))
    print(len(d))
    print(len(e))
    import pandas as pd
    df1= pd.DataFrame({'mz': a, 'intensity': d, 'scan': c, 'rt': b})
    df1.to_csv('masslist.csv')
