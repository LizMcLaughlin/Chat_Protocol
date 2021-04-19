#!/usr/bin/env python3
"""Server for multithreaded (asynchronous) chat application."""
import socket 
from threading import Thread
import selectors

def accept(client,mask):

	'''Sets up handling for incoming clients.'''

	client, address = client.accept() #server accepts incoming connection - returns client socket obj
	print("%s:%s has connected." % address)
	client.setblocking(False) #set socket to non-blocking mode
	sel.register(client, selectors.EVENT_READ, delegate) #set up selector to call delegate() w ea read for client

def delegate(client,mask): #STATEFUL

	'''When called by selector object - Parses packages sent by current client. 
	Directs to the appropriate function as directed by the method in request line. '''

	packet=client.recv(BUFSIZ).decode("utf8") #read incoming packet and decode into utf8

	#parse packet data
	request_ln,header_ln,body=packet.splitlines()
	method,address,version=request_ln.split(':')
	
	if method == '0001': #login request
		authenticate(client, header_ln,address) 
	if method == '0010': #broadcast / send msg request
		broadcast(client, body)
	if method == '0011': #broadcast notification to connected users of new connection to chat
		broadcast_new_connection(client, body)
	if method == '0100': #client request to quit chat
		quit(client, body)
	else:
		pass

def authenticate(client, credentials,address):

	'''Checks client's credentials before allowing access to the chat room.'''

	username, pw = credentials.split(':') #parse credentials
	
	try:
		if registered_users[username] ==  pw:
			status_code=331
			phrase='Login Success'
			print("{}:{} - {} has successfully logged in.".format(status_code, phrase, registered_users[username]))
			clients[client] = address #add clients to dict of current connections
		else: #incorrect password
			status_code=231
			phrase='Incorrect username or password'
	except KeyError: #incorrect username
			status_code=231
			phrase='Incorrect username or password'

	#packet creation
	status_ln=VERSION + ':' + str(status_code) + ':' + phrase + '\r\n'
	header_ln=username + '\r\n' #passes username w login confirmation
	body = 'na' #empty body
	packet_outgoing = status_ln + header_ln + body
	
	client.send(bytes(packet_outgoing, "utf8")) #send status to client

def broadcast_new_connection(client, body):

	'''Broadcasts notification to all current connections of new client connection'''

	#packet creation
	status_code='251' 
	phrase= 'New connection msg action completed.'
	username=clients[client]#name of client connection
	
	status_ln=VERSION + ':' + str(status_code) + ':' + phrase + '\r\n'
	header_ln=username + '\r\n' #passes username w login confirmation
	packet_outgoing = status_ln + header_ln + body

	print("sending notification of new connection...")
	while True:
		try:
			for socket in clients: socket.send(bytes(packet_outgoing,'utf8')) #sends to all logged clients
			break
		except BlockingIOError: # in case of I/O resource unavailable, loops back and tries again until success
			continue
 
def broadcast(client, body):

	'''General braodcast function - broadcasts messages clients wish to append to chat window.'''

	#packet creation
	status_code='250' 
	phrase= 'Msg action completed.'
	username=clients[client]#name of client connection
	
	status_ln=VERSION + ':' + str(status_code) + ':' + phrase + '\r\n'
	header_ln=username + '\r\n' #passes username w login confirmation
	packet_outgoing = status_ln + header_ln + body

	while True:
		try:
			for socket in clients: socket.send(bytes(packet_outgoing,'utf8')) #sends to all logged clients
			break
		except BlockingIOError: # in case of I/O resource unavailable, loops back and tries again until success
			continue

def quit(client, body):

	'''Quits client connection upon request, and notifies remaining connected clients.'''

	#packet creation
	status_code='250' 
	phrase= 'Client Connection Closed'
	username=clients[client]#name of client connection
	
	status_ln=VERSION + ':' + str(status_code) + ':' + phrase + '\r\n'
	header_ln=username + '\r\n' #passes username w login confirmation
	packet_outgoing = status_ln + header_ln + body

	client.close() #closes socket connection to client
	del clients[client] #removes client from dict of open connections
	sel.unregister(client) #unregisters client from polling obj tracking 


	print("sending closing notification...")
	while True:
		try:
			for socket in clients: socket.send(bytes(packet_outgoing,'utf8')) #sends to all logged clients
			break
		except BlockingIOError: # in case of I/O resource unavailable, loops back and tries again until success
			continue

#login and pw info for registered users        
registered_users = {'Liz':'pw1', 'Steve':'pw2','Bailey':'pw3'}
#dict to hold currently active (connected) clients
clients = {}

HOST = ''
PORT = 33318
BUFSIZ = 1024
ADDR = (HOST, PORT)
VERSION=f"{1:03}"  #version num w padding for extensibility

try:
	#creates new socket using TCP address family, stream socket type
	server = socket.socket(socket.AF_INET, socket.SOCK_STREAM) #creates new socket using TCP address family, stream socket type
except socket.error:
	print("Error creating to socket")
	sys.exit(1)


#prevents OSError when running same client several times
server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR,1) 
#set socket to non-blocking mode
server.setblocking(False)
#bind socket to server host address and port address 
server.bind((HOST,PORT))
print("Running on port {}".format(PORT))
#set socket to listen for incoming connection requests
server.listen()
print("Listening....")

#create selector obj to wait for I/O event readiness on multiple file objects - default uses most efficient implementation
sel = selectors.DefaultSelector()
keep_running = True
#register selector obj with the server socket to listen for incomoing I/0, and directs read events 
#(connection requests) to accept()
sel.register(server, selectors.EVENT_READ, accept)

#loop pulled from: https://docs.python.org/3/library/selectors.html#selectors.DefaultSelector
#gets callback from key and passes socket and event mask to 
while keep_running:
	for key, mask in sel.select(timeout=1):
		callback = key.data
		callback(key.fileobj, mask)



