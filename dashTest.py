#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Mar 12 14:46:29 2026

@author: inf-48-2025
"""

from dash import Dash, html, dcc, Input, Output, callback, State
import pandas as pd
from collections import Counter

# %%
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
app = Dash()

from igraph import Graph
import plotly.graph_objects as go

colors = {
    'blue': '#C5E3ED',
    'black': '#616161',
}

def haplogroup_storyteller(userGroup): 
    return_text= []
    
    userTrunc = userGroup
    
    upTheTree = False

    mainLineage = userGroup[0].lower()

    firstSplit = ancestDates.get(mainLineage, "ERROR")

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
    return_text.append(f"The {mainLineage} lineage is estimated to have diverged from the rest of humanity around {firstSplit-2000} BCE.")
    if upTheTree == True:
        return_text.append("Our database has no information on dates for futher divergances of the line.")
    else:    
        return_text.append(f"The most recent common ancestor for the {userTrunc} maternal line is estimated to have lived around {latestSplit-2000} BCE")
    return(return_text)

def graph_make(usergroup):
    layers = len(usergroup)

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
                    text=usergroup[0:(k+1)], # or replace labels with a different list for the text within the circle
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