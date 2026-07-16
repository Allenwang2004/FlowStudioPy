import os
import ctypes as ct
from typing import Tuple

class TestEngine():

    def __init__(self, path_to_dll):
        self.TestEngineDLL = None
        try:
            full_path = os.path.realpath(path_to_dll)
            if full_path.strip().lower().endswith('.dll'):
                path_to_dll = os.path.dirname(full_path) + '\\'  # Extract directory from DLL name
                
            if not path_to_dll.endswith('\\'):
                path_to_dll += '\\'

            if not path_to_dll + ';' in os.environ['PATH']: # add this to the path if not already present
                os.environ['PATH'] = path_to_dll + ';' + os.environ['PATH']

            self.TestEngineDLL = ct.windll.LoadLibrary(path_to_dll + 'TestEngine')
        except Exception as e:
            print("Cannot load TestEngine.dll from " + path_to_dll)
            if ct.sizeof(ct.c_void_p) == 8:
                print("Check that the DLL is present and 64 bit.\n"
                      "64 bit Python can only be used with 64 bit DLL")
            else:
                print("Check that the DLL is present and 32 bit\n"
                      "32 bit Python can only be used with 32 bit DLL")
            raise e
    # end __init__


    def openTestEngine(self, transport: int, transportDevice: str, dataRate: int, retryTimeOut: int, usbTimeOut: int) -> int:
        """Function TestEngine::openTestEngine() wrapper for openTestEngine in TestEngine DLL.

                        Python API:
                            openTestEngine(transport: int, transportDevice: str, dataRate: int, retryTimeOut: int, usbTimeOut: int) -> int

                        Python Example Call Syntax:
                            retval = myDll.openTestEngine(transport=0, transportDevice='abc', dataRate=0, retryTimeOut=0, usbTimeOut=0)
                            print(retval)

                        Detail From Wrapped C API:
                            Function :      uint32 openTestEngine(int32 transport,
                                                                  const char* transportDevice,
                                                                  uint32 dataRate, int32 retryTimeOut,
                                                                  int32 usbTimeOut)

                            Parameters :    transport -
                                                Defines the protocol to be used when setting up the
                                                communication with the device, where:
                                                <table>
                                                    <tr><td>BCSP = 1
                                                    <tr><td>USB = 2
                                                    <tr><td>H4 = 4
                                                    <tr><td>H5 = 8
                                                    <tr><td>H4DS = 16
                                                    <tr><td>PTAP = 64
                                                    <tr><td>TRB = 128
                                                    <tr><td>USBDBG = 256
                                                    <tr><td>COMDBG = 512
                                                </table>

                                            transportDevice -
                                                Defines the physical port to use. A string which defines which
                                                port is used, e.g. "\\.\COMn" where 'n' is the number of the
                                                COM port. USB device names take the form "\\.\CSRn".
                                                <p>
                                                NOTE: In C/C++, and possibly some other languages, literal '\'
                                                characters are written as "\\", otherwise they are interpreted
                                                as the start of an escape sequence. So for these languages,
                                                the literal string "\\.\COMn" is written as "\\\\.\\COMn" in
                                                the code. The prefix can be dropped for COM ports 1 to 9, i.e.
                                                "COM1" works the same as "\\\\.\\COM1". If using PTAP then
                                                this is the HifId followed by an optional COM port name if
                                                connecting via UART (i.e. "0:\\.\COM1").
                                                <p>
                                                For TRB, the serial number of the usb2trb converter e.g.
                                                "123456" may be used. For USBDBG, the port identifier of the
                                                corresponding USB Hub Filter (e.g. "100") may be used. For
                                                COMDBG, the COM port identifier may be used (e.g., "COM10",
                                                note, no "\\.\" or other prefix is required).
                                                Alternatively, a sequence number ranging from 1 to the number
                                                of connected devices may be used for TRB, USBDBG and COMDBG.
                                                For further details of TRB, USBDBG and COMDBG device
                                                identifiers, refer to the BlueSuite User Guide.

                                            dataRate -
                                                Defines the baud rate to be used (for UART connections only).
                                                This does not apply for COMDBG (UART) connections, for which
                                                the rate is automatically selected.

                                            retryTimeOut -
                                                Defines how long the function will retry, in ms, when trying
                                                to establish communication with the device. Care should be
                                                taken when selecting an appropriate retry timeout. BlueCore1
                                                and BlueCore2 running early firmware versions require a longer
                                                timeout. 5000ms should be enough to pick up these early
                                                devices but this value will make openTestEngine unresponsive.
                                                It would be better to set this parameter to 1000ms and call
                                                openTestEngine up to 5 times or until it passes.

                                            usbTimeout -
                                                Where transport = USB or USBDBG, this parameter will define how
                                                long the function will retry, in ms, when trying to detect if
                                                the specified USB device has enumerated. It has been found that
                                                some PC's take a longer time than expected to enumerate a USB
                                                device and, in some cases, the PC's internal USB hub may have
                                                been reset which can cause a further delay in enumeration.
                                                This parameter can be set to accommodate the extra time taken
                                                to reset USB devices. If USB is not used then this value can
                                                be set to 0.

                            Returns :       This function will return TE_INVALID_HANDLE_VALUE on failure or an
                                            unsigned integer which defines the handle used as a parameter for
                                            all other function calls.

                            Description :   One of the openTestEngine* set of functions has to be called
                                            before any communication with the device can begin.
                                            <p>
                                            This function opens a connection using a host transport protocol
                                            running over USB or a UART, or debug transport running over TRB,
                                            USBDBG, or COMDBG. To open a debug connection with a device which
                                            is not transport-locked, use openTestEngineDebug or
                                            openTestEngineDebugTrans. To open a debug connection with a device
                                            which is transport-locked, use openTestEngineDebugUnlock or
                                            openTestEngineDebugUnlockTrans.

                            Example :

                                uint32 teHandle = TE_INVALID_HANDLE_VALUE;
                                uint32 timeoutMs = 0;

                                do
                                {
                                    cout << "Trying to connect..." << endl;
                                    teHandle = openTestEngine(BCSP, "COM1", 115200, 1000, 0);
                                    timeoutMs += 1000;
                                } while (teHandle == TE_INVALID_HANDLE_VALUE && timeoutMs < MAX_TIMEOUT_MS);

                                if (teHandle != TE_INVALID_HANDLE_VALUE)
                                {
                                    cout << "Connected!" << endl;

                                    // Perform all your testing here

                                    closeTestEngine(teHandle);
                                }

        """
        self.TestEngineDLL.openTestEngine.restype = ct.c_uint32
        self.TestEngineDLL.openTestEngine.argtypes = [ct.c_int32, ct.c_char_p, ct.c_uint32, ct.c_int32, ct.c_int32]
        local_transportDevice = None if transportDevice is None else ct.create_string_buffer(bytes(transportDevice, encoding="UTF-8"))
        retval = self.TestEngineDLL.openTestEngine(transport, local_transportDevice, dataRate, retryTimeOut, usbTimeOut)
        
        return retval
    # end of openTestEngine


    def openTestEngineUnlock(self, transport: int, transportDevice: str, retryTimeOut: int, usbTimeOut: int, unlockKey: str) -> int:
        self.TestEngineDLL.openTestEngineUnlock.restype = ct.c_uint32
        self.TestEngineDLL.openTestEngineUnlock.argtypes = [ct.c_int32, ct.c_char_p, ct.c_int32, ct.c_int32, ct.c_char_p]
        local_transportDevice = None if transportDevice is None else ct.create_string_buffer(bytes(transportDevice, encoding="UTF-8"))
        local_unlockKey = None if unlockKey is None else ct.create_string_buffer(bytes(unlockKey, encoding="UTF-8"))
        retval = self.TestEngineDLL.openTestEngineUnlock(transport, local_transportDevice, retryTimeOut, usbTimeOut, local_unlockKey)
        
        return retval
    # end of openTestEngineUnlock


    def openTestEngineDebug(self, port: int, multi: int, transport: int) -> int:
        self.TestEngineDLL.openTestEngineDebug.restype = ct.c_uint32
        self.TestEngineDLL.openTestEngineDebug.argtypes = [ct.c_int32, ct.c_int32, ct.c_int32]
        
        retval = self.TestEngineDLL.openTestEngineDebug(port, multi, transport)
        
        return retval
    # end of openTestEngineDebug


    def openTestEngineDebugUnlock(self, port: int, multi: int, transport: int, unlockKey: str) -> int:
        self.TestEngineDLL.openTestEngineDebugUnlock.restype = ct.c_uint32
        self.TestEngineDLL.openTestEngineDebugUnlock.argtypes = [ct.c_int32, ct.c_int32, ct.c_int32, ct.c_char_p]
        local_unlockKey = None if unlockKey is None else ct.create_string_buffer(bytes(unlockKey, encoding="UTF-8"))
        retval = self.TestEngineDLL.openTestEngineDebugUnlock(port, multi, transport, local_unlockKey)
        
        return retval
    # end of openTestEngineDebugUnlock


    def openTestEngineDebugTrans(self, trans: str, multi: int) -> int:
        self.TestEngineDLL.openTestEngineDebugTrans.restype = ct.c_uint32
        self.TestEngineDLL.openTestEngineDebugTrans.argtypes = [ct.c_char_p, ct.c_int32]
        local_trans = None if trans is None else ct.create_string_buffer(bytes(trans, encoding="UTF-8"))
        retval = self.TestEngineDLL.openTestEngineDebugTrans(local_trans, multi)
        
        return retval
    # end of openTestEngineDebugTrans


    def openTestEngineDebugUnlockTrans(self, trans: str, multi: int, unlockKey: str) -> int:
        self.TestEngineDLL.openTestEngineDebugUnlockTrans.restype = ct.c_uint32
        self.TestEngineDLL.openTestEngineDebugUnlockTrans.argtypes = [ct.c_char_p, ct.c_int32, ct.c_char_p]
        local_trans = None if trans is None else ct.create_string_buffer(bytes(trans, encoding="UTF-8"))
        local_unlockKey = None if unlockKey is None else ct.create_string_buffer(bytes(unlockKey, encoding="UTF-8"))
        retval = self.TestEngineDLL.openTestEngineDebugUnlockTrans(local_trans, multi, local_unlockKey)
        
        return retval
    # end of openTestEngineDebugUnlockTrans


    def closeTestEngine(self, handle: int) -> int:
        self.TestEngineDLL.closeTestEngine.restype = ct.c_int32
        self.TestEngineDLL.closeTestEngine.argtypes = [ct.c_uint32]
        
        retval = self.TestEngineDLL.closeTestEngine(handle)
        
        return retval
    # end of closeTestEngine


    def closeTestEngineEx(self, handle: int, options: int) -> int:
        self.TestEngineDLL.closeTestEngineEx.restype = ct.c_int32
        self.TestEngineDLL.closeTestEngineEx.argtypes = [ct.c_uint32, ct.c_uint16]
        
        retval = self.TestEngineDLL.closeTestEngineEx(handle, options)
        
        return retval
    # end of closeTestEngineEx


    def teGetLastError(self, handle: int) -> int:
        self.TestEngineDLL.teGetLastError.restype = ct.c_uint32
        self.TestEngineDLL.teGetLastError.argtypes = [ct.c_uint32]
        
        retval = self.TestEngineDLL.teGetLastError(handle)
        
        return retval
    # end of teGetLastError



    def teGetAvailableDebugPorts(self, maxLen: int=0, ports: str='', trans: str='', count: int=0) -> Tuple[int, int, str, str, int]:
        self.TestEngineDLL.teGetAvailableDebugPorts.restype = ct.c_int32
        self.TestEngineDLL.teGetAvailableDebugPorts.argtypes = [ct.c_void_p, ct.c_char_p, ct.c_char_p, ct.c_void_p]
        local_maxLen = ct.c_uint16(maxLen)
        local_ports = None if ports is None else ct.create_string_buffer(bytes(ports, encoding="UTF-8"), 1024 if maxLen < 1024 else maxLen)
        local_trans = None if trans is None else ct.create_string_buffer(bytes(trans, encoding="UTF-8"), 1024 if maxLen < 1024 else maxLen)
        local_count = ct.c_uint16(count)
        retval = self.TestEngineDLL.teGetAvailableDebugPorts(ct.byref(local_maxLen), local_ports, local_trans, ct.byref(local_count))
        maxLen = local_maxLen.value
        ports = local_ports.value.decode()
        trans = local_trans.value.decode()
        count = local_count.value
        return retval, maxLen, ports, trans, count
    # end of teGetAvailableDebugPorts


    def teGetAvailableDebugPortsEx(self, criteria: int, maxLen: int=0, ports: str='', trans: str='', count: int=0) -> Tuple[int, int, str, str, int]:
        self.TestEngineDLL.teGetAvailableDebugPortsEx.restype = ct.c_int32
        self.TestEngineDLL.teGetAvailableDebugPortsEx.argtypes = [ct.c_uint32, ct.c_void_p, ct.c_char_p, ct.c_char_p, ct.c_void_p]
        local_maxLen = ct.c_uint16(maxLen)
        local_ports = None if ports is None else ct.create_string_buffer(bytes(ports, encoding="UTF-8"), 1024 if maxLen < 1024 else maxLen)
        local_trans = None if trans is None else ct.create_string_buffer(bytes(trans, encoding="UTF-8"), 1024 if maxLen < 1024 else maxLen)
        local_count = ct.c_uint16(count)
        retval = self.TestEngineDLL.teGetAvailableDebugPortsEx(criteria, ct.byref(local_maxLen), local_ports, local_trans, ct.byref(local_count))
        maxLen = local_maxLen.value
        ports = local_ports.value.decode()
        trans = local_trans.value.decode()
        count = local_count.value
        return retval, maxLen, ports, trans, count
    # end of teGetAvailableDebugPortsEx




    def teAppDisable(self, handle: int, reserved: int) -> int:
        self.TestEngineDLL.teAppDisable.restype = ct.c_int32
        self.TestEngineDLL.teAppDisable.argtypes = [ct.c_uint32, ct.c_uint16]
        
        retval = self.TestEngineDLL.teAppDisable(handle, reserved)
        
        return retval
    # end of teAppDisable

    def teAppWrite(self, handle: int, channel: int, data: list, length: int) -> int:
        r"""Function TestEngine::teAppWrite() wrapper for teAppWrite in TestEngine DLL.

        Python API:
            teAppWrite(handle: int, channel: int, data: list, length: int) -> int

        Python Example Call Syntax:
            retval = myDll.teAppWrite(handle=0, channel=0, data=[0,1], length=0)
            print(retval)

        Detail From Wrapped C API:
            Function :      int32 teAppWrite(uint32 handle, uint8 channel, const uint16* data,
                                             uint16 length)

            Parameters :    handle -
                                Handle to the device.

                            channel -
                                The channel number for the message (0...127).

                            data -
                                A pointer to an array of 16-bit unsigned integers containing
                                the message payload.

                            length -
                                The number of words to send. Must be non-zero and no larger
                                than the size of the data array. The maximum data length
                                which can be successfully sent is device dependent.

            Returns :       <table>
                                <tr><td>-1 = Invalid handle
                                <tr><td>0 = Error
                                <tr><td>1 = Success
                                <tr><td>2 = Unsupported function
                            </table>

            Description :   This function is used to write a message to an application
                            running on CSRA681xx and later ICs.
                            <p>
                            This function is not supported for BlueCore ICs - use vmWrite
                            instead.

            Example :

                cout << "Trying to connect..." << endl;
                uint32 teHandle = openTestEngine(TRB, "1", 0, 5000, 0);

                if (teHandle != TE_INVALID_HANDLE_VALUE)
                {
                    cout << "Connected!" << endl;

                    // Write a message
                    static const uint16 MSG_LEN = 3;
                    uint16 txData[MSG_LEN] = { 1, 2, 3 };
                    int32 teRet = teAppWrite(teHandle, 0, txData, MSG_LEN);
                    if (teRet == TE_OK)
                    {
                        cout << "Message sent to application" << endl;

                        // Read a message (e.g. response from application to above message)
                        static const uint16 MAX_MSG_LEN = 80;
                        uint16 rxData[MAX_MSG_LEN];
                        uint8 channel;
                        uint16 readLength;
                        teRet = teAppRead(teHandle, &channel, rxData, MAX_MSG_LEN, &readLength, 1000);
                        if (teRet == TE_OK)
                        {
                            cout << "Message received from application on channel "
                                 << static_cast<uint16>(channel) << ":" << endl;
                            for (uint16 i = 0; i < readLength; ++i)
                            {
                                cout << rxData[i] << endl;
                            }
                        }
                    }

                    closeTestEngine(teHandle);
                }

        """
        self.TestEngineDLL.teAppWrite.restype = ct.c_int32
        self.TestEngineDLL.teAppWrite.argtypes = [ct.c_uint32, ct.c_uint8, ct.c_void_p, ct.c_uint16]
        if data is None:
            data = []
        local_data = (ct.c_uint16 * len(data))(*data)
        retval = self.TestEngineDLL.teAppWrite(handle, channel, local_data, length)

        return retval

    # end of teAppWrite

    def teAppRead(self, handle: int, channel: int=0, data: list=None, dataLength: int=0, readLength: int=0, timeoutMs: int=0) -> Tuple[int, int, list, int]:
        r"""Function TestEngine::teAppRead() wrapper for teAppRead in TestEngine DLL.

        Python API:
            teAppRead(handle: int, channel: int=0, data: list=None, dataLength: int=0, readLength: int=0, timeoutMs: int=0) -> Tuple[int, int, list, int]

        Python Example Call Syntax:
            retval, channel, data, readLength = myDll.teAppRead(handle=0, data=[0,1], dataLength=0, timeoutMs=0)
            print(retval, channel, data, readLength)

        Detail From Wrapped C API:
            Function :      int32 teAppRead(uint32 handle, uint8* channel, uint16* data,
                                            uint16 dataLength, uint16* readLength,
                                            uint16 timeoutMs)

            Parameters :    handle -
                                Handle to the device.

                            channel -
                                Location where the channel number of the message will be
                                stored.

                            data -
                                A pointer to an array of 16-bit unsigned integers where the
                                message data will be stored.

                            dataLength -
                                The length of the data array. Must be >= 1.

                            readLength -
                                Location where the length of any message read will be stored.
                                If the dataLength indicates that the data array is too small to
                                hold the message data, TE_ERROR will be returned and the value
                                will be set to the length of the message. As much data as
                                possible will be stored in the data array in this case.

                            timeoutMs -
                                A timeout, in milliseconds, of the time to wait for a message.
                                A value of 0 means the function will just poll.

            Returns :       <table>
                                <tr><td>-1 = Invalid handle
                                <tr><td>0 = Error
                                <tr><td>1 = Success
                                <tr><td>2 = Unsupported function
                            </table>

            Description :   This function is used to read any message returned from an
                            application running on CSRA681xx and later ICs.
                            <p>
                            If a message has already been received, it will be returned
                            immediately, otherwise the function will wait for a message until
                            the timeout has expired. If no data has been read within the
                            timeout period, TE_ERROR will be returned and readLength will be
                            set to zero.
                            <p>
                            This function is not supported for BlueCore ICs - use vmRead
                            instead.

            Example:        See example code for teAppWrite.

        """
        self.TestEngineDLL.teAppRead.restype = ct.c_int32
        self.TestEngineDLL.teAppRead.argtypes = [ct.c_uint32, ct.c_void_p, ct.c_void_p, ct.c_uint16, ct.c_void_p, ct.c_uint16]
        local_channel = ct.c_uint8(channel)
        if data is None:
            data = []
        local_data = (ct.c_uint16 * max(dataLength, len(data)))(*data)
        local_readLength = ct.c_uint16(readLength)
        retval = self.TestEngineDLL.teAppRead(handle, ct.byref(local_channel), local_data, dataLength, ct.byref(local_readLength), timeoutMs)
        channel = local_channel.value
        data = local_data[:]
        readLength = local_readLength.value
        return retval, channel, data, readLength
    # end of teAppRead
    def teAudioOperatorMessage(self, handle: int, operatorId: int, message: list, messageLength: int) -> int:
        r"""Function TestEngine::teAudioOperatorMessage() wrapper for teAudioOperatorMessage in TestEngine DLL.

        Python API:
            teAudioOperatorMessage(handle: int, operatorId: int, message: list, messageLength: int) -> int

        Python Example Call Syntax:
            retval = myDll.teAudioOperatorMessage(handle=0, operatorId=0, message=[0,1], messageLength=0)
            print(retval)

        Detail From Wrapped C API:
            Function :      int32 teAudioOperatorMessage(uint32 handle, uint16 operatorId,
                                                         const uint16* message,
                                                         uint16 messageLength)

            Parameters :    handle -
                                Handle to the device.

                            operatorId -
                                Operator ID.

                            message -
                                Array of uint16 values forming the operator message.

                            messageLength -
                                Length of the message array (number of uint16s).

            Returns :       <table>
                                <tr><td>-1 = Invalid handle
                                <tr><td>0 = Error
                                <tr><td>1 = Success
                                <tr><td>2 = Unsupported function
                            </table>

            Description :   This function is used to send a message to an operator created
                            using teAudioCreateOperator.
                            <p>
                            This function is unsupported for BlueCore and CSRC9xxx ICs.
                            <p>
                            For further details of supported operator messages, please see the
                            Kymera Capability Library User Guide documentation relevant to the
                            ADK used to build the IC application firmware (see Operator
                            Messages).

            Example:        See example code for teAudioStartOperators.

        """
        self.TestEngineDLL.teAudioOperatorMessage.restype = ct.c_int32
        self.TestEngineDLL.teAudioOperatorMessage.argtypes = [ct.c_uint32, ct.c_uint16, ct.c_void_p, ct.c_uint16]
        if message is None:
            message = []
        local_message = (ct.c_uint16 * len(message))(*message)
        retval = self.TestEngineDLL.teAudioOperatorMessage(handle, operatorId, local_message, messageLength)

        return retval
    # end of teAudioOperatorMessage

# endclass TestEngine
