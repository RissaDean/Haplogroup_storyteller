#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Mar 10 09:08:13 2026

@author: inf-48-2025
"""

import pandas as pd

df = pd.read_excel('/home/inf-48-2025/BINP29/PopGenProj/Resources/Data/AADR_54.1/AADR_Annotations_2025.xlsx')
# %%
#read our list of old and new DNA from the input files

with open("/home/inf-48-2025/BINP29/PopGenProj/Resources/Data/AADR_54.1/Ancient_samples.txt") as oldList:
    lines = oldList.readlines()
    oldDNA = []
    for line in lines:
        line = line.lower().split()
        oldDNA.append(line[1])
    
with open("/home/inf-48-2025/BINP29/PopGenProj/Resources/Data/AADR_54.1/Modern_samples.txt") as newList:
    lines = newList.readlines()
    newDNA = []
    for line in lines:
        line = line.lower().split()
        newDNA.append(line[1])
        
# %%
oldHapGroups = {}
newHapGroups = {}
noncategorized = 0
for index, item in enumerate(df['Genetic ID'], start=0):
    item = str(item).strip().lower()
    if item in oldDNA:
        hapgroup = df.at[index, 'mtDNA haplogroup if >2x or published']
        oldHapGroups.update({item:hapgroup})
    elif item in newDNA:
        hapgroup = df.at[index, 'mtDNA haplogroup if >2x or published']
        newHapGroups.update({item:hapgroup})
    else:
        noncategorized = noncategorized+1