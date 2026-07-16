import xmltodict
import sounddevice as sd
import numpy as np
from PyQt5.QtCore import QThread, pyqtSignal
import time
DEBUG = False

# standard_sample_rates = ['8000', '9600', '11025', '12000',
#                          '16000', '22050', '24000', '32000',
#                          '44100', '48000', '88200', '96000',
#                          '192000']

standard_sample_rates = ['16000', '44100', '48000', '88200', '96000', '192000']
from collections import OrderedDict

class DevicesOrderedDict(OrderedDict):
    def __missing__(self, key):
        self[key] = type(self)()
        return self[key]

class AudioEnviroment(object):

    def __init__(self):
        self.initData()

    def initData(self):

        self.hostapiInfo = sd.query_hostapis()
        self.inputDevicesMap = dict()
        self.outputDevicesMap = dict()

        self.hostapiCount = len(self.hostapiInfo)
        for i in range(self.hostapiCount):
            # print(self.hostapiInfo[i])
            if self.hostapiInfo[i]['name'] == 'MME':
                self.MMEdevicesIdx = self.hostapiInfo[i]['devices']
                self.defaultInputMME = self.hostapiInfo[i]['default_input_device']
                self.defaultOutputMME = self.hostapiInfo[i]['default_output_device']
            elif self.hostapiInfo[i]['name'] == 'Windows WASAPI':
                self.WASAPIdevicesIdx = self.hostapiInfo[i]['devices']
                self.defaultInputWASAPI = self.hostapiInfo[i]['default_input_device']
                self.defaultOutputWASAPI  = self.hostapiInfo[i]['default_output_device']

            elif self.hostapiInfo[i]['name'] == 'ASIO':
                self.ASIOdevicesIdx = self.hostapiInfo[i]['devices']
                self.defaultInputASIO = self.hostapiInfo[i]['default_input_device']
                self.defaultOutputASIO = self.hostapiInfo[i]['default_output_device']

        # path = "../bin/audio_interface.flw"
        # with open(path, 'r', encoding='unicode_escape') as file:
        #     self.data = xmltodict.parse(file.read())
        #     self.hasDuplex = True if self.data['root']['Duplex'] else False
        #     self.hasInputs = True if self.data['root']['Inputs'] else False
        #     self.hasOutputs = True if self.data['root']['Outputs'] else False

    def defaultInput(self):

        return sd.default.device[0]

    def defaultOutput(self):
        return sd.default.device[1]

    # def defaultDriver(self):
    #     drivers = self.data['root']['Driver']
    #
    #     for key in drivers.keys():
    #         if drivers[key]['@isDefault'] == 'true':
    #             return (key[12:], key)
    #
    # def driverCount(self):
    #     return len(self.data['root']['Driver'])

    def driverList(self):
        res = []
        for i in range(self.hostapiCount):
            # print(self.hostapiInfo[i])
            if self.hostapiInfo[i]['name'] == 'MME':
                res.append('MME')
            elif self.hostapiInfo[i]['name'] == 'Windows WASAPI':
                res.append('Windows WASAPI')
            elif self.hostapiInfo[i]['name'] == 'ASIO':
                res.append('ASIO')
        # print("driver list: ", res)
        return res

    def inputList(self, api_index: str = '0'):
        res = []
        # print(api_index)
        # InputDevices = DevicesOrderedDict()
        if api_index == '0':
            for i in self.MMEdevicesIdx:
                try:
                    d = sd.query_devices(i, 'input')
                    res.append(d['name'])
                    self.inputDevicesMap[d['name']] = str(i)
                except:
                    None
        elif api_index == '1':
            for i in self.ASIOdevicesIdx:
                try:
                    d = sd.query_devices(i, 'input')
                    res.append(d['name'])
                    self.inputDevicesMap[d['name']] = str(i)
                except:
                    None
        elif api_index == '2':
            for i in self.WASAPIdevicesIdx:
                try:
                    d = sd.query_devices(i, 'input')
                    res.append(d['name'])
                    self.inputDevicesMap[d['name']] = str(i)
                except:
                    None
        # print(self.inputDevicesMap)
        return res

    def outputList(self, api_index: str = '0'):
        res = []
        if api_index == '0':
            for i in self.MMEdevicesIdx:
                try:
                    d = sd.query_devices(i, 'output')
                    res.append(d['name'])
                    self.outputDevicesMap[d['name']] = str(i)
                except:
                    None
        elif api_index == '1':
            for i in self.ASIOdevicesIdx:
                try:
                    d = sd.query_devices(i, 'output')
                    res.append(d['name'])
                    self.outputDevicesMap[d['name']] = str(i)
                except:
                    None
        elif api_index == '2':
            for i in self.WASAPIdevicesIdx:
                try:
                    d = sd.query_devices(i, 'output')
                    res.append(d['name'])
                    self.outputDevicesMap[d['name']] = str(i)
                except:
                    None
        # print(self.outputDevicesMap)
        return res

    def supportedSampleRate(self, inputDevice: str, outputDevice: str):
        # inputs = dict()
        # if self.hasInputs:
        #     inputs.update(self.data['root']['Inputs'])
        # if self.hasDuplex:
        #     inputs.update(self.data['root']['Duplex'])
        #
        # try:
        #     inputSampleRate = inputs[inputDevice]['@sampleRate'].split("/")
        # except Exception as e:
        #     inputSampleRate = standard_sample_rates
        #
        # outputs = dict()
        # if self.hasOutputs:
        #     outputs.update(self.data['root']['Outputs'])
        # if self.hasDuplex:
        #     outputs.update(self.data['root']['Duplex'])
        # try:
        #     outputSampleRate = outputs[outputDevice]['@sampleRate'].split("/")
        #     # print(outputSampleRate)
        # except Exception as e:
        #     outputSampleRate = standard_sample_rates

        inputSampleRate = standard_sample_rates
        outputSampleRate = standard_sample_rates
        res = set(inputSampleRate) & set(outputSampleRate)
        res = list(filter(None, res))
        res.sort(key=int)

        if res:
            return res
        else:
            return None

    def dialogStrToPaIndex(self, inputDeviceName: str, outputDeviceName: str):
        res_input = '0' if inputDeviceName == '' else self.inputDevicesMap[inputDeviceName]
        res_output = '0' if outputDeviceName == '' else self.outputDevicesMap[outputDeviceName]

        return (res_input, res_output)

    def getMaxChannelCount(self, inIdx, outIdx):
        # print(sd.query_devices())
        if self.inputList() == []:
            inChs = 0
        else:
            inDevice = sd.query_devices(int(inIdx), 'input')
            inChs = inDevice["max_input_channels"]

        if self.outputList() == []:
            outChs = 0
        else:
            outDevice = sd.query_devices(int(outIdx), 'output')
            outChs = outDevice["max_output_channels"]

        return inChs, outChs



    def startPaStream(self, engine, instance, paInDeviceIdx, paOutDeviceIdx, Fs, inCount, outCount, frameSize):
        import sounddevice as sd
        def deinterleave(input, framesize, channels):
            out = np.zeros((channels, framesize)).astype(np.float32)
            for ch in range(channels):
                for i in range(framesize):
                    out[ch][i] = input[i][ch]
            return out

        def interleave(input, framesize, channels):
            out = np.zeros((framesize, channels)).astype(np.float32)
            for ch in range(channels):
                for i in range(framesize):
                    out[i][ch] = input[ch][i]
            return out

        def callback(indata, outdata, frames, time, status):
            if status:
                print(status)
            inDeinterleave = deinterleave(indata, frameSize, inCount)

            out = engine.process(instance, inDeinterleave)

            outdata[:] = interleave(out, frameSize, outCount)

        try:

            print('opening Stream....')
            with sd.Stream(device=(paInDeviceIdx, paOutDeviceIdx),
                           samplerate=Fs, blocksize=frameSize,
                           dtype='float32', latency='low',
                           channels=(inCount, outCount), callback=callback):
                print('Starting Stream....')
                # print(sd.query_devices())
                SR = [44100, 48000, 88200, 96000, 192000]
                for rate in SR:
                    print("checking input sample rate: ", rate)
                    try:
                        with sd.check_input_settings(device=paInDeviceIdx, samplerate=rate):
                            print("check_input_settings")
                    except Exception as e:
                        print(e)

                    print("checking output sample rate: ", rate)
                    try:
                        with sd.check_output_settings(device=paOutDeviceIdx, samplerate=rate):
                            print("check_output_settings")
                    except Exception as e:
                        print(e)

                # print('#' * 80)
                # print('press Return to quit')
                # print('#' * 80)
                # input()
        # except KeyboardInterrupt:
        #     exit('')
                while True:
                    sd.sleep(500)
        except Exception as e:
            # exit(type(e).__name__ + ': ' + str(e))
            print(str(e))

