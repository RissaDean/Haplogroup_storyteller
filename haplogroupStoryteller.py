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

with open("/home/inf-48-2025/BINP29/PopGenProj/lineageDates.txt") as mtClock:
    lines = mtClock.readlines()
    ancestDates = {}
    for line in lines:
        line = line.split('\t')
        ancestDates.update({line[0].strip().lower():line[1].strip()})

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
#set user group and search out mtDNA clock info 
userGroup = 'u2'

#possible truncations in case full data isn't availible
userTrunc = userGroup
upTheTree = False

mainLineage = userGroup[0]

firstSplit = ancestDates.get(mainLineage, "ERROR")

latestSplit = ancestDates.get(userTrunc, "ERROR")

#if no data, go back until we find data
if firstSplit == "ERROR" or latestSplit == "ERROR":
    while len(userTrunc) >= 1 and latestSplit == "ERROR":
        userTrunc = userTrunc[:-1]
        latestSplit = ancestDates.get(userTrunc, "ERROR")
    if len(userTrunc) == 1 and latestSplit == "ERROR":
        print("This lineage is not in our database, please check spelling and try again.")
        quit()
    elif len(userTrunc) == 1:
        upTheTree = True

#print important info
firstSplit = int(firstSplit)
latestSplit = int(latestSplit)
print(f"The {mainLineage} lineage is estimated to have diverged from the rest of humanity around {firstSplit-2000} BCE")
if upTheTree == True:
    print("Our database has no information on dates for futher divergances of the line.")
else:    
    print(f"The most recent common ancestor for the {userTrunc} maternal line is estimated to have lived around {latestSplit-2000} BCE")
        
# %%
#separate out modern and ancient DNA from AADR database
modernPeople = []
oldPeople = []

for index, item in enumerate(df['Genetic ID'], start=0):
    item = str(item).strip().lower()
    if item in newDNA:
        modernPeople.append(index)
    if item in oldDNA:
        oldPeople.append(index)
    else:
        pass

# %%
#compile list of possible ancestors and relatives
ancestors = []
relatives = []

for oldPerson in oldPeople:
    oldHapGroup = str(df.at[oldPerson, 'mtDNA haplogroup if >2x or published']).lower()
    if oldHapGroup[0] == mainLineage:
        ancestors.append(oldPerson)

for modernPerson in modernPeople:
    newHapGroup = str(df.at[modernPerson, 'mtDNA haplogroup if >2x or published']).lower()
    if newHapGroup[0] == mainLineage:
        relatives.append(modernPerson)

# %%
# oldestAncestor = ''
# oldestAncestorDate = 0
# oldestAncestorHapGroup = 0

# newestAncestor = ''
# newestAncestorDate = 1000000000
# newestAncestorHapGroup = 0

# for ancestor in ancestors: 
#     if df.iat[ancestor, 8] > oldestAncestorDate:
#         oldestAncestor = ancestor
#         oldestAncestorDate = df.iat[ancestor, 8]
#         oldestAncestorHapGroup = df.at[ancestor,'mtDNA haplogroup if >2x or published']
        
# if oldestAncestorDate > 1950:
#     print(f"The oldest known member of the {userGroup} line lived around {(1950-oldestAncestorDate)*-1} BCE in modern-day {df.iat[oldestAncestor, 14]}")
# else:
#     print(f"The oldest known member of the {userGroup} line lived around {1950-oldestAncestorDate} CE in modern-day {df.iat[oldestAncestor, 14]}")

# %%
#whittle down possible ancestors list 

for index, letter in enumerate(str(userGroup), start=0):
    print(index, letter)
    print(len(ancestors))
    newAncestors = []
    for ancestor in ancestors:
        ancestorGroup = df.at[ancestor, 'mtDNA haplogroup if >2x or published']
        if len(ancestorGroup) <= index or len(ancestorGroup) > index and ancestorGroup[index].lower() == letter:
                newAncestors.append(ancestor)
    print(f"the length of the new group is {len(newAncestors)}")
    if len(newAncestors) != 0:
        ancestors = newAncestors
    else:
        break
newAncestors = []    
for index, ancestor in enumerate(ancestors):
    ancestorGroup = df.at[ancestor, 'mtDNA haplogroup if >2x or published']
    if len(ancestorGroup) <= len(userGroup):
        print(ancestorGroup)
        newAncestors.append(ancestor)
ancestors = newAncestors
    
    
# if df.iat[ancestor, 8] < newestAncestorDate:
#     newestAncestor = ancestor
#     newestAncestorDate = df.iat[ancestor, 8]
#     newestAncestorHapGroup = df.at[ancestor,'mtDNA haplogroup if >2x or published'] 
     


# if newestAncestorDate > 1950:
#     print(f"The most recent member of the {userGroup} line in the AADR database lived around {(1950-newestAncestorDate)*-1} BCE in modern-day {df.iat[newestAncestor, 14]}")
# else:
#     print(f"The most recent member of the {userGroup} line in the AADR database lived around {1950-newestAncestorDate} CE in modern-day {df.iat[newestAncestor, 14]}")

# %%
#find info on relatives
relativeOrigins = set()

for relative in relatives: 
    relativeOrigins.add(df.iat[relative, 14])
    
if len(relativeOrigins) > 0:
    print(f"{len(relatives)} other modern members of the {userGroup} lineage have submitted their DNA to AADR, tracing their origins to the following countries:")
    print(relativeOrigins)
    
else: 
    print(f"No other modern members of the {userGroup} lineage have submitted their DNA to AADR")
    
