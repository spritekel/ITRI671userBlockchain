#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Sep  7 21:30:36 2021

@author: sprite
"""

import hashlib
import json
from flask import Flask, jsonify
from flask.wrappers import Request
from flask import request
import base64
import bcrypt
import datetime

class userBlockchain:


    def __init__(self):
        self.chain = []
        self.create_block(proof=1, prev_Hash='0', username="GenesisNull", password=self.hash("GenesisNullPass"))

    def create_block(self, proof, prev_Hash, username, password):
        block = {
            'index': len(self.chain) + 1,
            'timestamp': str(datetime.datetime.now()),
            'proof': proof,
            'prev_hash': prev_Hash,
            'username': username,
            'password': password
        }
        self.chain.append(block)
        return block

    def get_prev_block(self):
        return self.chain[-1]

    def proof_of_work(self, prev_proof):
        new_proof = 1
        check_proof = False

        while check_proof is False:
            # this will determine the difficulty of mining(**2 make it harder but still easy)
            hash_operation = hashlib.sha256(
                str(new_proof**2 - prev_proof**2).encode()).hexdigest()
            if hash_operation[:4] == '0000':
                check_proof = True
            else:
                new_proof += 1
        return new_proof

    def hashString(self, data):
        data = data.encode('utf8')
        
        return str(hashlib.sha256(data).hexdigest())

    def hash(self, block):
        encoded_block = json.dumps(block, sort_keys=True).encode()
        return hashlib.sha256(encoded_block).hexdigest()

    def is_chain_valid(self, chain):
        prev_block = chain[0]
        block_index = 1
        while block_index < len(chain):
            block = chain[block_index]
            if block['prev_hash'] != self.hash(prev_block):
                return False
            prev_proof = prev_block['proof']
            proof = block['proof']

            # must be the same as the proofofwork
            hash_operation = hashlib.sha256(
                str(proof**2 - prev_proof**2).encode()).hexdigest()
            if hash_operation[:4] != '0000':
                return False
            prev_block = block
            block_index += 1
        return True
    
    def exists_in_chain(self, chain, username, password):
        #prev_block = chain[0]
        
        block_index = 0
        while block_index < len(chain):
            block = chain[block_index]
            if block['username'] == username and block['password'] == password:
                return True
            block_index += 1
        return False
                

# Part 2 - Mining our userBlockchain
# Create a web app
app = Flask(__name__)
app.config['JSONIFY_PRETTYPRINT_REGULAR'] = False

# Create a userBlockchain
userBlockchain = userBlockchain()

#default page 
@app.route('/')
def home():
    return "<h1>UserBlockchain landing page</h1>"

# mining a new block
@app.route('/mine_block', methods = ['POST'])
def mine_block():
    username = request.args.get('username')
    password = request.args.get('password')
    prev_block = userBlockchain.get_prev_block()
    prev_proof = prev_block['proof']
    proof = userBlockchain.proof_of_work(prev_proof)
    prev_hash = userBlockchain.hash(prev_block)


    block = userBlockchain.create_block(proof, prev_hash, username, password)
    response = {'message': 'Congradulations, added user to userBlockchain',
                'index': block['index'],
                'timestamp': block['timestamp'],
                'proof': block['proof'],
                'prev_hash': block['prev_hash']
                }
    print(jsonify(response))
    return jsonify(response), 200

# getting the full userBlockchain
@app.route('/get_chain', methods={'GET'})
def get_chain():
    response = {'userBlockchain': userBlockchain.chain,
                'length': len(userBlockchain.chain)}
    return jsonify(response), 200

#Checking if the chain is valid!!
@app.route('/is_valid', methods = ['GET'])
def is_valid():
    is_valid = userBlockchain.is_chain_valid(userBlockchain.chain)
    if is_valid:
        response = {'message': 'userBlockchain is valid'}
    else:
        response = {'message': 'userBlockchain is not valid!!! :('}
    return jsonify(response), 200

@app.route('/search_chain', methods = ['POST'])
def search_chain():
    username = request.args.get('username')
    password = request.args.get('password')
    print(username)
    print(password)

    is_valid = userBlockchain.exists_in_chain(userBlockchain.chain, username, password)
    if is_valid:
        response = {'message': 'Valid'}
    else:
        response = {'message': 'Rejected'}
    return jsonify(response), 200
    
    

# Functions to run the application
app.run()
