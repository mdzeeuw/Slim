
from __future__ import division
from collections import namedtuple
from collections import deque
from struct import *
import common.common


def load_packet_setup():

    Packets = {}

    # PID data
    PID_packet = Packet('', 0)
    #PID_packet.add('header', 'B')
    PID_packet.add('Kp', 'B')
    PID_packet.add('Ki', 'B')
    PID_packet.add('Kd', 'B')
    PID_packet.add('Setpoint', 'f')
    PID_packet.add('Input', 'f')
    PID_packet.add('Output', 'f')
    PID_packet.add('Interval', 'i16')
    #Packets[73] = PID_packet;

    #Room node
    ROOM_packet = Packet('', 0)
    #ROOM_packet.add('header', 'u8')
    ROOM_packet.add('Node', 'u8')
    ROOM_packet.add('Temp', 'i16', 100)
    ROOM_packet.add('Humi', 'u16', 10)
    ROOM_packet.add('Pir', 'u8')
    ROOM_packet.add('Light', 'u16')
    ROOM_packet.add('Supply', 'u8')
    Packets[81] = ROOM_packet

    #Central heating
    CH_packet = Packet('', 0)
    #CH_packet.add('header',     'u8')
    CH_packet.add('CHSetpoint',    'u8')
    CH_packet.add('CHTemp',        'u16',100)
    CH_packet.add('ReturnTemp',        'u16',100)
    CH_packet.add('Target',     'i16',10)
    CH_packet.add('Temperature',        'i16',100)
    CH_packet.add('Humidity',         'i16',100)
    CH_packet.add('Status',     'u8')
    Packets[72] = CH_packet


    ROOMIT_packet = Packet('', 0)
    #ROOMIT_packet.add('header',     'u8')
    ROOMIT_packet.add('Node',        'u8')
    ROOMIT_packet.add('Temp',         'i16', 10)
    ROOMIT_packet.add('Humi',         'u16', 10)
    ROOMIT_packet.add('Pir',         'u8')
    ROOMIT_packet.add('Light',         'u16')
    ROOMIT_packet.add('Temp_o1',     'i16', 10)
    ROOMIT_packet.add('Humi_o1',     'u8')
    ROOMIT_packet.add('Temp_o2',     'i16',10)
    ROOMIT_packet.add('Humi_o2',     'u8')
    Packets[82] = ROOMIT_packet

    GAS_packet = Packet('', 0)
    #GAS_packet.add('header',     'u8')
    GAS_packet.add('Gas',         'u32')
    GAS_packet.add('Elec',         'u32')
    GAS_packet.add('Temp',        'i16', 100)
    GAS_packet.add('Humi',        'u16', 100)
    GAS_packet.add('Pir',         'u8')
    Packets[2] = GAS_packet

    PRES_packet = Packet('', 0)
    #GAS_packet.add('header',     'u8')
    PRES_packet.add('Node',        'u8')
    PRES_packet.add('Temp',        'i16', 10)
    PRES_packet.add('Pressure',    'i32', 100)

    Packets[80] = PRES_packet

    LUX_packet = Packet('', 0)
    #GAS_packet.add('header',     'u8')
    LUX_packet.add('LUX_Low',    'u16')
    LUX_packet.add('LUX_High',    'u16')
    LUX_packet.add('Temp',         'i16', 10)
    LUX_packet.add('Humi',         'u16', 10)
    LUX_packet.add('Temp2',         'i16', 10)
    LUX_packet.add('Humi2',         'u16', 10)
    Packets[45] = LUX_packet


    return Packets


## Packet representation class
class Packet:
    def __init__(self, format, length):
        self.format = False
        self.length = 0
        self.fields = []
        self.types = []
        self.divide = []

        self.f = []

    #Decode a packet into different byte sized values
    def decode(self, data):

        if not(self.format):
            self.parse()

        #Data should be 2 chars longer then the packet length (we don't count the \r\n)
        if len(data) != self.length:
            print("Incorrect size {0} ! {1}".format(len(data), self.length))
            return False

        #try:

        #Unpack the data
        res = unpack(self.format, data[0:self.length])
        #print res
        #Parse it into the tupple
        #tpl = self.tuple._make(res)
        tpl = False

        values = {}
        #if tpl:
        i = 0
        for v in res:

            if self.divide[i]:
                v = v / self.divide[i]

            values[self.fields[i]] = v

            i += 1

        #print values
        return values

    #Just return false when something went wrong
    #except Exception, e:
    #   return False

    #Add a new variable to the packet
    def add(self, var, type, div=False):
        self.types.append(type)
        self.fields.append(var)
        self.divide.append(div)

        self.f.append((type, var, div))

    #parse the packet description into the decodable data
    def parse(self):
        #print "F list: ", self.f
        #It's       
        self.format = '<'
        self.length = 0

        #Loop all the vars
        for (type, name, div) in self.f:

            #Switch to decode the type
            for case in common.common.switch(type):
                if case('B'):
                    pass
                if case('uint8_t'):
                    pass
                if case('u8'):
                    self.length += 1
                    self.format += 'B'
                    break

                if case('b'):
                    pass
                if case('int8_t'):
                    pass
                if case('i8'):
                    self.length += 1
                    self.format += 'b'
                    break

                if case('u16'):
                    pass
                if case('H'):
                    self.length += 2
                    self.format += 'H'
                    break

                if case('h'):
                    pass
                if case('i16'):
                    self.length += 2
                    self.format += 'h'
                    break

                if case('f'):
                    self.length += 4
                    self.format += 'f'
                    break

                if case('i32'):
                    pass
                if case('i'):
                    self.length += 4
                    self.format += 'i'
                    break

                if case('u32'):
                    self.length += 4
                    self.format += 'I'
                    break

                if case():
                    print(type)
                    raise("Invalid parse type {0}".format(type))

        #Create the named tupple
        self.tuple = namedtuple('Packet', ' '.join(self.fields))
