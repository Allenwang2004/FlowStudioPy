from flowstudio.flow_conf import Debug
from flowstudio.flow_conf_list import *
from control.flow_control_widget import *
import copy
from controls.Switch import Switch
from controls.FileLoader import FileLoader
from controls.Label import Label
from controls.Button import Button
from controls.Menu import Menu
from controls.MuxMenu import MuxMenu
from controls.SpecialFloatSpinBox import SpecialFloatSpinBox
from controls.LinearIntSliderAndSpinBox import LinearIntSliderAndSpinBox
from controls.LogIntSliderAndSpinBox import LogIntSliderAndSpinBox
from controls.LinearFloatSliderAndSpinBox import LinearFloatSliderAndSpinBox
from controls.LogFloatSliderAndSpinBox import LogFloatSliderAndSpinBox
from controls.SpinBox import SpinBox
from controls.TapMenu import TapMenu


@enum.unique
class GUIType(enum.Enum):
    NODE_GUI = 0
    POPUP_GUI = 1


fc_value = [
    [1000],
    [100, 4000],
    [100, 630, 4000],
    [100, 315, 1000, 3150],
    [63, 250, 1000, 4000, 16000],
    [50, 160, 500, 1600, 5000, 16000],
    [40, 100, 250, 630, 1600, 4000, 10000],
    [32, 80, 200, 500, 1250, 3150, 8000, 16000],
    [32, 63, 125, 250, 500, 1000, 2000, 4000, 8000],
    [32, 63, 125, 250, 500, 1000, 2000, 4000, 8000, 16000]
]

class FLOW_Ctrl_Manager(object):

    def __init__(self, content_label_objname = None, is_temp=False, **kwargs):
        """
        :param content_label_objname: an attribute to present the type of 'Node' in :class:FLOW_Node
        :type content_label_objname: str
        :param **kwargs: a dict to construct the class
        :type **kwargs: dict
        """
        if content_label_objname == None:
            self.config = kwargs
            self.mode = GUIType.POPUP_GUI.value
        else:
            if not is_temp:
                self.config = copy.deepcopy(AUDIO_OBJECT[content_label_objname])
            else:
                self.config = copy.deepcopy(AUDIO_OBJECT_TEMP[content_label_objname])
            self.mode = GUIType.NODE_GUI.value
        self.tap_menu_parameter_name = None
        for parameter_name, parameter_value in self.config.items():
            if type(parameter_value) is TapMenu:
                self.tap_menu_parameter_name = parameter_name

        self.initAssets()

    def initAssets(self):
        self.font = QFont("Calibri", 10)
        # self.font.setFamily("Calibri")

        self.size = self.config

        self.parameterSet = OrderedDict()
        self.widgetSet = OrderedDict()

    @property
    def config(self):
        return self._config

    @config.setter
    def config(self, new_data):
        self._config = new_data

    @property
    def size(self):
        return self._size

    @size.setter
    def size(self, new_data: dict):
        if new_data.__contains__(self.tap_menu_parameter_name):
            self._size = new_data[self.tap_menu_parameter_name].parameters["cSize"] + len(self.config)
        else:
            self._size = len(self.config)

    def initNodeParam(self, parent: QWidget, parameterStored: bool):
        self.content = parent
        for key in self.config:
            parameter = self.config[key]
            res = self.createControlInterface(key, parameter, parent)
            if parameterStored: res.valueStored.connect(self.parameterStored)
            self.widgetSet[key] = res
            if key == self.tap_menu_parameter_name and parameter.parameters['pSize']:
                for i in range(parameter.parameters["pSize"]):
                    child_widget = res.widget(i)
                    for child_key in parameter.parameters["cParameter"]:
                        child_name = "%s_%i" % (child_key, i)

                        # fc in PEQ
                        if child_key == 'fc':
                            fc = fc_value[parameter.parameters['pSize'] - 1]
                            if 0 <= i <= 9:
                                parameter.parameters["cParameter"][child_key].parameters['pValue'] = fc[i]

                        child = self.createControlInterface(child_key, parameter.parameters["cParameter"][child_key],child_widget)
                        if parameterStored: child.valueStored.connect(self.parameterStored)
                        self.widgetSet[child_name] = child

    def initGUIParam(self, parent: QWidget, parameterChanged: bool):
        pass

    def initPos(self):
        startPos, tapStartPos, res = 0, 0, 0
        for key in self.config:
            self.widgetSet[key].move(10, 10 + startPos)
            startPos = startPos + self.widgetSet[key].row_height
            if not key == self.tap_menu_parameter_name:
                res = startPos
            else:
                for index in range(self.config[self.tap_menu_parameter_name].parameters['pSize']):
                    tapStartPos = 0
                    for child_key in self.config[self.tap_menu_parameter_name].parameters["cParameter"]:
                        child_name = "%s_%i" %(child_key, index)
                        self.widgetSet[child_name].move(0, 10 + tapStartPos)
                        tapStartPos = tapStartPos + self.widgetSet[child_name].row_height
                    res = tapStartPos + startPos
        return res

    def createControlInterface(self, key: str, parameter, widget):
        return parameter.get_widget(widget, self.mode)

    @property
    def Parameter(self):
        for key in self.widgetSet:
            self.parameterSet[key] = self.widgetSet[key].widget_value
        return self.parameterSet

    @Parameter.setter
    def Parameter(self, data: OrderedDict=None):
        for key in self.widgetSet:
            self.widgetSet[key].widget_value = data[key]

    def parameterStored(self):
        '''
        parameterChanged is a pyqtSlot type method, which is connected to QWidget::valueChanged a pyqtSignal.
        once parameterChanged is triggered, history stack will be save by 2 condition:
        1. once the sender() of parameterChanged is switch -> to save history stack while switched parameter widget
        2. hovered flag -> supplement of above expression, so we use hoverflag to make sure an real user is operating not redo/undo function
        :return:
        '''
        if self.content.node.is_temp_node:
            return
        self.content.node.scene.history.storeHistory("Change parameter %s" % self.content.node.__class__.__name__,
                                                     setModified=True)
        if Debug.DEBUG_Low_Level.value: print("Change parameter %s" % self.content.node.__class__.__name__)



