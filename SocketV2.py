#!/usr/bin/python3
# coding: utf-8

import socket
import sys
import queue
from time import sleep,time
import select
from _thread import start_new_thread


#Input stream
input_server="localhost"
input_port=2345
input_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
input_socket.connect((input_server, int(input_port)))
input_socket.setblocking(0)
input_file = input_socket.makefile(buffering=-1)

# Create a TCP/IP socket
output_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
output_socket.setblocking(0)
output_server=''
output_port=3456
print ('starting up on %s port %s' % (output_server,output_port))
output_socket.bind((output_server,output_port))

# Listen for outgoing connections
MAX_NUM_ClIENTS=5
output_socket.listen(MAX_NUM_ClIENTS)

# Sockets from which we expect to read
inputs = [ input_file, output_socket ]

# Sockets to which we expect to write
outputs = [ output_socket ]

# Outgoing message queues (socket:Queue)
BUFFER_LINES=10000
message_queue = queue.Queue(BUFFER_LINES) #Hold at most BUFFER_LINES entries

allowed_clients=[]
def refresh_allowed_clients(allow_client_list_file, sleep_time):
    global allowed_clients
    while 1:
        allowed_clients=[]
        with open(allow_client_list_file) as allowed_clients_file:
            for line in allowed_clients_file:
                allowed_clients.append(line.split('#')[0].strip())
        sleep(sleep_time)

REFRESH_INTERVAL=60
CLIENT_LIST_FILENAME='allowed_clients.txt'
print('Reading allowed clients list every %i s' % REFRESH_INTERVAL)
refresh_thread = start_new_thread(refresh_allowed_clients,(CLIENT_LIST_FILENAME, REFRESH_INTERVAL))

while inputs:

    # Wait for at least one of the sockets to be ready for processing
    readable, writable, exceptional = select.select(inputs, outputs, inputs)
    # Handle inputs
    for s in readable:
        if s is output_socket:
            # A "readable" server socket is ready to accept a connection
            connection, client_address = s.accept()
            if client_address[0] in allowed_clients:
                print ('new connection from', client_address)
                connection.setblocking(0)
                outputs.append(connection)
            else:
                print ('new connection attempt from', client_address)
                print('disconnecting')
                connection.close()

        else:
            data = input_file.readline() #s.recv(1024)
            if data : 
                if 1:
                    try:
                        message_queue.put(data,block=False)
                    except queue.Full:
                        #Queue is full, remove oldest
                        data2=message_queue.get_nowait()
                        message_queue.put(data,block=False)
    #if input_file in message_queue and len(writable)>0 :
    if message_queue.qsize()>0 and len(outputs)>1:
        try:
            next_msg = message_queue.get_nowait()
            next_msg=next_msg.encode('utf-8')
        except queue.Empty:
            pass
        else:
            for s in writable:
                try:
                    s.send(next_msg)
                except OSError:
                    print ('closing', client_address, 'after reading no data')
                    if s in outputs:
                        outputs.remove(s)
    # Handle "exceptional conditions"
    for s in exceptional:
        print ( 'handling exceptional condition for', s.getpeername())
        # Stop listening for input on the connection
        #inputs.remove(s)
        if s in outputs:
            outputs.remove(s)
        s.close()
    sleep(0.00001)
