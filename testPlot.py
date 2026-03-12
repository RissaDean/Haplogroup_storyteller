#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Mar 11 12:12:30 2026

@author: inf-48-2025
"""
#import networkx as nx
#import matplotlib.pyplot as plt
#import numpy as np

# %%
# seed = 6

# np.random.seed(seed)
# usergroup = "U2c1"

# nodes = []
# edges = []
# terminal_nodes = []
# layers = range(1,(len(usergroup)))
# G = nx.DiGraph()

# # for i in layers:
# #     nodes.append(i)

# for index, letter in enumerate(usergroup):
#     nodes.append(usergroup[0:index+1])
#     if index > 0:
#         #edges.append((index, usergroup[0:index+1]))
#         edges.append((usergroup[0:index], usergroup[0:index+1]))

        
# root_node = usergroup

    

# G.add_nodes_from(nodes)   
# G.add_edges_from(edges)



# %%
   

# plt.figure(figsize=(8, 6))
# pos = nx.spring_layout(G)
# pos[root_node] = (-2,(1/len(layers)))
# #write_dot(G,'test.dot')
# nx.draw(G, pos, with_labels=True, node_size=3000, node_color='skyblue', font_size=10, font_weight='bold', edge_color='gray')
# plt.gca().invert_yaxis()
# plt.title('Pedigree Analysis Chart')
# plt.show()

# %%

import igraph
from igraph import Graph, EdgeSeq
import plotly.graph_objects as go
from plotly.offline import plot

usergroup = "U2c1"
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
    print(position[edge[0]][0], position[edge[1]][0])

    Xe+=[position[edge[0]][0],position[edge[1]][0], None]
    Ye+=[2*M-position[edge[0]][1],2*M-position[edge[1]][1], None]


fig = go.Figure()
fig.add_trace(go.Scatter(x=Xn,
                   y=Yn,
                   mode='lines',
                   line=dict(color='rgb(210,210,210)', width=1),
                   hoverinfo='none'
                   ))
fig.add_trace(go.Scatter(x=Xn,
                  y=Yn,
                  mode='markers',
                  name='bla',
                  marker=dict(symbol='circle-dot',
                                size=18,
                                color='#6175c1',    #'#DB4551',
                                line=dict(color='rgb(50,50,50)', width=1)
                                ),
                  opacity=0.8
                  ))

axis = dict(showline=False, # hide axis line, grid, ticklabels and  title
            zeroline=False,
            showgrid=False,
            showticklabels=False,
            )

fig.update_layout(title= 'Tree with Reingold-Tilford Layout',
              font_size=12,
              showlegend=False,
              xaxis=axis,
              yaxis=axis,
              margin=dict(l=40, r=40, b=85, t=100),
              hovermode='closest',
              plot_bgcolor='rgb(248,248,248)'
              )
plot(fig, auto_open=True)