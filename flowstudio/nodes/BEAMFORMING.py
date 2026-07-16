from flowstudio.flow_conf import *
from flowstudio.flow_conf_co import SocketType
from flowstudio.flow_node_base import *
from flowstudio.flow_window_connection import *
from controls.LinearIntSliderAndSpinBox import LinearIntSliderAndSpinBox

class RadarConfig:
    BACKGROUND_COLOR = "#2D2D2D"
    GRID_COLOR = QColor("#4a4a4a")
    GRID_SECONDARY_COLOR = QColor("#3a3a3a")
    LINE_WIDTH = 1
    DOT_SIZE = 4
    
    CIRCLE_COUNT = 3
    DOT_COUNT = 24
    MIC_DOT_SIZE = 8
    
    MARGIN_LEFT = 50
    MARGIN_RIGHT = 25
    MARGIN_TOP = 20
    MARGIN_BOTTOM = 20
    
    MIC_COLOR = QColor("#00b894")
    MIC_SHADOW = QColor("#00a085")
    DOA_COLOR = QColor("#ff7675")
    DOA_SHADOW = QColor("#e55a5a")
    DOA_LINE_COLOR = QColor("#ff7675")
    LABEL_COLOR = QColor("#ffffff")
    ANGLE_LABEL_COLOR = QColor("#cccccc")

thread_timeout = 50

class RadarWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.config = RadarConfig()
        self.setStyleSheet(f"background-color: {self.config.BACKGROUND_COLOR};")
        self.setMinimumSize(700, 700)
        self.active_point = None  # The point to highlight (e.g., DOA)
        self.mic_positions = [
            {"x": 0.0, "y": 0.0},  # Mic1
            {"x": 0.0, "y": 0.0},  # Mic2
            {"x": 0.0, "y": 0.0},  # Mic3
            {"x": 0.0, "y": 0.0}   # Mic4
        ]

    def set_active_point(self, angle_degrees):
        """Set the active point to highlight on the radar."""
        self.active_point = angle_degrees
        self.update()

    def update_mic_positions(self, mic_index, x, y):
        """Update the position of a specific microphone."""
        if 0 <= mic_index < len(self.mic_positions):
            self.mic_positions[mic_index]["x"] = x
            self.mic_positions[mic_index]["y"] = y
            self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        # Set up
        center = QPointF(
            (self.width() - self.config.MARGIN_LEFT - self.config.MARGIN_RIGHT) / 2 + self.config.MARGIN_LEFT, (self.height() - self.config.MARGIN_TOP - self.config.MARGIN_BOTTOM) / 2 + self.config.MARGIN_TOP
        )
        radius = min(
            (self.width() - self.config.MARGIN_LEFT - self.config.MARGIN_RIGHT),
            (self.height() - self.config.MARGIN_TOP - self.config.MARGIN_BOTTOM)
        ) / 2

        # Draw outer circle (gray)
        pen = QPen(self.config.GRID_COLOR, self.config.LINE_WIDTH)
        painter.setPen(pen)
        painter.drawEllipse(center, radius, radius)

        # Draw inner circles (two)
        for i in range(1, self.config.CIRCLE_COUNT):
            inner_radius = radius * (i / self.config.CIRCLE_COUNT)
            if i == 1: # Innermost cicle slightly more preminent
                pen = QPen(self.config.GRID_COLOR, self.config.LINE_WIDTH + 1)
            else:
                pen = QPen(self.config.GRID_SECONDARY_COLOR, self.config.LINE_WIDTH)
            painter.setPen(pen)
            painter.drawEllipse(center, inner_radius, inner_radius)

        # Draw cross lines
        pen = QPen(self.config.GRID_COLOR, self.config.LINE_WIDTH)
        painter.setPen(pen)
        painter.drawLine(center.x() - radius, center.y(), center.x() + radius, center.y())
        painter.drawLine(center.x(), center.y() - radius, center.x(), center.y() + radius)

        pen = QPen(self.config.GRID_SECONDARY_COLOR, self.config.LINE_WIDTH)
        painter.setPen(pen)
        painter.drawLine(
            center.x() - radius * 0.7071, center.y() - radius * 0.7071,  # 0.7071 ≈ 1/√2
            center.x() + radius * 0.7071, center.y() + radius * 0.7071
        )
        painter.drawLine(
            center.x() + radius * 0.7071, center.y() - radius * 0.7071, center.x() - radius * 0.7071, center.y() + radius * 0.7071
        )

        # Draw angle markers (0°, 90°, 180°, 270°)
        font = QFont("Arial", 10, QFont.Bold)
        painter.setFont(font)
        pen = QPen(self.config.ANGLE_LABEL_COLOR)
        painter.setPen(pen)

        label_offset = 20 # offset from radius graph for text

        painter.drawText(center.x() + radius + label_offset - 6, center.y() + 6, "0°")
        painter.drawText(center.x() - 12, center.y() - radius  - label_offset, "90°")
        painter.drawText(center.x() - radius - label_offset - 15, center.y() + 6, "180°")
        painter.drawText(center.x() - 15, center.y() + radius + label_offset + 10, "270°")

        # Draw microphone positions 
        # use the positions from the input mic_positions
        for i, mic_pos in enumerate(self.mic_positions):
            x = center.x() + mic_pos["x"] * radius
            y = center.y() - mic_pos["y"] * radius # negative because y increases downwards

            # Draw the microphone shadow
            painter.setBrush(QBrush(self.config.MIC_SHADOW))
            painter.setPen(Qt.NoPen)
            painter.drawEllipse(QPointF(x + 1, y + 1), 12, 12)  # shadow offset

            # Draw the microphone position
            painter.setBrush(QBrush(self.config.MIC_COLOR))
            painter.setPen(Qt.NoPen)
            painter.drawEllipse(QPointF(x, y), 12, 12)

            # Draw the microphone number
            pen = QPen(self.config.LABEL_COLOR)
            painter.setPen(pen)
            font = QFont("Arial", 9, QFont.Bold)
            painter.setFont(font)
            text_rect = QRectF(x - 6, y - 6, 12, 12)
            painter.drawText(text_rect, Qt.AlignCenter, str(i + 1))

        # separate the radar into 24 sections by drawing 24 dots
        for i in range(self.config.DOT_COUNT):
            angle = i * (360 / self.config.DOT_COUNT)
            angle_rad = math.radians(angle)
            x = center.x() + radius * math.cos(angle_rad)
            y = center.y() - radius * math.sin(angle_rad)  # negative because y increases downwards

            if i % 6 == 0: # every 90 degrees
                dot_size = 4
                color = self.config.GRID_COLOR
            else:
                dot_size = 2
                color = self.config.GRID_SECONDARY_COLOR

            painter.setBrush(QBrush(color))
            painter.setPen(Qt.NoPen)
            painter.drawEllipse(QPointF(x, y), dot_size, dot_size)

        # Draw the active point (red)
        if self.active_point is not None:
            angle_rad = math.radians(self.active_point)
            x = center.x() + radius * math.cos(angle_rad)
            y = center.y() - radius * math.sin(angle_rad)  # negative because y increases downwards

            # Draw dash line from center to DOA point
            pen = QPen(self.config.DOA_LINE_COLOR, 2)
            pen.setStyle(Qt.DashLine)
            pen.setDashPattern([8, 4])
            painter.setPen(pen)
            painter.drawLine(center, QPointF(x, y))

            # Draw subtle shadow for the DOA point
            painter.setBrush(QBrush(self.config.DOA_SHADOW))
            painter.setPen(Qt.NoPen)
            painter.drawEllipse(QPointF(x + 1, y + 1), 12, 12)  # shadow offset

            # Draw the main DOA point
            painter.setBrush(QBrush(self.config.DOA_COLOR))
            painter.drawEllipse(QPointF(x, y), 12, 12)

            # Add center dot for better definition
            painter.setBrush(QBrush(QColor("#ffffff")))
            painter.drawEllipse(QPointF(x, y), 3, 3)


class BeamformingGUI(FLOW_GUI):
    cSocket = FLOW_Window_Connection.client

    def __init__(self, node: 'Node'):
        super().__init__(node)

        self.setFixedSize(800, 500)

        # 確保 gui_manager 存在
        if not hasattr(self, 'gui_manager'):
            print("Warning: gui_manager not found, initializing manually")
            try:
                self.gui_manager = FLOW_Ctrl_Manager(None, **node.manager.config)
            except Exception as e:
                print(f"Error initializing gui_manager: {e}")
                raise  # 如果無法初始化 gui_manager，直接拋出異常
        
        # create the radar widget
        self.radarWidget = RadarWidget()
        self.radarWidget.setFixedSize(500, 500)
        self.initExtraWidget()

        self.rightContainer = QWidget()
        self.rightLayout = QVBoxLayout()
        self.rightLayout.setContentsMargins(0, 0, 0, 0)
        self.rightLayout.setSpacing(0)
        self.rightContainer.setLayout(self.rightLayout)
        self.rightContainer.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        self.mic_widgets = {
            "Mic1X": None, "Mic1Y": None,
            "Mic2X": None, "Mic2Y": None,
            "Mic3X": None, "Mic3Y": None,
            "Mic4X": None, "Mic4Y": None,
            "DOADeg": None, "DOA": None,
            "MicDeg": None
        }

        # add the control widgets to the layout
        try:
            for key, widget in self.gui_manager.widgetSet.items():
                widget.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
                self.rightLayout.addWidget(widget, 1)
                widget.show()

                # save the references to connect to the signal
                if key in self.mic_widgets:
                    self.mic_widgets[key] = widget

            self.last_valid_doa_deg = 0.0
            self.is_update_on = True
            self.is_doa_on = True

            self.connect_signals()
            self.update_red_dot()

            self.updateSwitch = Switch("Update", "on").get_widget(self)
            self.updateSwitch.toggle.setChecked(False)
            self.rightLayout.addWidget(self.updateSwitch, 1)

            # self.doa_deg_control = LinearIntSliderAndSpinBox("DOADeg", 360, 0, 30)
            self.doa_deg_control = SpecialFloatSpinBox('DOADeg', 360, 0, 0).get_widget(self.node.content)
            # self.doa_deg_widget = self.doa_deg_control.get_widget(self, gui_type=1)
            self.rightLayout.addWidget(self.doa_deg_control, 1)
            # self.doa_deg_widget.setEnabled(True)
            self.mic_widgets["DOADeg"] = self.doa_deg_control

            self.updateSwitch.toggle.toggled.connect(self.on_update_switch_changed)

            mainLayout = QHBoxLayout(self)
            mainLayout.addWidget(self.radarWidget, 7) # 7 units
            mainLayout.addWidget(self.rightContainer, 3) # 3units
            mainLayout.setContentsMargins(0, 0, 0, 0)
            mainLayout.setSpacing(0)
            self.setLayout(mainLayout)

            self.init_default_mic_positions()

            self.update_red_dot()

        except Exception as e:
            print(f"Error in BeamformingGUI initialization: {e}")
            import traceback
            traceback.print_exc()
            raise 

    def on_update_switch_changed(self, checked):
        self.is_update_on = checked
        if not checked:
            # before turn odd update, record the last red dot position
            self.last_active_angle = self.get_current_red_dot()
            # close the thread etc
            self.client.terminate()
            self.client.wait(thread_timeout)
            self.client.logout()
            self.timer.stop()
            self.isConnected = False
            if Debug.DEBUG_THREAD.value: print('%s: thread terminate' % self.__class__.__name__)

        else:
            self.client = self.cSocket.createClient()
            self.client.login()
            self.timer.start(thread_timeout)
            self.isConnected = True
            if Debug.DEBUG_THREAD.value: print('%s: thread init' % self.__class__.__name__)
            
        self.update_red_dot()

    def get_current_red_dot(self):
        try:
            if self.is_doa_on:
                doa_widget = self.mic_widgets.get("DOADeg")
                if doa_widget is None:
                    return self.last_valid_doa_deg
                if hasattr(doa_widget, 'widget_value'):
                    angle = float(doa_widget.widget_value)
                else:
                    angle = float(doa_widget.text())
                return angle % 360
            else:
                mic_widget = self.mic_widgets.get("MicDeg")
                if mic_widget is None:
                    return self.last_valid_doa_deg
                if hasattr(mic_widget, 'widget_value'):
                    angle = float(mic_widget.widget_value)
                else:
                    angle = float(mic_widget.text())
                return angle % 360
        except Exception as e:
            print(f"[get_current_red_dot] error: {e}")
            return self.last_valid_doa_deg

    def init_default_mic_positions(self):
        """Initialize the microphone position widgets."""
        default_positions = [
            {"x": -0.5, "y": 0.5},  # Mic1
            {"x": 0.5, "y": 0.5},   # Mic2
            {"x": -0.5, "y": -0.5},  # Mic3
            {"x": 0.5, "y": -0.5}    # Mic4
        ]

        for i, pos in enumerate(default_positions):
            self.radarWidget.update_mic_positions(i, pos["x"], pos["y"])

        for i, pos in enumerate(default_positions):
            x_widget = self.mic_widgets[f"Mic{i+1}X"]
            y_widget = self.mic_widgets[f"Mic{i+1}Y"]
            
            if x_widget and y_widget:
                try:
                    if hasattr(x_widget, 'widget_value') and hasattr(y_widget, 'widget_value'):
                        x_widget.widget_value = pos["x"] * 100
                        y_widget.widget_value = pos["y"] * 100

                except Exception as e:
                    print(f"Error setting widget values: {e}")

    def init_doa(self):
        """Initialize the DOA input widget."""
        try:
            if self.mic_widgets["DOADeg"]:
                self.update_doa_from_mic_deg(None)

        except Exception as e:
            print(f"Error initializing DOA input: {e}")
            import traceback
            traceback.print_exc()

    def connect_signals(self):
        """Connect the signals for the GUI elements."""
        self.connect_mic_widgets()

        if self.mic_widgets["MicDeg"]:
            self.mic_widgets["MicDeg"].valueChanged.connect(lambda _: self.update_red_dot())

        if self.mic_widgets["DOADeg"]:
            self.mic_widgets["DOADeg"].valueChanged.connect(self.update_doa_from_mic_deg)
        
        if self.mic_widgets["DOA"]:
            if hasattr(self.mic_widgets["DOA"], 'toggled'):
                self.mic_widgets["DOA"].toggled.connect(self.update_doa_visibility)
            elif hasattr(self.mic_widgets["DOA"], 'stateChanged'):
                self.mic_widgets["DOA"].stateChanged.connect(self.update_doa_visibility)
            elif hasattr(self.mic_widgets["DOA"], 'valueChanged'):
                self.mic_widgets["DOA"].valueChanged.connect(self.update_doa_visibility)

    def update_doa_visibility(self, state):
        """Update the visibility of the DOA input based on the checkbox state."""
        try:
            self.is_doa_on = bool(state)
            self.update_red_dot()

        except Exception as e:
            print(f"Error updating DOA visibility: {e}")
            import traceback
            traceback.print_exc()

    def connect_mic_widgets(self):
        """Connect the signals for the microphone position widgets."""
        try:
            for i in range(1, 5): # for each mic
                x_widget = self.mic_widgets[f"Mic{i}X"]
                y_widget = self.mic_widgets[f"Mic{i}Y"]

                if x_widget and y_widget:
                    def create_x_update_fn(idx, x_w, y_w):
                        return lambda _: self.update_mic_positions_from_x(idx, x_w, y_w)
                    
                    def create_y_update_fn(idx, x_w, y_w):
                        return lambda _: self.update_mic_positions_from_y(idx, x_w, y_w)
                    
                    x_update_fn = create_x_update_fn(i-1, x_widget, y_widget)
                    y_update_fn = create_y_update_fn(i-1, x_widget, y_widget)

                    x_widget.valueChanged.connect(x_update_fn)
                    y_widget.valueChanged.connect(y_update_fn)

                    self.update_mic_positions(i-1, x_widget, y_widget)
        except Exception as e:
            print(f"Error connecting mic widgets: {e}")
            import traceback
            traceback.print_exc()
    
    def update_mic_positions_from_x(self, mic_index, x_widget, y_widget):
        """Update the microphone position based on the x-coordinate input."""
        self.update_mic_positions(mic_index, x_widget, y_widget)
    
    def update_mic_positions_from_y(self, mic_index, x_widget, y_widget):
        """Update the microphone position based on the y-coordinate input."""
        self.update_mic_positions(mic_index, x_widget, y_widget)

    def update_mic_positions(self, mic_index, x_widget, y_widget):
        """Update the microphone position based on the input from the GUI."""
        try:
            if hasattr(x_widget, 'widget_value'):
                x_val = float(x_widget.widget_value)
                y_val = float(y_widget.widget_value)
            
            x_scaled = x_val / 100.0
            y_scaled = y_val / 100.0
            
            x_scaled = max(-1.0, min(1.0, x_scaled))
            y_scaled = max(-1.0, min(1.0, y_scaled))
            
            self.radarWidget.update_mic_positions(mic_index, x_scaled, y_scaled)
        except (ValueError, AttributeError) as e:
            print(f"Error updating mic position: {e}, x_widget={x_widget}, y_widget={y_widget}")
            import traceback
            traceback.print_exc()
    
    def update_doa_from_mic_deg(self, _):
        """from DOADeg input, update the radar active point."""
        try:
            doa_widget = self.mic_widgets.get("DOADeg")
            if hasattr(doa_widget, 'widget_value'):
                angle = float(doa_widget.widget_value)
            else:
                angle = float(doa_widget.text())
            # Ensure the angle is within the range [0, 360)
            angle = angle % 360
            self.last_valid_doa_deg = angle
            self.update_red_dot()
        except ValueError as e:
            # ignore invalid input
            print(f"[update_doa_from_mic_deg] error: {e}")

    def update_red_dot(self):
        """Update red dot angle due to DOA/Update state and display"""
        if self.is_doa_on:
            # If DOA is on, red dot display on DOADeg
            if not self.is_update_on:
                # Turn Update off, red dot is on the last DOADeg value
                self.radarWidget.set_active_point(getattr(self, 'last_active_angle', self.last_valid_doa_deg))
                return
            try:
                doa_widget = self.mic_widgets.get("DOADeg")
                if doa_widget is None:
                    raise ValueError("DOADeg widget not found")
                if hasattr(doa_widget, 'widget_value'):
                    angle = float(doa_widget.widget_value)
                else:
                    angle = float(doa_widget.text())
                # Ensure the angle is within the range [0, 360)
                angle = angle % 360
                self.last_valid_doa_deg = angle
                self.radarWidget.set_active_point(angle)        
            except Exception as e:
                print(f"[Update_red_dot] DOADeg error: {e}")
                self.radarWidget.set_active_point(self.last_valid_doa_deg)
        else:
            # DOA is off, red dot is MicDeg
            try:
                mic_widget = self.mic_widgets.get("MicDeg")
                if mic_widget is None:
                    raise ValueError("MicDeg widget not found")
                if hasattr(mic_widget, 'widget_value'):
                    angle = float(mic_widget.widget_value)
                else:
                    angle = float(mic_widget.text())
                angle = angle % 360
                self.radarWidget.set_active_point(angle)
            except Exception as e:
                print(f"[Update_red_dot] MicDeg error: {e}")
                self.radarWidget.set_active_point(self.last_valid_doa_deg)

    def initExtraWidget(self):
            self.timer = QTimer(self)
            print("[BEAMFORMING] initExtraWidget")
            self.timer.timeout.connect(self.fetchData)

    def toggle(self, bool):
        if self.isConnected and not bool:
            self.client.terminate()
            self.client.wait(thread_timeout)
            self.client.logout()
            self.timer.stop()
            self.isConnected = False
            if Debug.DEBUG_THREAD.value: print('%s: thread terminate' % self.__class__.__name__)
        elif not self.isConnected and bool and self.cSocket.connection:
            self.client = self.cSocket.createClient()
            self.client.login()
            self.timer.start(thread_timeout)
            self.isConnected = True
            if Debug.DEBUG_THREAD.value: print('%s: thread init' % self.__class__.__name__)

    def fetchData(self):
        if self.cSocket.connection and not self.client.isRunning():
            AO_Name = self.node.content_label_objname + "_" + str(self.node.designator)
            Parameter_Name = "DOADeg"
            cmd = "get/%s/%s/" % (AO_Name, Parameter_Name)
            self.client.setQueryTask(cmd, 64)
            self.client.start()
            self.client.wait(thread_timeout)
            if self.client.result[0] == True:
                self.process()
            elif self.client.result[0] == False:
                self.toggle(False)
                self.updateSwitch.toggle.setChecked(False)
        elif not self.cSocket.connection and self.isConnected:
            self.toggle(False)
            self.updateSwitch.toggle.setChecked(False) 

    def process(self):
        val = self.client.result[1].decode("utf-8").rstrip('\x00').replace('.', '')
        self.doa_deg_control.numbox.setValue(int(val))
        self.update_red_dot()

@register_node(OP_NODE_BEAMFORMING)
class FLOW_Node_BEAMFORMING(FLOW_Node):
    #icon = "icons/in.png"
    op_code = OP_NODE_BEAMFORMING
    op_title = "BEAMFORMING"
    content_label_objname = "BEAMFORMING"
    display_name = '4 Mic Beamforming'
    info = 'Beamforming process according DOA can implement various functionalities implemented including but not limited to localizing and tracking the sound sources, extracting the signal of interest, suppressing ambient noise, and separating different sound sources.'
    expandable = True
    openable = True
    linkType = 1

    def __init__(self, scene, mic_count=4):
        self.inctrls = [SocketType.FLOAT.value]
        self.inputs = []
        self.outputs = []
        for i in range(mic_count):
            self.inputs.append(1)
        self.outputs.append(1)

        super().__init__(scene, inputs=[1, 1, 1, 1], outputs=[1,1], inctrls=self.inctrls)
        self.initControl()
        self.eval()

    def initInnerClasses(self):
        super().initInnerClasses()
        # self.widget = BEAMFORMING_GUI(self)
        try:
            self.manager = FLOW_Ctrl_Manager(self.content_label_objname)
            self.content = FLOW_Content(self)
            self.grNode = FLOW_GraphicsNode(self)
            self.widget = BeamformingGUI(self)
            if hasattr(self, 'widget'):
                        print("[BEAMFORMING] Widget attribute exists")
            else:
                print("[BEAMFORMING] ERROR: Widget attribute does not exist!")

        except Exception as e:
            print(f"Error initializing inner classes: {e}")
            import traceback
            traceback.print_exc()
            # Do not raise the exception, continue execution to prevent the application from crashing
            # Ensure the widget attribute has at least a default value
            if not hasattr(self, 'widget'):
                self.widget = None
                print("Set widget to None as a fallback")
