from nodeeditor.node_graphics_socket import QDMGraphicsSocket
from nodeeditor.node_socket import Socket

class FLOW_Graphics_Socket(QDMGraphicsSocket):

    def __init__(self, socket:'Socket'):
        super().__init__(socket)

        self.radius = 7.0
        self.outline_width = 3.0