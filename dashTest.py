#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Mar 12 14:46:29 2026

@author: inf-48-2025
"""

from dash import Dash, html, dcc, Input, Output, State
import pandas as pd
from collections import Counter
import plotly.graph_objects as go
from pathlib import Path
import argparse


parser = argparse.ArgumentParser()

parser.add_argument("AADR_metadata", help= "the file containing our AADR metadata information")
parser.add_argument("--lineage_dates", help= "file containing desired lineage divergence dates", default= Path(__file__).parent/ "./Assets/lineageDates.txt")
parser.add_argument("--ancient_samples", help= "file containing AADR gene IDs for ancient DNA samples", default= Path(__file__).parent/ "./Assets/Ancient_samples.txt")
parser.add_argument("--modern_samples", help= "file containing AADR gene IDs for modern DNA samples", default= Path(__file__).parent/ "./Assets/Modern_samples.txt")

args = parser.parse_args()

AADRfile = args.AADR_metadata
lineageDates = args.lineage_dates
ancientSamples = args.ancient_samples
modernSamples = args.modern_samples



mainDF = pd.read_excel(AADRfile)
#extract just the relevant sections of the AADR dataset for more efficient searching down the line

            
df = pd.concat([mainDF.iloc[:, 0] , mainDF.iloc[:, 9], mainDF.iloc[:, 15], mainDF.iloc[:, 31], mainDF.iloc[:, 24]], axis=1)

# %%
with open(lineageDates) as mtClock:
    lines = mtClock.readlines()
    ancestDates = {}
    for line in lines:
        line = line.split('\t')
        ancestDates.update({line[0].strip().lower():line[1].strip()})

with open(ancientSamples) as oldList:
    lines = oldList.readlines()
    oldDNA = []
    for line in lines:
        line = line.lower().split()
        oldDNA.append(line[1])
    
with open(modernSamples) as newList:
    lines = newList.readlines()
    newDNA = []
    for line in lines:
        line = line.lower().split()
        newDNA.append(line[1])
# %%
app = Dash()



colors = {
    'blue': '#C5E3ED',
    'black': '#616161',
}

def haplogroup_storyteller(userGroup): 
    return_text= []
    
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
            return_text.append("This lineage is not in our database, please check spelling and try again.")
            return(return_text)
        elif len(userTrunc) == 1:
            upTheTree = True

    #print important info
    firstSplit = int(firstSplit)
    latestSplit = int(latestSplit)
    
    return_text.append(f"The {mainLineage.upper()} lineage is estimated to have diverged from the rest of humanity around {firstSplit-2000} BCE")
    if upTheTree == True:
        return_text.append("Our database has no information on dates for futher divergances of the line.")
    else:    
        userTrunc = userTrunc[0].upper() + userTrunc[1:]
        return_text.append(f"The most recent common ancestor for the {userTrunc} maternal line is estimated to have lived around {latestSplit-2000} BCE")
    
    #separate out modern and ancient DNA from AADR database
    modernPeople = []
    oldPeople = []

    #run through the database and compile a list of the index values for our anchient and modern DNA sets
    for index, item in enumerate(df.iloc[:,0], start=0):
        item = str(item).strip().lower()
        if item in newDNA:
            modernPeople.append(index)
        if item in oldDNA:
            oldPeople.append(index)
        else:
            pass
    
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
        return_text.append(f"The oldest known member of the {userGroupPrint} line was a {oldestAncestorSex} who lived around {(1950-oldestAncestorDate)*-1} BCE in modern-day {df.iat[oldestAncestor, 2]}")
    else:
        return_text.append(f"The oldest known member of the {userGroupPrint} line a {oldestAncestorSex} who lived around {1950-oldestAncestorDate} CE in modern-day {df.iat[oldestAncestor, 2]}")
      
        
    if newestAncestorDate > 1950 and oldestAncestor != newestAncestor:
        return_text.append(f"The most recent archeological record of the {userGroupPrint} line in the AADR database was a {newestAncestorSex} who lived around {(1950-newestAncestorDate)*-1} BCE in modern-day {df.iat[newestAncestor, 2]}")
    elif oldestAncestor != newestAncestor:
        return_text.append(f"The most recent archeological record of the {userGroupPrint} line in the AADR database was a {newestAncestorSex} who lived around {1950-newestAncestorDate} CE in modern-day {df.iat[newestAncestor, 2]}")
    
    #find info on relatives
    relativeOrigins = []

    #store the origins of all found relatives in a list 
    for relative in relatives: 
        relativeOrigins.append(str(df.iat[relative, 2]).strip())

    #use Counter to tally results    
    groupCounts = Counter(relativeOrigins)

    #if we don't find any relatives, give a placeholder message     
    if len(relativeOrigins) == 0:
        return_text.append(f"No modern members of the {mainLineage.upper()} lineage have submitted their DNA to AADR")
    #output results in user-friendly format    
    else: 
        acrossTheWorld = (f"{len(relatives)} other modern members of the {mainLineage.upper()} lineage have submitted their DNA to AADR, tracing their origins to ")
        for index, country in enumerate(groupCounts.keys()):
            if len(groupCounts.keys()) == 1:
                acrossTheWorld = acrossTheWorld + f"{country} ({groupCounts[country]})."
            elif index < len(groupCounts.keys())-1 and len(groupCounts.keys()) > 2:
                acrossTheWorld = acrossTheWorld + f"{country} ({groupCounts[country]}), "
            elif index < len(groupCounts.keys())-1:
                acrossTheWorld = acrossTheWorld + f"{country} ({groupCounts[country]}) "
            elif index == len(groupCounts.keys())-1:
                acrossTheWorld = acrossTheWorld + f"and {country} ({groupCounts[country]})."
        return_text.append(acrossTheWorld)
    return(return_text)
# %%


def graph_make(usergroup):
    layers = len(usergroup)
    userGroupPrint = usergroup[0].upper()+usergroup[1:].lower() #a properly formatted one for output printing
    position = []
    for k in range(0,layers):
        position.append((((k - (layers/2))),((layers-k))))
    for k in range(0,layers):
        if k > 0:
            position.append((((k - (layers/2) + 0.5)),((layers-k+1)))) 

    M = layers
    
    E = [] 
    for i in range(0,layers-1):
        E.append((i,i+1))
    for i in range(0,layers):    
        if i > 0:
            E.append((i+layers-1,i))

    L = len(position)
    Xn = [position[k][0] for k in range(L)]
    Yn = [2*M-position[k][1] for k in range(L)]
    Xe = []
    Ye = []
    for edge in E:
        Xe+=[position[edge[0]][0],position[edge[1]][0], None]
        Ye+=[2*M-position[edge[0]][1],2*M-position[edge[1]][1], None]


    annotations = []
    for k in range(L):
        if k < layers:
            annotations.append( 
                dict(
                    text=userGroupPrint[0:(k+1)], # or replace labels with a different list for the text within the circle
                    x=position[k][0], y=2*M-position[k][1],
                    xref='x1', yref='y1',
                    font=dict(color=colors['black'], size=18),
                    showarrow=False))
        else:
                annotations.append( 
                    dict(
                 text='', # or replace labels with a different list for the text within the circle
                 x=position[k][0], y=2*M-position[k][1],
                 xref='x1', yref='y1',
                 font=dict(color=colors['black'], size=18),
                 showarrow=False) )


    fig = go.Figure()
    fig.add_trace(go.Scatter(x=Xe,
                   y=Ye,
                   mode='lines',
                   line=dict(color=colors['black'], width=3),
                   hoverinfo='none'
                   ))
    fig.add_trace(go.Scatter(x=Xn,
                  y=Yn,
                  mode='markers',
                  name='bla',
                  hoverinfo='none',
                  marker=dict(symbol='circle',
                                size=60,
                                color='#EDE3C5',    #'#DB4551',
                                line=dict(color=colors['black'], width=5)
                                ),
                  opacity=1
                  ))

    axis = dict(showline=False, # hide axis line, grid, ticklabels and  title
            zeroline=False,
            showgrid=False,
            showticklabels=False,
            )

    fig.update_layout(annotations=annotations, 
              font_size=12,
              showlegend=False,
              xaxis=axis,
              yaxis=axis,
              margin=dict(l=0, r=0, b=0, t=0),
              plot_bgcolor='#FFFFFF'
              )
    fig.update_yaxes(autorange="reversed")
    return(fig)

app.layout = html.Div(children=[
    html.H1(children='Your Haplogroup Story',style={'textAlign': 'center','color': colors['black'],'font-size': 65}), 
    
    dcc.Input(id='input1', style={'color': colors['black']}),
    
    html.Button('click to see your haplogroup story', id='button'),

   html.Div(style={'backgroundColor':'#FFFFFF', 'display': 'flex', 'flexDirection': 'row'}, 
            children=[html.Div(id= 'textOutput'),
       html.Div(style={'display': 'flex', 'flexDirection': 'row', 'vertical-align': 'top'}, children=[   
           html.Div(id='graphOutput',),
        
           ])])],)

@app.callback([
    Output('graphOutput', 'children'),
    Output('textOutput', 'children')],
    [Input('button', 'n_clicks')],
    State('input1', 'value'))

def update_output_div(n_clicks, input1):
    if input1 == None:
        graph = ''
        returntext = ''
    else:
        input_value = input1.lower()
        display_text = haplogroup_storyteller(input_value)
        returntext = []
        for statement in display_text:
            returntext.append(dcc.Markdown(statement, style={"display":"flex", "flexDirection":"column", 'vertical-align': 'top', 'background-color': colors['blue'],
                                                         'border-radius': '25px', 'border-style':'solid', 'border-color': colors['black'], 'padding-left':10, 'padding-right':10,
                                                         'marginBottom': '1em', 'color':colors['black'], 'font-size':18}))
        fig = graph_make(input_value)
        graph = dcc.Graph(id='dynamic-graph', figure=fig, style={"display": 'flex','color':'#FFFFFF', 'padding': 10, 'flex': 1}, )
    return(graph, returntext)


if __name__ == '__main__':
    app.run(debug=True)