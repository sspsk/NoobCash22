import binascii

import Crypto
import Crypto.Random
from Crypto.Hash import SHA
from Crypto.PublicKey import RSA
from Crypto.Signature import PKCS1_v1_5

import hashlib
import json
from time import time
from urllib.parse import urlparse
from uuid import uuid4



class wallet:

	def __init__(self):

		self.private_key = RSA.generate(1024, Crypto.Random.new().read)
		self.public_key = self.private_key.publickey()
		self.signer = PKCS1_v1_5.new(self.private_key)



	# def balance():

