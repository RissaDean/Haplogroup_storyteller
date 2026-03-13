#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Mar 13 14:12:54 2026

@author: inf-48-2025
"""
from dash import Dash, html, dcc, Input, Output, callback


app = Dash()

def crazy_text_outputer(input_value): 
    mainLineage= input_value[0]
    mainLineageDate=1000
    lineageLength= len(input_value)
    return(f"{input_value} is a sub-lineage of the {mainLineage} group\
           which emerged around the year {mainLineageDate} and is {lineageLength} generations long.")

app.layout = html.Div([
    html.H6("Change the value in the text box to see callbacks in action!"),
    html.Div([
        "Input: ",
        dcc.Input(id='my-input', value='initial value', type='text')
    ]),
    html.Br(),
    html.Div(id='my-output'),

])


@callback(
    Output(component_id='my-output', component_property='children'),
    Input(component_id='my-input', component_property='value')
)
def update_output_div(input_value):
    display_text = crazy_text_outputer(input_value)
    return(display_text)
           
if __name__ == '__main__':
    app.run(debug=True)