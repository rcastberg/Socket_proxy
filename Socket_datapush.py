import socket
import sys
from time import sleep, time
from _thread import start_new_thread

import argparse

parser = argparse.ArgumentParser(description='Generate data on a socket')
parser.add_argument('freq', nargs='?', help='frequency to print data to socket', default=300)
parser.add_argument('filename', nargs='?', help='file containing data with to send')
parser.add_argument('--host', nargs='?', help='port to start the socket', default='')
parser.add_argument('--port', nargs='?', help='host to start socket', default=2345)
parser.add_argument('--ram', help='Read from ram', action="store_true")

args = parser.parse_args()
ReadFromRam=bool(args.ram)
print(ReadFromRam)

if args.filename == None:
    print('Invalid filename!')
    parser.print_help()
    sys.exit(1)
try:
    sendFile = open(args.filename,'r')
except FileNotFoundError:
    print('\n\nError invalid filename')
    print('Please provide a valid filename')
    parser.print_help()
    sys.exit(1)
if ReadFromRam:
    FileData=[]
    for line in sendFile:
        FileData.append(line)
    sendFile.close()

HOST = args.host   # Symbolic name, meaning all available interfaces
PORT = int(args.port)   # Arbitrary non-privileged port
freq = float(args.freq)   # number of messages a sec
wait = 1/freq

print('Starting datageneration on socket')
print('Host : \'' + str(HOST) + '\' ')
print('Port : ' + str(PORT))
print('Freq : ' + str(freq) + 'Hz (' +str(wait) + 's)' )

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
print('Socket created')

#Bind socket to local host and port
try:
    s.bind((HOST, PORT))
#except OSError as msg:
#    print('Bind failed. Error Code : ' + str(msg[0]) + ' Message ' + msg[1])
#    sys.exit()
except socket.error as msg:
    print('Bind failed. Error Code : ' + str(msg))
    sys.exit()

print('Socket bind complete')

#Start listening on socket
s.listen(10)
print('Socket now listening')

#Function for handling connections. This will be used to create threads
def clientthread(conn,addr):
    try:
        l=0
        i=0
        start_time=time()
        while True:
            l+=1
            i+=1
            if l > freq:
                print('Current freq : ' + str(l/(time()-start_time)))
                l=0
                start_time=time()
            if ReadFromRam :
                data=FileData[i]
            else:
                data=sendFile.readline().strip()+'\r\n'
            conn.sendall(data.encode('utf-8'))
            sleep(wait)
    except BrokenPipeError:
        print('Client diconnected : ' + addr[0] + ':' + str(addr[1]))
    except KeyboardInterrupt as e:
        conn.close()
        raise(e)
    #came out of loop
    conn.close()

#now keep talking with the client
while 1:
    #wait to accept a connection - blocking call
    try:
        conn, addr = s.accept()
    except KeyboardInterrupt as e:
        s.close()
        exit(0)
    print('Connected with ' + addr[0] + ':' + str(addr[1]))

    #start new thread takes 1st argument as a function name to be run, second is the tuple of arguments to the function.
    start_new_thread(clientthread ,(conn,addr))

s.close()
