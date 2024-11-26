# Wecome to a message
#https://medium.com/developer-rants/simple-thread-handling-in-python-d6c4bf0cc13c

import socket
import time
from kiwi import wsclient
import mod_pywebsocket.common
from mod_pywebsocket.stream import Stream
from mod_pywebsocket.stream import StreamOptions
import numpy as np
import sys
import threading

#-------------

#Handle incoming request message from client
def start_secondary():

    while True:
        bytesAddressPair = UDPServerSocket.recvfrom(bufferSize)
        message = bytesAddressPair[0]
        address = bytesAddressPair[1]

        request = message
 
        if bytearray2str(request[0:3]) == "SET":
            print(request)
        
            action = bytearray2str(request[4:20]) #find action required
            kiwi_msg = ("SET " + action)
            print("Sending: ", kiwi_msg)
            mystream.send_message(kiwi_msg)
        
secondary_thread = threading.Thread(target = start_secondary)
secondary_thread.daemon = True #ensures both threads are killed on cntl C

#---------

print ( "SYSTEM IS ", sys.version_info)

# I REALLY want to loose this
if sys.version_info > (3,):
    print( "SYS V 3")
    buffer = memoryview
    def bytearray2str(b):
        return b.decode('ascii')
else:
    def bytearray2str(b):
        return str(b)

hostname = socket.gethostname()
IPAddr = socket.gethostbyname(hostname)

print("Computer Name is:" + hostname)
print("Computer IP Address is:" + IPAddr)

# Local UDP-ZXP port to monitor activity (ZXP Style) >>>
localIP = IPAddr
localPort   = 11366
bufferSize  = 1024
msgFromServer   = "Hello UDP Client"

# Create a datagram socket
UDPServerSocket = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)

#The next line did not help with the  "address already in use" issue
#UDPServerSocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

# Bind to address and ip
UDPServerSocket.bind((localIP, localPort))


#print("UDP server up and listening")

# Listen for incoming datagrams
bytesAddressPair = UDPServerSocket.recvfrom(bufferSize)
message = bytesAddressPair[0]
address = bytesAddressPair[1]

# End of UDP-ZXP stuff <<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<

host = "norsom.proxy.kiwisdr.com"
port = 8073

print ("KiwiSDR Server: %s:%d" % (host,port))
# the default number of bins is 1024
bins = 1024
print ("Number of waterfall bins: %d" % bins)

#zoom = options['zoom']
zoom = 5

print ("Zoom factor:", zoom)

full_span = 30000.0 # for a 30MHz kiwiSDR

if zoom>0:
    span = full_span / 2.**zoom
else:
	span = full_span

start = 15000.0 # options['offset_khz']
stop = start + span
rbw = span/bins
center_freq = span/2+start

# Calculating the start, stop, centre etc >>>

print ("Start %.3f, Stop %.3f, Center %.3f, Span %.3f (MHz)" % (start/1000, stop/1000, center_freq/1000, span/1000))

if start < 0 or stop > full_span:
    s = "Frequency and zoom values result in span outside 0 - %d kHz range" % full_span
    raise Exception(s)

print ("Trying to contact server...")
try:
    mysocket = socket.socket()
    mysocket.connect((host, port))
except:
    print ("Failed to connect")
    exit()   
print ("Socket open...")

uri = '/%d/%s' % (int(time.time()), 'W/F')
handshake = wsclient.ClientHandshakeProcessor(mysocket, host, port)
handshake.handshake(uri)

request = wsclient.ClientRequest(mysocket)
request.ws_version = mod_pywebsocket.common.VERSION_HYBI13

stream_option = StreamOptions()
stream_option.mask_send = True
stream_option.unmask_receive = False

mystream = Stream(request, stream_option)
print ("Data stream active...")

# send a sequence of messages to the server, hardcoded for now
# max wf speed, no compression

mystream.send_message('SET auth t=kiwi p=')
mystream.send_message('SET zoom=%d cf=%d'%(zoom,center_freq))
mystream.send_message('SET maxdb=0 mindb=-100')
mystream.send_message('SET wf_speed=2')
mystream.send_message('SET wf_comp=0')

print ("Starting to retrieve waterfall data...")
max_time = 500
k_time = 0

secondary_thread.start()
time.sleep(1)

xfer_line = bytearray(1040)
temp_line = bytearray(1040)

#>>>>>>>>>>>>>>>>>>>>>>>>>>>  LOOPIN >>>>>>>>>>>>>>>>>>>>>>>

while k_time < max_time:

    #xfer_line = mystream.receive_message() #this changes the length of the array soze of xfer_line
    temp_line = mystream.receive_message() #this changes the length of the array soze of xfer_line
    lll = len(temp_line)
    #print("Lenny ", lll)

    if lll > 1040:
        lll = 1040

    for i in range(lll-1):
        xfer_line[i] = temp_line[i]
   
    if True: #k_time > 25:
        xfer_line[100] = 1  #poke nubmers don't work if xfer_line len was too short !!! crap !!!
        xfer_line[120] = 254
    UDPServerSocket.sendto( xfer_line, address) 
    k_time += 1
    #print ("ktime: ",k_time)

try:
    mystream.close_connection(mod_pywebsocket.common.STATUS_GOING_AWAY)
    mysocket.close()
except Exception as e:
    print ("exception: %s" % e)

print ("\n All done!")

#------

