import xml.etree.ElementTree as ET
from xml.dom import minidom
from flowstudio.flow_topological_sort import *
import os
import json
from flowstudio.flow_conf import OP_NODE_SUBPATCH, AOS_ONLY_ALLOW_PC_SIXTEEN_K_SR, AOS_ONLY_ALLOW_FORTY_EIGHT_K_SR, \
    OP_NODE_SRC
import numpy as np
DEBUG = False

class FLOW_File_Convert(object):

    def __init__(self, data, windows=None, rate = 0):
        """
            FLOW_File_Convert instance initialization

            :param data: dict, main sub_window information, includes nodes and edges information
            :param windows: list, contains displayed QMdiSubWindow objects; default:None

        """
        self.in_ch = 0
        self.out_ch = 0
        self.windows = windows
        self.root = ET.Element('TADS_CONFIG')
        self.raw_nodes = data['nodes']
        self.raw_edges = data['edges']
        self.removeCommentNodes()
        self.extractGroupNodes()
        self.device_sample_rate = int(rate)
        self.device_frame_size = int(int(rate) * 0.001)
        self.socket_type_list = {1: '', 7: "bool", 8: 'int', 9: 'float', 10: 'string'}

        new_data = {'nodes': self.raw_nodes, 'edges': self.raw_edges}
        self.routing = self.mtfkFormatConverter(new_data)

    def createAttrib(self, index):
        return str(self.raw_nodes[index]['type']) + '_' + str(self.raw_nodes[index]['designator'])

    def process(self):

        # create audio object
        for node_index in range(len(self.raw_nodes)):
            # create AO attrib
            AO = ET.SubElement(self.root, 'AO')
            AO.set('id', self.createAttrib(node_index))
            AO.set('type', self.raw_nodes[node_index]['node_type'])
            # AO.set('id', str(self.nodes[node_index]['title']) + '_' + str(self.nodes[node_index]['id']))

            # create id
            obj_id = ET.SubElement(AO, 'id')
            obj_id.text = str(self.raw_nodes[node_index]['type']) + '_' + str(self.raw_nodes[node_index]['designator'])

            # create type
            obj_type = ET.SubElement(AO, 'type')
            obj_type.text = str(self.raw_nodes[node_index]['type'])

            # create name
            obj_name = ET.SubElement(AO, 'name')
            obj_name.text = str(self.raw_nodes[node_index]['title'])

            # create order
            obj_order = ET.SubElement(AO, 'order')
            obj_order.text = str(node_index)

            # create from
            for k in range(len(self.routing['from'])):
                if self.raw_nodes[node_index]['id'] in self.routing['from'][k]:
                    obj = ET.SubElement(AO, 'to')
                    obj.set('dir', str(self.routing['from'][k][self.raw_nodes[node_index]['id']][0]['dir']))
                    obj.set('index', str(self.routing['from'][k][self.raw_nodes[node_index]['id']][1]['index']))
                    obj.set('port', str(self.routing['from'][k][self.raw_nodes[node_index]['id']][2]['port']))
                    value = self.socket_type_list[int(self.routing['from'][k][self.raw_nodes[node_index]['id']][3]['socket_type'])]
                    if value != '':
                        obj.set('type', value)

            # create to
            for k in range(len(self.routing['to'])):
                if self.raw_nodes[node_index]['id'] in self.routing['to'][k]:
                    obj = ET.SubElement(AO, 'from')
                    obj.set('dir', str(self.routing['to'][k][self.raw_nodes[node_index]['id']][0]['dir']))
                    obj.set('index', str(self.routing['to'][k][self.raw_nodes[node_index]['id']][1]['index']))
                    obj.set('port', str(self.routing['to'][k][self.raw_nodes[node_index]['id']][2]['port']))
                    value = self.socket_type_list[
                        int(self.routing['to'][k][self.raw_nodes[node_index]['id']][3]['socket_type'])]
                    if value != '':
                        obj.set('type', value)

            # create ctrlfrom
            for k in range(len(self.routing['ctrl_from'])):
                if self.raw_nodes[node_index]['id'] in self.routing['ctrl_from'][k]:
                    obj = ET.SubElement(AO, 'ctrlto')
                    obj.set('dir', str(self.routing['ctrl_from'][k][self.raw_nodes[node_index]['id']][0]['dir']))
                    obj.set('index', str(self.routing['ctrl_from'][k][self.raw_nodes[node_index]['id']][1]['index']))
                    obj.set('port', str(self.routing['ctrl_from'][k][self.raw_nodes[node_index]['id']][2]['port']))

            # create ctrlto
            # for k in range(len(self.routing['ctrl_to'])):
            #     if self.raw_nodes[node_index]['id'] in self.routing['ctrl_to'][k]:
            #         obj = ET.SubElement(AO, 'ctrlfrom')
            #         obj.set('dir',str(self.routing['ctrl_to'][k][self.raw_nodes[node_index]['id']][0]['dir']))
            #         obj.set('index',str(self.routing['ctrl_to'][k][self.raw_nodes[node_index]['id']][1]['index']))
            #         obj.set('port',str(self.routing['ctrl_to'][k][self.raw_nodes[node_index]['id']][2]['port']))

            AO.set("link", str(self.raw_nodes[node_index]['linktype']))

            if self.raw_nodes[node_index]['linktype'] != 0:
                if self.raw_nodes[node_index]['type'] == 'upHear VQE':
                    AO.set("in_ch", str(self.raw_nodes[node_index]['mic']))
                    AO.set("out_ch", str(self.raw_nodes[node_index]['ref']))
                else:
                    AO.set("in_ch", str(len(self.raw_nodes[node_index]['inputs'])))
                    AO.set("out_ch", str(len(self.raw_nodes[node_index]['outputs'])))


            ch = 0
            # create param
            if len(self.raw_nodes[node_index]['content']):
                if self.raw_nodes[node_index]['type'] == 'DIRAC':
                    continue

                if 'tap_menu_parameter_name' in self.raw_nodes[node_index] and self.raw_nodes[node_index]['content'].__contains__(self.raw_nodes[node_index]['tap_menu_parameter_name']):
                    j = ET.SubElement(AO, 'param')

                    j.set('name', self.raw_nodes[node_index]['tap_menu_parameter_name'])
                    tap_value = self.raw_nodes[node_index]['content'][self.raw_nodes[node_index]['tap_menu_parameter_name']][1]
                    j.set('val', str(tap_value))
                    self.raw_nodes[node_index]['content'].pop(self.raw_nodes[node_index]['tap_menu_parameter_name'])



                for dict_key, dict_value in self.raw_nodes[node_index]['content'].items():

                    if str(dict_key) == 'File':
                        if self.raw_nodes[node_index]['type'] in ['FIR', "FIR_FP"]:
                            if dict_value[0]:
                                j = ET.SubElement(AO, 'param')
                                j.set('name', 'tap')
                                j.set('val', str(len(dict_value[1][0])))
                                for index in range(len(dict_value[1][0])):
                                    addParam = ET.SubElement(AO, 'param')
                                    addParam.set('name', 'b_' + str(index))
                                    addParam.set('val', str(dict_value[1][0][index]))
                                    addParam.set('row', str(index))
                                    addParam.set('col', '0')
                            else:
                                j = ET.SubElement(AO, 'param')
                                j.set('name', 'tap')
                                j.set('val', '32')

                                for index in range(32):
                                    addParam = ET.SubElement(AO, 'param')
                                    addParam.set('name', 'b_' + str(index))
                                    value = '1' if index == 0 else '0'
                                    addParam.set('val', value)
                                    addParam.set('row', str(index))
                                    addParam.set('col', '0')

                        elif self.raw_nodes[node_index]['type'] in ['IIRCOEF', 'IIRCOEF_FP']:
                            if dict_value[0]:
                                for index in range(len(dict_value[1][0])):
                                    addParam = ET.SubElement(AO, 'param')
                                    addParam.set('name', 'b_' + str(index))
                                    addParam.set('val', str(dict_value[1][0][index]))
                                    addParam.set('row', str(index))
                                    addParam.set('col', '0')
                                for index in range(len(dict_value[1][1])):
                                    addParam = ET.SubElement(AO, 'param')
                                    addParam.set('name', 'a_' + str(index))
                                    addParam.set('val', str(dict_value[1][1][index]))
                                    addParam.set('row', str(index))
                                    addParam.set('col', '0')
                            else:
                                pass

                    else:
                        if dict_key == 'fftsize':
                            addParam = ET.SubElement(AO, 'param')
                            addParam.set('name', str(dict_key))
                            value = dict_value[0]
                            addParam.set('val', str(value))
                            addParam.set('row', '0')
                            addParam.set('col', '0')
                        else:
                            addParam = ET.SubElement(AO, 'param')
                            paramName = str(dict_key).split('_')
                            addParam.set('name', dict_key)
                            value = dict_value[1] if isinstance(dict_value, list) else dict_value
                            addParam.set('val', str(value))
                            try:
                                addParam.set('row', paramName[1])
                            except:
                                addParam.set('row', '0')

                            try:
                                addParam.set('col', paramName[2])
                            except:
                                addParam.set('col', '0')

                    if self.raw_nodes[node_index]['type'] == 'SRC':
                        if str(dict_key) == 'srin':
                            Parameter_Value = dict_value[0]
                        if str(dict_key) == 'srout':
                            Parameter_Value = dict_value[0]
                        if str(dict_key) == 'Quality':
                            Parameter_Value = dict_value[1]
                        # if str(dict_key) == 'Latency':
                        #     Parameter_Value = dict_value
                        addParam.set('val', str(Parameter_Value))

                    if self.raw_nodes[node_index]['type'] == 'upHear VQE':
                        if str(dict_key) == 'UrocMicSetup':
                            Parameter_Value = dict_value[1]
                            if Parameter_Value >= 15:
                                Parameter_Value += 2
                            elif Parameter_Value > 7:
                                Parameter_Value += 1

                            value = Parameter_Value
                        elif str(dict_key) == "FrameSize":
                            value = dict_value[0]
                        elif str(dict_key) == "processmode":
                            Parameter_Value = dict_value[1]
                            value = 17 if Parameter_Value == 2 else Parameter_Value
                        elif str(dict_key) == "id":
                            value = dict_value[0]
                        addParam.set('val', str(value))

                        try:
                            addParam.set('row', paramName[1])
                        except:
                            addParam.set('row', '0')

                        try:
                            addParam.set('col', paramName[2])
                        except:
                            addParam.set('col', '0')

                    elif self.raw_nodes[node_index]['type'] == 'CINGO':
                        if str(dict_key) in ["ChSpatial_L", "ChMute_L", "ChAzimuth_L", "ChElevation_L", "ChSpatial_R",
                                             "ChMute_R", "ChAzimuth_R", "ChElevation_R"]:
                            ss = str.split(str(dict_key), '_')
                            if ss[1] == "L":
                                Parameter_Index = '0'
                            elif ss[1] == "R":
                                Parameter_Index = '1'
                            addParam.set('name', ss[0])
                            addParam.set('col', Parameter_Index)
                            addParam.set('row', '0')

        not_support_nodes = []
        is_has_SRC = False
        for node in self.raw_nodes:
            if node['op_code'] == OP_NODE_SRC:
                is_has_SRC = True

        if is_has_SRC:
            # Create frame size
            ao_connections, ao_types, ao_items, ao_op_code = self.build_AO_connections(self.root)
            all_paths = self.build_all_path(ao_connections, ao_types)
            frame_sizes, sample_rates, not_support_nodes = self.calculate_AO_frame_size_and_sample_rate(all_paths, ao_connections, ao_types, ao_items)
            self.add_child_to_AOs(frame_sizes, sample_rates)

            # Check SRC
            if DEBUG: print("============== check SRC start ==============")
            not_support_nodes = self.check_the_settings_of_SRC_sample_rate(all_paths, ao_types, ao_items, ao_op_code, sample_rates, not_support_nodes)
            if DEBUG: print("============== check SRC end ==============")

        sortedData = self.graphicSort(self.root)
        return minidom.parseString(ET.tostring(sortedData)).toprettyxml(indent="   "), not_support_nodes
        # return minidom.parseString(ET.tostring(self.root)).toprettyxml(indent="   ")

    def addCanvasInformation(self, data):
        # add canvas information to root
        scene = ET.SubElement(self.root, 'SCENE')
        scene.set('id', str(data['id']))
        scene.set('scene_width', str(data['scene_width']))
        scene.set('scene_height', str(data['scene_height']))

    def removeCommentNodes(self):
        # remove comment nodes from root
        index, length = 0, len(self.raw_nodes)
        while index < length:
            if self.raw_nodes[index]['type'] == 'COMMENT':
                self.raw_nodes.remove(self.raw_nodes[index])
                index = index - 1
                length = length - 1
            if self.raw_nodes[index]['node_type'] == 'CO':
                self.raw_nodes.remove(self.raw_nodes[index])
                index = index - 1
                length = length - 1
            index = index + 1

    def extractGroupNodes(self):
        dummy_index = 0
        dummy_designator = 0
        input_socket_index = 0
        output_socket_index = 0

        def process_edges(edges, to_delete_edges):
            """Helper function to process and clean up edges"""
            final_edges = []
            edge_ids = set()

            for edge in edges:
                if edge not in to_delete_edges:
                    # Check if this connection already exists
                    connection = (edge['start'], edge['end'])
                    if connection not in edge_ids:
                        edge_ids.add(connection)
                        final_edges.append(edge)

            return final_edges

        for parent_node in self.raw_nodes:
            if parent_node['op_code'] == OP_NODE_SUBPATCH:
                def dfs_extract_group_nodes(parent_node, dummy_index, dummy_designator, input_socket_index, output_socket_index):
                    is_subpatch_inside = False
                    subpatch = parent_node
                    parent_inputs = subpatch['inputs']
                    parent_outputs = subpatch['outputs']
                    for window in self.windows:
                        sub_window_name = window.widget().getPrettyFilename()
                        if sub_window_name == subpatch['cwd']:
                            raw_data = json.dumps(window.widget().scene.serialize(), indent=4)
                            data = json.loads(raw_data)
                            SUBPATCH = data
                    child_nodes = SUBPATCH['nodes']
                    child_edges = SUBPATCH['edges']
                    # region add NONE AO into subpatch page if INLET directly connects to OUTLET
                    add_edges = []
                    for child_edge in child_edges:
                        start_child_node = self.find_node_by_output_or_outctrl_socket_id(child_edge['start'], child_nodes)
                        end_child_node = self.find_node_by_input_or_inctrl_socket_id(child_edge['end'], child_nodes)
                        if start_child_node['type'] == 'INLET' and end_child_node['type'] == 'OUTLET':
                            dummy_index -= 1
                            dummy_designator -= 1
                            input_socket_index += 1
                            output_socket_index -= 1
                            dummy = {
                                'id': dummy_index,
                                'title': f'NONE_{dummy_designator}',
                                'inputs': [{'id': input_socket_index, 'index': 0, 'multi_edges': False, 'position': 1,
                                            'socket_type': 1}],
                                'outputs': [{'id': output_socket_index, 'index': 0, 'multi_edges': True, 'position': 4,
                                             'socket_type': 1}],
                                'content': {"mute": [
                                    "off",
                                    0
                                ]},
                                'op_code': -99,
                                'type': 'NONE',
                                'designator': dummy_designator
                            }
                            add_edges.append([output_socket_index, end_child_node['inputs'][0]['id']])
                            child_edge['end'] = input_socket_index
                            child_nodes.append(dummy)
                    for add_edge in add_edges:
                        child_edges.append({
                            "id": 0,
                            "edge_type": 2,
                            "start": add_edge[0],
                            "end": add_edge[1]
                        })
                    # endregion
                    nodes = self.raw_nodes + child_nodes
                    edges = self.raw_edges + child_edges
                    subpatchs_inside = []
                    # map inputs, outputs, nodes, edges here!
                    for child_node in child_nodes:
                        if child_node['type'] == 'INLET':
                            inlet = child_node

                            # get subpatch output socket(start of a edge), find end socket's id, start - edge - end
                            # inlet's first output(which is also the only output of INLET)
                            inletStartSocket = inlet['outputs'][0]['id']
                            # this output socket which is the start of the edge, get end socket and edge back
                            outputs = self.findEndSocketsByStartSocket(inletStartSocket, child_edges)
                            for output in outputs:
                                targetChildInput, inletEdge = output[0], output[1]
                                # end socket is the input of target child node, find the node itself
                                targetChildNode = self.find_node_by_input_or_inctrl_socket_id(targetChildInput, child_nodes)

                                # end socket will replace the inputs[n] of group

                                # the designator of the inlet decide the index of inputs of group node
                                designator = inlet['designator']
                                # by designator, we can get group node's input socket
                                parentInputSocket = parent_inputs[designator-1]['id']
                                # replace here!
                                index = self.findInputIndexBySocket(targetChildInput, targetChildNode)
                                targetChildNode['inputs'][index]['id'] = parentInputSocket

                                # remove inlet[n]
                                if inlet in nodes:
                                    nodes.remove(inlet)
                                # remove inlet[n]'s edges
                                if inletEdge in edges:
                                    edges.remove(inletEdge)

                        elif child_node['type'] == 'OUTLET':
                            outlet = child_node

                            # get subpatch input socket(end of a edge), find start socket's id, start - edge - end
                            # outlet's first input(which is also the only input of OUTLET)
                            outletEndSocket = outlet['inputs'][0]['id']
                            # this input socket which is the end of the edge, get start socket and edge back
                            targetChildOutput, outletEdge = self.findStartSocketByEndSocket(outletEndSocket, child_edges)
                            # start socket is the output of target child node, find the node itself
                            targetChildNode = self.find_node_by_output_or_outctrl_socket_id(targetChildOutput, child_nodes)

                            # start socket will replace the outputs[n] of group

                            # the designator of the outlet decide the index of outputs of group node
                            designator = outlet['designator']
                            # by designator, we can get group node's output socket
                            parentOutputSocket = parent_outputs[designator - 1]['id']
                            # replace here!
                            index = self.findOutputIndexBySocket(targetChildOutput, targetChildNode)
                            if 'change_to' not in targetChildNode['outputs'][index]:
                                targetChildNode['outputs'][index]['change_to'] = [parentOutputSocket]
                                targetChildNode['outputs'][index]['original'] = targetChildNode['outputs'][index]['id']
                            else:
                                targetChildNode['outputs'][index]['change_to'].append(parentOutputSocket)
                            targetChildNode['outputs'][index]['id'] = parentOutputSocket

                            # replace another edges array here!
                            array = self.findEndSocketsByStartSocket(targetChildOutput, child_edges)
                            for id, edge in array:
                                edge['start'] = parentOutputSocket

                            # remove outlet[n]
                            nodes.remove(outlet)
                            # remove outlet[n]'s edges
                            edges.remove(outletEdge)

                        if child_node['op_code'] == OP_NODE_SUBPATCH:
                            is_subpatch_inside = True
                            subpatchs_inside.append(child_node)

                        # remove group's nodes
                        if subpatch in nodes:
                            nodes.remove(subpatch)
                            self.raw_nodes = nodes
                            self.raw_edges = edges
                    if not is_subpatch_inside:
                        return
                    for subpatch_inside in subpatchs_inside:
                        dfs_extract_group_nodes(subpatch_inside, dummy_index, dummy_designator, input_socket_index,
                                                output_socket_index)

                dfs_extract_group_nodes(parent_node, dummy_index, dummy_designator, input_socket_index, output_socket_index)
                nodes = self.raw_nodes
                edges = self.raw_edges
                to_add_edges = []
                to_delete_edges = []
                to_delete_nodes = []
                new_edge_index = 0
                sockets = []
                for node in nodes:
                    if node['type'] == 'COMMENT':
                        to_delete_nodes.append(node)

                    if node['type'] == 'NONE':
                        dummy_end_socket = node['inputs'][0]['id']
                        for another_node in nodes:
                            if another_node['type'] != 'NONE':
                                if len(another_node['inputs']) > 0:
                                    for i in range(len(another_node['inputs'])):
                                        if another_node['inputs'][i]['id'] == dummy_end_socket:
                                            input_socket_index += 1
                                            new_edge_index -= 1
                                            another_node['inputs'][i]['id'] = input_socket_index
                                            sockets.append(input_socket_index)

                        in_ao_output_socket, dummy_start_edge = self.findStartSocketByEndSocket(dummy_end_socket, edges)
                        dummy_start_socket = node['outputs'][0]['id']
                        out_ao_input_sockets_and_dummy_end_edges = self.findEndSocketsByStartSocket(dummy_start_socket, edges)
                        for out_ao_input_socket, _ in out_ao_input_sockets_and_dummy_end_edges:
                            new_edge_index -= 1
                            to_add_edges.append({
                                'id': new_edge_index,
                                'edge_type': 2,
                                'start': in_ao_output_socket,
                                'end': out_ao_input_socket
                            })
                        for socket in sockets:
                            new_edge_index -= 1
                            to_add_edges.append({
                                'id': new_edge_index,
                                'edge_type': 2,
                                'start': in_ao_output_socket,
                                'end': socket
                            })
                        for another_node in nodes:
                            if another_node['type'] != 'NONE' and another_node['type'] != 'OUT':
                                for edge in edges:
                                    if len(another_node['inputs']) > 0:
                                        for i in range(len(another_node['inputs'])):
                                            if edge['start'] == dummy_start_socket and edge['end'] == another_node['inputs'][i]['id']:
                                                new_edge_index -= 1
                                                to_add_edges.append({
                                                    'id': new_edge_index,
                                                    'edge_type': 2,
                                                    'start': in_ao_output_socket,
                                                    'end': another_node['inputs'][i]['id']
                                                })
                                                to_delete_edges.append(edge)
                        to_delete_edges.append(dummy_start_edge)
                        for _, dummy_end_edge in out_ao_input_sockets_and_dummy_end_edges:
                            to_delete_edges.append(dummy_end_edge)
                        to_delete_nodes.append(node)
                    else:
                        sockets = []
                        if len(node['inputs']) > 0 and len(node['outputs']) > 0:
                            for output in node['outputs']:
                                if 'change_to' in output and len(output['change_to']) > 1:
                                    for start_socket_id in output['change_to']:
                                        for edge in edges:
                                            if edge['start'] == start_socket_id:
                                                edge['start'] = output['original']
                                    output['id'] = output['original']
                                    del output['change_to']
                                    del output['original']
                                elif 'change_to' in output and len(output['change_to']) == 1:
                                    del output['change_to']
                                    del output['original']
                            dummy_end_socket = node['inputs'][0]['id']
                            need_to_fix = False
                            for another_node in nodes:
                                if another_node != node:
                                    if len(another_node['inputs']) > 0:
                                        for i in range(len(another_node['inputs'])):
                                            if another_node['inputs'][i]['id'] == dummy_end_socket:
                                                need_to_fix = True
                                                input_socket_index += 1
                                                new_edge_index -= 1
                                                another_node['inputs'][i]['id'] = input_socket_index
                                                sockets.append(input_socket_index)
                            if need_to_fix:
                                in_ao_output_socket, dummy_start_edge = self.findStartSocketByEndSocket(dummy_end_socket, edges)
                                for socket in sockets:
                                    new_edge_index -= 1
                                    to_add_edges.append({
                                        'id': new_edge_index,
                                        'edge_type': 2,
                                        'start': in_ao_output_socket,
                                        'end': socket
                                    })
                self.raw_edges = process_edges([*self.raw_edges, *to_add_edges], to_delete_edges)
                for to_delete_node in to_delete_nodes:
                    if to_delete_node in self.raw_nodes:
                        self.raw_nodes.remove(to_delete_node)

    def openFile(self, filename):
        with open(filename, "r") as file:
            raw_data = file.read()
            data = json.loads(raw_data)
            return data

    def findEndSocketByStartSocket(self, start_socket, edges):
        for edge in edges:
            if edge['start'] == start_socket:
                return edge['end'], edge

    def findEndSocketsByStartSocket(self, start_socket, edges):
        res = []
        for edge in edges:
            if edge['start'] == start_socket:
                res.append([edge['end'], edge])

        return res

    def findStartSocketByEndSocket(self, end_socket, edges):
        for edge in edges:
            if edge['end'] == end_socket:
                return edge['start'], edge

    def find_node_by_output_or_outctrl_socket_id(self, output_socket_id, nodes):
        for node in nodes:
            for output in node['outputs']:
                if output['id'] == output_socket_id:
                    return node
            if 'outctrls' not in node:
                continue
            for outctrls in node['outctrls']:
                if outctrls['id'] == output_socket_id:
                    return node

    def find_node_by_input_or_inctrl_socket_id(self, input_socket_id, nodes):
        for node in nodes:
            for input in node['inputs']:
                if input['id'] == input_socket_id:
                    return node
            if 'inctrls' not in node:
                continue
            for inctrls in node['inctrls']:
                if inctrls['id'] == input_socket_id:
                    return node

    def findInputIndexBySocket(self, input_socket, node):
        for input in node['inputs']:
            if input['id'] == input_socket:
                return input['index']

    def findOutputIndexBySocket(self, output_socket, node):
        for output in node['outputs']:
            if output['id'] == output_socket:
                return output['index']

    def mtfkFormatConverter(self, data) -> dict:
        # convert json into flw style
        numberofedges = len(data['edges'])
        numberofnodes = len(data['nodes'])
        fromlist = []
        tolist = []
        ctrl_fromlist = []
        ctrl_tolist = []
        for i in range(0, numberofedges):

            # print(data['edges'][i]['start'])
            for j in range(0, numberofnodes):
                if data['nodes'][j]['outputs']:
                    NumberOfOutputsInThdeNodes = len(data['nodes'][j]['outputs'])
                    for k in range(0, NumberOfOutputsInThdeNodes):
                        # print(k)
                        # print(data['nodes'][j]['outputs'][k]['id'])
                        if data['nodes'][j]['outputs'][k]['id'] == data['edges'][i]['start']:
                            if Debug.DEBUG_Low_Level.value: print("Node:", data['nodes'][j]['id'], "Port:", data['edges'][i]['start'],
                                            "is a start of the edge, output of the node")
                            if Debug.DEBUG_Low_Level.value: print("Index of this node is: ", data['nodes'][j]['outputs'][k]['index'])
                            if Debug.DEBUG_Low_Level.value: print("the node above will connect to: ", data['edges'][i]['end'])

                            for l in range(0, numberofnodes):
                                for m in range(0, len(data['nodes'][l]['inputs'])):
                                    if data['nodes'][l]['inputs'][m]['id'] == data['edges'][i]['end']:
                                        if Debug.DEBUG_Low_Level.value: print("its parent node is: ", data['nodes'][l]['id'], "index: ",
                                                        data['nodes'][l]['inputs'][m]['index'])
                                        if Debug.DEBUG_Low_Level.value: print("from: ", data['nodes'][j]['id'],
                                                        data['nodes'][j]['outputs'][k]['index'],
                                                        "to: ", data['nodes'][l]['id'],
                                                        data['nodes'][l]['inputs'][m]['index'])

                                        index = {"index": data['nodes'][j]['outputs'][k]['index']}

                                        socket_type = {"socket_type": data['nodes'][j]['outputs'][k]['socket_type']}
                                        #
                                        if data['nodes'][l]['type'] in ['IN', 'OUT']:
                                            port = {"port": data['nodes'][l]['type'] + '_' + str(
                                                data['nodes'][l]['designator'])}
                                        else:
                                            port = {"port": data['nodes'][l]['type'] + '_' + str(
                                                data['nodes'][l]['designator'])}
                                            # port = {"port": data['nodes'][l]['title'] + '_' + str(data['nodes'][l]['id'])}
                                        #
                                        dst = {"dir": data['nodes'][l]['inputs'][m]['index']}

                                        inputslist = ([dst, index, port, socket_type])

                                        fromdict = {data['nodes'][j]['id']: inputslist}
                            fromlist.append(fromdict)
                            # fromlist.append({data['nodes'][j]['id']: inputslist})
                            if Debug.DEBUG_Low_Level.value: print("\n")
                    # print("yeah")
            # print(data['edges'][i]['end'])
            for j in range(0, numberofnodes):
                if data['nodes'][j]['inputs']:
                    NumberOfInputsInTheNodes = len(data['nodes'][j]['inputs'])
                    for k in range(0, NumberOfInputsInTheNodes):
                        # print(k)
                        # print(data['nodes'][j]['inputs'][k]['id'])
                        if data['nodes'][j]['inputs'][k]['id'] == data['edges'][i]['end']:
                            if Debug.DEBUG_Low_Level.value: print("Node:", data['nodes'][j]['id'], "Port:", data['edges'][i]['start'],
                                            "is a end of the edge, input of the node")
                            if Debug.DEBUG_Low_Level.value: print("Index of this node is: ", data['nodes'][j]['inputs'][k]['index'])
                            if Debug.DEBUG_Low_Level.value: print("the node above will connect to: ", data['edges'][i]['start'])

                            for l in range(0, numberofnodes):
                                for m in range(0, len(data['nodes'][l]['outputs'])):
                                    if data['nodes'][l]['outputs'][m]['id'] == data['edges'][i]['start']:
                                        if Debug.DEBUG_Low_Level.value: print("its parent node is: ", data['nodes'][l]['id'], "index: ",
                                                        data['nodes'][l]['outputs'][m]['index'])
                                        if Debug.DEBUG_Low_Level.value: print("to: ", data['nodes'][j]['id'],
                                                        data['nodes'][j]['inputs'][k]['index'],
                                                        "from: ", data['nodes'][l]['id'],
                                                        data['nodes'][l]['outputs'][m]['index'])

                                        index = {"index": data['nodes'][j]['inputs'][k]['index']}

                                        socket_type = {"socket_type": data['nodes'][j]['inputs'][k]['socket_type']}
                                        #
                                        if data['nodes'][l]['type'] in ['IN', 'OUT']:
                                            port = {"port": data['nodes'][l]['type'] + '_' + str(
                                                data['nodes'][l]['designator'])}
                                        else:
                                            port = {"port": data['nodes'][l]['type'] + '_' + str(
                                                data['nodes'][l]['designator'])}
                                            # port = {"port": data['nodes'][l]['title'] + '_' + str(data['nodes'][l]['id'])}
                                        #
                                        dst = {"dir": data['nodes'][l]['outputs'][m]['index']}

                                        outputslist = ([dst, index, port, socket_type])

                                        todict = {data['nodes'][j]['id']: outputslist}
                            tolist.append(todict)
                            # outputlist.append([dst, index, port])
                            # print(outputlist)
                            # tolist.append({data['nodes'][j]['id']: outputlist})
                            if Debug.DEBUG_Low_Level.value: print("\n")

        # print('outctrl')
        for i in range(0, numberofedges):
            for j in range(0, numberofnodes):
                if data['nodes'][j]['outctrls']:
                    NumberOfoutctrlsInThdeNodes = len(data['nodes'][j]['outctrls'])
                    for k in range(0, NumberOfoutctrlsInThdeNodes):
                        if data['nodes'][j]['outctrls'][k]['id'] == data['edges'][i]['start']:
                            # print(data['nodes'][j]['outctrls'][k]['id'],'index')
                            for l in range(0, numberofnodes):
                                for m in range(0, len(data['nodes'][l]['inctrls'])):
                                    if data['nodes'][l]['inctrls'][m]['id'] == data['edges'][i]['end']:
                                        # print(data['nodes'][l]['inctrls'][m]['id'],'index')

                                        index = {"index": data['nodes'][j]['outctrls'][k]['index']}
                                        port = {"port": data['nodes'][l]['type'] + '_' + str(
                                            data['nodes'][l]['designator'])}
                                        dst = {"dir": data['nodes'][l]['inctrls'][m]['index']}

                                        outctrls_list = ([dst, index, port])
                                        todict = {data['nodes'][j]['id']: outctrls_list}

                            ctrl_fromlist.append(todict)
                            if Debug.DEBUG_Low_Level.value: print("\n")

            for j in range(0, numberofnodes):
                if data['nodes'][j]['inctrls']:
                    NumberOfinctrlsInThdeNodes = len(data['nodes'][j]['inctrls'])
                    for k in range(0, NumberOfinctrlsInThdeNodes):
                        if data['nodes'][j]['inctrls'][k]['id'] == data['edges'][i]['end']:
                            # print(data['nodes'][j]['inctrls'][k]['id'],'index')
                            for l in range(0, numberofnodes):
                                for m in range(0, len(data['nodes'][l]['outctrls'])):
                                    if data['nodes'][l]['outctrls'][m]['id'] == data['edges'][i]['start']:
                                        # print(data['nodes'][l]['inctrls'][m]['id'],'index')

                                        index = {"index": data['nodes'][j]['inctrls'][k]['index']}
                                        port = {"port": data['nodes'][l]['type'] + '_' + str(
                                            data['nodes'][l]['designator'])}
                                        dst = {"dir": data['nodes'][l]['outctrls'][m]['index']}

                                        inctrls_list = ([dst, index, port])
                                        todict = {data['nodes'][j]['id']: inctrls_list}

                            ctrl_tolist.append(todict)
                            if Debug.DEBUG_Low_Level.value: print("\n")


        if Debug.DEBUG_Low_Level.value: print("FLW Compiled...")
        return {"from": fromlist, "to": tolist, 'ctrl_from':ctrl_fromlist, 'ctrl_to':ctrl_tolist}

    def graphicSort(self, data):
        network = Graph(len(data.findall('AO')))
        for child in data.findall('AO'):
            tos = child.findall('to')
            for to in tos:
                if Debug.DEBUG_Low_Level.value: print('audio object name: %s : %s' %(child.attrib['id'], to.attrib['port']))
                if Debug.DEBUG_Low_Level.value: print('audio object order: %s : %s' %(child.find('order').text, self.port2order(data, to.attrib['port'])))
                network.addEdge(int(child.find('order').text), int(self.port2order(data, to.attrib['port'])))

        sort_result = network.topologicalSort()
        if sort_result:
            header = []
            for index in range(len(sort_result)):
                sub = [data.findall('AO')[index].find('order').text, sort_result[index], index]
                header.append(sub)

            header.sort(key=self.takeSecond)

            for index in range(len(sort_result)):
                data.findall('AO')[index].find('order').text = str(header[index][0])

        return data

    def takeSecond(self, elem):
        return elem[1]

    def port2order(self, data, id):
        for child in data.findall('AO'):
            if child.attrib['id'] == id:
                return child.find('order').text

    def build_AO_connections(self, element_root):
        """
            Build the connection relationship between AO and AO type list.

            :param element_root: XML root element containing AO elements.
            :return: A tuple containing:
                     - ao_connections: Dictionary mapping AO ID to their 'from' and 'to' connections.
                     - ao_types: Dictionary mapping AO ID to their types.
                     - ao_items: Dictionary mapping AO ID to their content.
                     - ao_op_code: Dictionary mapping AO op_code.
        """
        root = element_root
        ao_connections = defaultdict(dict)
        ao_types = {}
        ao_items = {}
        ao_op_code = {}

        for ao in root.findall('AO'):
            ao_id = ao.get('id')
            ao_type = ao.find('type').text
            ao_types[ao_id] = ao_type
            connections = {'from': [], 'to': []}

            # Collect the '<from>' of the current AO
            for from_elem in ao.findall('from'):
                connections['from'].append(from_elem.get('port') + "/" + from_elem.get('index'))
            sorted_items = sorted(connections['from'], key=lambda x: int(x.split('/')[1]))
            result = [item.split('/')[0] for item in sorted_items]
            connections['from'] = result

            # Collect the '<to>' of the current AO
            for to_elem in ao.findall('to'):
                connections['to'].append(to_elem.get('port') + "/" +to_elem.get('index'))
            sorted_items = sorted(connections['to'], key=lambda x: int(x.split('/')[1]))
            result = [item.split('/')[0] for item in sorted_items]
            connections['to'] = result

            ao_connections[ao_id] = connections

        # Collect the content of each AO node
        for node in self.raw_nodes:
            ao_items[str(node['type']) + '_' + str(node['designator'])] = node['content']
            ao_op_code[str(node['type']) + '_' + str(node['designator'])] = node['op_code']

        return ao_connections, ao_types, ao_items, ao_op_code

    def build_all_path(self, ao_connections, ao_types):
        start_node_type = ['IN', 'WAVPLAYER', 'TONEGEN', 'NOISEGEN', 'CHIRP']
        start_nodes = []
        for node, info in ao_connections.items():
            if ao_types[node] in start_node_type:
                start_nodes.append(node)
        all_paths = []

        def trace_paths(node, current_path):
            current_path.append(node)

            if not ao_connections[node]['to']:
                all_paths.append(current_path.copy())
                return

            for next_node in ao_connections[node]['to']:
                trace_paths(next_node, current_path.copy())

        for start_node in start_nodes:
            trace_paths(start_node, [])

        return all_paths

    def calculate_AO_frame_size_and_sample_rate(self, all_paths, ao_connections, ao_types, ao_items):
        frame_sizes = { 'src_output_frame_size': self.device_frame_size }
        sample_rates = { 'src_output_sample_rate': self.device_sample_rate }
        not_support_nodes = []
        if DEBUG: print(all_paths)
        if DEBUG: print(ao_connections)
        if DEBUG: print(ao_types)
        if DEBUG: print(ao_items)
        if DEBUG: print("============== xml generation START ==============")
        start_node_type = ['IN', 'WAVPLAYER', 'TONEGEN', 'NOISEGEN', 'CHIRP']
        end_node_type = ['OUT', 'DUMP', 'VISUALIZER', 'SPECTRUM', 'RTA']

        for path in all_paths:
            frame_sizes['src_output_frame_size'] = self.device_frame_size
            sample_rates['src_output_sample_rate'] = self.device_sample_rate
            if DEBUG: print("Processing path:", len(path),path)
            nonintegerflag = 0
            current_framesize = self.device_frame_size
            for node_index, node in enumerate(path, 1):
                if ao_types[node] == 'SRC':
                    Input_Freq = int(ao_items[node]['srin'][0])
                    Output_Freq = int(ao_items[node]['srout'][0])
                    ratio = Output_Freq / Input_Freq
                    new_framesize = current_framesize * ratio

                    if not new_framesize.is_integer():
                        AO_framesize = int(np.floor(new_framesize))
                        nonintegerflag = 1
                    else:
                        AO_framesize = int(new_framesize)
                        nonintegerflag = 0

                    frame_sizes[node] = current_framesize

                    if Output_Freq == self.device_sample_rate:
                        current_framesize = self.device_frame_size
                        nonintegerflag = 0
                    else:
                        current_framesize = AO_framesize

                    sample_rates[node] = Input_Freq
                    sample_rates['src_output_sample_rate'] = Output_Freq
                elif ao_types[node] in start_node_type or ao_types[node] in end_node_type:
                    if current_framesize != self.device_frame_size:
                        not_support_nodes.append(node)
                        if DEBUG: print(f"Node {node} - accepted frame size are different")
                    frame_sizes[node] = self.device_frame_size
                    current_framesize = self.device_frame_size
                    sample_rates[node] = self.device_sample_rate
                else:
                    if node not in frame_sizes:
                        if nonintegerflag == 1:
                            frame_sizes[node] = current_framesize * 2
                        else:
                            frame_sizes[node] = current_framesize

                    if node in sample_rates:
                        if sample_rates[node] != sample_rates["src_output_sample_rate"]:
                            not_support_nodes.append(node)
                            if DEBUG: print(f"Node {node} - accepted sample rate are different")
                            continue
                    else:
                        sample_rates[node] = sample_rates['src_output_sample_rate']

        if DEBUG: print('frame_sizes', frame_sizes)
        if DEBUG: print('sample_rates', sample_rates)
        if DEBUG: print("============== xml generation END ==============")
        return frame_sizes, sample_rates, not_support_nodes


    def add_child_to_AOs(self, frame_sizes, sample_rates):
        """
            Add 'framesize' and 'samplerate' as child elements to all AO elements in the XML tree.

            :param frame_sizes: Dictionary storing the frame_sizes for AO elements. {ao_id: framesize}
            :param sample_rates: Dictionary storing the samplerate for AO elements. {ao_id: samplerate}
        """
        for ao in self.root.findall('AO'):
            child = ET.SubElement(ao, 'framesize')
            child.text = str(frame_sizes[ao.get('id')])

            child1 = ET.SubElement(ao, 'samplerate')
            child1.text = str(sample_rates[ao.get('id')])

    def check_the_settings_of_SRC_sample_rate(self, all_paths, ao_types, ao_items, ao_op_code, sample_rates, not_support_nodes):
        for i, path in enumerate(all_paths, 1):
            if DEBUG: print(f"verify path {i}: {' → '.join(path)}")
            for j, node in enumerate(path, 1):
                if ao_types.get(node) == 'SRC':
                    if ao_types.get(path[j-2]) == 'SRC':
                        if (int(ao_items[node]['srin'][0]) != int(ao_items[path[j-2]]['srout'][0])):
                            if DEBUG: print(f"{node}: Input sample rate does not match output sample rate of previous SRC node {path[j-2]}.")
                            not_support_nodes.append(node)
                            continue

                    elif sample_rates[node] != sample_rates[path[j-2]]:
                        if DEBUG: print(f"{node}: Sample rate mismatch with previous node {path[j-2]}.")
                        not_support_nodes.append(node)
                        continue

                    elif (int(ao_items[node]['srin'][0]) != self.device_sample_rate
                            and int(ao_items[node]['srout'][0]) != self.device_sample_rate):
                        if DEBUG: print(f"{node}: Input and output sample rates do not match device sample rate.")
                        not_support_nodes.append(node)
                        continue

            sample_rate = self.device_sample_rate
            for node in path:
                if ao_types.get(node) == 'SRC':
                    sample_rate = ao_items[node]['srout'][0]

                if ao_op_code[node] in AOS_ONLY_ALLOW_PC_SIXTEEN_K_SR:
                    if int(sample_rate) != 16000:
                        not_support_nodes.append(node)

                if ao_op_code[node] in AOS_ONLY_ALLOW_FORTY_EIGHT_K_SR:
                    if int(sample_rate) != 48000:
                        not_support_nodes.append(node)

        if DEBUG: print('not_support_nodes:', not_support_nodes)
        return list(set(not_support_nodes))