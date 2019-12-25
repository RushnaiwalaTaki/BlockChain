import datetime
import hashlib
import json
from flask import Flask,jsonify,request
import requests
from uuid import uuid4
from urllib.parse import urlparse

class BlockChain:
	def __init__(self):
		self.chain=[]
		self.transactions = []
		self.createBlock(proof=1,prev_hash='0')
		self.nodes = set()
		
	def createBlock(self,proof,prev_hash):
		block = {'index':len(self.chain)+1,
				 'timestamp':str(datetime.datetime.now()),
				 'proof':proof,
				 'prev_hash':prev_hash,
				 'transactions':self.transactions}
		self.transactions = []
		self.chain.append(block)
		return block

	def get_perv_block(self):
		return self.chain[-1]

	def hash(self,block):
		encode_block = json.dumps(block,sort_keys=True).encode()
		return hashlib.sha256(encode_block).hexdigest()

	def proof_of_work(self,prev_proof):
		new_proof=1
		check_proof=False
		while check_proof is False:
			hash_op = hashlib.sha256(str(new_proof**2 - prev_proof**2).encode()).hexdigest()
			if hash_op[:4]=='0000':
				check_proof=True
			else:
				new_proof+=1
		return new_proof

	def chain_valid(self,chain):
		prev_block = chain[0]
		block_index=1
		while block_index<len(chain):
			block = chain[block_index]
			if block['prev_hash']!=self.hash(prev_block):
				return False
			prev_proof = prev_block['proof']
			proof = block['proof']
			hash_op = hashlib.sha256(str(proof**2 - prev_proof**2).encode()).hexdigest()
			if hash_op[:4]!='0000':
				check_proof=False
			prev_block=block
			block_index+=1
		return True

	def add_transaction(self,sender,reciever,amount):
		self.transactions.append({'sender':sender,'reciever':reciever,'amount':amount})
		prev_block = self.get_perv_block()
		return prev_block['index']+1

	def add_node(self,address):
		parse_url = urlparse(address)
		self.nodes.add(parse_url.netloc)

	def replace_chain(self):
		network = self.nodes
		longchain = None
		maxlen = len(self.chain)
		for nodes in network:
			res = requests.get(f'http://{nodes}/get_chain')
			if res.status_code == 200:
				length = res.json()['length']
				chain = res.json()['chain']
				if length>maxlen and self.chain_valid(chain):
					maxlen=length
					longchain = chain
		if longchain:
			self.chain = longchain
			return True
		return False



app = Flask(__name__)


node_address = str(uuid4()).replace('-','')



blockchain = BlockChain()

@app.route('/mine_block',methods=['GET'])
def mine_block():
	prev_block = blockchain.get_perv_block()
	prev_proof = prev_block['proof']
	proof = blockchain.proof_of_work(prev_proof)
	prev_hash = blockchain.hash(prev_block)
	blockchain.add_transaction(sender=node_address,reciever='VISHAL',amount=1)
	block = blockchain.createBlock(proof,prev_hash)

	response = {'message':'Congtatulation, U Just Mine a Block!',
				'index':block['index'],
				'timestamp':block['timestamp'],
				'proof':block['proof'],
				'prev_hash':block['prev_hash'],
				'transactions':block['transactions']}
	return jsonify(response),200

@app.route('/get_chain',methods=['GET'])
def get_chain():
	response = {'chain':blockchain.chain,
				'length':len(blockchain.chain)}
	return jsonify(response),200


@app.route('/add_transaction',methods=['POST'])
def add_transaction():
	json = request.get_json()
	transaction_key = ['sender','reciever','amount']
	if not all(key in json for key in transaction_key):
		return 'Some Transaction Keys Are Missing.',400
	index = blockchain.add_transaction(json['sender'],json['reciever'],json['amount'])
	response = {'message':f'This Transaction Will be Added in the BlockChain block {index}'}
	return jsonify(response),201


@app.route('/connect_node',methods=['POST'])
def connect_node():
	json = request.get_json()
	nodes = json.get('nodes')
	if nodes is None:
		return "No Nodes.",400
	for node in nodes:
		blockchain.add_node(node)
	response = {'message':'All the nodes are connected, blockchain now containe following nodes:',
				'total_nodes':list(blockchain.nodes)}
	return jsonify(response),201

@app.route('/replace_chain',methods=['GET'])
def replace_chain():
	ischain_replace = blockchain.replace_chain()
	if ischain_replace:
		response = {'message':'The Node has different chain.so, The chain is replace by the longest one.',
					'new_chain':blockchain.chain}
	else:
		response = {'message':'All Good. The Chain is Largest One',
					'actual_chain':blockchain.chain}
	return jsonify(response),200

app.run(host='0.0.0.0',port='5001')