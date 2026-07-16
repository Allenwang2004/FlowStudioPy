from flowstudio.flow_conf import *
from flowstudio.flow_node_base import *
from control.flow_control_widget import *
from flowstudio.flow_window_connection import *
from control.flow_widget_plot import *
from flowstudio.controls.MeterComponets import ModernMeterContainer, ModernMeterGUIBase

thread_timeout = 50


class METER_GUI(FLOW_GUI, ModernMeterGUIBase):
    """
    Modern multi-channel meter GUI using reusable meter components.
    """

    cSocket = FLOW_Window_Connection.client

    def __init__(self, node):
        super().__init__(node)
        ModernMeterGUIBase.__init__(self)

        # Create the modern meter container for multiple channels
        channel_count = len(node.inputs)
        channel_labels = [f"CH {i + 1}" for i in range(channel_count)]
        self.meters = ModernMeterContainer(channel_count, channel_labels)

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
        self.display = Switch('update', 'off').get_widget(self)
        self.display.toggle.toggled.connect(self.toggle)

    def init_layout(self):
        """Setup the layout with modern spacing and alignment."""
        # Calculate size based on meter count
        meter_count = len(self.node.inputs)
        widget_width = (self.config.METER_WIDTH + 25 + self.config.SPACING) * meter_count + self.config.MARGIN * 2
        widget_height = self.config.METER_HEIGHT + 130  # Increased space for controls

        self.setFixedSize(max(widget_width, 150), widget_height)

        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(self.config.MARGIN, self.config.MARGIN,
                                       self.config.MARGIN, self.config.MARGIN)
        main_layout.setSpacing(self.config.SPACING)

        # Add the meters container
        main_layout.addWidget(self.meters, alignment=Qt.AlignCenter)

        # Add some spacing before controls
        main_layout.addSpacing(10)

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
            cmd = f"getAllCol/{AO_Name}/{Parameter_Name}/"

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
        """Reset all meters to minimum values."""
        self.meters.reset_all()

    def process(self):
        """Process incoming data and update all meters."""
        try:
            # Parse the incoming data (same logic as original)
            magnitude_strings = self.client.result[1].decode().split('/')

            # Convert to float values
            db_values = []
            for i, mag_str in enumerate(magnitude_strings):
                if i < len(self.node.inputs):  # Only process valid channels
                    try:
                        db_value = float(mag_str)
                        db_values.append(db_value)
                    except ValueError:
                        db_values.append(-120.0)  # Default to silence on error

            # Update all meters at once using the container's method
            self.meters.set_levels(db_values)

        except (ValueError, IndexError) as e:
            print(f"Error processing meter data: {e}")


@register_node(OP_NODE_METER)
class FLOW_Node_METER(FLOW_Node):
    """
    Multi-channel level meter node using modern meter components.
    """
    op_code = OP_NODE_METER
    op_title = "METER"
    content_label_objname = "METER"
    display_name = 'Level Meter'
    info = 'Signal level detector using peak metering with pre-defined attack and release time'
    openable = True
    linkType = 2
    type_ao_addition = TypeAOAddition.DYNAMIC_NUM_CHANNELS.value

    def __init__(self, scene, channel):
        self.inputs = []
        for i in range(channel):
            self.inputs.append(1)
        super().__init__(scene, self.inputs, outputs=[])
        self.eval()

    def initInnerClasses(self):
        self.manager = FLOW_Ctrl_Manager(self.content_label_objname)
        self.content = FLOW_Content(self)
        self.grNode = FLOW_GraphicsNode(self)
        self.widget = METER_GUI(self)