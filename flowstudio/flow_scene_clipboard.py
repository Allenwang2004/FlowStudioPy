import os
import json
from flowstudio.flow_conf import Debug
from nodeeditor.node_scene_clipboard import *
from nodeeditor.node_scene import Scene

class FLOW_Scene_Clipboard(SceneClipboard):

    def __init__(self, scene:'Scene'):
        super().__init__(scene)

    def deserializeFromClipboard(self, data: dict, *args, **kwargs):
        """
        Deserializes data from Clipboard.

        :param data: ``dict`` data for deserialization to the :class:`nodeeditor.node_scene.Scene`.
        :type data: ``dict``
        """

        hashmap = {}

        # calculate mouse pointer - scene position
        view = self.scene.getView()
        mouse_scene_pos = view.last_scene_mouse_position

        # calculate selected objects bbox and center
        minx, maxx, miny, maxy = 10000000, -10000000, 10000000, -10000000
        for node_data in data['nodes']:
            x, y = node_data['pos_x'], node_data['pos_y']
            if x < minx: minx = x
            if x > maxx: maxx = x
            if y < miny: miny = y
            if y > maxy: maxy = y

        # add width and height of a node
        maxx -= 180
        maxy += 100

        relbboxcenterx = (minx + maxx) / 2 - minx
        relbboxcentery = (miny + maxy) / 2 - miny

        if Debug.DEBUG_Low_Level.value:
            print(" *** PASTA:")
            print("Copied boudaries:\n\tX:", minx, maxx, "   Y:", miny, maxy)
            print("\tbbox_center:", relbboxcenterx, relbboxcentery)

        # calculate the offset of the newly creating nodes
        mousex, mousey = mouse_scene_pos.x(), mouse_scene_pos.y()

        # create each node
        created_nodes = []

        self.scene.setSilentSelectionEvents()

        self.scene.doDeselectItems()

        # Obtain the AO created by OA
        OA_data = []
        OA_path = os.path.join(os.path.expanduser('~'), 'flow', 'custom', 'custom-aos-config.json')
        if os.path.exists(OA_path):
            with open(OA_path, "r", encoding="utf-8") as file:
                OA_data = json.load(file)

        for node_data in data['nodes']:
            if node_data.get('type') in ['LPF', 'HPF', 'IIRCOEF', 'FIR', 'GAIN', 'ATTEN', 'POLARITY',
                                         'LIMITER', 'COMP', 'GAIN_FP', 'HPF_FP', 'COMP_FP', 'LIMITER_FP',
                                        'COMP_Combo', 'AUTO_COMP','CLIPPER', 'GATE', 'SMART_GATE', 'DELAY',
                                        'DELAY_FP', 'METER', 'DEESSER', 'AGC', 'VBASS', 'DBASS', 'DLOUDNESS', 'DYNAMIC_EQ',
                                         'METER_FP', 'IIRCOEF_FP', 'FIR_FP', 'COMP_COMBO_FP', 'CLIPPER_FP', 'NTTS_AGC',
                                        'MUTE', 'GAME_EQ']:
                new_node = self.scene.getNodeClassFromData(node_data)(self.scene, len(node_data.get('inputs')))
            elif node_data.get('type') in ['MULTITAP', 'LONG_APF', 'LPF_COMB_FILTER']:
                new_node = self.scene.getNodeClassFromData(node_data)(self.scene,node_data.get('content').get(node_data.get('tap_menu_parameter_name'))[1])
            elif node_data.get('type') in ['PEQ', 'BIQUAD', 'PEQ_FP', 'PEQ_V2']:
                new_node = self.scene.getNodeClassFromData(node_data)(self.scene, node_data.get('content').get(node_data.get('tap_menu_parameter_name'))[1], len(node_data.get('outputs')), node_data.get('control'))
            elif node_data.get('type') in ['BIQUAD_LOAD']:
                new_node = self.scene.getNodeClassFromData(node_data)(self.scene,  node_data.get('content').get('maxBand'), len(node_data.get('inputs')))
            elif node_data.get('type') in ['FIR_LOAD']:
                new_node = self.scene.getNodeClassFromData(node_data)(self.scene,  node_data.get('content').get('maxTap'), len(node_data.get('inputs')))
            elif node_data.get('type') in ['MUX', 'MUX_FP']:
                new_node = self.scene.getNodeClassFromData(node_data)(self.scene, len(node_data.get('outputs')))
            elif node_data.get('type') in ['MIXER']:
                new_node = self.scene.getNodeClassFromData(node_data)(self.scene, len(node_data.get('inputs')), node_data.get('content').get(node_data.get('tap_menu_parameter_name'))[1])
            elif node_data.get('type') in ['upHear VQE']:
                new_node = self.scene.getNodeClassFromData(node_data)(self.scene, node_data.get('mic'),
                                                                      node_data.get('ref'))
            elif node_data.get('type') in ['DIRAC']:
                new_node = self.scene.getNodeClassFromData(node_data)(self.scene, node_data.get('content')['configure'][0])
            elif node_data.get('type') in ['CINGO']:
                new_node = self.scene.getNodeClassFromData(node_data)(self.scene, len(node_data.get('inputs')))
            elif node_data.get('type') in ['SUBPATCH']:
                new_node = self.scene.getNodeClassFromData(node_data)(self.scene, len(node_data.get('inputs')), len(node_data.get('outputs')))
            # AO created by OA
            elif node_data.get('op_code') > 1000000000 and node_data.get('node_type') == "AO":
                for OA in OA_data:
                    if OA['ao_code'] == node_data['op_code']:
                        if OA['type_ao_addition'] == 1:
                            new_node = self.scene.getNodeClassFromData(node_data)(self.scene)
                        elif OA['type_ao_addition'] == 2:
                            new_node = self.scene.getNodeClassFromData(node_data)(self.scene, len(node_data.get('inputs')))
            # CO
            elif node_data.get('node_type') == "CO":
                if node_data.get("type") in ["HW_IN", "CONSTANT"]:
                    new_node = self.scene.getNodeClassFromData(node_data)(self.scene, node_data.get('outctrls')[0]["socket_type"])
                elif node_data.get("type") in ["ADD", "MULTIPLY", "INVERSE", "POWER", "SQRT", "LOG", "EXP", "CLAMP",
                                               "OR", "AND", "NOT", "CO_DELAY", "CO_METER"]:
                    new_node = self.scene.getNodeClassFromData(node_data)(self.scene, node_data.get('inctrls')[0]["socket_type"], len(node_data.get('inctrls')))
                elif node_data.get("type") in ["HW_OUT", "THRESHOLD", "LOOKUP_TABLE"]:
                    new_node = self.scene.getNodeClassFromData(node_data)(self.scene, node_data.get('inctrls')[0]["socket_type"])
                else:
                    new_node = self.scene.getNodeClassFromData(node_data)(self.scene)
            else:
                new_node = self.scene.getNodeClassFromData(node_data)(self.scene)
            new_node.deserialize(node_data, hashmap, restore_id=False, *args, **kwargs)
            created_nodes.append(new_node)

            # readjust the new nodeeditor's position

            # new node's current position
            posx, posy = new_node.pos.x(), new_node.pos.y()
            newx, newy = mousex + posx - minx, mousey + posy - miny

            new_node.setPos(newx, newy)

            new_node.doSelect()

            if Debug.DEBUG_Low_Level.value:
                print("** PASTA SUM:")
                print("\tMouse pos:", mousex, mousey)
                print("\tnew node pos:", posx, posy)
                print("\tFINAL:", newx, newy)

        # create each edge
        if 'edges' in data:
            for edge_data in data['edges']:
                new_edge = Edge(self.scene)
                new_edge.deserialize(edge_data, hashmap, restore_id=False, *args, **kwargs)

        self.scene.setSilentSelectionEvents(False)

        # store history
        self.scene.history.storeHistory("Pasted elements in scene", setModified=True)

        return created_nodes