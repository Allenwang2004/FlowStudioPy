from flowstudio.flow_conf import *
from flowstudio.flow_node_base import *

@register_node(OP_NODE_OUTLET)
class FLOW_Node_OUTLET(FLOW_Node):
    #icon = "icons/in.png"
    op_code = OP_NODE_OUTLET
    op_title = "OUTLET"
    content_label_objname = "OUTLET"

    def __init__(self, scene):
        super().__init__(scene, inputs=[1], outputs=[], rule_check_mode=-2)
        self.eval()

    def evalImplementation(self):
        hasValidInput = self.dynamicRuleCheck(self.rule_check_mode, self.inputs)
        hasINLET = False
        if self.inputs[0].hasAnyEdge():
            start_node = self.inputs[0].edges[0].start_socket.node
            end_node = self.inputs[0].edges[0].end_socket.node
            start_node_label = start_node.content_label_objname
            end_node_label = end_node.content_label_objname
            if start_node_label == 'INLET' and end_node_label == 'OUTLET':
                # 讓INLET可以直接連OUTLET
                hasINLET = False
            elif start_node_label == 'OUTLET' and end_node_label == 'INLET':
                hasINLET = True
            else:
                hasINLET = False
        res = hasValidInput and (not hasINLET)
        if res:
            self.grNode.setToolTip("")
            self.markInvalid(False)
            self.markDirty(False)
        else:
            self.markDirty()

    def initSettings(self):
        super().initSettings()
        self.input_multi_edged = False
        self.output_multi_edged = False