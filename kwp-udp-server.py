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

#xth = 0

def start_secondary():
  y = 0
  while True:
    y += 1
    #print("Secondary thread " + str(y) + " and x is " + str(xth))
    #time.sleep(1.0)
    #mable=UDPServerSocket.recvfrom(16)
    #print( "MESSAGE FROM GUI:" , mable)

    bytesAddressPair = UDPServerSocket.recvfrom(bufferSize)
    message = bytesAddressPair[0]
    address = bytesAddressPair[1]

    xyz = message #"Message from Client:{}".format(message)
    #print(">>>",xyz)

    if bytearray2str(xyz[0:3]) == "abc":
        print(" ABC got ")


    if bytearray2str(xyz[0:4]) == "fall":
        fint = bytearray2str(xyz[5:6])
        mystream.send_message('SET wf_speed=',fint)  #,(fint-'0'))
        print(" waterfall ",fint)

    if bytearray2str(xyz[0:4]) == "freq":
        fint = bytearray2str(xyz[5:11])

        show = int(fint)
        print('$$: ',show)        

        mystream.send_message('SET zoom=6 cf=%d'%(show))  #%d',10260)
        print(" Frequency is  ", fint)

    if bytearray2str(xyz[0:4]) == "zoom":
        print(" zooms are us got ")


    #clientMsg = "Message from Client:{}".format(message)
    #print(clientMsg)

    #mystream.send_message('SET wf_speed=2')


secondary_thread = threading.Thread(target = start_secondary)

secondary_thread.daemon = True #ensures both threads are killed on cntl C
#secondary_thread.start()

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

# A couple of arrays - to be investigated
#exp_line =  bytearray(1024)


# Local UDP-ZXP port to monitor activity (ZXP Style) >>>
localIP     = "192.168.2.2"
localPort   = 11361
bufferSize  = 1024
msgFromServer   = "Hello UDP Client"

# Create a datagram socket
UDPServerSocket = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)

# Bind to address and ip
UDPServerSocket.bind((localIP, localPort))

print("UDP server up and listening")


# Listen for incoming datagrams
bytesAddressPair = UDPServerSocket.recvfrom(bufferSize)
message = bytesAddressPair[0]
address = bytesAddressPair[1]
#clientMsg = "Message from Client:{}".format(message)
#clientIP  = "Client IP Address:{}".format(address)


#print(clientIP)

#test pattern
#for i in range(1024):
#    xfer_line[i] =  i // 8
#    i=i+5
#xfer_line[0] = 0x42  #the magic number for ZXP

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

#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>

secondary_thread.start()
time.sleep(1)

#>>>>>>>>>>>>>>>>>>>>>>>>>>>  LOOPIN >>>>>>>>>>>>>>>>>>>>>>>
xfer_line = bytearray(1040) 

while k_time < max_time:
    xfer_line = mystream.receive_message()
    xfer_line[0] = 0x42  #the magic number for ZXP
    UDPServerSocket.sendto( xfer_line, address) # (thebytesToSend, address)
    k_time += 1
    print ("ktime: ",k_time)
    # end of ktime <<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<

try:
    mystream.close_connection(mod_pywebsocket.common.STATUS_GOING_AWAY)
    mysocket.close()
except Exception as e:
    print ("exception: %s" % e)

print ("\n All done!")


'''
while time<length:
    # receive one msg from server
    tmp = mystream.receive_message()
    if bytearray2str(tmp[0:3]) == "W/F": # this is one waterfall line
        tmp = tmp[16:] # remove some header from each msg
        if options['verbosity']:
            print (time)
        #spectrum = np.array(struct.unpack('%dB'%len(tmp), tmp) ) # convert from binary data to uint8
        spectrum = np.ndarray(len(tmp), dtype='B', buffer=tmp) # convert from binary data to uint8
        if filename:
            binary_wf_list.append(tmp) # append binary data to be saved to file
        #wf_data[time, :] = spectrum-255 # mirror dBs
        wf_data[time, :] = spectrum
        wf_data[time, :] = -(255 - wf_data[time, :])  # dBm
        wf_data[time, :] = wf_data[time, :] - 13  # typical Kiwi wf cal
        time += 1
    else: # this is chatter between client and server
        #print (tmp)
        pass
'''
