from nodeeditor.node_socket import *
from nodeeditor.node_node import Node

from flowstudio.flow_graphics_socket import FLOW_Graphics_Socket


class FLOW_Socket(Socket):

    Socket_GR_Class = FLOW_Graphics_Socket

    def __init__(self, node:'Node', index:int=0, position:int=LEFT_TOP, socket_type:int=1, multi_edges:bool=True, count_on_this_node_side:int=1, is_input:bool=False):
        super().__init__(node, index, position, socket_type, multi_edges, count_on_this_node_side, is_input)
