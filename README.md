# Socket_proxy
Share a readonly socket to multiple new clients

#Developing :
Tested using socket created on developer node:
Input socket :
$ while [ 1 -lt 2 ]; do echo $RANDOM; sleep 1; done|nc -kl localhost 5678

Output socket :
nc localhost 12345
