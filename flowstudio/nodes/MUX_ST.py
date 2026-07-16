from flowstudio.flow_conf import *
from flowstudio.flow_node_base import *

@register_node(OP_NODE_MUX_ST)
class FLOW_Node_MUX(FLOW_Node):
    #icon = "icons/in.png"
    op_code = OP_NODE_MUX_ST
    op_title = "MUX_ST"
    content_label_objname = "MUX_ST"
    expandable = False
    expand = True

    def __init__(self, scene):
        super().__init__(scene, inputs=[1,1,1,1,1,1,1,1], outputs=[1,1])
        self.initControl()
        self.eval()

    def initSocketTooltip(self):
        for i in range(8):
            self.inputs[i].grSocket.setToolTip("in " + str(i + 1))
        self.outputs[0].grSocket.setToolTip("out 1")
        self.outputs[1].grSocket.setToolTip("out 2")

    def tweaker(self, key):
        AO_Name = self.content_label_objname + "_" + str(self.designator)
        Parameter_Name = key
        Parameter_Value = self.manager.widgetSet[key].widget_value[1] if isinstance(self.manager.widgetSet[key].widget_value, list) else self.manager.widgetSet[key].widget_value
        ch = int(Parameter_Value)
        cmd_left = "setCoord/%s/%s/%s/0/0" % (AO_Name, Parameter_Name, str(2*ch))
        cmd_right = "setCoord/%s/%s/%s/0/1" % (AO_Name, Parameter_Name, str(2*ch + 1))

        if Debug.DEBUG_TWEAKER.value:
            print(" _> %s control left command: %s" % (self.__class__.__name__, cmd_left))
            print(" _> %s control right command: %s" % (self.__class__.__name__, cmd_right))

        if self.cSocket.connection:
            if not self.cSocket.mainSocket.isRunning():
                self.cSocket.mainSocket.setQueryTasks([cmd_left, cmd_right], 32)
                self.cSocket.mainSocket.start()
                # self.cSocket.mainSocket.wait()
                # print(self.cSocket.mainSocket.result)
                if Debug.DEBUG_TWEAKER.value: print(" _> %s thread process: success" % (self.__class__.__name__))
            else:
                if Debug.DEBUG_TWEAKER.value: print(" _> %s thread process: failed" % (self.__class__.__name__))

    def serialize(self):
        res = super().serialize()
        res['content']['ch'] = 2
        return res