import sys
import time
import os
import traceback
try:
    import serial
    import serial.tools.list_ports
except ImportError as e:
    error = "Please install pyserial 2.7+! pip install pyserial"
    raise ImportError(error)

CMD = 12

class Serial(object):
    foundDevices = []
    deviceIDS = {}
    deviceVers = []

    def __init__(self, dev="", hardwareID=None):

        self._hardwareID = hardwareID
        self._com = None
        self.dev = dev

        resp = self._connect()
        if not resp:
            raise Exception("Error connecting to serial device!")

    def __exit__(self, type, value, traceback):
        if self._com is not None:
            print("Closing connection to: %s", self.dev)
            self._com.close()

    @staticmethod
    def findSerialDevices(hardwareID):
        hardwareID = "(?i)" + hardwareID  # forces case insensitive
        if len(Serial.foundDevices) == 0:
            Serial.foundDevices = []
            Serial.deviceIDS = {}
            for port in serial.tools.list_ports.grep(hardwareID):
                Serial.foundDevices.append(port[0])

        return Serial.foundDevices

    def _connect(self):
        try:
            if(self.dev == "" or self.dev is None):
                Serial.findSerialDevices(self._hardwareID)

                self.dev = Serial.foundDevices[0]

                print("Using COM Port: {}".format(self.dev))

            try:
                self._com = serial.Serial(self.dev, timeout=5)
            except serial.SerialException as e:
                ports = Serial.findSerialDevices(self._hardwareID)
                error = "Invalid port specified. No COM ports available."
                if len(ports) > 0:
                    error = "Invalid port specified. Try using one of: \n" + \
                        "\n".join(ports)
                print(error)
                raise Exception(error)

            self._com.write(b'x')

            resp = self._com.readline()
            return bool(resp)

        except serial.SerialException as e:
            error = "Unable to connect to the device. Please check that it is connected and the correct port is selected."
            print(traceback.format_exc())
            print(error)
            raise e

    @staticmethod
    def _generateHeader(cmd):
        packet = bytearray()
        packet.append(cmd)
        return packet

    def readline(self, cmd=None, data=None):
        # packet = None
        # if cmd:
        #     packet = Serial._generateHeader(cmd)
        #     if data:
        #         packet.extend(data)

        # if packet:
        #     self._com.write(packet)

        self._com.write(b'x')
        resp = self._com.readline()

        return resp



# class DriverTeensySmartMatrix(Serial):
#     def __init__(self, width, height, dev="", deviceID=None, hardwareID="16C0:0483"):
#         super(DriverTeensySmartMatrix, self).__init__(type=LEDTYPE.GENERIC, num=width * height, deviceID=deviceID, hardwareID=hardwareID)
#         self.sync = self._sync