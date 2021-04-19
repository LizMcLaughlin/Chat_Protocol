#!/usr/bin/env python3
import tkinter as tk
import socket
from threading import Thread
import sys
from time import sleep

class Window(tk.Frame):
	
	'''Defines our window object'''

	def __init__(self, parent):
		tk.Frame.__init__(self, parent)
		self.parent = parent
		self.welcome_window()

		#creates separate thread of control for incoming messages
		#enables client program to insert incoming messages concurrent with sending 
		self.receive_thread = Thread(target=self.delegate) 
		self.receive_thread.start()

	def welcome_window(self):

		'''Window that opens to obtain login credentials'''

		self.parent.geometry("400x200")
		self.parent.title("LOGIN")        
		self.welcomeLabel=tk.Label(self.parent,text="Welcome! Please enter username and password.")
		self.welcomeLabel.pack()
		self.namelabel=tk.Label(self.parent,text="Username")
		self.namelabel.pack()
		
		#for login name entry
		self.username=tk.StringVar()			
		self.usernameEntry=tk.Entry(self.parent, textvariable=self.username)
		self.usernameEntry.pack()
		
		#for password entry
		self.pwlabel=tk.Label(self.parent,text="Password")
		self.pwlabel.pack()
		self.pw=tk.StringVar()
		self.pwEntry=tk.Entry(self.parent, textvariable=self.pw)
		self.pwEntry.pack()

		#to submit credentials
		self.enter_button=tk.Button(self.parent,text="Enter", command=self.authenticate)
		self.enter_button.pack()

		#to display success/failure message
		self.response=tk.Label(self.parent, text='')
		self.response.pack()

		self.msg_frame=tk.Frame(self.parent)
		self.scrollbar= tk.Scrollbar(self.msg_frame) #to scroll up to past msgs
		self.messages = tk.Listbox(self.msg_frame, height=15,width=50,yscrollcommand=self.scrollbar.set)

		
	def chat_window(self):

		'''Chat window - Opens to allow communication once user passes correct login credentials'''

		self.parent.geometry('400x400')
		self.parent.title('LIZ\'S CHAT ROOM')

		#remove login items from window
		self.enter_button.destroy()
		self.pwlabel.destroy()
		self.pwEntry.destroy()
		self.usernameEntry.destroy()
		self.namelabel.destroy()
		self.welcomeLabel.destroy()
		self.response.destroy()

		self.msg_frame=tk.Frame(self.parent)
		self.msg = tk.StringVar() #messages I send
		self.msg.set('Enter your message here.') 
		self.scrollbar= tk.Scrollbar(self.msg_frame) #to scroll up to past msgs
		self.messages = tk.Listbox(self.msg_frame, height=15,width=50,yscrollcommand=self.scrollbar.set)
		self.scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
		self.messages.pack(side=tk.LEFT, fill=tk.BOTH)
		self.messages.pack()
		self.msg_frame.pack()

		#field to enter messages to send to chat widow
		self.entry_field = tk.Entry(self.parent, textvariable=self.msg)
		self.entry_field.pack()

		#to quit chat
		self.quitbutton=tk.Button(self.parent,text="Quit", command=self.quit)
		self.quitbutton.pack()


	def authenticate(self):

		'''After connection opens to server, client must provide credentials to join the chat under "username"'''

		try:

			global USERNAME

			#PACKET CREATION
			USERNAME = self.username.get()
			password = self.pw.get()
			body='na' #body of packet is empty for login
			
			#request line 
			method='0001' #4 bits w/ padding for method portion of header
			address=l_socket.ljust(32,' ') #32 bit local socket address w/ padding
			request_line = method + ':' + address + ':' + VERSION + '\r\n'		

			#header line creation -> user credentials
			header=USERNAME + ':' + password + '\r\n'
			
			packet=request_line+header+body 
			client.send(bytes(packet, ENCODE))
			print('user credentials sent to server')

			#clear credential fields
			self.pw.set('')
			self.username.set('')

		except BrokenPipeError:
			pass		


	def pass_authentication(self, header):

		'''Once credentials are verified, open chat window to initiate session with curernt connections'''

		USERNAME=header.split(':')[0]
		self.chat_window() #initiates chat window
		welcome = 'Welcome %s!' % USERNAME 
		self.messages.insert(tk.END, welcome) #appends welcome msg to user's chat window

		#PACKET CREATION			
		#request line 
		method='0011' #broadcast
		address=l_socket.ljust(32,' ') #32 bit local socket address w/ padding
		request_line = method + ':' + address + ':' + VERSION + '\r\n'		
		header=USERNAME + '\r\n'
		body='*** {} has joined the chat ***'.format(USERNAME)			
		packet=request_line+header+body

		client.send(bytes(packet, ENCODE)) #send packet to server to broadcast to all connected users

	def delegate(self): #STATEFUL

		'''Handles receiving of messages, and actions to take on them (directed by status code)'''
		try:
			while True:
				packet=client.recv(BUFSIZ).decode(ENCODE)
				status_line,header,body=packet.splitlines() #parse lines of packet
				status=status_line.split(':')[1] #get status code from status_line

				if status == '250': #broadcast msg
					#appends msg broadcast from server to chat windows
					self.messages.insert(tk.END, body)
				if status == '331': #login confirmed
					#call funct to initiate chat window/session
					self.pass_authentication(header)
				if status == '231':
					#send label to login window indicating incorrect username and/or pw
					self.response.config(text="Password is incorrect")
				if status == '251': #send welcome and initiate chat priviledges
					self.messages.insert(tk.END, body)
					self.entry_field.bind("<Return>", self.send) #only allows msg sending once connection has been announced
	
		except ValueError:
			pass
			

	def send(self, event): 

		'''Handles sending of messages entered by user in entry field of chat window.'''
		
		body = self.msg.get() #pull msg from tkinter entry
		body = USERNAME + ': ' + body
		self.msg.set('') #clear entry box on window

		#PACKET CREATION			
		#request line 
		method='0010' #4 bits w/ padding for method portion of header
		address=l_socket.ljust(32,' ') #32 bit local socket address w/ padding
		request_line = method + ':' + address + ':' + VERSION + '\r\n'		

		#header line blank for broadcast requests 
		header=' ' + '\r\n'
			
		packet=request_line+header+body
		client.send(bytes(packet, ENCODE))

	def quit(self):

		'''handles exit from chat'''

		#PACKET CREATION			
		#request line 
		method='0100' #4 bits w/ padding for method portion of header
		address=l_socket.ljust(32,' ') #32 bit local socket address w/ padding
		request_line = method + ':' + address + ':' + VERSION + '\r\n'		
		header=USERNAME + '\r\n'
		body='*** {} has left the chat ***'.format(USERNAME)	
		packet=request_line+header+body
		
		client.send(bytes(packet, ENCODE))

		self.entry_field.destroy() #destroy entry field, but leave window open for access to thread of text
		self.close() #closes connection to server
		self.destroy() #exits the chat window
		self.quitbutton.destroy() #remove quit button from window
		

if __name__ == '__main__':

	root = tk.Tk() #creates top level widget of Tk ~ main window of app
	
	HOST = input('Host: ')
	PORT = 33318
	BUFSIZ=1024
	VERSION='0001'  #4 bit version (version=1) num w / padding
	USERNAME=''
	ENCODE=input('Encode format: ') 

	#try/catch found at: 
	#https://stackoverflow.com/questions/34883234/attempting-to-reconnect-after-a-connection-was-refused-python
	#socket remains open for a short period after command to close, blocking attempt to reconnect
	#loop continues until reconnect succeeds
	while True:
		try:	
			client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
			client.connect((HOST,PORT))
			break
		except socket.error:
			print("Connection Failed. Retrying...")
			time.sleep(1)

	#local socket info
	lhost,lport=client.getsockname()
	l_socket=(str(lhost)+'..'+str(lport))
	print('socket address: {}'.format(l_socket))

	run = Window(root)
	root.mainloop()


