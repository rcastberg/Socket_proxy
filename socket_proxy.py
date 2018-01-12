#!/usr/bin/python3

# coding: utf-8

import socket
import sys
from _thread import *
from time import sleep

socketserver="localhost"
socket_port=5678

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect((socket_server, int(socket_port)))
f = s.makefile()


#####################################
# Store socket Data in a global variable
#####################################
GLOBALDATA=''
def poll_socket():
    while 1:
        line=f.readline().strip()
        global GLOBALDATA
        GLOBALDATA=line

thread = start_new_thread(poll_socket,())

#####################################
# Store allowed clients in a list.
# This is refreshed every 60s
# And can be compared later to see if
# client is allowed
#####################################
allowed_clients=[]
def refresh_allowed_clients():
    global allowed_clients
    while 1:
        allowed_clients=[]
        with open('allowed_clients.txt') as allowed_clients_file:
            for line in allowed_clients_file:
                allowed_clients.append(line.split('#')[0].strip())
        sleep(60)

thread_clients = start_new_thread(refresh_allowed_clients,())

HOST = ''   # Symbolic name meaning all available interfaces
PORT = 12345 #Arbitrary non-privileged port
 
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
print('Socket created')
 
#Bind socket to local host and port
try:
    s.bind((HOST, PORT))
except socket.error as msg:
    print('Bind failed. Error Code : ' + str(msg[0]) + ' Message ' + msg[1])
    sys.exit()
     
print('Socket bind complete')
 
#Start listening on socket
s.listen(10)
print('Socket now listening')
 
#Function for handling connections. This will be used to create threads
def clientthread(conn, addr):
    #Sending message to connected client
    global GLOBALDATA
    prev=''
    try:
        #infinite loop so that function do not terminate and thread do not end.
        while True:
            current=GLOBALDATA
            if current != prev:
                conn.sendall((current.strip()+'\n').encode('utf-8'))
            prev=current
    except BrokenPipeError:
        print('Diconnected from' + addr[0] + ':' + str(addr[1]))
    #We have came out of loop, close connection
    conn.close()
 
#now keep talking with the client

while 1:
    #wait to accept a connection - blocking call
    conn, addr = s.accept()
    if addr[0] in allowed_clients:
        print('Connected with ' + addr[0] + ':' + str(addr[1]))
        #start new thread takes 1st argument as a function name to be run, second is the tuple of arguments to the function.
        start_new_thread(clientthread ,(conn,addr))
    else:
        print('Attempted connection from ' + addr[0] + ':' + str(addr[1]))
        conn.close()

s.close()

#Check output with:
# $ nc localhost 8895
