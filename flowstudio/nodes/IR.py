from flowstudio.flow_conf import *
from flowstudio.flow_node_base import *
import wavio

@register_node(OP_NODE_IR)
class FLOW_Node_IR(FLOW_Node):
    #icon = "icons/in.png"
    op_code = OP_NODE_IR
    op_title = "IR"
    content_label_objname = "IR"
    display_name = 'IR convolver'
    info = 'Fast impulse response convolver with low latency feature, it is idea for application like speaker cabinet modeling. With faster processor and larger memory, it could use as a convolutional reverb with large amount and long impulse response to simulate the real world acoustical space.'
    expandable = True
    # openable = True

    def __init__(self, scene):
        super().__init__(scene, inputs=[1], outputs=[1])
        self.flen = 1
        self.initControl()
        self.eval()

    def initInnerClasses(self):
        self.manager = FLOW_Ctrl_Manager(self.content_label_objname)
        self.content = FLOW_Content(self)
        self.grNode = FLOW_GraphicsNode(self)
        self.widget = FLOW_GUI(self)

    def initControl(self):
        for key in self.manager.widgetSet:
            self.manager.widgetSet[key].valueChanged.connect(partial(self.tweaker, key))

    @property
    def flen(self):
        return self._flen

    @flen.setter
    def flen(self, input_data: str):
        self._flen = self.fname2flen(input_data)

    def fname2flen(self, fname):
        try:
            file = wavio.read(fname)
            return len(file.data)
        except Exception as e:
            if DEBUG: dumpException(e)
            return 1

    def serialize(self):
        res = super().serialize()

        self.flen = self.manager.widgetSet['path'].widget_value
        res['content']['ntaps'] = self.flen

        return res
    
    def sendCmd(self, cmd):
        if self.cSocket.connection:
            if not self.cSocket.mainSocket.isRunning():
                self.cSocket.mainSocket.setQueryTask(cmd, 16)
                self.cSocket.mainSocket.start()
                if Debug.DEBUG_THREAD.value: print(" _> %s thread process: success" % (self.__class__.__name__))
            else:
                if Debug.DEBUG_THREAD.value: print(" _> %s thread process: failed" % (self.__class__.__name__))

    def tweaker(self, key):
        Parameter_Value = self.manager.widgetSet[key].widget_value
        AO_Name = self.content_label_objname + "_" + str(self.designator)
        if key == "path":
            cmd = "setStringCoord:#%s:#%s:#%s:#0:#0:#" % (AO_Name, "path", Parameter_Value)
            self.sendCmd(cmd)
            cmd = "set/%s/ntaps/%s/" % (AO_Name, str(self.flen))
            self.sendCmd(cmd)
        elif key == "gain":
            cmd = "set/%s/gain/%s/" % (AO_Name, Parameter_Value)
            self.sendCmd(cmd)

        if Debug.DEBUG_TWEAKER.value: print(" _> %s control command: %s" % (self.__class__.__name__, cmd))