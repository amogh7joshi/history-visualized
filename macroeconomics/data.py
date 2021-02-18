#!/usr/bin/env python3
# -*- coding = utf-8 -*-
import os

import numpy as np
import pandas as pd

df = pd.read_excel(os.path.join(os.path.dirname(__file__), 'data/mpd2020.xlsx'), sheet_name = 'Full data')
unique = np.unique(df.country)
for u in unique:
   try:
      print(u)
      if df.loc[df['country'] == u]['year'].tolist()[0] == 1:
         print(df.loc[df['country'] == u]['year'].tolist())
         print(df.loc[df['country'] == u]['gdppc'].tolist())
   except:
      print('HELP!')

