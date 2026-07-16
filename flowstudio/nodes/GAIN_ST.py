from flowstudio.flow_conf import *
from flowstudio.flow_node_base import *

@register_node(OP_NODE_GAIN_ST)
class FLOW_Node_GAIN_ST(FLOW_Node):
    #icon = "icons/in.png"
    op_code = OP_NODE_GAIN_ST
    op_title = "GAIN_ST"
    content_label_objname = "GAIN_ST"
    expandable = True

    def __init__(self, scene):
        super().__init__(scene, inputs=[1, 1], outputs=[1, 1], rule_check_mode=-2)
        self.initControl()
        self.eval()

    def initInnerClasses(self):
        self.manager = FLOW_Ctrl_Manager(self.content_label_objname)
        self.content = FLOW_Content(self)
        self.grNode = FLOW_GraphicsNode(self)

    def tweaker(self, key):
        AO_Name = self.content_label_objname + "_" + str(self.designator)
        Parameter_Name = key
        Parameter_Value = self.manager.widgetSet[key].widget_value[1] if isinstance(self.manager.widgetSet[key].widget_value, list) else self.manager.widgetSet[key].widget_value

        cmd_left = "setCoord/%s/%s/%s/0/0" % (AO_Name, Parameter_Name, Parameter_Value)
        cmd_right = "setCoord/%s/%s/%s/0/1" % (AO_Name, Parameter_Name, Parameter_Value)

        if self.cSocket.connection:
            while self.cSocket.mainSocket.isRunning():
                time.sleep(0.01)
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

