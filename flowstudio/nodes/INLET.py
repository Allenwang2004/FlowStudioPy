from flowstudio.flow_conf import *
from flowstudio.flow_node_base import *

@register_node(OP_NODE_INLET)
class FLOW_Node_INLET(FLOW_Node):
    #icon = "icons/in.png"
    op_code = OP_NODE_INLET
    op_title = "INLET"
    content_label_objname = "INLET"

    def __init__(self, scene):
        super().__init__(scene, inputs=[], outputs=[1], rule_check_mode=-2)
        self.eval()

    def evalImplementation(self):
        hasValidOutput = self.dynamicRuleCheck(self.rule_check_mode, self.outputs)
        hasOUTLET = False
        if self.outputs[0].hasAnyEdge():
            start_node = self.outputs[0].edges[0].start_socket.node
            end_node = self.outputs[0].edges[0].end_socket.node
            start_node_label = start_node.content_label_objname
            end_node_label = end_node.content_label_objname
            if start_node_label == 'INLET' and end_node_label == 'OUTLET':
                # 讓INLET可以直接連OUTLET
                hasOUTLET = False
            elif start_node_label == 'OUTLET' and end_node_label == 'INLET':
                hasOUTLET = True
            else:
                hasOUTLET = False

        res = hasValidOutput and (not hasOUTLET)
        if res:
            self.grNode.setToolTip("")
            self.markInvalid(False)
            self.markDirty(False)
        else:
            self.markDirty()

    def initSettings(self):
        super().initSettings()
        self.input_multi_edged = False
        self.output_multi_edged = True