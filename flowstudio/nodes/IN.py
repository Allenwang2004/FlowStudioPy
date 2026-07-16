from flowstudio.flow_conf import *
from flowstudio.flow_node_base import *
from control.flow_control_widget import *
from flowstudio.flow_window_connection import *
from control.flow_widget_plot import *
# Removed the module-level import of Switch
from flowstudio.controls.MeterComponets import ModernMeterBar, ModernMeterGUIBase

thread_timeout = 50


class IN_GUI(FLOW_GUI, ModernMeterGUIBase):
    """
    Modern Input GUI using reusable meter components.
    """

    cSocket = FLOW_Window_Connection.client

    def __init__(self, node):
        super().__init__(node)
        ModernMeterGUIBase.__init__(self)

        # Create the modern meter without top label
        self.meter = ModernMeterBar("INPUT", show_label=False)

        # Setup styling and layout
        self.setup_styling()
        self.init_controls()
        self.init_layout()

        self.isConnected = False

    def setup_styling(self):
        """Setup modern styling using the base class."""
        self.setup_base_styling(self)

    def closeEvent(self, a0: QCloseEvent) -> None:
        super().closeEvent(a0)
        self.toggle(False)
        if hasattr(self, 'display'):
            self.display.toggle.setChecked(False)

    def init_controls(self):
        """Initialize control widgets."""
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.fetchData)

        # Create modern toggle switch
        from flowstudio.controls.Switch import Switch  # Moved import here to avoid cyclic dependency
        self.display = Switch('update', 'off').get_widget(self)
        self.display.toggle.toggled.connect(self.toggle)

    def init_layout(self):
        """Setup the layout with modern spacing and alignment."""
        self.setFixedSize(90, 280)  # Increased width from 80 to 100

        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(self.config.MARGIN, self.config.MARGIN,
                                       self.config.MARGIN, self.config.MARGIN)
        main_layout.setSpacing(self.config.SPACING)

        # Add the meter widget
        main_layout.addWidget(self.meter, alignment=Qt.AlignCenter)

        # Add some spacing before controls
        main_layout.addSpacing(8)

        # Add controls using the base class helper
        self.add_controls_to_layout(main_layout, [self.display])

    def toggle(self, bool_val):
        """Toggle meter updates with improved error handling."""
        if self.isConnected and not bool_val:
            try:
                self.client.terminate()
                self.client.wait(thread_timeout)
                self.client.logout(index=1)
                self.timer.stop()
                self.clean_plot()
                self.isConnected = False
                if Debug.DEBUG_THREAD.value:
                    print(f'{self.__class__.__name__}: thread terminate')
            except Exception as e:
                print(f"Error during disconnect: {e}")

        elif not self.isConnected and bool_val and self.cSocket.connection:
            try:
                self.client = self.cSocket.createClient()
                self.client.login()
                self.timer.start(thread_timeout)
                self.isConnected = True
                if Debug.DEBUG_THREAD.value:
                    print(f'{self.__class__.__name__}: thread init')
            except Exception as e:
                print(f"Error during connect: {e}")

    def fetchData(self):
        """Fetch data with improved error handling."""
        if not (self.cSocket.connection and not self.client.isRunning()):
            if not self.cSocket.connection and self.isConnected:
                self.toggle(False)
                self.display.toggle.setChecked(False)
            elif self.client.isRunning():
                if Debug.DEBUG_THREAD.value:
                    print(f'{self.node}: current query is still running, skip this query.')
            return

        try:
            AO_Name = self.node.content_label_objname + "_" + str(self.node.designator)
            Parameter_Name = "Level"
            cmd = f"getSerialized/{AO_Name}/{Parameter_Name}/"

            self.client.setQueryTask(cmd, 16)
            self.client.start()

            # Adaptive timeout based on target
            if self.client.target in [Target.AIROHA_AB1585_UART.value,
                                      Target.AIROHA_AB1565_UART.value,
                                      Target.FLOW_APO.value]:
                self.client.wait(150)
            else:
                self.client.wait(thread_timeout)

            if self.client.result[0]:
                self.process()
            else:
                self.toggle(False)
                self.display.toggle.setChecked(False)

        except Exception as e:
            print(f"Error fetching data: {e}")

    def clean_plot(self):
        """Reset meter to minimum value."""
        self.meter.reset()

    def process(self):
        """Process incoming data and update meter."""
        try:
            # Parse the incoming data (same logic as original)
            magnitude = float(self.client.result[1].decode().split('/')[0])

            # Update the meter with the new level
            self.meter.set_level(magnitude)

        except (ValueError, IndexError) as e:
            print(f"Error processing input data: {e}")


@register_node(OP_NODE_ADC)
class FLOW_Node_IN(FLOW_Node):
    """
    Input node using modern meter components.
    """
    op_code = OP_NODE_ADC
    op_title = "IN"
    content_label_objname = "IN"
    display_name = 'Input'
    info = 'An audio capture interface from your target device physical hardware'
    openable = True

    def __init__(self, scene):
        super().__init__(scene, inputs=[], outputs=[1])
        self.eval()

    def initInnerClasses(self):
        self.manager = FLOW_Ctrl_Manager(self.content_label_objname)
        self.content = FLOW_Content(self)
        self.grNode = FLOW_GraphicsNode(self)
        self.widget = IN_GUI(self)
