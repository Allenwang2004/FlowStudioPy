import datetime
import shutil
import socket
import time
from datetime import datetime
from queue import Queue

import hid
import serial
import serial.tools.list_ports
from PyQt5.QtCore import QThread,QMutex
from PyQt5.QtWidgets import QDialog
from flowstudio.flow_conf import Target, Debug
import ctypes as ct
from PyQt5.QtCore import QMutexLocker

DEBUG = False

class FLOW_Thread(QThread):

    _addr = None
    _port = None

    def __init__(self, addr: str = "127.0.0.1", port: int = 54010, vid:str = "", pid: str = "", target: int = Target.PC.value,
                 con: str = '', com: str = '', rate: str = '', parity: str = '', bits: str = '', engine: str = '',
                 transports: str = '', header: str = '', s7_rate: str = ''):
        super().__init__()
        if target == Target.AIROHA_AB1585_UART.value or target == Target.AIROHA_AB1565_UART.value or target == Target.AIROHA_USB.value:
            self.airohadll = ct.cdll.LoadLibrary("./btapi.dll")

            self.airohadll.globalInitResource.argtype = None
            self.airohadll.globalInitResource.restype = ct.c_int

            self.airohadll.globalFreeResource.argtype = None
            self.airohadll.globalFreeResource.restype = ct.c_int

            self.airohadll.getHandler.argtype = None
            self.airohadll.getHandler.restype = ct.c_int

            self.airohadll.getSlotHandler.argtype = ct.c_int
            self.airohadll.getSlotHandler.restype = ct.c_int

            self.airohadll.destroyHandler.argtype = ct.c_int
            self.airohadll.destroyHandler.restype = ct.c_int

            # self.airohadll.regCallbackDevice.argtypes = [ct.c_int, c_char_p]
            # self.airohadll.regCallbackDevice.restype = ct.c_int
            #
            # self.airohadll.deRegCallbackDevice.argtype = None
            # self.airohadll.deRegCallbackDevice.restype = ct.c_int

            self.airohadll.transactStart.argtypes = [ct.c_int, ct.c_int]
            self.airohadll.transactStart.restype = ct.c_int

            self.airohadll.transactParam.argtype = [ct.c_int, ct.c_char_p, ct.c_char_p]
            self.airohadll.transactParam.restype = ct.c_int

            self.airohadll.transactComplete.argtype = ct.c_int
            self.airohadll.transactComplete.restype = ct.c_int

            self.airohadll.transactResult.argtypes = [ct.c_int, ct.c_char_p, ct.c_char_p, ct.c_int]
            self.airohadll.transactResult.restype = None

            self.airohadll.transactResultXml.argtypes = [ct.c_int, ct.c_char_p, ct.c_int]
            self.airohadll.transactResultXml.restype = None

            self.airohadll.setLogResult.argtypes = [ct.c_int, ct.c_bool]
            self.airohadll.setLogResult.restype = None

            self.airohadll.globalInitResource()
            self.handler = self.airohadll.getHandler()

        self._addr = addr
        self._port = port
        self._vid = vid
        self._pid = pid
        self._target = target
        self._con = con
        self._com = com
        self._rate = rate
        self._parity = parity
        self._bits = bits
        self._engine = engine
        self._transports = transports
        self._header = header
        self._s7_rate = s7_rate
        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.result = [None, None]
        self.usbcom = []
        self.uartcom = []
        self.Airohacom = False
        self.S7com = []
        self.S7te = None
        self.s7_write_timestamp = 0
        self.cpu_loading = {}
        self.Ret = False
        self.mutex = QMutex()

    def __del__(self):
        try:
            self.wait()
        except:
            if Debug.DEBUG_THREAD.value: print("FLOW_Thread has been deleted")

    @property
    def addr(self):
        return self._addr

    @addr.setter
    def addr(self, input_data):
        self._addr = input_data

    @property
    def port(self):
        return self._port

    @port.setter
    def port(self, input_data):
        self._port = input_data

    @property
    def vid(self):
        return self._vid

    @vid.setter
    def vid(self, new_vid: str):
        self._vid = new_vid

    @property
    def pid(self):
        return self._pid

    @pid.setter
    def pid(self, new_pid: str):
        self._pid = new_pid

    @property
    def target(self):
        return self._target

    @target.setter
    def target(self, new_target: int):
        self._target = new_target

    @property
    def con(self):
        return self._con

    @con.setter
    def con(self, new_con: str):
        self._con = new_con

    @property
    def rate(self):
        return self._rate

    @rate.setter
    def rate(self, new_rate: str):
        self._rate = new_rate

    @property
    def com(self):
        return self._com

    @com.setter
    def com(self, new_com: str):
        self._com = new_com

    @property
    def parity(self):
        return self._parity

    @parity.setter
    def parity(self, new_parity: str):
        self._parity = new_parity

    @property
    def bits(self):
        return self._bits

    @bits.setter
    def bits(self, new_bits: str):
        self._bits = new_bits

    @property
    def engine(self):
        return self._engine

    @engine.setter
    def engine(self, new_engine: str):
        self._engine = new_engine

    @property
    def transports(self):
        return self._transports

    @transports.setter
    def transports(self, new_transports: str):
        self._transports = new_transports

    @property
    def header(self):
        return self._header

    @header.setter
    def header(self, new_header: str):
        self._header = new_header

    @property
    def s7_rate(self):
        return self._s7_rate

    @s7_rate.setter
    def s7_rate(self, new_s7_rate: str):
        self._s7_rate = new_s7_rate

    def login(self):
        target = self.target
        response = b''
        if target == Target.CORTEX_M_USB.value or target == Target.GX8008C_USB.value or target == Target.FLOW_EVK_USB.value:
            try:
                vid = int(self.vid, 16)
                pid = int(self.pid, 16)
                self.usbcom = FLOW_USB_HID_COMM(vid=vid,
                                                pid=pid,
                                                target_type=target)
                response = b'USB CONNECT SUCCESSFUL connected'
            except Exception as e:
                if Debug.DEBUG_THREAD.value: print("Login Error > %s: %s" % (self.usbcom, e))
                response = b'usb connect fail'
            return response.decode()
        if target == Target.CORTEX_M_UART.value or target == Target.FLOW_EVK_UART.value:
            try:
                if self.uartcom == []:
                    self.uartcom = serial.Serial(self.com, self.rate, bytesize=8, parity='N', stopbits=1, timeout=10)
                if (self.uartcom.isOpen()):
                    self.Ret = True
                    response = b'UART CONNECT SUCCESSFUL connected'
            except Exception as e:
                if Debug.DEBUG_THREAD.value: print("Login Error > %s: %s" % (self.uartcom, e))
                response = b'UART connect fail'
            return response.decode()
        if target in [Target.AIROHA_AB1585_UART.value, Target.AIROHA_AB1565_UART.value]:
            try:
                com = self.com.lstrip(self.com[0:3])
                if self.Airohacom == False:
                    self.AirohaLogin(self.airohadll, self.handler)
                    self.AirohaUARTConnect(com, self.airohadll, self.handler)
                response = b'Airoha UART CONNECT SUCCESSFUL connected'
            except Exception as e:
                if Debug.DEBUG_THREAD.value: print("Login Error > %s: %s" % (self.uartcom, e))
                response = b'Airoha UART connect fail'
            return response.decode()
        if target == Target.AIROHA_USB.value:
            try:
                if self.Airohacom == False:
                    self.AirohaLogin(self.airohadll, self.handler)
                    self.AirohaUSBConnect(self.airohadll, self.handler, self.vid, self.pid)
                response = b'Airoha USB CONNECT SUCCESSFUL connected'
            except Exception as e:
                if Debug.DEBUG_THREAD.value: print("Login Error > %s: %s" % (self.uartcom, e))
                response = b'Airoha USB connect fail'
            return response.decode()
        if target == Target.S7.value:
            try:
                from bin.S7_helper import usbConnect
                TEST_ENGINE_INDEX = "TestEngine_DLL"
                self.S7te = usbConnect.UsbConnect("../bin/S7_helper/TestEngine.dll")
                transports = dict()
                transports[TEST_ENGINE_INDEX] = self.S7te.list_transports()
                current_connection_string = transports[TEST_ENGINE_INDEX][self.transports]
                self.S7com = self.S7te.usbconnect(current_connection_string)
                response = b'S7 USB CONNECT SUCCESSFUL connected'

                header = int(self.header, 16)
                rate = int(self.s7_rate)
                data16bit = [0x1, 0x7, header, 0x0, 0x2, rate]
                res = self.S7te.teAppWrite(self.S7com, 0, data16bit, len(data16bit))
                if res != 1:
                    response = b'S7 USB connect fail, Sample rate setting failed'
            except Exception as e:
                if Debug.DEBUG_THREAD.value: print("Login Error > %s: %s" % (self.S7com, e))
                response = b'S7 USB connect fail'
            return response.decode()
        else:
            try:
                if Debug.DEBUG_THREAD.value: print("Login Information > IP: %s Port: %d" %(self.addr, self.port))
                self.client.connect((self.addr, self.port))
                if Debug.DEBUG_THREAD.value: print("Login Process > Socket connected")
                response = self.client.recv(32)
                if Debug.DEBUG_THREAD.value: print("Login Process > Socket received message: %s" %response.decode())
            except Exception as e:
                if Debug.DEBUG_THREAD.value: print("Login Error > %s: %s" %(self.client, e))
            return response.decode()

    def logout(self, index=0):
        self.client.detach()
        self.client.close()
        if self.vid != "000000" and self.usbcom is None:
            self.usbcom.write_msg("quit")
        if index == 0 and self.uartcom != []:
            self.uartcom.close()
        if self.target in [Target.AIROHA_AB1585_UART.value, Target.AIROHA_AB1565_UART.value] and index == 0:
            com = self.com.lstrip(self.com[0:3])
            self.AirohaUARTDisconnect(com, self.airohadll, self.handler)
            self.Airohacom = False
            self.airohadll.destroyHandler(self.handler)
            self.airohadll.globalFreeResource()
        if self.target == Target.AIROHA_USB.value and index == 0:
            self.AirohaUSBDisconnect(self.airohadll, self.handler)
            self.Airohacom = False
            self.airohadll.destroyHandler(self.handler)
            self.airohadll.globalFreeResource()
        # if self.target == Target.S7.value and index == 0:
        #     print(self.S7te.usbdisconnect(self.S7com))

    def cmdQuery(self, data: str, size: int) -> tuple:
        if Debug.DEBUG_THREAD.value: print("cmdQuery cmd: ", data)
        byte_data = data.encode()
        postfix = None
        recv_response = b''
        index = 0

        target = self.target
        if target == Target.CORTEX_M_USB.value or target == Target.GX8008C_USB.value or target == Target.FLOW_EVK_USB.value:
            try:
                if target == Target.GX8008C_USB.value:
                    head_list = {'USB_TX': 'TX  ', 'USB_RX': 'RX  '}
                    head = head_list[self.engine]
                    data = head + data
                with QMutexLocker(self.mutex):
                    recv = self.usbcom.write_msg(data)
                recv_response = recv.encode()
                if Debug.DEBUG_THREAD.value: print("cmdQuery recv_response: ", recv_response)
                return True, recv_response
            except Exception as e:
                if Debug.DEBUG_THREAD.value: print('cmdQuery send Error: %s' % e)
                return False, False

        elif target == Target.CORTEX_M_UART.value or target == Target.FLOW_EVK_UART.value:
            try:
                if (self.Ret):
                    conversion = Conversion()
                    data = conversion.conversionData(data)
                    # print(bytes(data))
                    with QMutexLocker(self.mutex):
                        self.uartcom.write(bytes(data))
                        header = self.uartcom.read(4)
                        header_l = list(header)
                        recv = self.uartcom.read(header_l[3])
                    recv_response = recv
                    if Debug.DEBUG_THREAD.value: print("cmdQuery recv_response: ", recv_response)
                    return True, recv_response
            except Exception as e:
                if Debug.DEBUG_THREAD.value: print("cmdQuery send Error > %s: %s" % (self.uartcom, e))
                return False, False

        elif target in [Target.AIROHA_AB1585_UART.value, Target.AIROHA_AB1565_UART.value, Target.AIROHA_USB.value]:
            try:
                head_list = {'USB_TX': 'TX  ', 'USB_RX': 'RX  ', 'HFP_TX': 'BTTX', 'HFP_RX': 'BTRX',
                             'A2DP': 'A2DP', 'BIS RX': 'BISR', 'CIS TX': 'CIST', 'CIS RX': 'CISR'}
                head = head_list[self.engine]
                cmd = head + data
                if Debug.DEBUG_THREAD.value: print("cmdQuery cmd: ", cmd)
                with QMutexLocker(self.mutex):
                    if target in [Target.AIROHA_AB1585_UART.value, Target.AIROHA_AB1565_UART.value]:
                        recv = self.AirohaUARTRunCommand(cmd, self.airohadll, self.handler)
                    else:
                        recv = self.AirohaUSBRunCommand(cmd, self.airohadll, self.handler)
                if recv == '':
                    return False, False
                recv_response = (recv + '\n\x00').encode()
                if Debug.DEBUG_THREAD.value: print("cmdQuery recv_response: ", recv_response)
                return True, recv_response
            except Exception as e:
                if Debug.DEBUG_THREAD.value: print("cmdQuery send Error > %s: %s" % (self.uartcom, e))
                return False, False

        elif target in [Target.S7.value]:
            try:
                res = self.S7_send_cmd(data)
                if res != 1:
                    return False, False
                time.sleep(0.01)
                res, response = self.S7_read_value(data)
                if res != 1:
                    return False, False
                recv_response = (response + '\n\x00').encode()
                if Debug.DEBUG_THREAD.value: print("cmdQuery recv_response: ", recv_response)
                return True, recv_response
            except Exception as e:
                if Debug.DEBUG_THREAD.value: print("cmdQuery send Error > %s: %s" % (e))
                return False, False

        else:
            try:
                send_response = self.client.sendall(byte_data)
            except Exception as e:
                if Debug.DEBUG_THREAD.value: print('cmdQuery send Error: %s %s' % (self.__class__.__name__, e))
                return False, None

            if send_response == None:
                while not postfix == "\n\00":
                    if Debug.DEBUG_THREAD.value: print('times to recv message: %d' %index)
                    index = index + 1
                    try:
                        buffer = self.client.recv(size)
                    except Exception as e:
                        if Debug.DEBUG_THREAD.value: print('cmdQuery recv Error: %s %s' % (self.__class__.__name__, e))
                        return False, False
                    recv_response = recv_response + buffer
                    if 'VISUALIZER' in data:
                        break
                    postfix = recv_response.decode()[-2:]
                    if Debug.DEBUG_THREAD.value: print("cmdQuery recv_response: ", recv_response)
                return True, recv_response

    def is_number(self, s):
        try:
            float(s)
            return True
        except ValueError:
            return False

    def doubleCmdQuery(self, data1: str, data2: str, size: int) -> tuple:
        send_response1, recv_response1 = self.cmdQuery(data1, size)
        send_response2, recv_response2 = self.cmdQuery(data2, size)
        return [send_response1, send_response2], [recv_response1, recv_response2]

    def cmdQuerys(self, data: list, size: int):
        looptimes = len(data)
        send_result = list()
        recv_result = list()
        for index in range(looptimes):
            cmd = data[index]
            send_response, recv_response = self.cmdQuery(cmd, size)
            send_result.append(send_response)
            recv_result.append(recv_response)
        return send_result, recv_result

    def hQuery(self, data):
        if Debug.DEBUG_THREAD.value: print("hQuery cmd: ", data)
        byte_data = data.encode()
        target = self.target
        if target == Target.CORTEX_M_USB.value or target == Target.GX8008C_USB.value or target == Target.FLOW_EVK_USB.value:
            try:
                if target == Target.GX8008C_USB.value:
                    head_list = {'USB_TX': 'TX  ', 'USB_RX': 'RX  '}
                    head = head_list[self.engine]
                    data = head + data
                with QMutexLocker(self.mutex):
                    recv = self.usbcom.write_msg(data)
                recv_response = recv.encode()
                if Debug.DEBUG_THREAD.value: print("hQuery recv_response: ", recv_response)
            except Exception as e:
                if Debug.DEBUG_THREAD.value: print('hQuery send Error: %s' %e)
                return False, False

        elif target == Target.CORTEX_M_UART.value or target == Target.FLOW_EVK_UART.value:
            try:
                if (self.Ret):
                    conversion = Conversion()
                    data = conversion.conversionData(data)
                    # print(bytes(data))
                    with QMutexLocker(self.mutex):
                        self.uartcom.write(bytes(data))
                        header = self.uartcom.read(4)
                        header_l = list(header)
                        recv = self.uartcom.read(header_l[3])
                    # print('recv',recv)
                    recv_response = recv
                    if Debug.DEBUG_THREAD.value: print("hQuery recv_response: ", recv_response)
            except Exception as e:
                if Debug.DEBUG_THREAD.value: print("hQuery send Error > %s: %s" % (self.uartcom, e))
                return False, False

        elif target in [Target.AIROHA_AB1585_UART.value, Target.AIROHA_AB1565_UART.value, Target.AIROHA_USB.value]:
            try:
                head_list = {'USB_TX': 'TX  ', 'USB_RX': 'RX  ', 'HFP_TX': 'BTTX', 'HFP_RX': 'BTRX',
                             'A2DP': 'A2DP', 'BIS RX': 'BISR', 'CIS TX': 'CIST', 'CIS RX': 'CISR'}
                head = head_list[self.engine]
                cmd = head + data
                if Debug.DEBUG_THREAD.value: print("hQuery cmd: ", cmd)
                with QMutexLocker(self.mutex):
                    if target in [Target.AIROHA_AB1585_UART.value, Target.AIROHA_AB1565_UART.value]:
                        recv = self.AirohaUARTRunCommand(cmd, self.airohadll, self.handler)
                    else:
                        recv = self.AirohaUSBRunCommand(cmd, self.airohadll, self.handler)
                if recv == '':
                    return False, False
                recv_response = (recv + '\n\x00').encode()
                if Debug.DEBUG_THREAD.value: print("hQuery recv_response: ", recv_response)
                return True, recv_response
            except Exception as e:
                if Debug.DEBUG_THREAD.value: print("hQuery send Error > %s: %s" % (e))
                return False, False

        elif target in [Target.S7.value]:
            try:
                res = self.S7_send_cmd(data)
                if res == 2:
                    return True, self.cpu_loading[data]
                if res != 1:
                    return False, False
                time.sleep(0.01)
                res, response = self.S7_read_value(data)
                if res != 1:
                    return False, False
                recv_response = (response + '\n\x00').encode()
                if data in ['mem/', 'memTotal/', 'cpu/']:
                    self.cpu_loading[data] = recv_response
            except Exception as e:
                if Debug.DEBUG_THREAD.value: print("hQuery send Error > %s: %s" % (e))
                return False, False

        else:
            try:
                self.client.sendall(byte_data)
            except Exception as e:
                if Debug.DEBUG_THREAD.value: print('hQuery send Error: %s' %e)
                return False, False

            try:
                recv_response = self.client.recv(32)
            except Exception as e:
                if Debug.DEBUG_THREAD.value: print('hQuery recv Error: %s' %e)
                return False, False
        if Debug.DEBUG_THREAD.value: print("hQuery-recv_response: ", recv_response)
        return True, recv_response

    def cmdSned(self, data):
        with QMutexLocker(self.mutex):
            self.usbcom.write_msg(data, 2)

    def setQueryTask(self, data, size):
        self.args = {'data': data, 'size': size}
        self.funcPtr = self.cmdQuery

    def setQueryTasks(self, data, size):
        self.args = {'data': data, 'size': size}
        self.funcPtr = self.cmdQuerys

    def run(self):
        # send_response, recv_response = self.cmdQuery(**self.args)
        send_response, recv_response = self.funcPtr(**self.args)
        self.result = [send_response, recv_response]

    def AirohaLogin(self, airohadll, handler):
        print(handler)
        print(airohadll.transactStart(handler, 5))
        print(airohadll.transactParam(handler, b"airoha_task", b"ToolLogLevel"))
        print(airohadll.transactParam(handler, b"level", b"2"))
        res = airohadll.transactComplete(handler)
        print(res)
        myArray = ct.create_string_buffer(4096)
        print(airohadll.transactResult(handler, b"result", myArray, 4096))
        print(myArray.value)

    def AirohaUARTConnect(self, com, airohadll, handler):
        print(handler)
        print(airohadll.transactStart(handler, 5))
        print(airohadll.transactParam(handler, b"airoha_task", b"ConnectSerialHost"))
        print(airohadll.transactParam(handler, b"host", b"serial"))
        print(airohadll.transactParam(handler, b"action", b"connect"))
        data_s = com
        print(airohadll.transactParam(handler, b"port", data_s.encode('utf-8')))
        data_s = "3000000"
        print(airohadll.transactParam(handler, b"rate", data_s.encode('utf-8')))
        data_s = "DUT"
        print(airohadll.transactParam(handler, b"device_name", data_s.encode('utf-8')))
        print(airohadll.transactParam(handler, b"transport", b"h4"))
        print(airohadll.transactParam(handler, b"handshake", b"XOnXOff"))

        res = airohadll.transactComplete(handler)
        print(res)
        myArray = ct.create_string_buffer(4096)
        print(airohadll.transactResult(handler, b"result", myArray, 4096))
        print(myArray.value)
        self.Airohacom = True

    def AirohaUSBConnect(self, airohadll, handler, vendor_id: str, product_id: str):
        device_name = "DUT_USB"
        airohadll.transactStart(handler, 5)
        airohadll.transactParam(handler, b"airoha_task", b"ConnectDutByUsbHid")
        airohadll.transactParam(handler, b"action", b"connect")
        airohadll.transactParam(handler, b"vendor_id", vendor_id.encode('utf-8'))
        airohadll.transactParam(handler, b"product_id", product_id.encode('utf-8'))
        airohadll.transactParam(handler, b"device_name", device_name.encode('utf-8'))
        airohadll.transactParam(handler, b"transport", b"USB_HID")
        airohadll.transactParam(handler, b"handshake", b"none")
        res = airohadll.transactComplete(handler)
        print(res)
        myArray = ct.create_string_buffer(4096)
        airohadll.transactResult(handler, b"result", myArray, 4096)
        print(myArray.value)
        self.Airohacom = True


    def ASCII2HEX(self, asc_code: str):
        # print(f'ASCII: {asc_code}')
        hex_string = ''
        list_h = []
        for c in asc_code:
            list_h.append(str(hex(ord(c))[2:]))
        hex_string = hex_string.join(list_h)
        # print(hex_string)
        return hex_string

    def data_flip(self, data: str):
        data_aft = data[::-1]
        # print(data_aft)
        return data_aft

    def HEX2ASCII(self, hex_code: str):
        # print(f'HEX: {hex_code}')
        asc_string = ''
        list_s = []
        for i in range(0, len(hex_code), 2):
            list_s.append(chr(int(hex_code[i:i + 2], 16)))
        asc_string = asc_string.join(list_s)
        # print(asc_string)
        return asc_string

    def AirohaUARTRunCommand(self, data, airohadll, handler):
        (handler)
        (airohadll.transactStart(handler, 5))
        (airohadll.transactParam(handler, b"airoha_cmd", b"RACE_FLOW_COMMAND"))
        data_s = "DUT"
        (airohadll.transactParam(handler, b"device_name", data_s.encode('utf-8')))
        (airohadll.transactParam(handler, b"command_xml", b"command_sample.xml"))
        (data_s)
        data_s = "0x" + self.ASCII2HEX(self.data_flip(data))
        (airohadll.transactParam(handler, b"%flow_send", data_s.encode('utf-8')))

        res = airohadll.transactComplete(handler)
        (res);
        myArray = ct.create_string_buffer(4096)
        # print(airohadll.transactResult(handler, b"result", myArray, 4096))
        (airohadll.transactResult(handler, b"flow_res", myArray, 4096))
        # print(myArray.raw)
        # print(self.data_flip(self.HEX2ASCII(myArray.value)))
        return self.data_flip(self.HEX2ASCII(myArray.value))

    def AirohaUSBRunCommand(self, data, airohadll, handler):
        DUT_NAME = "DUT_USB"
        (handler)
        (airohadll.transactStart(handler, 5))
        (airohadll.transactParam(handler, b"airoha_cmd", b"RACE_FLOW_COMMAND"))
        (airohadll.transactParam(handler, b"device_name", DUT_NAME.encode('utf-8')))
        (airohadll.transactParam(handler, b"command_xml", b"command_sample.xml"))
        # (data_s)
        data_s = "0x" + self.ASCII2HEX(self.data_flip(data))
        (airohadll.transactParam(handler, b"%flow_send", data_s.encode('utf-8')))

        res = airohadll.transactComplete(handler)
        # (res)
        print(data)
        myArray = ct.create_string_buffer(4096)
        # print(airohadll.transactResult(handler, b"result", myArray, 4096))
        (airohadll.transactResult(handler, b"flow_res", myArray, 4096))
        # print(myArray.raw)
        return self.data_flip(self.HEX2ASCII(myArray.value))

    def AirohaUARTDisconnect(self, com, airohadll, handler):
        print(airohadll.transactStart(handler, 5))
        print(airohadll.transactParam(handler, b"airoha_task", b"DisconnectDUT"))
        data_s = com
        print(airohadll.transactParam(handler, b"port", data_s.encode('utf-8')))
        airohadll.transactComplete(handler)
        myArray = ct.create_string_buffer(4096)
        airohadll.transactResult(handler, b"result", myArray, 4096)
        if DEBUG: print(myArray.value, 'disconnect res')

    def AirohaUSBDisconnect(self, airohadll, handler):
        device_name = "DUT_USB"
        airohadll.transactStart(handler, 5)
        airohadll.transactParam(handler, b"airoha_task", b"DisconnectDUT")
        airohadll.transactParam(handler, b"device_name", device_name.encode('utf-8'))
        airohadll.transactParam(handler, b"device_type", b"USB_HID")
        res = airohadll.transactComplete(handler)
        if DEBUG: print(res, 'disconnect res')

    def combine_to_16bit(self, eight_bit_list):
        sixteen_bit_list = []
        for i in range(0, len(eight_bit_list), 2):
            if i + 1 < len(eight_bit_list):
                combined = (eight_bit_list[i + 1] << 8) | eight_bit_list[i]
                sixteen_bit_list.append(combined)
        return sixteen_bit_list

    def query_with_timeout(self, data16bit, chanel_num, timeout=1):
        import threading
        result = [None]

        def target():
            result[0] = self.S7te.teAppWrite(self.S7com, chanel_num, data16bit, len(data16bit))

        thread = threading.Thread(target=target)
        thread.start()
        thread.join(timeout)
        if Debug.DEBUG_THREAD.value: print("query_with_timeout: ", result[0])
        if thread.is_alive():
            self.S7te = []
            self.S7com = []
            return 0
        return result[0]

    def S7_send_cmd(self, data):
        try:
            if data in ['mem/', 'memTotal/', 'cpu/']:
                if self.s7_write_timestamp > time.time() - 1:
                    return 2
            elif data in ['memFreeSpace/']:
                self.s7_write_timestamp = 0
            else:
                self.s7_write_timestamp = time.time()

            cmdstr = data
            hex_value = int(self.header, 16)
            # 格式化输出为十六进制字符串，并加上前缀 '0x'
            # data16bit = [0x1, 0x5, 0x04065, 0x0,  0x8, 0x0, 0x0, 0x01, 0x0]
            data16bit = [0x1, 0x5, hex_value, 0x0, 0x8, 0x0, 0x0, 0x00, 0x0]

            # Add null terminator to the string
            if len(cmdstr) % 2 == 0:
                cmdstr += '\0\0'
            else:
                cmdstr += '\0\0\0'
            # Convert mystr to 8-bit list
            data8bit = [ord(c) for c in cmdstr]

            # Combine 8-bit list to 16-bit values
            data16bit_from_str = self.combine_to_16bit(data8bit)

            # Add the length of mystr (including null terminators) to the fifth value in data16bit
            data16bit[4] += len(data8bit)

            # Append 16-bit values to data16bit array
            data16bit.extend(data16bit_from_str)

            res = self.query_with_timeout(data16bit, 0)
            if Debug.DEBUG_THREAD.value: print("res", res)
            return res
        except Exception as e:
            if Debug.DEBUG_THREAD.value: print('S7_send_cmd error: %s' % e)
            return 0

    def S7_read_value(self, data):
        try:
            hex_value = int(self.header, 16)
            data16bit = [0x1, 0x6, hex_value, 0x0]
            # print(len(data16bit))
            self.S7te.teAppWrite(self.S7com, 0, data16bit, len(data16bit))

            retval, channel, data, readLength = self.S7te.teAppRead(self.S7com, channel=0, dataLength=15,
                                                                    timeoutMs=5000)
            # print(retval, channel, data, readLength)
            # Print data in hexadecimal format
            # print([hex(x) for x in data])
            data_as_string = ''.join(chr(x & 0xFF) + chr((x >> 8) & 0xFF) for x in data[4:])
            if Debug.DEBUG_THREAD.value: print("data_as_string", data_as_string)
            if Debug.DEBUG_THREAD.value: print("retval", retval)
            if retval == 0:
                data_as_string = 0
            return retval, data_as_string
        except Exception as e:
            if Debug.DEBUG_THREAD.value: print('S7_read_value error: %s' % e)
            return 0, 0

class FLOW_Thread_Manager(object):

    _connection = False
    global usbclient
    usbclient = ""

    def __init__(self, addr: str = "127.0.0.1", port: int = 54010, vid: str = "000000", pid: str = "000000",
                 target: int = Target.PC.value, con: str = '', com: str = '', rate: str = '', parity: str = '',
                 bits: str = '', engine: str = '', transports: str = '', header: str = '', s7_rate: str = ''):
        super().__init__()
        self._addr = addr
        self._port = port
        self._vid = vid
        self._pid = pid
        self._target = target
        self._con = con
        self._com = com
        self._rate = rate
        self._parity = parity
        self._bits = bits
        self._engine = engine
        self._transports = transports
        self._header = header
        self._s7_rate = s7_rate

    @property
    def connection(self):
        return self._connection

    @connection.setter
    def connection(self, new_data: bool):
        self._connection = new_data

    @property
    def addr(self):
        return self._addr

    @addr.setter
    def addr(self, new_addr:str):
        self._addr = new_addr

    @property
    def port(self):
        return self._port

    @port.setter
    def port(self, new_port:int):
        self._port = new_port

    @property
    def vid(self):
        return self._vid

    @vid.setter
    def vid(self, new_vid: str):
        self._vid = new_vid

    @property
    def pid(self):
        return self._pid

    @pid.setter
    def pid(self, new_pid: str):
        self._pid = new_pid

    @property
    def target(self):
        return self._target

    @target.setter
    def target(self, new_target: int):
        self._target = new_target

    @property
    def con(self):
        return self._con

    @con.setter
    def con(self, new_con: str):
        self._con = new_con

    @property
    def rate(self):
        return self._rate

    @rate.setter
    def rate(self, new_rate: str):
        self._rate = new_rate

    @property
    def com(self):
        return self._com

    @com.setter
    def com(self, new_com: str):
        self._com = new_com

    @property
    def parity(self):
        return self._parity

    @parity.setter
    def parity(self, new_parity: str):
        self._parity = new_parity

    @property
    def bits(self):
        return self._bits

    @bits.setter
    def bits(self, new_bits: str):
        self._bits = new_bits

    @property
    def engine(self):
        return self._engine

    @engine.setter
    def engine(self, new_engine: str):
        self._engine = new_engine

    @property
    def transports(self):
        return self._transports

    @transports.setter
    def transports(self, new_transports: str):
        self._transports = new_transports

    @property
    def header(self):
        return self._header

    @header.setter
    def header(self, new_header: str):
        self._header = new_header

    @property
    def s7_rate(self):
        return self._s7_rate

    @s7_rate.setter
    def s7_rate(self, new_s7_rate: str):
        self._s7_rate = new_s7_rate

    def createClient(self):
        if self.target == Target.CORTEX_M_USB.value or \
                self.target == Target.CORTEX_M_UART.value or \
                self.target == Target.AIROHA_AB1585_UART.value or \
                self.target == Target.AIROHA_AB1565_UART.value or \
                self.target == Target.AIROHA_USB.value or \
                self.target == Target.FLOW_EVK_UART.value or \
                self.target == Target.GX8008C_USB.value or \
                self.target == Target.FLOW_EVK_USB.value or \
                self.target == Target.S7.value:
            global usbclient
            if not usbclient:
                # connect UART
                if self.target == Target.CORTEX_M_UART.value or self.target == Target.FLOW_EVK_UART.value:
                    usbclient = FLOW_Thread(target=self.target, con=self.con, com=self.com, rate=self.rate,
                                            parity=self.parity, bits=self.bits)
                # connect Airaho
                elif self.target in [Target.AIROHA_AB1585_UART.value, Target.AIROHA_AB1565_UART.value,
                                     Target.AIROHA_USB.value]:
                    usbclient = FLOW_Thread(com=self.com, engine=self.engine, target=self.target, vid=self.vid,
                                            pid=self.pid)
                elif self.target in [Target.GX8008C_USB.value]:
                    usbclient = FLOW_Thread(addr=self.addr, port=self.port, vid=self.vid, pid=self.pid,
                                            target=self.target, engine=self.engine)
                elif self.target in [Target.S7.value]:
                    usbclient = FLOW_Thread(target=self.target, transports=self.transports, header=self.header, s7_rate=self.s7_rate)
                else:
                    usbclient = FLOW_Thread(self.addr, self.port, self.vid, self.pid, self.target)
            return usbclient
        else:
            client = FLOW_Thread(addr=self.addr, port=self.port, vid=self.vid, pid=self.pid, target=self.target)
            return client

    def cancelClient(self):
        global usbclient
        usbclient = ""

    """
    COMMAND TABLE
	{ "info/",					OnInfo },
	{ "upTime/",				OnUpTime },
	{ "cpu/",					OnCpu},
	{ "cpuAO/",					OnCpuAO },
	{ "cpuTotal/",				OnCpuTotal },
	{ "setRoot/",				OnSetRoot },
	{ "set/",					OnSet },
	{ "setCoord/",				OnSetCoord },
	{ "setSerializeCoord/",		OnSetSerializeCoord },
	{ "get/",					OnGet },
	{ "getRootSpec/",			OnGetRootSpec },
	{ "getCoord/",				OnGetCoord },
	{ "getSerialized/",			OnGetSerialized },
	{ "getSerializedAmount/",	OnGetSerializedAmount },
	{ "getAOlist/",				OnGetAOlist },
	{ "getAOspec/",				OnGetAOspec },
	{ "getAOspecCoord/",		OnGetAOspecCoord },
	{ "getParamSpec/",			OnGetParamSpec },
    """



HID_BUFFER_LEN = 64
FLOW_USB_PACKET_HEADER_LEN = 4
MAX_PAYLOAD_LEN_IN_ONE_PACKET = HID_BUFFER_LEN - FLOW_USB_PACKET_HEADER_LEN

class FLOW_USB_HID_COMM:
    def __init__(self, vid, pid, target_type):
        self.usb_dev = hid.Device(vid=vid,
                                  pid=pid,
                                  path=hid.enumerate(vid, pid)[1]['path']) \
            if target_type == Target.GX8008C_USB.value else hid.Device(vid, pid)
        self.nPacketCount = 0

    def write_msg(self, msg, header2: int = 1):
        try:
            msg_len = len(msg)
            self.nPacketCount = msg_len

            # split msg to chunks that matches the max payload length in one packet
            msg_chunks = list(self.chunk_msg(msg, MAX_PAYLOAD_LEN_IN_ONE_PACKET))
            # print(msg_chunks)
            chunk_idx = 0

            while self.nPacketCount > 0:
                self.nPacketCount = self.nPacketCount - MAX_PAYLOAD_LEN_IN_ONE_PACKET
                header = [0] * 4
                # report ID
                header[0] = 1
                # max msg len MSB & LSB
                if header2 == 1:
                    header[1] = msg_len >> 8
                else:
                    header[1] = 2
                header[2] = msg_len & 0xFF

                # current valid payload len
                if self.nPacketCount >= MAX_PAYLOAD_LEN_IN_ONE_PACKET:
                    valid_payload_len = MAX_PAYLOAD_LEN_IN_ONE_PACKET
                else:
                    valid_payload_len = msg_len % MAX_PAYLOAD_LEN_IN_ONE_PACKET
                header[3] = valid_payload_len

                payload = list(msg_chunks[chunk_idx])

                for i in range(valid_payload_len):
                    payload[i] = ord(payload[i])

                usb_out_data = header + payload
                print("cmd", msg)
                print(usb_out_data)
                self.usb_dev.write(bytes(usb_out_data))

            if header2 != 2:
                readbuf = self.usb_dev.read(64, timeout=2000)

                # read the first packet to get total count of msg response


                total_bytes_to_recv = readbuf[1]*256 + readbuf[2]
                # print(readbuf[4:], list(readbuf))
                # print(total_bytes_to_recv)
                response = readbuf[4:]
                while total_bytes_to_recv > MAX_PAYLOAD_LEN_IN_ONE_PACKET:
                    total_bytes_to_recv = total_bytes_to_recv - MAX_PAYLOAD_LEN_IN_ONE_PACKET
                    readbuf = self.usb_dev.read(total_bytes_to_recv + FLOW_USB_PACKET_HEADER_LEN)
                    response = response + readbuf[4:]
                    # print(readbuf[4:], list(readbuf))

                # print the final response
                print('response:', str(response, 'utf-8'))
                return str(response, 'utf-8')
        except:
            return None

    def chunk_msg(self, msg, length):
        return (msg[0 + i:length + i] for i in range(0, len(msg), length))

class Conversion:


    def conversionData(self, msg):
        msg_len = len(msg)
        self.nPacketCount = msg_len

        # split msg to chunks that matches the max payload length in one packet
        msg_chunks = list(self.chunk_msg(msg, MAX_PAYLOAD_LEN_IN_ONE_PACKET))
        chunk_idx = 0

        while self.nPacketCount > 0:
            self.nPacketCount = self.nPacketCount - MAX_PAYLOAD_LEN_IN_ONE_PACKET
            header = [0] * 4
            # report ID
            header[0] = 1
            # max msg len MSB & LSB
            header[1] = msg_len >> 8
            header[2] = 0
            # current valid payload len
            if self.nPacketCount >= MAX_PAYLOAD_LEN_IN_ONE_PACKET:
                valid_payload_len = MAX_PAYLOAD_LEN_IN_ONE_PACKET
            else:
                valid_payload_len = msg_len % MAX_PAYLOAD_LEN_IN_ONE_PACKET
            header[3] = valid_payload_len
            payload = list(msg_chunks[chunk_idx])

            for i in range(valid_payload_len):
                payload[i] = ord(payload[i])
            uart_out_data = header + payload
            return uart_out_data

    def chunk_msg(self, msg, length):
        return (msg[0 + i:length + i] for i in range(0, len(msg), length))
