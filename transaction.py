# from collections import OrderedDict

import binascii

import Crypto
import Crypto.Random
from Crypto.Hash import SHA
from Crypto.PublicKey import RSA
from Crypto.Signature import PKCS1_v1_5
from uuid import uuid4
import json

# import requests
# from flask import Flask, jsonify, request, render_template


class TransactionInput:

    def __init__(self, transaction_output,data=None):
        if data is not None:
            self.parentOutputId = data['parentOutputId']
        else:
            self.parentOutputId = transaction_output.get_id()

    def to_dict(self):
        d = {
            'parentOutputId':self.parentOutputId 
        }
        return d 

    def get_id(self):
        return self.parentOutputId


class TransactionOutput:
    def __init__(self, receiver_address, amount,data = None):
        if data is not None:
            self.recipient = data['recipient']
            self.amount = data['amount']
            self.transactionId = data['transactionId']
        else:
            self.recipient = receiver_address
            self.amount = amount
            self.transactionId = str(uuid4())

    def to_dict(self):
        d = {
            'transactionId':self.transactionId,
            'recipient': self.recipient,
            'amount': self.amount
        }
        return d

    def set_id(self, tid):
        self.transactionId = tid

    def get_id(self):
        return self.transactionId
             
    def get_receiver(self):
        return  self.recipient

    def get_amount(self):
        return self.amount


# EXAMPLE TRANSACTION 
# utxos = [(1,rep1,100),(2,rep1,65)]
# Transaction(_,_,105,utxos)

# inputs = [1,2]
# outs = [(3,receiver_address,105),(4,sender_address,60)]

class Transaction:

    def __init__(self, sender_wallet, receiver_address, amount, sender_utxos,is_genesis=False,data=None):

        ##set

        if data is not None:
            #fill fields from data
            self.sender_address = data['sender_address']
            self.receiver_address = data['receiver_address']
            self.amount = data['amount']
            self.transaction_inputs = [TransactionInput(None,d) for d in data['transaction_inputs']]
            self.transaction_outputs = [TransactionOutput(None,None,d) for d in data['transaction_outputs']]
            self.hash = None 
            self.signature = binascii.unhexlify(data['signature'])


        else:
            self.receiver_address = receiver_address
            self.amount = amount
            if is_genesis:
                self.sender_address = 0
                self.transaction_inputs = []  #no need
                self.transaction_outputs = [TransactionOutput(receiver_address,amount)]  #no need
                self.hash = None
                self.signature = b'signature'
            else:
                self.sender_address = sender_wallet.get_pubaddress()
                self.transaction_inputs = [TransactionInput(to) for to in sender_utxos]
                self.transaction_outputs = self.make_transaction_ouputs(sender_wallet,sender_utxos) #we should check the index creation
                self.hash = self.make_hash() #maybe we need the hex string
                self.signature = self.sign_transaction(sender_wallet)


            
            

            
            




    def trans_to_dict(self):
        temp = {'sender_address':self.sender_address,
                'receiver_address':self.receiver_address,
                'amount':self.amount,
                'transaction_inputs':[t.to_dict() for t in self.transaction_inputs ],
                'transaction_outputs':[t.to_dict() for t in self.transaction_outputs]
                 }
        return temp
    
    def jsonify_transaction(self):
        temp = {'sender_address':self.sender_address,
                'receiver_address':self.receiver_address,
                'amount':self.amount,
                'transaction_inputs':[t.to_dict() for t in self.transaction_inputs ],
                'transaction_outputs':[t.to_dict() for t in self.transaction_outputs],
                'signature': binascii.hexlify(self.signature).decode('ascii')
                 }
        return json.dumps(temp,sort_keys=True)
        
    def make_hash(self):
        h = SHA.new(json.dumps(self.trans_to_dict(),sort_keys=True).encode())
        self.hash = h
        return h

    def sign_transaction(self,wallet):
        """
        Sign transaction with private key
        """
        s = wallet.signer.sign(self.hash)
        return s
    
    def make_transaction_ouputs(self,wallet,sender_utxos):
        sender_balance = wallet.balance(sender_utxos)
        out1 = TransactionOutput(self.receiver_address,self.amount)
        out2 = TransactionOutput(self.sender_address,sender_balance-self.amount)

        return  [out1,out2]

    def verify_transaction(self,pub_key):
        h = self.make_hash()
        return PKCS1_v1_5.new(pub_key).verify(h,self.signature)



    def validate_transaction(self,pub_key,utxos_list):
        if self.verify_transaction(pub_key):
            #check balance
            bal = 0
            for item in self.transaction_inputs:
                temp_id = item.get_id()
                found = False
                temp_utx = []
                for utxo in utxos_list:
                    if utxo.get_id() == temp_id:
                        found = True 
                        bal += utxo.get_amount()
                        temp_utx.append(utxo)
                        utxos_list.remove(utxo)
                if found == False:
                    for utxo in temp_utx:   #restore funds on sender in failure
                        utxos_list.append(utxo)
                    return False
            if bal >= self.amount:
                return True 
            else:
                for utxo in temp_utx:   #restore funds on sender in failure
                    utxos_list.append(utxo)
                return False

        else:
            return False

    def get_hash(self):
        return self.hash

    def get_sender(self):
        return self.sender_address

    def get_receiver(self):
        return self.receiver_address

    def get_transaction_outputs(self):
        # first element = receiver, second = sender
        return self.transaction_outputs
