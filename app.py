from flask import Flask, render_template, request, jsonify
import numpy as np
import random
import pandas as pd
import os
import scipy.optimize as spo
import optimization as op
import io
import base64
import matplotlib.pyplot as plt

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')## generates 5 random stock names


@app.route('/get_random_portfolio')
def get_random_portfolio():
    try:
        op_object = op.Optimize()
        
        results_as_object = op_object.optimize_portfolio()
        image = results_as_object.get('encoded_image') #encoded image
        allocs = results_as_object.get('allocs') #list
        computations = results_as_object.get('computations') #list
        symbols = results_as_object.get('symbols') #list

        #print(f'Allocs: {type(allocs)} \nComputation: {type(computations)} \nSymbols: {type(symbols)}')
        return jsonify({'image' : image, 'allocs': allocs, 'computations': computations, 'symbols': symbols})
    
    except Exception as e:
        return jsonify({'error' : str(e)})
    



if __name__ == '__main__':
    app.run(debug=True)
    
