from flask import Flask, render_template, url_for, request
from flask_socketio import SocketIO, send, emit, join_room, leave_room
import datetime
from Crypto.Cipher import AES
from Crypto import Random
import random
import math
from pymongo import MongoClient
import time
import socket
import threading
import atexit
import base64
import hashlib

BLOCK_SIZE = 16
pad = lambda s: s + (BLOCK_SIZE - len(s) % BLOCK_SIZE) * chr(BLOCK_SIZE - len(s) % BLOCK_SIZE)
unpad = lambda s: s[:-ord(s[len(s) - 1:])]

password = -1
def encrypt(raw, password):
    private_key = hashlib.sha256(str(password).encode("utf-8")).digest()
    raw = pad(raw)
    iv = Random.new().read(AES.block_size)
    cipher = AES.new(private_key, AES.MODE_CBC, iv)
    return base64.b64encode(iv + cipher.encrypt(raw))
def decrypt(enc, password):
    private_key = hashlib.sha256(str(password).encode("utf-8")).digest()
    enc = base64.b64decode(enc)
    iv = enc[:16]
    cipher = AES.new(private_key, AES.MODE_CBC, iv)
    return unpad(cipher.decrypt(enc[16:]))

def isPrime(p):
	for i in range(2, int(math.sqrt(p)+1)):
		if p%i == 0:
			return 0
	return 1


m_client = MongoClient("mongodb://burhankhom:Burhan123@cluster0-shard-00-00-tzgdv.mongodb.net:27017,cluster0-shard-00-01-tzgdv.mongodb.net:27017,cluster0-shard-00-02-tzgdv.mongodb.net:27017/test?ssl=true&replicaSet=Cluster0-shard-0&authSource=admin&retryWrites=true")
m_db = m_client["cryptography"]
m_collection = m_db["cryptdata"]
clients = []


def exit_handler():
	print('Server is exiting!')
	m_collection.remove()
atexit.register(exit_handler)

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app)
data = {}

@app.route('/', methods=['GET', 'POST'])
def hello():
    return render_template("home.html")

@app.route('/index.html')
def handle():
	allData = m_collection.find()
	g=-1
	n=-1
	a=1
	pK=-1
	ss1 = -1
	ss2 = -1
	message = ""
	sender = "no one"
	receiver = "no one"

	def function_that_waits_for_Bob(a, n):
		x = m_collection.find()
		for doc in x:
			for key in doc.keys():
				if key == 'pK2':
					flag = 1
					ss1 = pow(int(doc.get('pK2')), int(data['a']), n)
					password = str(ss1)
					print("****ALICE***", ss1)
					break
	for document in allData:
		for key in document.keys():
			data[key] = document.get(key, -1)
	print(data)
	if data.get('G', -1) == -1 or data.get('N', -1) == -1:
		primes = [i for i in range(2,100) if isPrime(i)]
		g = random.choice(primes)
		n = random.randint(1e31, 99999999999999999999999999999999)
		a = random.randint(1, n)
		m_collection.insert({'a':str(a)})
		publicKey = pow(g, a, n)
		finalKey = str(publicKey)
		pK = finalKey
		m_collection.insert({'G':g})
		data['G'] = g
		m_collection.insert({'N':str(n)})
		data['N'] = n
		m_collection.insert({'pK':pK})
		data['pK'] = pK
		data['message'] = "Generated "
		sender = 'Alice'
		receiver = 'Bob'
	else:
		data['message'] = "Received "
		g = int(data['G'])
		n = int(data['N'])
		b = random.randint(1, n)
		pK2 = str(pow(g, b, n))
		m_collection.insert({'pK2':pK2})
		ss2 = pow(int(data['pK']), b, n)
		m_collection.insert({'sharedSecret':str(ss2)})
		print("***BOB****", ss2)
		sender = 'Bob'
		receiver = 'Alice'
		password = str(ss2) #shared Secret
		function_that_waits_for_Bob(a, n)
	keyTime = datetime.datetime.now()
	keyTime = str(keyTime)

	data['user'] = request.args.get('user')
	data['rid'] = request.args.get('rid')
	data['sender'] = sender
	data['receiver'] = receiver
	return render_template("index.html", data=data)

@socketio.on('message')
def handle_message(msg):
	send(msg, broadcast=True) # send(request.sid)
	encrypted = encrypt(msg, password)
	m_collection.insert({'EncryptedMessage':str(encrypted)[2:]})
	print('******Encrypted Message', str(encrypted)[2:])

	decrypted = decrypt(encrypted, password)
	m_collection.insert({'DecryptedMessage':bytes.decode(decrypted)})
	print('******Decrypted Message', bytes.decode(decrypted))
	print('received message: ' + msg)

@socketio.on('join')
def on_join(data):
	username = request.args.get('user')
	room = request.sid
	join_room(room)
	send(username + ' has entered the room.', broadcast=True)
	print('Session ID: ', request.sid)

if __name__ == '__main__':
	socketio.run(app, debug=True)
