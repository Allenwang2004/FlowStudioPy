from flowstudio.flow_conf import *
from flowstudio.flow_conf_co import SocketType
from flowstudio.flow_node_base import *

@register_node(OP_NODE_BEAMFORMING_3ch)
class FLOW_Node_BEAMFORMING_3ch(FLOW_Node):
    #icon = "icons/in.png"
    op_code = OP_NODE_BEAMFORMING_3ch
    op_title = "BEAMFORMING_3ch"
    content_label_objname = "BEAMFORMING_3ch"
    display_name = '3 Mic Beamforming'
    info = 'Beamforming process according DOA can implement various functionalities implemented including but not limited to localizing and tracking the sound sources, extracting the signal of interest, suppressing ambient noise, and separating different sound sources.'
    expandable = True
    openable = True

    linkType = 1
    def __init__(self, scene):
        self.inctrls = [SocketType.FLOAT.value]
        super().__init__(scene, inputs=[1, 1, 1], outputs=[1, 1], inctrls=self.inctrls)
        self.initControl()
        self.eval()
