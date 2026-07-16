from flowstudio.flow_conf import *
from flowstudio.flow_node_base import *


@register_node(OP_NODE_MIXER8)
class FLOW_Node_MIXER8(FLOW_Node):
    # icon = "icons/in.png"
    op_code = OP_NODE_MIXER8
    op_title = "MIXER8"
    content_label_objname = "MIXER8"
    expandable = False
    expand = True
    DEBUG_Tweaker = False

    def __init__(self, scene):
        super().__init__(scene, inputs=[1, 1, 1, 1, 1, 1, 1, 1], outputs=[1])
        self.initControl()
        self.eval()

    def tweaker(self, key):
        AO_Name = self.content_label_objname + "_" + str(self.designator)
        Parameter_Name = key[0:-2]
        Parameter_Value = self.manager.widgetSet[key].widget_value
        Parameter_Index = int(key[-1])

        cmd = "setCoord/%s/%s/%s/%s/0" % (AO_Name, Parameter_Name, Parameter_Value, Parameter_Index)

        if Debug.DEBUG_TWEAKER.value: print(" _> %s control command: %s" % (self.__class__.__name__, cmd))

        if self.cSocket.connection:
            if not self.cSocket.mainSocket.isRunning():
                self.cSocket.mainSocket.setQueryTask(cmd, 16)
                self.cSocket.mainSocket.start()
                if Debug.DEBUG_TWEAKER.value: print(" _> %s thread process: success" % (self.__class__.__name__))
            else:
                if Debug.DEBUG_TWEAKER.value: print(" _> %s thread process: failed" % (self.__class__.__name__))