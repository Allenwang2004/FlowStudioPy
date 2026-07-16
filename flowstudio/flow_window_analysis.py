from template.analysis_dialog import Ui_Dialog
from control.flow_widget_plot import *

class FLOW_Window_Analysis(object):

    def __init__(self, parent, dialog):
        super().__init__()
        self.window = parent

        # init from ui template file
        self.controlDialog = Ui_Dialog()
        self.controlDialog.setupUi(dialog)

        self.plotWidget = waveform(dialog)
        self.controlDialog.horizontalLayout.addWidget(self.plotWidget)

        #init a dill instance
        #get the ui parmeter here
        #parmeter value send into dll
        #request output from dll
        #plot widget update