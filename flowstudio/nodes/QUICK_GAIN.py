import threading
from flowstudio.flow_node_base import *
from flowstudio.flow_window_connection import *
from control.flow_widget_plot import *
from flowstudio.controls.MeterComponets import ModernMeterBar, ModernMeterGUIBase

thread_timeout = 50


class QUICK_GAIN_GUI(FLOW_GUI, ModernMeterGUIBase):
    """
    Modern AUTO GAIN GUI using reusable meter components.
    """

    cSocket = FLOW_Window_Connection.client

    def __init__(self, node):
        super().__init__(node)
        ModernMeterGUIBase.__init__(self)

        # Create the modern meter without top label
        self.meter = ModernMeterBar("AUTO GAIN", show_label=False)

        # Setup styling and layout
        self.setup_styling()
        self.init_controls()
        self.init_layout()

        self.isConnected = False

    def set_button_states(self, start_text=None, start_disabled=None,
                         reset_text=None, reset_disabled=None):
        """Helper method to set button states."""
        if start_text is not None:
            self.start_btn.setText(start_text)
        if start_disabled is not None:
            self.start_btn.setDisabled(start_disabled)
        if start_disabled:
            self.start_btn.setStyleSheet("background: #353535; color: white;font-size: 15px;")
        else:
            self.start_btn.setStyleSheet("background: #696969; color: white;font-size: 15px;")

        if reset_text is not None:
            self.reset_btn.setText(reset_text)
        if reset_disabled is not None:
            self.reset_btn.setDisabled(reset_disabled)
        if reset_disabled:
            self.reset_btn.setStyleSheet("background: #353535; color: white;font-size: 15px;")
        else:
            self.reset_btn.setStyleSheet("background: #696969; color: white;font-size: 15px;")

    def showEvent(self, event):
        super().showEvent(event)
        AO_Name = f"{self.node.content_label_objname}_{self.node.designator}"
        if self.cSocket.connection:
            self.db_display.setText("Loading...")
            self.set_button_states(
                start_text='Starting Rec...',
                start_disabled=True,
                reset_disabled=True
            )


            self.gain_timer = QTimer()
            self.gain_timer.timeout.connect(lambda: self.check_gain_status(AO_Name))
            self.gain_timer.start(500)

    def check_gain_status(self, ao_name):
        try:
            cmd = f"get/{ao_name}/remainedRecTime/"
            res = self.tweaker(cmd)

            if res and res[1].decode('utf-8').strip('\n\x00') == '0.':
                self.gain_timer.stop()
                cmd = f"get/{ao_name}/appliedGain/"
                res = self.tweaker(cmd)
                if res:
                    self.db_display.setText(res[1].decode('utf-8').strip('\n\x00') + " dB")
                    self.set_button_states(
                        start_text='Start Rec',
                        start_disabled=False,
                        reset_disabled=False
                    )
        except Exception as e:
            self.gain_timer.stop()
            print(f"Error checking gain status: {e}")


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
        label_width = 120
        spinbox_width = 60
        label_style = "font-size: 18px;"
        spinbox_style = "font-size: 18px;background: #606060;"

        # Main window setup
        self.setFixedSize(420, 300)  # Wider to accommodate both panels
        self.setStyleSheet("background: #212121; color: white;")

        # Main layout
        main_layout = QHBoxLayout(self)
        main_layout.setContentsMargins(10, 10, 10, 10)  # Outer margins
        main_layout.setSpacing(20)  # Space between left/right panels

        # --- Left Panel (Meter) ---
        left_layout = QVBoxLayout()
        left_layout.setContentsMargins(self.config.MARGIN, self.config.MARGIN,
                                       self.config.MARGIN, self.config.MARGIN)
        left_layout.setSpacing(self.config.SPACING)
        left_layout.addWidget(self.meter, alignment=Qt.AlignCenter)

        self.add_controls_to_layout(left_layout, [self.display])

        # --- Right Panel (Controls) ---
        right_layout = QVBoxLayout()

        # Add controls dynamically
        controls = [
            ("onoff", label_width, label_style, None),
            ("targetLUFS", label_width, label_style, spinbox_width),
            ("recTime", label_width, label_style, spinbox_width),
            ("minThreshold", label_width, label_style, spinbox_width)
        ]
        for control_name, lbl_width, lbl_style, spin_width in controls:
            control = self.gui_manager.widgetSet[control_name]
            control.label.setFixedWidth(lbl_width)
            control.label.setStyleSheet(lbl_style)
            if spin_width:
                control.spinbox.setFixedWidth(spin_width)
                control.spinbox.setStyleSheet(spinbox_style)
            right_layout.addWidget(control, alignment=Qt.AlignCenter)

        # Large dB display
        self.db_display = QLabel("0 dB")
        self.db_display.setAlignment(Qt.AlignCenter)
        self.db_display.setStyleSheet("font-size: 32px; font-weight: bold;")
        self.db_display.setFixedHeight(50)
        right_layout.addWidget(self.db_display, alignment=Qt.AlignCenter)

        # Auto Gain label
        auto_label = QLabel("Auto Gain Applied")
        auto_label.setAlignment(Qt.AlignCenter)
        auto_label.setStyleSheet(label_style)
        right_layout.addWidget(auto_label, alignment=Qt.AlignCenter)

        # Button row
        button_layout = QHBoxLayout()
        button_layout.setSpacing(10)
        self.reset_btn = self.gui_manager.widgetSet["resetGain"].button
        self.start_btn = self.gui_manager.widgetSet["startRec"].button
        for btn, handler in [(self.reset_btn, self.handle_reset_rec), (self.start_btn, self.handle_start_rec)]:
            btn.clicked.connect(handler)
            btn.setFixedHeight(25)
            btn.setFixedWidth(100)
            btn.setStyleSheet("background: #555; color: white;font-size: 15px;")
            button_layout.addWidget(btn)
        right_layout.addLayout(button_layout)

        # Combine layouts
        main_layout.addLayout(left_layout, stretch=1)
        main_layout.addLayout(right_layout, stretch=2)  # Right panel wider

    def handle_start_rec(self):
        try:
            AO_Name = self.node.content_label_objname + "_" + str(self.node.designator)
            cmd = "set/%s/%s/%s/" % (AO_Name, 'startRec', '1')
            res = self.tweaker(cmd)
            if res[0]:
                times_ms = self.gui_manager.widgetSet["recTime"].widget_value * 1000
                QTimer.singleShot(times_ms, self.timer_start_success)
                self.set_button_states(
                    start_text='Recording...',
                    start_disabled=True,
                    reset_disabled=True
                )
                self.db_display.setText("Loading...")
        except Exception as e:
            print(f"Error starting recording: {e}")


    def handle_reset_rec(self):
        try:
            AO_Name = self.node.content_label_objname + "_" + str(self.node.designator)
            cmd = "set/%s/%s/%s/" % (AO_Name, 'resetGain', '1')
            res = self.tweaker(cmd)
            if res:
                times_ms = 1000
                QTimer.singleShot(times_ms, self.timer_reset_success)
                self.set_button_states(
                    reset_text='Resetting...',
                    start_disabled=True,
                    reset_disabled=True
                )
        except Exception as e:
            print(f"Error resetting gain: {e}")

    def timer_reset_success(self):
        self.set_button_states(
            reset_text='Reset Gain',
            start_disabled=False,
            reset_disabled=False
        )
        self.db_display.setText("0 dB")

    def timer_start_success(self):
        self.set_button_states(
            start_text='Start Rec',
            start_disabled=False,
            reset_disabled=False
        )
        self.db_display.setText("0 dB")
        self.get_appliedGain()

    def get_appliedGain(self):
        try:
            AO_Name = self.node.content_label_objname + "_" + str(self.node.designator)
            cmd = "get/%s/%s/" % (AO_Name, 'remainedRecTime')
            res = self.tweaker(cmd)
            if res:
                while res[1].decode('utf-8').strip('\n\x00') != '0.':
                    time.sleep(0.1)
                    res = self.tweaker(cmd)

                cmd = "get/%s/%s/" % (AO_Name, 'appliedGain')
                res = self.tweaker(cmd)
                self.db_display.setText(res[1].decode('utf-8').strip('\n\x00') + " dB")
        except Exception as e:
            print(f"Error fetching applied gain: {e}")

    def tweaker(self, cmd):
        if Debug.DEBUG_TWEAKER.value: print(" _> %s control command: %s" % (self.__class__.__name__, cmd))

        if self.cSocket.connection:
            while self.cSocket.mainSocket.isRunning():
                time.sleep(0.01)
            if not self.cSocket.mainSocket.isRunning():
                self.cSocket.mainSocket.setQueryTask(cmd, 16)
                self.cSocket.mainSocket.start()
                self.cSocket.mainSocket.wait(150)
                if Debug.DEBUG_TWEAKER.value: print(" _> %s thread process: success" % (self.__class__.__name__))
                return self.cSocket.mainSocket.result
            else:
                if Debug.DEBUG_TWEAKER.value: print(" _> %s thread process: failed" % (self.__class__.__name__))
                return None
        return None

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

@register_node(OP_NODE_QUICK_GAIN)
class FLOW_Node_QUICK_GAIN(FLOW_Node):
    #icon = "icons/in.png"
    op_code = OP_NODE_QUICK_GAIN
    op_title = "QUICK_GAIN"
    content_label_objname = "QUICK_GAIN"
    display_name = 'Quick Gain'
    info = ''
    openable = True
    expandable = True

    def __init__(self, scene):
        super().__init__(scene, inputs=[1], outputs=[1])
        self.initControl()
        self.eval()

        self.start_btn = self.manager.widgetSet["startRec"].button
        self.start_btn.clicked.connect(self.handle_start_rec)
        self.reset_btn = self.manager.widgetSet["resetGain"].button
        self.reset_btn.clicked.connect(self.handle_reset_rec)

    def initInnerClasses(self):
        self.manager = FLOW_Ctrl_Manager(self.content_label_objname)
        self.content = FLOW_Content(self)
        self.grNode = FLOW_GraphicsNode(self)
        self.widget = QUICK_GAIN_GUI(self)

    def handle_start_rec(self):
        if self.cSocket.connection:
            times_ms = self.manager.widgetSet["recTime"].widget_value * 1000
            QTimer.singleShot(times_ms, self.timer_start_success)
            self.reset_btn.setDisabled(True)
            self.start_btn.setDisabled(True)
            self.start_btn.setText('Starting Rec...')

    def handle_reset_rec(self):
        if self.cSocket.connection:
            times_ms =  1000
            QTimer.singleShot(times_ms, self.timer_reset_success)
            self.start_btn.setDisabled(True)
            self.reset_btn.setDisabled(True)
            self.reset_btn.setText('Resetting...')

    def timer_start_success(self):
        self.start_btn.setDisabled(False)
        self.reset_btn.setDisabled(False)
        self.start_btn.setText('Start Rec')

    def timer_reset_success(self):
        self.reset_btn.setDisabled(False)
        self.start_btn.setDisabled(False)
        self.reset_btn.setText('Reset Gain')

    def expandNode(self):
        super().expandNode()
        res = self.tweaker('remainedRecTime')
        if res:
            if res[1].decode('utf-8').strip('\n\x00') != '0.':
                time_str = res[1].decode('utf-8').strip('\n\x00')
                times_ms = math.ceil(float(time_str)) * 1000
                QTimer.singleShot(times_ms, self.timer_start_success)
                self.reset_btn.setDisabled(True)
                self.start_btn.setDisabled(True)
                self.start_btn.setText('Starting Rec...')

    def tweaker(self, key):

        cmd = None
        if isinstance(key, str):
            AO_Name = self.content_label_objname + "_" + str(self.designator)
            if key == 'remainedRecTime':
                cmd = "get/%s/%s/" % (AO_Name, 'remainedRecTime')
            else:
                Parameter_Name = key
                Parameter_Value = self.manager.widgetSet[key].widget_value[1] if isinstance(
                    self.manager.widgetSet[key].widget_value, list) else self.manager.widgetSet[key].widget_value
                if Parameter_Name in ['startRec', 'resetGain']:
                    Parameter_Value = '1'
                cmd = "set/%s/%s/%s/" % (AO_Name, Parameter_Name, Parameter_Value)

        elif isinstance(key, list):
            AO_Name = self.content_label_objname + "_" + str(self.designator)
            Parameter_Index = key[0]
            Parameter_Name = key[1]
            Parameter_Value = self.manager.widgetSet[key[2]].widget_value[1] if isinstance(
                self.manager.widgetSet[key[2]].widget_value, list) else self.manager.widgetSet[key[2]].widget_value
            cmd = "setCoord/%s/%s/%s/%s/0" % (AO_Name, Parameter_Name, Parameter_Value, Parameter_Index)

        if Debug.DEBUG_TWEAKER.value: print(" _> %s control command: %s" % (self.__class__.__name__, cmd))

        if self.cSocket.connection:
            while self.cSocket.mainSocket.isRunning():
                time.sleep(0.01)
            if not self.cSocket.mainSocket.isRunning():
                self.cSocket.mainSocket.setQueryTask(cmd, 16)
                self.cSocket.mainSocket.start()
                self.cSocket.mainSocket.wait(150)
                if Debug.DEBUG_TWEAKER.value: print(" _> %s thread process: success" % (self.__class__.__name__))
                return self.cSocket.mainSocket.result
            else:
                if Debug.DEBUG_TWEAKER.value: print(" _> %s thread process: failed" % (self.__class__.__name__))
                return None
        return None
