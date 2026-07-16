from flowstudio.flow_conf import *
from flowstudio.flow_conf_co import SocketType
from flowstudio.flow_node_base import *

@register_node(OP_NODE_BEAMFORMING_2ch)
class FLOW_Node_BEAMFORMING_2ch(FLOW_Node):
    #icon = "icons/in.png"
    op_code = OP_NODE_BEAMFORMING_2ch
    op_title = "BEAMFORMING_2ch"
    content_label_objname = "BEAMFORMING_2ch"
    display_name = '2 Mic Beamforming'
    info = 'Beamforming process according DOA can implement various functionalities implemented including but not limited to localizing and tracking the sound sources, extracting the signal of interest, suppressing ambient noise, and separating different sound sources.'
    expandable = True
    openable = True

    linkType = 1
    def __init__(self, scene):
        self.inctrls = [SocketType.FLOAT.value]
        super().__init__(scene, inputs=[1, 1], outputs=[1, 1], inctrls=self.inctrls)
        self.initControl()
        self.eval()
