from flowstudio.flow_conf import *
from flowstudio.flow_node_base import *

@register_node(OP_NODE_MUX)
class FLOW_Node_MUX(FLOW_Node):
    #icon = "icons/in.png"
    op_code = OP_NODE_MUX
    op_title = "MUX"
    content_label_objname = "MUX"
    display_name = 'Multiplexer'
    info = 'The Mux function serves as a multiplexer that combines multiple input signals and allows the selection of a specific input to be routed to the output.'
    expandable = False
    expand = True
    linkType = 2
    type_ao_addition = TypeAOAddition.DYNAMIC_NUM_OUTPUTS_AND_FOUR_TIMES_INPUTS.value

    def __init__(self, scene, out, type=""):
        self.inputs = []
        self.outputs = []
        self.type = type
        for i in range(out*4):
            self.inputs.append(1)
        for i in range(out):
            self.outputs.append(1)
        super().__init__(scene, self.inputs, self.outputs)
        self.initControl()
        self.eval()

    def initSocketTooltip(self):
        for i in range(len(self.inputs)):
            self.inputs[i].grSocket.setToolTip("input " + str(i + 1))
        self.outputs[0].grSocket.setToolTip("output")

    def initInnerClasses(self):
        self.manager = FLOW_Ctrl_Manager(self.content_label_objname)
        self.content = FLOW_Content(self)
        self.grNode = FLOW_GraphicsNode(self)

        # Execute when opening a file
        if self.type != '' and self.scene.filename != None:
            filename = self.scene.filename
            # Retrieve data from the. json file
            with open(filename, "r") as file:
                raw_data = file.read()
                try:
                    data = json.loads(raw_data)
                    for node in data['nodes']:
                        if node['op_code'] == OP_NODE_MUX and node['title'] == self.type:
                            self.update_labels(node['labels'])
                    self.type = ""
                except Exception as e:
                    dumpException(e)
        # Execute when  add channel or reduce channel
        else:
            items = []
            l = []
            for i in range(1, len(self.inputs) + 1, len(self.outputs)):
                l.append(i)
            for i in range(4):
                items.append('Ch %s - %s' % (l[i], l[i] + len(self.outputs) - 1))

            self.update_labels(items)

    def serialize(self):
        res = super().serialize()
        res['content']['ch'] = 1
        return res

    # Modify the label of the button and drop-down box
    def update_labels(self, items):
        self.manager.widgetSet['select'].comboBox.clear()
        self.manager.widgetSet['select'].comboBox.addItems(items)

        index = 0
        for button in self.manager.widgetSet['select'].default_buttons:
            button.setText(items[index])
            index = index + 1