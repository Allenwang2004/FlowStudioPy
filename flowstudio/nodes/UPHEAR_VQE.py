from flowstudio.flow_conf import *
from flowstudio.flow_node_base import *
DEBUG_Tweaker = False
@register_node(OP_NODE_UPHEAR_VQE)
class FLOW_Node_UPHEAR_VQE(FLOW_Node):
    icon = '../resources/upHear-VQE-icon.png'
    op_code = OP_NODE_UPHEAR_VQE
    op_title = "upHear VQE"
    content_label_objname = "upHear VQE"
    display_name = 'upHear VQE'
    info = "Smart-assistant-ecosystem agnostic microphone processing technology that extracts the user’s voice<br><a href='https://www.iis.fraunhofer.de/en/ff/amm/communication/uphear-vqe.html'>https://www.iis.fraunhofer.de/en/ff/amm/communication/uphear-vqe.html</a>"
    expandable = True
    linkType = 1
    type_ao_addition = TypeAOAddition.DYNAMIC_NUM_INPUTS_AND_OUTPUTS.value

    def __init__(self, scene, mic, ref):
        self.message_box = 0
        self.inputs = []
        for i in range(mic):
            self.inputs.append(1)
        for i in range(ref):
            self.inputs.append(1)
        super().__init__(scene, self.inputs, [1], mic=mic, ref=ref)
        self.initControl()
        self.eval()

        change_channel_implementation().VQE_change_channel(self.manager, mic)
        self.UrocMicSetupMenuChange()
        self.manager.widgetSet['UrocMicSetup'].valueChanged.connect(self.UrocMicSetupMenuChange)

        # self.ProcessmodeMenuChange()
        # self.manager.widgetSet['processmode'].valueChanged.connect(self.ProcessmodeMenuChange)
        # self.manager.widgetSet['id'].valueChanged.connect(self.idMenuChange)

        self.manager.widgetSet['MicDist1'].valueChanged.connect(self.MicDistValueChange)
        self.manager.widgetSet['MicDist2'].valueChanged.connect(self.MicDistValueChange)

    def initInnerClasses(self):
        self.manager = FLOW_Ctrl_Manager(self.content_label_objname)
        self.content = FLOW_Content(self)
        self.grNode = FLOW_GraphicsNode(self)
        # self.manager.widgetSet['FrameSize'].comboBox.model().item(0).setEnabled(False)
        # self.manager.widgetSet['FrameSize'].comboBox.model().item(2).setEnabled(False)
        for key in ['FrameSize', 'UrocMicSetup', 'id', 'processmode']:
            self.manager.widgetSet[key].comboBox.setStyleSheet("QComboBox\n"
                                                                      "{\n"
                                                                      "    color: black;\n"
                                                                      "}\n"
                                                                      "\n"
                                                                      "QComboBox QAbstractItemView\n"
                                                                      "{\n"
                                                                      "     border: 1px solid rgb(161,161,161);\n"
                                                                      "}\n"
                                                                      "\n"
                                                                      "QComboBox QAbstractItemView::item\n"
                                                                      "{\n"
                                                                      "    height: 24px;\n"
                                                                      "}\n"
                                                                      "\n"
                                                                      "QComboBox QAbstractItemView::item:selected\n"
                                                                      "{    \n"
                                                                      "    background-color: rgba(54, 98, 180);\n"
                                                                      "}\n"
                                                                      "\n"
                                                                      "QComboBox::item:!enabled\n"
                                                                      "{\n"
                                                                      "    color: gray;\n"
                                                                      "}")



    def UrocMicSetupMenuChange(self):
        if self.manager.widgetSet['UrocMicSetup'].widget_value[0] != 'QUAD_NONULA':
            self.manager.widgetSet['MicDist2'].numbox.setValue(0.00)
            self.manager.widgetSet['MicDist2'].slider.setValue(0.00)
            self.manager.widgetSet["MicDist2"].disableWidget(True)
        else:
            self.manager.widgetSet["MicDist2"].disableWidget(False)

        if self.manager.widgetSet['UrocMicSetup'].widget_value[0] == 'SINGLE':
            self.manager.widgetSet['MicDist1'].numbox.setValue(0.00)
            self.manager.widgetSet['MicDist1'].slider.setValue(0.00)
            self.manager.widgetSet["MicDist1"].disableWidget(True)
        else:
            self.manager.widgetSet["MicDist1"].disableWidget(False)

    # def ProcessmodeMenuChange(self):
    #     self.manager.widgetSet['processmode'].comboBox.model().item(0).setEnabled(False)
    #     self.manager.widgetSet['id'].comboBox.model().item(0).setEnabled(False)
    #     self.manager.widgetSet['id'].comboBox.model().item(1).setEnabled(False)
    #     self.manager.widgetSet['id'].comboBox.model().item(2).setEnabled(False)
    #
    #     if self.manager.widgetSet['processmode'].widget_value[1] == 1:
    #         self.manager.widgetSet['id'].comboBox.setCurrentIndex(0)
    #         self.manager.widgetSet['id'].comboBox.model().item(0).setEnabled(True)
    #         self.manager.widgetSet['id'].comboBox.model().item(2).setEnabled(True)
    #     elif self.manager.widgetSet['processmode'].widget_value[1] == 2:
    #         self.manager.widgetSet['id'].comboBox.setCurrentIndex(1)
    #         self.manager.widgetSet['id'].comboBox.model().item(1).setEnabled(True)

    # def idMenuChange(self):
    #     if self.manager.widgetSet['id'].widget_value[0] == '10011':
    #         self.manager.widgetSet["agc"].disableWidget(False)
    #         self.manager.widgetSet['FrameSize'].comboBox.model().item(0).setEnabled(True)
    #         self.manager.widgetSet["FilterLength"].disableWidget(False)
    #         self.manager.widgetSet["numSpk"].disableWidget(False)
    #     elif self.manager.widgetSet['id'].widget_value[0] == '10013':
    #         self.manager.widgetSet["agc"].disableWidget(True)
    #         self.manager.widgetSet['agc'].numbox.setValue(0.00)
    #         self.manager.widgetSet['agc'].slider.setValue(0.00)
    #         self.manager.widgetSet['FrameSize'].comboBox.model().item(0).setEnabled(False)
    #         self.manager.widgetSet["FilterLength"].disableWidget(True)
    #         self.manager.widgetSet['FilterLength'].numbox.setValue(0)
    #         self.manager.widgetSet['FilterLength'].slider.setValue(0)
    #         self.manager.widgetSet["numSpk"].disableWidget(True)
    #         self.manager.widgetSet['numSpk'].numbox.setValue(0)
    #         self.manager.widgetSet['numSpk'].slider.setValue(0)
    #         self.manager.widgetSet['UrocMicSetup'].comboBox.setCurrentIndex(1)
    #     else:
    #         self.manager.widgetSet["agc"].disableWidget(True)
    #         self.manager.widgetSet['agc'].numbox.setValue(0.00)
    #         self.manager.widgetSet['agc'].slider.setValue(0.00)
    #         self.manager.widgetSet['FrameSize'].comboBox.model().item(0).setEnabled(True)
    #         self.manager.widgetSet["FilterLength"].disableWidget(False)
    #         self.manager.widgetSet["numSpk"].disableWidget(False)

    def MicDistValueChange(self):

        if self.manager.widgetSet['MicDist2'].widget_value == self.manager.widgetSet['MicDist1'].widget_value * 3 and \
            self.manager.widgetSet['MicDist2'].widget_value !=0:

            self.message_box = self.message_box + 1
            if self.message_box % 2 == 0:
                statement = "The value of MicDist2 cannot be set to three times the value of MicDist1 (d2 != 3 * d1)"
                QMessageBox.about(self.scene.getView().window(), "Error Tip", "%s" % statement)
                self.manager.widgetSet['MicDist2'].numbox.setValue(self.manager.widgetSet['MicDist2'].widget_value - 1)


    def tweaker(self, key):
        cmd = None
        AO_Name = self.content_label_objname + "_" + str(self.designator)
        if key == "UrocMicSetup":
            Parameter_Value = self.manager.widgetSet[key].widget_value[1]
            if Parameter_Value >= 15:
                Parameter_Value += 2
            elif Parameter_Value > 7:
                Parameter_Value += 1
            cmd = "setCoord/%s/%s/%s/0/0" % (AO_Name, key, Parameter_Value)
        elif key == "FrameSize":
            Parameter_Value = self.manager.widgetSet[key].widget_value[0]
            cmd = "setCoord/%s/%s/%s/0/0" % (AO_Name, key, Parameter_Value)
        elif key == "processmode":
            Parameter_Value = self.manager.widgetSet[key].widget_value[1]
            Parameter_Value = 17 if Parameter_Value == 2 else Parameter_Value
            cmd = "setCoord/%s/%s/%s/0/0" % (AO_Name, key, Parameter_Value)
        elif key == "id":
            Parameter_Value = self.manager.widgetSet[key].widget_value[0]
            cmd = "setCoord/%s/%s/%s/0/0" % (AO_Name, key, Parameter_Value)
        else:
            AO_Name = self.content_label_objname + "_" + str(self.designator)
            Parameter_Name = key
            Parameter_Value = self.manager.widgetSet[key].widget_value[1] if isinstance(
                self.manager.widgetSet[key].widget_value, list) else self.manager.widgetSet[key].widget_value
            cmd = "setCoord/%s/%s/%s/0/0" % (AO_Name, Parameter_Name, Parameter_Value)

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