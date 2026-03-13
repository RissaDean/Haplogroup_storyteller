#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Mar 11 12:12:30 2026

@author: inf-48-2025
"""

# %%

from igraph import Graph
import plotly.graph_objects as go
from plotly.offline import plot

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

fig.update_layout(title= 'Tree with Reingold-Tilford Layout',
              annotations=annotations, 
              font_size=12,
              showlegend=False,
              xaxis=axis,
              yaxis=axis,
              margin=dict(l=40, r=40, b=85, t=100),
              plot_bgcolor='#ABCDD9'
              )
fig.update_yaxes(autorange="reversed")

plot(fig, auto_open=True)