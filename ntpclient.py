#!/usr/bin/env python
# from collections import tuple

import socket as socket
import struct
from datetime import datetime
import math

def getTime():
    time_difference = datetime.utcnow() - datetime(1970, 1, 1, 0, 0, 0)
    secs = time_difference.days*24.0*60.0*60.0 + time_difference.seconds
    timestamp_float  = secs + float(time_difference.microseconds / 1000000.0)
    return timestamp_float

def getNTPTimeValue(server="time.apple.com", port=123):
    
    fs = "!1B" + 47 * "B"

    send_pkt = struct.pack(fs, 0x1b, *([0] * 47))
    soc = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    # time stamp before:
    T1 = getTime()
    soc.sendto(send_pkt, (server, port))

    # time stamp after:
    pkt = soc.recv(200)
    T4 = getTime()
    
    return (pkt, T1, T4)
    

def ntpPktToRTTandOffset(pkt: bytes, T1: float, T4: float):

    ntp_epoch = 2208988800
    recieve_sec, recieve_frac, transmit_sec, transmit_frac = struct.unpack("!4I", pkt[32:48])
    T2 = recieve_sec - ntp_epoch + (recieve_frac/2**32)
    T3 = transmit_sec - ntp_epoch + (transmit_frac/2**32)

    # calculate RTT value:    
    rtt = ((T4 - T1) + (T3 - T2))

    # calculate offset value:
    offset = ((T2 - T1) + (T3 - T4)) / 2

    #! DELETE PRINT STATEMENTS
    #print("offset: " + str(offset))
    #print("T2: " + str(T2))
    #print("T1: " + str(T1))
    #print("T3: " + str(T3))
    #print("T4: " + str(T4))
    
    
    return (rtt, offset)

def getCurrentTime(server="time.apple.com", port=123, iters=20):
    
    offsets = []
    # may have to convert from NTP to Unix prior to adding offsets
    for i in range(iters):
        pkt, T1, T4 = getNTPTimeValue(server, port)
        _, offset = ntpPktToRTTandOffset(pkt, T1, T4)
        offsets.append(offset)    
    currentTime = getTime() + sum(offsets) / len(offsets)

    return currentTime


if __name__ == "__main__":
    print("test get Time: " + str(getTime()))
    print(getCurrentTime())
