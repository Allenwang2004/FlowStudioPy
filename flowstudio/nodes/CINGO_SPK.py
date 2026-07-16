import time

import numpy as np

from flowstudio.flow_conf import *
from flowstudio.flow_node_base import *
from control.flow_control_widget import *
from flowstudio.flow_window_connection import *
from control.flow_widget_plot import *
import open3d as o3d
from PyQt5.QtGui import QWindow
import win32gui

thread_timeout = 50

STUDIO = 0
BOOTH = 1
LECTURE_HALL = 2
OFFICE = 3
CINEMA = 4
CHURCH = 5
OUTDOOR = 6
CAVE = 7
CAR_PARK = 8
ARENA = 9
CONCERT_HALL = 10
BATHROOM = 11

SOFT = 0
MEDIUM = 1
HARD = 2

class FLOW_Node_CINGO_SPK_GUI(FLOW_GUI):

    cSocket = FLOW_Window_Connection.client

    def __init__(self, node):
        super().__init__(node)
        self.setFixedSize(850, 690)
        self.initExtraWidget()
        self.initLayout()

        self.isConnected = False
        self.toggle_euler_update(True if self.gui_manager.widgetSet['EulerUpdate'].widget_value[0] ==
                                         self.node.manager.config['EulerUpdate'].parameters['pMax'] else False)
        self.old_yaw = 0.0
        self.old_pitch = 0.0
        self.old_roll = 0.0

    def initExtraWidget(self):
        # Head Rotation Visualizer
        self.head_rotation_visualizer = QLabel(self)
        self.head_rotation_visualizer.setText('Head Rotation Visualizer')
        self.head_rotation_visualizer.setStyleSheet("font:bold 20px")

        self.logo_label = QLabel(self)
        pixmap = QPixmap('..\\resources\\Fraunhofer-logo.png')
        scaled_pixmap = pixmap.scaledToWidth(150)
        self.logo_label.setPixmap(scaled_pixmap)
        self.logo_label.setFixedSize(scaled_pixmap.size())


        # self.head_reset = QPushButton(self)
        # self.head_reset.setText("3D Reset")
        # self.head_reset.setFixedWidth(100)
        # self.head_reset.clicked.connect(self.onReset)

        self.gui_manager.widgetSet['EulerUpdate'].toggle.toggled.connect(self.toggle_euler_update)

        self.yaw = QLabel(self)
        self.yaw.setText("Yaw = 0.0")

        self.pitch = QLabel(self)
        self.pitch.setText("Pitch = 0.0")

        self.roll = QLabel(self)
        self.roll.setText("Roll = 0.0")

        # Processing Mode
        self.processing_mode = QLabel(self)
        self.processing_mode.setText('Processing Mode')
        self.processing_mode.setStyleSheet("font:bold 19px;color:#16a085")

        self.gui_manager.widgetSet['VSP'].comboBox.activated.connect(self.VSPMenuChange)

        # HeadRotation Setting
        self.head_rotation_setting = QLabel(self)
        self.head_rotation_setting.setText('HeadRotation Setting')
        self.head_rotation_setting.setStyleSheet("font:bold 19px;color:white")

        # self.reset_cooldown_ms = QLabel(self)
        # self.reset_cooldown_ms.setText('ms')
        #
        # self.reset_apply_time_ms = QLabel(self)
        # self.reset_apply_time_ms.setText('ms')

        self.gui_manager.widgetSet['HR'].toggle.toggled.connect(self.head_rotation_toggle)
        self.gui_manager.widgetSet['HRreset'].toggle.toggled.connect(self.auto_euler_reset_toggle)

        # Virtual Environment
        self.virtual_environment = QLabel(self)
        self.virtual_environment.setText('Virtual Environment')
        self.virtual_environment.setStyleSheet("font:bold 19px;color:#16a085")

        # Virtual Speaker Settings
        self.virtual_speaker_settings = QLabel(self)
        self.virtual_speaker_settings.setText('Speaker Settings')
        self.virtual_speaker_settings.setStyleSheet("font:bold 19px;color:#16a085")
        # self.gui_manager.widgetSet['DialogEnable'].label.setText('DialogPlus')


        self.left_channel = QLabel(self)
        self.left_channel.setText('Left Channel')
        self.left_channel.setStyleSheet("font:bold 16px;color:#fdcb6e")

        self.right_channel = QLabel(self)
        self.right_channel.setText('Right Channel')
        self.right_channel.setStyleSheet("font:bold 16px;color:#fdcb6e")

        self.left_azimuth_degrees = QLabel(self)
        self.left_azimuth_degrees.setText('degrees')

        self.left_elevation_degrees = QLabel(self)
        self.left_elevation_degrees.setText('degrees')

        self.right_azimuth_degrees = QLabel(self)
        self.right_azimuth_degrees.setText('degrees')

        self.right_elevation_degrees = QLabel(self)
        self.right_elevation_degrees.setText('degrees')

        for key in self.gui_manager.widgetSet:
            if key != 'EulerUpdate':
                self.gui_manager.widgetSet[key].label.setFixedWidth(220)
        self.gui_manager.widgetSet["EulerUpdate"].label.setFixedWidth(90)
        self.gui_manager.widgetSet["time"].label.setFixedWidth(80)

        self.euler_update_timer = QTimer(self)
        self.euler_update_timer.timeout.connect(self.fetchData)

    def initLayout(self):

        # Head Rotation Visualizer Layout
        head_rotation_Visualizer_setting_layout = QVBoxLayout()
        head_rotation_Visualizer_setting_layout.addStretch()
        # head_rotation_Visualizer_setting_layout.addWidget(self.head_reset, alignment=Qt.AlignCenter)

        head_rotation_Visualizer_setting_layout.addWidget(self.gui_manager.widgetSet['EulerUpdate'], alignment=Qt.AlignCenter)
        head_rotation_Visualizer_setting_layout.addWidget(self.gui_manager.widgetSet['time'],
                                                          alignment=Qt.AlignCenter)
        head_rotation_Visualizer_setting_layout.addWidget(self.yaw, alignment=Qt.AlignCenter)
        head_rotation_Visualizer_setting_layout.addWidget(self.pitch, alignment=Qt.AlignCenter)
        head_rotation_Visualizer_setting_layout.addWidget(self.roll, alignment=Qt.AlignCenter)
        head_rotation_Visualizer_setting_layout.addStretch()

        self.head_rotation_layout = QHBoxLayout()
        self.head_rotation_layout.addLayout(head_rotation_Visualizer_setting_layout, 4)

        head_rotation_Visualizer_layout = QVBoxLayout()
        head_rotation_Visualizer_layout.addWidget(self.logo_label, alignment=Qt.AlignRight)
        head_rotation_Visualizer_layout.setContentsMargins(0, 0, 0, 0)
        head_rotation_Visualizer_layout.addWidget(self.head_rotation_visualizer, alignment=Qt.AlignCenter)
        head_rotation_Visualizer_layout.addLayout(self.head_rotation_layout)

        # Processing Mode Layout
        processing_mode_layout = QVBoxLayout()
        processing_mode_layout.addWidget(self.processing_mode, alignment=Qt.AlignLeft)
        processing_mode_layout.addWidget(self.gui_manager.widgetSet['VSP'], alignment=Qt.AlignLeft)

        # HeadRotation Setting Layout
        # reset_cooldown_layout = QHBoxLayout()
        # reset_cooldown_layout.addWidget(self.gui_manager.widgetSet['HRtimeTH'], alignment=Qt.AlignCenter)
        # reset_cooldown_layout.addWidget(self.reset_cooldown_ms, alignment=Qt.AlignCenter)
        #
        # reset_apply_time_layout = QHBoxLayout()
        # reset_apply_time_layout.addWidget(self.gui_manager.widgetSet['HRTimeApply'], alignment=Qt.AlignCenter)
        # reset_apply_time_layout.addWidget(self.reset_apply_time_ms, alignment=Qt.AlignCenter)

        head_rotation_setting_layout = QVBoxLayout()
        head_rotation_setting_layout.addWidget(self.head_rotation_setting, alignment=Qt.AlignCenter)
        head_rotation_setting_layout.addWidget(self.gui_manager.widgetSet['HR'], alignment=Qt.AlignCenter)
        head_rotation_setting_layout.addWidget(self.gui_manager.widgetSet['HRreset'], alignment=Qt.AlignCenter)
        head_rotation_setting_layout.addWidget(self.gui_manager.widgetSet['HRtimeTH'], alignment=Qt.AlignCenter)
        head_rotation_setting_layout.addWidget(self.gui_manager.widgetSet['HRTimeApply'], alignment=Qt.AlignCenter)
        head_rotation_setting_layout.addWidget(self.gui_manager.widgetSet['HRAngleTH'], alignment=Qt.AlignCenter)
        # head_rotation_setting_layout.addLayout(reset_cooldown_layout)
        # head_rotation_setting_layout.addLayout(reset_apply_time_layout)

        # Left Layout
        right_layout = QVBoxLayout()
        right_layout.addLayout(head_rotation_Visualizer_layout)
        right_layout.addLayout(head_rotation_setting_layout)

        # Virtual Environment Layout
        virtual_environment_layout = QVBoxLayout()
        virtual_environment_layout.addWidget(self.virtual_environment, alignment=Qt.AlignLeft)
        virtual_environment_layout.addWidget(self.gui_manager.widgetSet['VE'], alignment=Qt.AlignLeft)
        virtual_environment_layout.addWidget(self.gui_manager.widgetSet['RoomScale'], alignment=Qt.AlignLeft)
        virtual_environment_layout.addWidget(self.gui_manager.widgetSet['AbsorptionCurve'], alignment=Qt.AlignLeft)
        virtual_environment_layout.addWidget(self.gui_manager.widgetSet['ReverbMix'], alignment=Qt.AlignLeft)
        virtual_environment_layout.addWidget(self.gui_manager.widgetSet['IndivFactor'], alignment=Qt.AlignLeft)

        # Virtual Speaker Settings Layout
        left_azimuth_angle_layout = QHBoxLayout()
        left_azimuth_angle_layout.addWidget(self.gui_manager.widgetSet['ChAzimuth_L'], alignment=Qt.AlignLeft)
        left_azimuth_angle_layout.addWidget(self.left_azimuth_degrees)

        left_elevation_angle_layout = QHBoxLayout()
        left_elevation_angle_layout.addWidget(self.gui_manager.widgetSet['ChElevation_L'], alignment=Qt.AlignLeft)
        left_elevation_angle_layout.addWidget(self.left_elevation_degrees)

        right_azimuth_angle_layout = QHBoxLayout()
        right_azimuth_angle_layout.addWidget(self.gui_manager.widgetSet['ChAzimuth_R'], alignment=Qt.AlignLeft)
        right_azimuth_angle_layout.addWidget(self.right_azimuth_degrees)

        right_elevation_angle_layout = QHBoxLayout()
        right_elevation_angle_layout.addWidget(self.gui_manager.widgetSet['ChElevation_R'], alignment=Qt.AlignLeft)
        right_elevation_angle_layout.addWidget(self.right_elevation_degrees)

        virtual_speaker_ettings_layout = QVBoxLayout()
        virtual_speaker_ettings_layout.addWidget(self.virtual_speaker_settings, alignment=Qt.AlignLeft)

        # virtual_speaker_ettings_layout.addWidget(self.gui_manager.widgetSet['DialogEnable'], alignment=Qt.AlignLeft)
        virtual_speaker_ettings_layout.addWidget(self.gui_manager.widgetSet['DialogBoost'], alignment=Qt.AlignLeft)
        virtual_speaker_ettings_layout.addWidget(self.gui_manager.widgetSet['Angle'], alignment=Qt.AlignLeft)
        virtual_speaker_ettings_layout.addWidget(self.gui_manager.widgetSet['DynEqCenter'], alignment=Qt.AlignLeft)
        virtual_speaker_ettings_layout.addWidget(self.gui_manager.widgetSet['DynEqAmb'], alignment=Qt.AlignLeft)

        # virtual_speaker_ettings_layout.addStretch()
        virtual_speaker_ettings_layout.addWidget(self.left_channel, alignment=Qt.AlignLeft)
        virtual_speaker_ettings_layout.addWidget(self.gui_manager.widgetSet['ChSpatial_L'], alignment=Qt.AlignLeft)
        virtual_speaker_ettings_layout.addWidget(self.gui_manager.widgetSet['ChMute_L'], alignment=Qt.AlignLeft)
        virtual_speaker_ettings_layout.addLayout(left_azimuth_angle_layout)
        virtual_speaker_ettings_layout.addLayout(left_elevation_angle_layout)
        virtual_speaker_ettings_layout.addStretch()
        virtual_speaker_ettings_layout.addWidget(self.right_channel, alignment=Qt.AlignLeft)
        virtual_speaker_ettings_layout.addWidget(self.gui_manager.widgetSet['ChSpatial_R'], alignment=Qt.AlignLeft)
        virtual_speaker_ettings_layout.addWidget(self.gui_manager.widgetSet['ChMute_R'], alignment=Qt.AlignLeft)
        virtual_speaker_ettings_layout.addLayout(right_azimuth_angle_layout)
        virtual_speaker_ettings_layout.addLayout(right_elevation_angle_layout)


        # Right Layout
        left_layout = QVBoxLayout()
        left_layout.addLayout(processing_mode_layout)
        left_layout.addLayout(virtual_environment_layout)
        left_layout.addLayout(virtual_speaker_ettings_layout)

        layout = QHBoxLayout(self)
        layout.addLayout(left_layout)
        layout.addLayout(right_layout)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(10)

    def VSPMenuChange(self, index):
        show = index != 0
        self.gui_manager.widgetSet['ChSpatial_L'].toggle.setChecked(show)
        self.gui_manager.widgetSet['ChSpatial_L'].toggle.setEnabled(show)
        self.gui_manager.widgetSet['ChSpatial_R'].toggle.setChecked(show)
        self.gui_manager.widgetSet['ChSpatial_R'].toggle.setEnabled(show)
        self.gui_manager.widgetSet['EulerUpdate'].toggle.setChecked(False)
        self.gui_manager.widgetSet['EulerUpdate'].toggle.setEnabled(show)

    def head_rotation_toggle(self, bool):
        self.gui_manager.widgetSet['EulerUpdate'].toggle.setChecked(False)
        self.gui_manager.widgetSet['EulerUpdate'].toggle.setEnabled(bool)

    def auto_euler_reset_toggle(self, bool):
        self.gui_manager.widgetSet['HRtimeTH'].spinbox.setEnabled(bool)
        self.gui_manager.widgetSet['HRTimeApply'].spinbox.setEnabled(bool)
        self.gui_manager.widgetSet['HRAngleTH'].spinbox.setEnabled(bool)
        if not bool:
            self.gui_manager.widgetSet['HRtimeTH'].spinbox.setMaximum(
                self.gui_manager.widgetSet['HRtimeTH'].widget_value)
            self.gui_manager.widgetSet['HRtimeTH'].spinbox.setMinimum(
                self.gui_manager.widgetSet['HRtimeTH'].widget_value)
            self.gui_manager.widgetSet['HRTimeApply'].spinbox.setMaximum(
                self.gui_manager.widgetSet['HRTimeApply'].widget_value)
            self.gui_manager.widgetSet['HRTimeApply'].spinbox.setMinimum(
                self.gui_manager.widgetSet['HRTimeApply'].widget_value)
            self.gui_manager.widgetSet['HRAngleTH'].spinbox.setMaximum(
                self.gui_manager.widgetSet['HRAngleTH'].widget_value)
            self.gui_manager.widgetSet['HRAngleTH'].spinbox.setMinimum(
                self.gui_manager.widgetSet['HRAngleTH'].widget_value)
        else:
            self.gui_manager.widgetSet['HRtimeTH'].spinbox.setMaximum(10000)
            self.gui_manager.widgetSet['HRtimeTH'].spinbox.setMinimum(0)
            self.gui_manager.widgetSet['HRTimeApply'].spinbox.setMaximum(5500)
            self.gui_manager.widgetSet['HRTimeApply'].spinbox.setMinimum(0)
            self.gui_manager.widgetSet['HRAngleTH'].spinbox.setMaximum(90)
            self.gui_manager.widgetSet['HRAngleTH'].spinbox.setMinimum(20)

    def toggle_euler_update(self, should_update):
        should_hide_x_y_z = not should_update
        self.yaw.setHidden(should_hide_x_y_z)
        self.pitch.setHidden(should_hide_x_y_z)
        self.roll.setHidden(should_hide_x_y_z)
        if self.isConnected and not should_update:
            self.client.terminate()
            self.client.wait(int(self.gui_manager.widgetSet['time'].widget_value))
            self.client.logout(index=1)
            self.euler_update_timer.stop()
            self.isConnected = False
            if Debug.DEBUG_THREAD.value: print('%s: thread terminate' % self.__class__.__name__)
        elif not self.isConnected and should_update and self.cSocket.connection:
            self.client = self.cSocket.createClient()
            self.client.login()
            self.euler_update_timer.start(int(self.gui_manager.widgetSet['time'].widget_value))
            self.isConnected = True
            if Debug.DEBUG_THREAD.value: print('%s: thread init' % self.__class__.__name__)

    def fetchData(self):
        if self.cSocket.connection and not self.client.isRunning():
            ao_name = self.node.content_label_objname + "_" + str(self.node.designator)
            parameter_name = "HREularFlow"
            cmd = f'getRow/{ao_name}/{parameter_name}/0/2/0/'
            self.client.setQueryTask(cmd, 20)
            self.client.start()

            if self.client.target in [Target.AIROHA_AB1585_UART.value, Target.AIROHA_AB1565_UART.value, Target.FLOW_APO.value]:
                self.client.wait(150)
            else:
                self.client.wait(int(self.gui_manager.widgetSet['time'].widget_value))

            if self.client.result[0] == True:
                val = self.client.result[1].decode().split('\n')[0].split('/')
                if Debug.DEBUG_THREAD.value: print('HREularFlow:', val)
                if len(val) == 4:
                    try:
                        self.yaw.setText(f'Yaw = {float(val[0])}')
                        self.pitch.setText(f'Pitch = {float(val[1])}')
                        self.roll.setText(f'Roll = {float(val[2])}')

                        R = self.mesh.get_rotation_matrix_from_zyx((self.old_roll, self.old_yaw, -self.old_pitch))
                        self.mesh.rotate(R)
                        self.vis.update_geometry(self.mesh)

                        self.old_yaw = (float(val[0]) / 180) * np.pi
                        self.old_pitch = (float(val[1]) / 180) * np.pi
                        self.old_roll = (float(val[2]) / 180) * np.pi

                        R = self.mesh.get_rotation_matrix_from_xyz((self.old_pitch, -self.old_yaw, -self.old_roll))
                        self.mesh.rotate(R)
                        self.vis.update_geometry(self.mesh)
                    except Exception as e:
                        if Debug.DEBUG_THREAD.value:
                            print("%s Error in returning value, please check the format of the value" % self.__class__.__name__)

            elif self.client.result[0] == False:
                self.toggle_euler_update(False)
                self.gui_manager.widgetSet['EulerUpdate'].widget_value = [
                    self.node.manager.config['EulerUpdate'].parameters['pMin']]

        elif not self.cSocket.connection and self.isConnected:
            self.toggle_euler_update(False)
            self.gui_manager.widgetSet['EulerUpdate'].widget_value = [
                self.node.manager.config['EulerUpdate'].parameters['pMin']]
        elif self.client.isRunning():
            if Debug.DEBUG_THREAD.value: print('%s: current query is still running, skip this query.' % self.node)

    def onReset(self):
        self.old_yaw = 0.0
        self.old_pitch = 0.0
        self.old_roll = 0.0
        self.yaw.setText('Yaw = 0.0')
        self.pitch.setText('Pitch = 0.0')
        self.roll.setText('Roll = 0.0')
        self.gui_manager.widgetSet['EulerUpdate'].toggle.setChecked(False)
        self.head_reset.setEnabled(False)
        ao_name = self.node.content_label_objname + "_" + str(self.node.designator)
        parameter_name = "HREular"
        for index in range(3):
            cmd = f'setCoord/{ao_name}/{parameter_name}/0.0/{index}/0/'
            if self.cSocket.connection:
                while self.cSocket.mainSocket.isRunning():
                    time.sleep(0.01)
                if not self.cSocket.mainSocket.isRunning():
                    self.cSocket.mainSocket.setQueryTask(cmd, 16)
                    self.cSocket.mainSocket.start()
                    if Debug.DEBUG_THREAD.value: print(" _> %s thread process: success" % (self.__class__.__name__))
                else:
                    if Debug.DEBUG_THREAD.value: print(" _> %s thread process: failed" % (self.__class__.__name__))

        self.head_rotation_layout.removeWidget(self.displayer)
        self.displayer.deleteLater()
        self.vis.destroy_window()
        self.timer.stop()
        self.init3D()
        self.head_rotation_layout.insertWidget(0, self.displayer, 6)
        self.head_reset.setEnabled(True)

    def init3D(self):
        self.vis = o3d.visualization.Visualizer()
        self.vis.create_window(visible=False)
        self.winid = win32gui.FindWindow('GLFW30', None)
        self.sub_window = QWindow.fromWinId(self.winid)
        self.displayer = self.createWindowContainer(self.sub_window)

        # 获取渲染器
        render_option = self.vis.get_render_option()
        # 设置背景颜色（RGB值范围为0-1之间）
        render_option.background_color = [33/255, 33/255, 33/255]

        self.mesh = o3d.io.read_triangle_mesh('head_planes_reference.glb')
        self.mesh.compute_vertex_normals()
        self.vis.add_geometry(self.mesh)
        self.vis.update_geometry(self.mesh)
        self.initial_rotate()
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.draw_update)
        self.timer.start(1)

    def draw_update(self):
        self.vis.poll_events()
        self.vis.update_renderer()

    def initial_rotate(self):
        # x y z
        # X轴：Pitch（俯仰）上下
        # Y轴：Yaw（偏航）右左
        # Z轴：Roll（翻滚）逆时针
        R = self.mesh.get_rotation_matrix_from_xyz((np.pi / 8, np.pi, 0))
        self.mesh.rotate(R)

    def refresh(self):
        super().refresh()
        self.init3D()
        self.head_rotation_layout.insertWidget(0, self.displayer, 6)

    def closeEvent(self, a0: QCloseEvent) -> None:
        try:
            self.head_rotation_layout.removeWidget(self.displayer)
            self.displayer.deleteLater()
            self.vis.destroy_window()
            self.timer.stop()
            self.toggle_euler_update(False)
            self.gui_manager.widgetSet['EulerUpdate'].widget_value = [self.node.manager.config['EulerUpdate'].parameters['pMin']]
            super().closeEvent(a0)
        except Exception as e:
            if Debug.DEBUG_COMMON.value: print('%s: %s' % (self.__class__.__name__, e))

    # def changeEvent(self, a0: QtCore.QEvent) -> None:
    #     if a0.type() == QEvent.WindowStateChange:
    #         if self.windowState() & Qt.WindowMinimized:
    #             self.vis.update_geometry(self.mesh)


@register_node(OP_NODE_CINGO_SPK)
class FLOW_Node_CINGO_SPK(FLOW_Node):
    icon = '../resources/cingo-ao-icon.png'
    op_code = OP_NODE_CINGO_SPK
    op_title = "CINGO_SPK"
    content_label_objname = "CINGO_SPK"
    display_name = 'Cingo for Speaker'
    info = "Cingo brings life-like Dynamic Spatial Audio to headphones and creates enveloping 3D sound through stereo speakers.<br><a href='https://www.iis.fraunhofer.de/en/ff/amm/consumer-electronics/cingo.html'>https://www.iis.fraunhofer.de/en/ff/amm/consumer-electronics/cingo.html</a>"
    openable = True
    linkType = 1

    def __init__(self, scene):
        super().__init__(scene, inputs=[1, 1], outputs=[1, 1])
        self.initControl()
        self.eval()
        for i in self.manager.widgetSet:
            self.manager.widgetSet[i].setHidden(True)

    def initInnerClasses(self):
        self.manager = FLOW_Ctrl_Manager(self.content_label_objname)
        self.content = FLOW_Content(self)
        self.grNode = FLOW_GraphicsNode(self)
        self.widget = FLOW_Node_CINGO_SPK_GUI(self)

    def tweaker(self, key):
        cmd = None

        if key in ['EulerUpdate']:
            return

        if key in ["ChSpatial_L", "ChMute_L", "ChAzimuth_L", "ChElevation_L",
                   "ChSpatial_R", "ChMute_R", "ChAzimuth_R", "ChElevation_R"]:
            AO_Name = self.content_label_objname + "_" + str(self.designator)
            ss = str.split(key, '_')
            if ss[1] == "L":
                Parameter_Index = '0'
            elif ss[1] == "R":
                Parameter_Index = '1'

            Parameter_Name = ss[0]
            Parameter_Value = self.manager.widgetSet[key].widget_value[1] if isinstance(
                self.manager.widgetSet[key].widget_value, list) else self.manager.widgetSet[key].widget_value
            cmd = "setCoord/%s/%s/%s/0/%s" % (AO_Name, Parameter_Name, Parameter_Value, Parameter_Index)

        else:
            AO_Name = self.content_label_objname + "_" + str(self.designator)
            Parameter_Name = key
            Parameter_Value = self.manager.widgetSet[key].widget_value[1] if isinstance(
                self.manager.widgetSet[key].widget_value, list) else self.manager.widgetSet[key].widget_value
            cmd = "set/%s/%s/%s/" % (AO_Name, Parameter_Name, Parameter_Value)

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
