from flowstudio.flow_conf import *
from flowstudio.flow_node_base import *

@register_node(OP_NODE_WAVPLAYER)
class FLOW_Node_WAVPLAYER(FLOW_Node):
    #icon = "icons/in.png"
    op_code = OP_NODE_WAVPLAYER
    op_title = "WAVPLAYER"
    content_label_objname = "WAVPLAYER"
    display_name = 'Wav Player'
    info = '"WAVPLAYER" object can provide maximum 8 output from wav file. It is super useful when user need to play some test tone, test music for some custom operation.'
    expandable = True


    def __init__(self, scene):
        super().__init__(scene, inputs=[], outputs=[1, 1, 1, 1, 1, 1, 1, 1])

        self.eval()
        self.initControl()


    def tweaker(self, key):

        Parameter_Value = self.manager.widgetSet[key].widget_value
        AO_Name = self.content_label_objname + "_" + str(self.designator)
        # if DEBUG_Tweaker: print(" _> %s control command: %s" % (self.__class__.__name__, cmd))

        if self.cSocket.connection:
            while self.cSocket.mainSocket.isRunning():
                time.sleep(0.01)
            if not self.cSocket.mainSocket.isRunning():
                if key == 'Path':
                    cmd = "setStringCoord:#%s:#%s:#%s:#0:#0:#" % (AO_Name, key, Parameter_Value)

                elif key == 'Gain':
                    cmd = "setCoord/%s/%s/%s/0/0/" % (AO_Name, key, Parameter_Value)

                if Debug.DEBUG_TWEAKER.value: print(" _> %s control command: %s" % (self.__class__.__name__, cmd))

                # send param commands to Engine
                self.cSocket.mainSocket.setQueryTask(cmd, 16)
                self.cSocket.mainSocket.start()

                # get wav file info from Engine
                if key == 'Path':
                    cmdInfo = "getStringCoord:#%s:#%s:#0:#0:#" % (AO_Name, 'Info')
                    if Debug.DEBUG_TWEAKER.value: print(" _> %s control command: %s" % (self.__class__.__name__, cmdInfo))
                    self.client = self.cSocket.createClient()
                    self.client.login()
                    self.client.setQueryTask(cmdInfo, 64)
                    self.client.start()
                    self.client.wait(50)
                    if self.client.result[0] == True:
                        # print(self.client.result[1])
                        info = (self.client.result[1].decode().rstrip('\n\x00').split(','))
                        # print(info)

                        if info[0] == 'unsupported format':
                            fmt = info[0]
                            ch = ''
                            fs = ''
                        else:
                            fmt = info[0] + ', '
                            if info[1] == ' 1':
                                ch = 'mono, '
                            elif info[1] == ' 2':
                                ch = 'stereo, '
                            else:
                                ch = info[1] + 'ch, '

                            fs = str(float(info[2])/1000) + 'kHz'
                        newInfo = fmt+ch+fs
                        # print(newInfo)
                        self.manager.widgetSet['Info'].label.setText(str(newInfo))
                    self.client.terminate()
                    self.client.wait(50)
                    self.client.logout(index=1)

                if Debug.DEBUG_TWEAKER.value: print(" _> %s thread process: success" % (self.__class__.__name__))
            else:
                if Debug.DEBUG_TWEAKER.value: print(" _> %s thread process: failed" % (self.__class__.__name__))



