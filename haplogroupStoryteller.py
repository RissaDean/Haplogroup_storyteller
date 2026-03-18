#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Mar 10 09:08:13 2026

@author: inf-48-2025
"""
# %%
#import needed modules and set up our data

#import needed modules
import pandas as pd
from collections import Counter

#read the AADR dataset 
mainDF = pd.read_excel('/home/inf-48-2025/BINP29/PopGenProj/Resources/Data/AADR_54.1/v62.0_1240k_public.xlsx')

#extract just the relevant sections of the AADR dataset for more efficient searching down the line

            
df = pd.concat([mainDF.iloc[:, 0] , mainDF.iloc[:, 9], mainDF.iloc[:, 15], mainDF.iloc[:, 31], mainDF.iloc[:, 24]], axis=1)
# %%
#read our list of old and new DNA from the input files

#read in our list of estimated mtHaplogroup divergance dates
with open("/home/inf-48-2025/BINP29/PopGenProj/lineageDates.txt") as mtClock:
    lines = mtClock.readlines()
    ancestDates = {}
    for line in lines:
        line = line.split('\t')
        ancestDates.update({line[0].strip().lower():line[1].strip()})

#read in our list of anchient DNA samples
with open("/home/inf-48-2025/BINP29/PopGenProj/Resources/Data/AADR_54.1/Ancient_samples.txt") as oldList:
    lines = oldList.readlines()
    oldDNA = []
    for line in lines:
        line = line.lower().split()
        oldDNA.append(line[1])

#read in our list of modern DNA samples    
with open("/home/inf-48-2025/BINP29/PopGenProj/Resources/Data/AADR_54.1/Modern_samples.txt") as newList:
    lines = newList.readlines()
    newDNA = []
    for line in lines:
        line = line.lower().split()
        newDNA.append(line[1])
        
# %%
#set user group and search out mtDNA clock info 

#set user group
userGroup = 'm9a2c'
userGroupPrint = userGroup[0].upper()+userGroup[1:].lower() #a properly formatted one for output printing

#possible truncations in case full data isn't availible
userTrunc = userGroup
upTheTree = False
mainLineage = userGroup[0].lower()

#find the date our 'core' lineage split from the rest of humanity
firstSplit = ancestDates.get(mainLineage, "ERROR")

#find the latest divergence point present in our estimation data 
latestSplit = ancestDates.get(userTrunc, "ERROR")
#if no data, go back until we find data
if firstSplit == "ERROR" or latestSplit == "ERROR":
    while len(userTrunc) >= 1 and latestSplit == "ERROR":
        userTrunc = userTrunc[:-1]
        latestSplit = ancestDates.get(userTrunc, "ERROR")
    if len(userTrunc) == 1 and latestSplit == "ERROR":
        print("This lineage is not in our database, please check spelling and try again.")
    elif len(userTrunc) == 1:
        upTheTree = True

#print important info
firstSplit = int(firstSplit)
latestSplit = int(latestSplit)
print(f"The {mainLineage.upper()} lineage is estimated to have diverged from the rest of humanity around {firstSplit-2000} BCE")
if upTheTree == True:
    print("Our database has no information on dates for futher divergances of the line.")
else:    
    userTrunc = userTrunc[0].upper() + userTrunc[1:]
    print(f"The most recent common ancestor for the {userTrunc} maternal line is estimated to have lived around {latestSplit-2000} BCE")
        
# %%
#separate out modern and ancient DNA from AADR database
modernPeople = []
oldPeople = []

#run through the database and compile a list of the index values for our anchient and modern DNA sets
for index, item in enumerate(df.iloc[:, 0], start=0):
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

#iterate through the anchient and modern DNA sets and find all members of the core lineages
for oldPerson in oldPeople:
    oldHapGroup = str(df.at[oldPerson, 'mtDNA haplogroup if >2x or published']).lower()
    if oldHapGroup[0] == mainLineage:
        ancestors.append(oldPerson)

for modernPerson in modernPeople:
    newHapGroup = str(df.at[modernPerson, 'mtDNA haplogroup if >2x or published']).lower()
    if newHapGroup[0] == mainLineage:
        relatives.append(modernPerson)

# %%
#whittle down possible ancestors list 

#remove all members who differentiate into different lineages (example - if the user is U2c, all members of 
#U, U2, and U2c will be kept, but not U1 or U2a)
for index, letter in enumerate(str(userGroup), start=0):
    newAncestors = []
    for ancestor in ancestors:
        ancestorGroup = df.at[ancestor, 'mtDNA haplogroup if >2x or published']
        if len(ancestorGroup) <= index or len(ancestorGroup) > index and ancestorGroup[index].lower() == letter:
                newAncestors.append(ancestor)

#run through the ancester group one more time to throw out anything further differentiated than the user-submitted info
newAncestors = []    
for ancestor in ancestors:
    ancestorGroup = str(df.at[ancestor, 'mtDNA haplogroup if >2x or published']).strip()
    if len(ancestorGroup) <= len(userGroup):
        newAncestors.append(ancestor)
ancestors = newAncestors

# %%
#now we have only the ancient DNA that is the same group as our user (or from the same tree and not differentiated further) and we 
#can look for the oldest and newest members of this group

#empty variables to store our data
oldestAncestor = ''
oldestAncestorDate = 0
oldestAncestorHapGroup = 0

newestAncestor = ''
newestAncestorDate = 1000000000 #unlikely we'll have billion-year old samples, so this choice of starting point is unlikely to leave defaults active
newestAncestorHapGroup = 0

#run through the ancestors and keep track of the oldest and youngest members of the group
for ancestor in ancestors: 
    if df.iat[ancestor, 1] > oldestAncestorDate:
        oldestAncestor = ancestor
        oldestAncestorDate = df.iat[ancestor, 1]
        oldestAncestorHapGroup = df.at[ancestor,'mtDNA haplogroup if >2x or published']
    if df.iat[ancestor, 1] < newestAncestorDate:
        newestAncestor = ancestor
        newestAncestorDate = df.iat[ancestor, 1]
        newestAncestorHapGroup = df.at[ancestor,'mtDNA haplogroup if >2x or published'] 

#check the sex of the oldest and youngest ancestors
if df.at[oldestAncestor, 'Molecular Sex'].upper() == 'F':
    oldestAncestorSex = 'female'
elif df.at[oldestAncestor, 'Molecular Sex'].upper() == 'M':
    oldestAncestorSex = 'male'
else: 
    oldestAncestorSex = 'person of unknown sex'

if df.at[newestAncestor, 'Molecular Sex'].upper() == 'F':
    newestAncestorSex = 'female'
elif df.at[newestAncestor, 'Molecular Sex'].upper() == 'M':
    newestAncestorSex = 'male'
else: 
    newestAncestorSex = 'person of unknown sex'

#output information in user-friendly format      
if oldestAncestorDate > 1950:
    print(f"The oldest known member of the {userGroupPrint} line was a {oldestAncestorSex} who lived around {(1950-oldestAncestorDate)*-1} BCE in modern-day {df.iat[oldestAncestor, 2]}")
else:
    print(f"The oldest known member of the {userGroupPrint} line a {oldestAncestorSex} who lived around {1950-oldestAncestorDate} CE in modern-day {df.iat[oldestAncestor, 2]}")
  
    
if newestAncestorDate > 1950:
    print(f"The most recent archeological record of the {userGroupPrint} line in the AADR database was a {newestAncestorSex} who lived around {(1950-newestAncestorDate)*-1} BCE in modern-day {df.iat[newestAncestor, 2]}")
else:
    print(f"The most recent archeological record of the {userGroupPrint} line in the AADR database was a {newestAncestorSex} who lived around {1950-newestAncestorDate} CE in modern-day {df.iat[newestAncestor, 2]}")


# %%
#find info on relatives
relativeOrigins = []

#store the origins of all found relatives in a list 
for relative in relatives: 
    relativeOrigins.append(str(df.iat[relative, 2]).strip())

#use Counter to tally results    
groupCounts = Counter(relativeOrigins)

#if we don't find any relatives, give a placeholder message     
if len(relativeOrigins) == 0:
    print(f"No modern members of the {mainLineage.upper()} lineage have submitted their DNA to AADR")
#output results in user-friendly format    
else: 
    print(f"{len(relatives)} other modern members of the {mainLineage.upper()} lineage have submitted their DNA to AADR, tracing their origins to ")
    for index, country in enumerate(groupCounts.keys()):
        if len(groupCounts.keys()) == 1:
            print(f"{country} ({groupCounts[country]}.")
        elif index < len(groupCounts.keys())-1 and len(groupCounts.keys()) > 2:
            print(f"{country} ({groupCounts[country]}), ")
        elif index < len(groupCounts.keys())-1:
            print(f"{country} ({groupCounts[country]})")
        elif index == len(groupCounts.keys())-1:
            print(f"and {country} ({groupCounts[country]}).")
    


