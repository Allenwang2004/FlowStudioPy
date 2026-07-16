from flowstudio.flow_conf import *
from flowstudio.flow_node_base import *
from control.flow_widget_knob import QDoubleDial, QIntegerDial

@register_node(OP_NODE_MIXER_FP)
class FlowNodeMixerFP(FlowFixedPointNode):
    # icon = "icons/in.png"
    op_code = OP_NODE_MIXER_FP
    op_title = "MIXER_FP"
    content_label_objname = "MIXER_FP"
    display_name = 'Mixer (fixed-point)'
    info = 'Fixed-point version of MIXER'
    linkType = 2
    expandable = False
    expand = True
    DEBUG_Tweaker = False
    type_ao_addition = TypeAOAddition.DYNAMIC_NUM_INPUTS_AND_OUTPUTS.value

    def __init__(self, scene, m_in , m_out):
        self.inputs = []
        self.outputs = []
        self.tap = m_out
        for i in range(m_in):
            self.inputs.append(1)
        for i in range(m_out):
            self.outputs.append(1)
        super().__init__(scene, self.inputs, self.outputs)
        self.initControl()
        self.eval()
        self.renameTextLabel()

    def renameTextLabel(self):

        for i in range(len(self.outputs)):
            for j in range(8):
                str = 'MixGain_%s_%s' % (j, i)
                self.manager.widgetSet[str].setVisible(False)

        for i in range(len(self.inputs)):
            for j in range(len(self.outputs)):
                str = 'MixGain_%s_%s' % (i, j)
                self.manager.widgetSet[str].setVisible(True)


    def tweaker(self, key):
        AO_Name = self.content_label_objname + "_" + str(self.designator)
        Parameter_Index = key[0]
        Parameter_Name = key[1]
        Parameter_Value = self.manager.widgetSet[key[2]].widget_value[1] if isinstance(
            self.manager.widgetSet[key[2]].widget_value, list) else self.manager.widgetSet[key[2]].widget_value
        cmd = "setCoord/%s/%s/%s/%s/%s/" % (AO_Name, Parameter_Name, Parameter_Value,  Parameter_Index, key[2][-1])

        if Debug.DEBUG_TWEAKER.value: print(" _> %s control command: %s" % (self.__class__.__name__, cmd))

        if self.cSocket.connection:
            while self.cSocket.mainSocket.isRunning():
                time.sleep(0.01)
            if not self.cSocket.mainSocket.isRunning():
                self.cSocket.mainSocket.setQueryTask(cmd, 16)
                self.cSocket.mainSocket.start()
                if Debug.DEBUG_TWEAKER.value: print(" _> %s thread process: success" % (self.__class__.__name__))
            else:
                if Debug.DEBUG_TWEAKER.value: print(" _> %s thread process: failed" % (self.__class__.__name__))