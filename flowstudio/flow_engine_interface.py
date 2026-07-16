import ctypes
import numpy as np

audioBuffer = np.ctypeslib.ndpointer(dtype=np.uintp, ndim=1, flags='C_CONTIGUOUS')

class FLOW_Engine_Interface(object):

    def __init__(self, libraryPath):
        self.library = ctypes.cdll.LoadLibrary(libraryPath)
        self._frameSize = None
        self._sampleRate = None
        self._audioBuffer = None

    @property
    def frameSize(self):
        return self._frameSize

    @frameSize.setter
    def frameSize(self, input_data):
        self._frameSize = input_data

    @property
    def sampleRate(self):
        return self._sampleRate

    @sampleRate.setter
    def sampleRate(self, input_data):
        self._sampleRate = input_data

    def create(self, name, configFilePath, inputsChannel, outputsChannel, sampleRate, frameSize):
        self.frameSize = frameSize
        self.sampleRate = sampleRate
        self.library.FlowEngine_create.restype = ctypes.c_void_p
        self.library.FlowEngine_create.argtypes = [ctypes.c_char_p, ctypes.c_char_p, ctypes.c_int, ctypes.c_int]
        instance = self.library.FlowEngine_create(bytes(name, 'ascii'), bytes(configFilePath, 'ascii'), ctypes.c_int(inputsChannel), ctypes.c_int(outputsChannel))

        return instance

    def prepare(self, instance, sampleRate, frameSize):
        self.library.FlowEngine_prepare.restype = ctypes.c_int
        self.library.FlowEngine_prepare.argtypes = (ctypes.c_void_p, ctypes.c_float, ctypes.c_int)
        response = self.library.FlowEngine_prepare(instance, ctypes.c_float(sampleRate), ctypes.c_int(frameSize))

        return response

    def destroy(self, instance):
        self.library.FlowEngine_destroy.restype = None
        self.library.FlowEngine_destroy.argtypes = [ctypes.c_void_p, ]
        self.library.FlowEngine_destroy(instance)

    def setCMD(self, instance, cmd):
        self.library.FlowEngine_set_cmd.restype = None
        self.library.FlowEngine_set_cmd.argtypes = [ctypes.c_void_p, ctypes.c_char_p]
        self.library.FlowEngine_set_cmd(instance, bytes(cmd, 'ascii'))

    def getCMD(self, instance):
        self.library.FlowEngine_get_cmd.restype = ctypes.c_char_p
        self.library.FlowEngine_get_cmd.argtypes = [ctypes.c_void_p, ]
        response = self.library.FlowEngine_get_cmd(instance)

        return response.decode("UTF-8")

    def queryCMD(self, instance, cmd):
        self.library.FlowEngine_query_cmd.restype = ctypes.c_char_p
        self.library.FlowEngine_query_cmd.argtypes = [ctypes.c_void_p, ctypes.c_char_p]
        response = self.library.FlowEngine_query_cmd(instance, bytes(cmd, 'ascii'))

        return response.decode("UTF-8")

    def createTcpServer(self, instance, port):
        self.library.FlowEngine_create_tcp_server.restype = ctypes.c_int
        self.library.FlowEngine_create_tcp_server.argtypes = [ctypes.c_void_p, ctypes.c_int]
        self.library.FlowEngine_create_tcp_server(instance, ctypes.c_int(port))

    def process(self, instance, input):
        output = np.zeros_like(input)

        xpp = (input.__array_interface__['data'][0] + np.arange(input.shape[0]) * input.strides[0]).astype(np.uintp)
        ypp = (output.__array_interface__['data'][0] + np.arange(output.shape[0]) * output.strides[0]).astype(np.uintp)

        self.library.FlowEngine_Process.restype = None
        self.library.FlowEngine_Process.argtypes = [ctypes.c_void_p, audioBuffer, audioBuffer, ctypes.c_int]
        self.library.FlowEngine_Process(instance, xpp, ypp, ctypes.c_int(self.frameSize))

        return output
