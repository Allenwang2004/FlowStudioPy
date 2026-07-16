from flowstudio.flow_conf import TypeAOAddition
from flowstudio.flow_conf_co import OP_NODE_CO_METER, register_node_co, SocketType
from flowstudio.flow_node_base import FLOW_Node


@register_node_co(OP_NODE_CO_METER)
class FLOW_Node_METER(FLOW_Node):
    #icon = "icons/in.png"
    op_code = OP_NODE_CO_METER
    op_title = "CO_METER"
    content_label_objname = "CO_METER"
    display_name = 'Meter'
    node_type = 'CO'
    info = "Used for debug/visualization (analog to AO block)"
    type_ao_addition = TypeAOAddition.DYNAMIC_SOCKET_TYPE_AND_SOCKET_NUM.value

    def __init__(self, scene, socket_type, num):
        self.inputs = []
        for i in range(int(num)):
            self.inputs.append(socket_type)
        super().__init__(scene, inctrls=self.inputs, outctrls=[])
        self.eval()

    def onControlChanged(self, socket_type, value):
        if socket_type == SocketType.BOOL.value:
            self.manager.widgetSet['value'].widget_value = value == 1
        else:
            self.manager.widgetSet['value'].widget_value = value
