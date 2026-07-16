import os
import ctypes
from ctypes import wintypes
import sys

if not sys.path[0] == os.path.dirname(os.path.dirname(os.path.abspath(__file__))):
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if __package__ is None or __package__ == '':
    __package__ = os.path.basename(os.path.dirname(os.path.abspath(__file__)))

from .TestEngineAPI import TestEngine as TestEngineAPI

TRANSPORTS = {"USBDBG": 256}

class UsbConnect(TestEngineAPI):
    def __init__(self, dll_dir=''):
        if not dll_dir:
            script_path = os.path.dirname(os.path.realpath(__file__))
            default_dll = "".join([script_path, ""])
            dll_dir = os.path.realpath(default_dll)
        fullpath = os.path.realpath(dll_dir)
        fullpath_copy = fullpath.strip()
        self.error = ""
        if fullpath_copy.lower().endswith('.dll'):
            self.dll_dir = os.path.dirname(fullpath)
        else:
            self.dll_dir = fullpath
        try:
            super().__init__(self.dll_dir)

        except Exception as error:
            self.TestEngineDLL = None
            self.error = str(error)

    def clean_up(self, usb_handle=0):
        if self.TestEngineDLL is None:
            return

        if isinstance(usb_handle, list):
            for handle in usb_handle:
                self.usbdisconnect(handle)
        else:
            if usb_handle:
               self.usbdisconnect(usb_handle)

        ctypes.windll.kernel32.FreeLibrary.argtypes = [wintypes.HMODULE]
        ctypes.windll.kernel32.FreeLibrary(self.TestEngineDLL._handle)
        self.TestEngineDLL = None
        self.error = ""

    def load_dll(self, new_dll_location=None):
        if self.TestEngineDLL is not None:
            return True
        if new_dll_location is not None:
            self.dll_dir = new_dll_location
        try:
            self.__init__(self.dll_dir)
            return True
        except Exception as error:
            self.TestEngineDLL = None
            self.error = str(error)
            return False

    def list_transports(self):
        result, max_len, _, _, _ = super().teGetAvailableDebugPorts(maxLen=0)
        result, _, ports, trans, _ = super().teGetAvailableDebugPorts(maxLen=max_len)
        if not result or not ports or not trans:
            return dict()
        ports = ports.split(",")
        transports = trans.split(",")
        return {ports[i].strip(): transports[i].strip() for i in range(len(ports))}

    def usbconnect(self, trans_string, retry_time_out=5000, usb_time_out=5000):
        trans = trans_string.split("SPITRANS=")[1].split(" ")[0]
        port = trans_string.split("SPIPORT=")[1]

        if trans not in TRANSPORTS:
            return False

        if trans == 'LPT' or trans == "USB" and port.isnumeric():
            return super().openTestEngineDebugTrans(trans=trans_string, multi=0)

        trans_number = TRANSPORTS[trans]
        return super().openTestEngine(trans_number, port, 0, retry_time_out, usb_time_out)

    def usbdisconnect(self, usb_handle):
        return super().closeTestEngine(usb_handle)
