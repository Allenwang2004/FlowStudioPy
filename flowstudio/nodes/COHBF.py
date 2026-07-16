from flowstudio.flow_conf import *
from flowstudio.flow_node_base import *

@register_node(OP_NODE_COHBF)
class FlowNodeCOHBF(FLOW_Node):
    #icon = "icons/in.png"
    op_code = OP_NODE_COHBF
    op_title = "COHBF"
    content_label_objname = "COHBF"
    display_name = 'Coherence Beamforming'
    info = 'Achieving endfire beamforming effects through microphone correlation, supporting 2-3 microphones. Endfire beamforming can be achieved with 2 microphones, while 3 microphones must be arranged in a triangular configuration, allowing for six directional beams.'
    expandable = True
    openable = True

    linkType = 1
    def __init__(self, scene):
        # self.inctrls = [0]
        super().__init__(scene, inputs=[1, 1], outputs=[1])
        self.initControl()
        self.eval()
