#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Mar 12 14:46:29 2026

@author: inf-48-2025
"""

from dash import Dash, html, dcc, Input, Output, callback, State
import pandas as pd
from collections import Counter

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
        
def haplogroup_storyteller(userGroup): 
    return_text= ''
    nl = '\n'
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
    return_text = return_text+f"The {mainLineage} lineage is estimated to have diverged from the rest of humanity around {firstSplit-2000} BCE."
    return_text = return_text + "  "
    if upTheTree == True:
        return_text= return_text+"Our database has no information on dates for futher divergances of the line."
    else:    
        return_text= return_text+f"\nThe most recent common ancestor for the {userTrunc} maternal line is estimated to have lived around {latestSplit-2000} BCE"
    return(return_text)

app = Dash()

from igraph import Graph
import plotly.graph_objects as go

colors = {
    'background': '#ABCDD9',
    'text': '#F7FCFF'
}

usergroup = "U2c"
layers = len(usergroup)

nr_vertices = (len(usergroup)+(len(usergroup)-1))
v_label = list(map(str, range(nr_vertices)))
G = Graph.Tree(nr_vertices, 2) # 2 stands for children number

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
                font=dict(color='#FFFFFF', size=18),
                showarrow=False))
    else:
        annotations.append( 
             dict(
                 text='', # or replace labels with a different list for the text within the circle
                 x=position[k][0], y=2*M-position[k][1],
                 xref='x1', yref='y1',
                 font=dict(color='#FFFFFF', size=18),
                 showarrow=False) )


fig = go.Figure()
fig.add_trace(go.Scatter(x=Xe,
                   y=Ye,
                   mode='lines',
                   line=dict(color='#F0F0F0', width=3),
                   hoverinfo='none'
                   ))
fig.add_trace(go.Scatter(x=Xn,
                  y=Yn,
                  mode='markers',
                  name='bla',
                  hoverinfo='none',
                  marker=dict(symbol='circle',
                                size=60,
                                color='#81B1E3',    #'#DB4551',
                                line=dict(color='#FFFFFF', width=5)
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
              plot_bgcolor=colors['background']
              )
fig.update_yaxes(autorange="reversed")

app.layout = html.Div(children=[
    html.H1(children='Your Haplogroup Story',style={'textAlign': 'center','color': colors['text'],'font-size': 65}), 
    
    dcc.Input(id='input1'),
    
    html.Button('click me', id='button'),

   html.Div(#style={'backgroundColor': colors['background'], 'display': 'flex', 'flexDirection': 'column'}, 
            children=[
       html.Div(style={'display': 'flex', 'flexDirection': 'row'}, children=[   
           html.Div(id='output', style={"display": 'flex','textAlign': 'center', 'vertical-align': 'top',
                                        'color': '#292929', 'justify-content': 'center', 'background-color':'#F0F0F0', 'padding': 10, 'flex': 1}),

           html.Div(children=[dcc.Graph(id='example-graph', figure=fig, style={"display": 'flex','color':colors['background'], 'padding': 10, 'flex': 1}, 
           ), ])          
           ])])])

@app.callback(
    Output('output', 'children'),
    [Input('button', 'n_clicks')],
    State('input1', 'value'))

def update_output_div(n_clicks, input_value):
    display_text = haplogroup_storyteller(input_value)
    return(display_text)


if __name__ == '__main__':
    app.run(debug=True)