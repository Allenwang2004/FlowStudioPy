import os
import json
from flowstudio.flow_node_base import FLOW_GraphicsNode
from nodeeditor.node_scene import Scene
from nodeeditor.utils import dumpException
from nodeeditor.node_edge import Edge

from flowstudio.flow_scene_clipboard import FLOW_Scene_Clipboard

DEBUG = False

class FLOW_Scene(Scene):

    def __init__(self, is_draw_nothing=False, is_temp=False):
        self.is_draw_nothing = is_draw_nothing
        self.is_temp = is_temp
        self.propertyDockWidget = None
        super().__init__()
        self.clipboard = FLOW_Scene_Clipboard(self)

    def getSelectedItems(self) -> list:
        return super().getSelectedItems()

    def getSelectedNodeItems(self)-> list:
        Items=self.grScene.scene.getSelectedItems()
        grNodeList=list()
        for i in Items:
            if type(i) is FLOW_GraphicsNode:
                grNodeList.append(i)
        return grNodeList

    def getLastSelectedNode(self):
        minimum_select_time_grNode = None
        for i in self.getSelectedNodeItems():
            if minimum_select_time_grNode == None:
                minimum_select_time_grNode = i
            if i.selected_time >= minimum_select_time_grNode.selected_time:
                minimum_select_time_grNode = i
        return minimum_select_time_grNode

    def getOrderSelectedNodes(self):
        order_nodes = self.getSelectedNodeItems().copy()
        for i in range(len(order_nodes) - 1):
            for j in range(len(order_nodes) - 1):
                if j == len(order_nodes) - 1 - i: break
                if order_nodes[j].selected_time >= order_nodes[j + 1].selected_time:
                    order_nodes[j], order_nodes[j + 1] = order_nodes[j + 1], order_nodes[j]
        return order_nodes

    def onItemSelected(self, silent:bool=False):
        if self.propertyDockWidget != None:
            grNode=self.getLastSelectedNode()
            if grNode != None:
                dict=grNode.node.serialize()
                self.propertyDockWidget.dict_value = dict
            else:
                self.propertyDockWidget.dict_value = {}
        super().onItemSelected(silent)

    def onItemsDeselected(self, silent:bool=False):
        if self.propertyDockWidget != None:
            self.propertyDockWidget.dict_value = {}
        super().onItemsDeselected(silent)

    def deserialize(self, data: dict, hashmap: dict = {}, restore_id: bool = True, *args, **kwargs) -> bool:
        hashmap = {}

        if restore_id: self.id = data['id']

        # -- deserialize NODES

        ## Instead of recreating all the nodes, reuse existing ones...
        # get list of all current nodes:
        all_nodes = self.nodes.copy()

        # Obtain the AO created by OA
        OA_data = []
        OA_path = os.path.join(os.path.expanduser('~'), 'flow', 'custom', 'custom-aos-config.json')
        if os.path.exists(OA_path):
            with open(OA_path, "r", encoding="utf-8") as file:
                OA_data = json.load(file)

        # go through deserialized nodes:
        for node_data in data['nodes']:
            # can we find this node in the scene?
            found = False
            for node in all_nodes:
                if node.id == node_data['id']:
                    found = node

                    # Channel or Band  undo redo
                    if 'Channel' or 'Created' or 'Reduce' or 'Band' in self.history.history_stack[self.history.history_current_step]["desc"]:
                        found = False
                    break

            if not found:
                try:
                    if node_data.get('content').get('tap'):
                        if node_data.get('type') in ['PEQ', 'BIQUAD', 'PEQ_FP', 'PEQ_V2']:
                            new_node = self.getNodeClassFromData(node_data)(self, node_data['content']['tap'][1], len(node_data.get('inputs')), node_data.get('control'))
                        elif node_data.get('type') in ['MIXER']:
                            new_node = self.getNodeClassFromData(node_data)(self, len(node_data.get('inputs')), len(node_data.get('outputs')))
                        else:
                            new_node = self.getNodeClassFromData(node_data)(self, node_data['content']['tap'][1])
                    elif node_data.get('tap_menu_parameter_name'):
                        new_node = self.getNodeClassFromData(node_data)(self, node_data['content'][node_data['tap_menu_parameter_name']][1])
                    elif node_data.get('type') == 'BIQUAD_LOAD':
                        new_node = self.getNodeClassFromData(node_data)(self, node_data.get('content').get('maxBand'),
                                                                              len(node_data.get('inputs')))
                    elif node_data.get('type') == 'FIR_LOAD':
                        new_node = self.getNodeClassFromData(node_data)(self, node_data.get('content').get('maxTap'),
                                                                              len(node_data.get('inputs')))
                    elif node_data.get('type') == 'upHear VQE':
                        new_node = self.getNodeClassFromData(node_data)(self, node_data.get('mic'), node_data.get('ref'))
                    elif node_data.get('type') == 'DIRAC':
                        new_node = self.getNodeClassFromData(node_data)(self, node_data['content']['configure'][0])
                    elif node_data.get('type') == 'CINGO':
                        new_node = self.getNodeClassFromData(node_data)(self, len(node_data.get('inputs')))
                    elif node_data.get('type') == 'SUBPATCH':
                        new_node = self.getNodeClassFromData(node_data)(self, len(node_data.get('inputs')), len(node_data.get('outputs')))
                    # elif node_data.get('type') in ['BIQUAD_LOAD']:
                    #     new_node = self.getNodeClassFromData(node_data)(self, node_data['content']['num'],
                    #                                                     len(node_data.get('outputs')))
                    elif node_data.get('type') in ['GAIN', 'LPF', 'HPF', 'IIRCOEF', 'FIR', 'ATTEN', 'POLARITY', 'MUTE',
                                                   'LIMITER', 'HPF_FP', 'LPF_FP', 'COMP_FP', 'LIMITER_FP', 'GAIN_FP',
                                                   'COMP', 'COMP_Combo', 'AUTO_COMP', 'CLIPPER', 'GATE', 'SMART_GATE', 'DYNAMIC_EQ',
                                                   'DELAY', 'DELAY_FP', 'DEESSER', 'AGC', 'VBASS', 'DBASS','METER',
                                                   'MUX', 'DLOUDNESS', 'METER_FP', 'MUX_FP', 'IIRCOEF_FP', 'FIR_FP',
                                                   'COMP_COMBO_FP', 'CLIPPER_FP', 'DBASS_FP', 'NTTS_AGC', 'GAME_EQ', 'Custom_EQ']:
                        if node_data.get('type') in ['MUX']:
                            new_node = self.getNodeClassFromData(node_data)(self, len(node_data.get('outputs')), type=node_data['title'])
                        elif node_data.get('type') in ['MUX_FP']:
                            new_node = self.getNodeClassFromData(node_data)(self, len(node_data.get('outputs')))
                        else:
                            new_node = self.getNodeClassFromData(node_data)(self, len(node_data.get('inputs')))
                    # AO created by OA
                    elif node_data.get('op_code') > 1000000000 and node_data.get('node_type') == "AO":
                        for OA in OA_data:
                            if OA['ao_code'] == node_data['op_code']:
                                if OA['type_ao_addition'] == 1:
                                    new_node = self.getNodeClassFromData(node_data)(self)
                                elif OA['type_ao_addition'] == 2:
                                    new_node = self.getNodeClassFromData(node_data)(self, len(node_data.get('inputs')))
                    # CO
                    elif node_data.get('node_type') == "CO":
                        if node_data.get("type") in ["HW_IN", "CONSTANT"]:
                            new_node = self.getNodeClassFromData(node_data)(self, node_data.get('outctrls')[0]["socket_type"])
                        elif node_data.get("type") in ["ADD", "MULTIPLY", "INVERSE", "POWER", "SQRT", "LOG", "EXP",
                                                       "CLAMP", "OR", "AND", "NOT", "CO_DELAY", "CO_METER"]:
                            new_node = self.getNodeClassFromData(node_data)(self, node_data.get('inctrls')[0]["socket_type"], len(node_data.get('inctrls')))
                        elif node_data.get("type") in ["HW_OUT", "THRESHOLD", "LOOKUP_TABLE"]:
                            new_node = self.getNodeClassFromData(node_data)(self, node_data.get('inctrls')[0]["socket_type"])
                        else:
                            new_node = self.getNodeClassFromData(node_data)(self)
                    else:
                        new_node = self.getNodeClassFromData(node_data)(self)
                    new_node.deserialize(node_data, hashmap, restore_id, *args, **kwargs)
                    new_node.onDeserialized(node_data)
                    # print("New node for", node_data['title'])
                except:
                    dumpException()
            else:
                try:
                    found.deserialize(node_data, hashmap, restore_id, *args, **kwargs)
                    found.onDeserialized(node_data)
                    all_nodes.remove(found)
                    # print("Reused", node_data['title'])
                except:
                    dumpException()

        # remove nodes which are left in the scene and were NOT in the serialized data!
        # that means they were not in the graph before...
        while all_nodes != []:
            node = all_nodes.pop()
            node.remove()

        # -- deserialize EDGES

        ## Instead of recreating all the edges, reuse existing ones...
        # get list of all current edges:
        all_edges = self.edges.copy()

        # go through deserialized edges:
        for edge_data in data['edges']:
            # can we find this node in the scene?
            found = False
            for edge in all_edges:
                if edge.id == edge_data['id']:
                    found = edge
                    break

            if not found:
                new_edge = Edge(self).deserialize(edge_data, hashmap, restore_id, *args, **kwargs)
                # print("New edge for", edge_data)
            else:
                found.deserialize(edge_data, hashmap, restore_id, *args, **kwargs)
                all_edges.remove(found)

        # remove nodes which are left in the scene and were NOT in the serialized data!
        # that means they were not in the graph before...
        while all_edges != []:
            edge = all_edges.pop()
            edge.remove()

        return True