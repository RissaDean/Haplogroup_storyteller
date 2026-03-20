#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
haplogroupStoryteller.py

Description: This is a simple program that interfaces with the Allen Ancient DNA Resource and mtDNA
haplogroup divergence preditions from Soares et al to create a non-scientist-friendly summarization
of information availible from a user-input haplogroup. 

User-defined functions: None
Non-standard modules: None

Procedure:
    1. Import needed modules and set up command-line arguements
    2. Read asset files for use within program
    3. Define main function
        3a. Parse user input
        3b. Compile list of "possible ancestors" and "possible relatives" and filter
        3c. Find oldest and youngest ancestor in AADR database and their moelcular sex
        3d. compile origins of possible relatives
        3e. Store information in readable format and return as list. 
    4. Define graphing function
        4a. Set node positions
        4b. Define edges to connect nodes 
        4c. list annotations
        4d. Create figure, add nodes and edges
        4e. Update graph visuals for readability
        4f. Return figure
    5. Set up app layout
    6. Define callback function
    7. Run dash app

Input: AADR metadata excel file, text document with lineage divergence dates (provided), text documents with
        lists of ancient and modern lineage IDs (provided)
    
Output: interactive dashboard

Usage: haplogroupStoryteller.py AADR_54.1/v62.0_1240k_public.xlsx --lineage_dates lineageDates.txt[optional] --ancient_samples ancientSamples.txt[optional] --modern_samples modernSamples.txt[optional]
    
Version 1.0: 
Date: 19-3-2026
Name: Marissa Dean
"""
# %%
#import needed modules and set up command-line arguements

#import modules
from dash import Dash, html, dcc, Input, Output, State
import pandas as pd
from collections import Counter
import plotly.graph_objects as go
from pathlib import Path
import argparse

#set up the command-line arguements
parser = argparse.ArgumentParser()


parser.add_argument("AADR_metadata", help= "the file containing our AADR metadata information")
parser.add_argument("--lineage_dates", help= "file containing desired lineage divergence dates", default= Path(__file__).parent/ "./Assets/lineageDates.txt")
parser.add_argument("--ancient_samples", help= "file containing AADR gene IDs for ancient DNA samples", default= Path(__file__).parent/ "./Assets/Ancient_samples.txt")
parser.add_argument("--modern_samples", help= "file containing AADR gene IDs for modern DNA samples", default= Path(__file__).parent/ "./Assets/Modern_samples.txt")

#read the arguements from the console
args = parser.parse_args()

AADRfile = args.AADR_metadata
lineageDates = args.lineage_dates
ancientSamples = args.ancient_samples
modernSamples = args.modern_samples

#check that our inputs are real files
def input_test(argument):
    try: 
        open(argument)
    except:
        print(f"The {argument} file does not exist or cannot be opened.")
        exit()

input_test(AADRfile)
input_test(lineageDates)
input_test(ancientSamples)
input_test(modernSamples)


# %%
#read input files

#read the AADR file into the program
mainDF = pd.read_excel(AADRfile)

#extract just the relevant sections of the AADR dataset for more efficient searching down the line           
df = pd.concat([mainDF.iloc[:, 0] , mainDF.iloc[:, 9], mainDF.iloc[:, 15], mainDF.iloc[:, 31], mainDF.iloc[:, 24]], axis=1)

#read in the lineage divergence dates from the Soares et al estimates
with open(lineageDates) as mtClock:
    lines = mtClock.readlines()
    ancestDates = {}
    for line in lines:
        line = line.split('\t')
        ancestDates.update({line[0].strip().lower():line[1].strip()})

#read in the list of AADR ancient DNA sample IDs
with open(ancientSamples) as oldList:
    lines = oldList.readlines()
    oldDNA = []
    for line in lines:
        line = line.lower().split()
        oldDNA.append(line[1])

#read in the list of AADR modern DNA sample IDs
with open(modernSamples) as newList:
    lines = newList.readlines()
    newDNA = []
    for line in lines:
        line = line.lower().split()
        newDNA.append(line[1])

#correlate our sample IDs with dataframe index numbers
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
# %%
#set up the data-filtering function

def haplogroup_storyteller(userGroup): 
    #variable to store the text we'll be outputting to the app display
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
        return_text.append(f"The woman who was the most recent common ancestor for the {userTrunc} line is estimated to have lived around {latestSplit-2000} BCE")

    
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

    newestAncestor = ''
    newestAncestorDate = 1000000000 #unlikely we'll have billion-year old samples, so this choice of starting point is unlikely to leave defaults active

    #run through the ancestors and keep track of the oldest and youngest members of the group
    for ancestor in ancestors: 
        if df.iat[ancestor, 1] > oldestAncestorDate:
            oldestAncestor = ancestor
            oldestAncestorDate = df.iat[ancestor, 1]
        if df.iat[ancestor, 1] < newestAncestorDate:
            newestAncestor = ancestor
            newestAncestorDate = df.iat[ancestor, 1]

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
        return_text.append(f"The oldest known member of the {userGroupPrint} line was a {oldestAncestorSex} who lived around {int((1950-oldestAncestorDate)*-1)} BCE in modern-day {df.iat[oldestAncestor, 2]}")
    else:
        return_text.append(f"The oldest known member of the {userGroupPrint} line was a {oldestAncestorSex} who lived around {int(1950-oldestAncestorDate)} CE in modern-day {df.iat[oldestAncestor, 2]}")
      
        
    if newestAncestorDate > 1950 and oldestAncestor != newestAncestor:
        return_text.append(f"The most recent archeological record of the {userGroupPrint} line in the AADR database was a {newestAncestorSex} who lived around {int((1950-newestAncestorDate)*-1)} BCE in modern-day {df.iat[newestAncestor, 2]}")
    elif oldestAncestor != newestAncestor:
        return_text.append(f"The most recent archeological record of the {userGroupPrint} line in the AADR database was a {newestAncestorSex} who lived around {int(1950-newestAncestorDate)} CE in modern-day {df.iat[newestAncestor, 2]}")
    
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
#define the graphing function

def graph_make(usergroup):
    layers = len(usergroup) #this will determine how many "generations" our figure shows 
    userGroupPrint = usergroup[0].upper()+usergroup[1:].lower() #a properly formatted one for output printing
    
    #list the nodes of the tree graph
    position = []
    for k in range(0,layers): #nodes for each layer of the haplogroup
        position.append((((k - (layers/2))),((layers-k))))
    for k in range(0,layers): #extra nodes to represent the paternal lines
        if k > 0:
            position.append((((k - (layers/2) + 0.5)),((layers-k+1)))) 
    
    #list edges
    E = [] 
    for i in range(0,layers-1): #edges to connect maternal line
        E.append((i,i+1))
    for i in range(0,layers): #tying paternal line into offspring
        if i > 0:
            E.append((i+layers-1,i))
    
    #connect the nodes with the edges
    L = len(position)
    Xn = [position[k][0] for k in range(L)]
    Yn = [2*layers-position[k][1] for k in range(L)]
    Xe = []
    Ye = []
    for edge in E:
        Xe+=[position[edge[0]][0],position[edge[1]][0], None]
        Ye+=[2*layers-position[edge[0]][1],2*layers-position[edge[1]][1], None]

    #create the list of annotations
    annotations = []
    for k in range(L):
        if k < layers: #annotate the haplogroup distinctions onto the maternal nodes
            annotations.append( 
                dict(
                    text=userGroupPrint[0:(k+1)], 
                    x=position[k][0], y=2*layers-position[k][1],
                    xref='x1', yref='y1',
                    font=dict(color=colors['black'], size=18),
                    showarrow=False))
        else: #we don't need annotations on the paternal nodes
                annotations.append( 
                    dict(
                 text='', 
                 x=position[k][0], y=2*layers-position[k][1],
                 xref='x1', yref='y1',
                 font=dict(color=colors['black'], size=18),
                 showarrow=False) )

    #create the figure
    fig = go.Figure()
    
    #add the lines
    fig.add_trace(go.Scatter(x=Xe,
                   y=Ye,
                   mode='lines',
                   line=dict(color=colors['black'], width=3),
                   hoverinfo='none'
                   ))
    #add the nodes
    fig.add_trace(go.Scatter(x=Xn,
                  y=Yn,
                  mode='markers',
                  name='bla',
                  hoverinfo='none',
                  marker=dict(symbol='circle',
                                size=60,
                                color='#EDE3C5', 
                                line=dict(color=colors['black'], width=5)
                                ),
                  opacity=1
                  ))

    #hide axis line, grid, ticklabels and  title
    axis = dict(showline=False, 
            zeroline=False,
            showgrid=False,
            showticklabels=False,
            )

    #improve visual look of plot
    fig.update_layout(title= f'Maternal descent of {userGroupPrint} line',
              annotations=annotations, 
              font_size=12,
              showlegend=False,
              xaxis=axis,
              yaxis=axis,
              margin=dict(l=0, r=0, b=0, t=0),
              plot_bgcolor=colors['white']
              )
    fig.update_yaxes(autorange="reversed")
    
    #send the figure back to the main script
    return(fig)
# %%
#set up dash app and layout

app = Dash()

#dictionary of colors to use later
colors = {
    'blue': '#C5E3ED',
    'black': '#616161',
    'white':'#FFFFFF'
}

#app layout
app.layout = html.Div(children=[
    html.H1(children='Your Haplogroup Story',style={'textAlign': 'center','color': colors['black'],'font-size': 65}), #title
    
    dcc.Markdown("""The mitochondrial DNA (or mtDNA) is passed directly from mother to child. Over the millenia, mutations have accumulated in different lines of humanity, allowing us to identify specific "haplogroups". 
                 These groups are characteristic patterns of mutation that can identify the divergence of ancient humanity. Enter your mitochondrial haplogroup to learn more about your evolutionary history and see
                 a 'family tree' of your maternal lineage based on the work of Soares et al and the Allen Ancient DNA Resource (AADR)"""),
    
    dcc.Input(id='input1', style={'color': colors['black']}), #input box
    
    html.Button('click to see your haplogroup story', id='button'), #button to update callbacks

   html.Div(style={'backgroundColor':colors['white'], 'display': 'flex', 'flexDirection': 'row', }, #main content
            children=[html.Div(id= 'textOutput', style={'padding-right':15}), #textboxes
       html.Div(style={'display': 'flex', 'flexDirection': 'row', 'vertical-align': 'top', }, children=[ #graph
           html.Div(id='graphOutput', ), 
        
           ])])],)
# %%
#set up callbacks

@app.callback([
    Output('graphOutput', 'children'),
    Output('textOutput', 'children')],
    [Input('button', 'n_clicks')],
    State('input1', 'value'))

#callback update function
def update_output_div(n_clicks, input1):
    if input1 == None or input1 == '': #blank content to display initially or with misclicks
        graph = ''
        returntext = ''
    else:
        input_value = input1.lower() #this value will be the haplogroup we input
        display_text = haplogroup_storyteller(input_value) #run the data filtering function to get the text for the textboxes
        returntext = []
        for statement in display_text: #throw each statement into its own textbox
            returntext.append(dcc.Markdown(statement, style={"display":"flex", "flexDirection":"column", 'vertical-align': 'top', 'background-color': colors['blue'],
                                                         'border-radius': '25px', 'border-style':'solid', 'border-color': colors['black'], 'padding-left':10, 'padding-right':10,
                                                         'marginBottom': '1em', 'color':colors['black'], 'font-size':18}))
        fig = graph_make(input_value) #run the graphmaking function to give us a figure
        #place the figure in a graph module
        graph = dcc.Graph(id='dynamic-graph', figure=fig, style={'color': colors['white'], 'padding': 10, 'flex': 1,}, )
    return(graph, returntext)

#run the application!
if __name__ == '__main__':
    app.run(debug=True)