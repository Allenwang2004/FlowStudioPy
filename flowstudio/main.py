import os
import sys
from PyQt5.QtWidgets import QApplication, QDesktopWidget, QMessageBox
from PyQt5.QtGui import QFont, QIcon
from PyQt5.QtCore import QTimer, Qt
from flowstudio.functions.track_worker import TrackManager

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

class ApplicationLoader:
    def __init__(self):
        # Add HiDPI support here
        QApplication.setAttribute(Qt.AA_ShareOpenGLContexts)
        QApplication.setAttribute(Qt.AA_EnableHighDpiScaling, True)
        QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps, True)

        self.app = QApplication(sys.argv)

        # Create and store icon as class member
        self.app_icon = QIcon("../resources/main-theme.png")
        self.app.setWindowIcon(self.app_icon)

        # Set other appearance settings
        self.app.setStyle('Fusion')
        self.app.setFont(QFont("Calibri", 8))
        self.app.processEvents()

        # Create and show splash screen
        from flowstudio.functions.SplashScreen import SplashScreen
        self.splash = SplashScreen(self.app_icon)
        self.splash.show()

        # Initialize module storage
        self.flow_audio_manager = None
        self.License_Mechanism = None
        self.FLOW_Window = None

        # Start initialization after a short delay
        QTimer.singleShot(100, self.initialize_application)

        # Process events to start animation
        self.app.processEvents()

    def _show_error(self, error):
        """Show error message and properly close the application"""
        # Close splash screen if it exists
        if hasattr(self, 'splash') and self.splash:
            self.splash.close()

        # Show error message
        QMessageBox.critical(None, 'Initialization Failed',
                             f'Initialization Failed: {error}')

        # Ensure the error message is shown before exiting
        self.app.processEvents()

        # Exit the application
        sys.exit(1)

    def _load_stage_1(self):
        try:
            # Stage 1: Core module imports
            self.splash.set_loading_stage(1)

            # Store module imports at class level
            from flowstudio.flow_window import FLOW_Window
            self.FLOW_Window = FLOW_Window

            import flowstudio.flow_audio_manager
            self.flow_audio_manager = flowstudio.flow_audio_manager

            from flowstudio.flow_license_mechanism import License_Mechanism
            self.License_Mechanism = License_Mechanism

            # Create main window
            self.wnd = self.FLOW_Window()
            monitor = QDesktopWidget().screenGeometry(0)
            self.wnd.move(monitor.left(), monitor.top())
            self.wnd.resize(1368, 768)

            QTimer.singleShot(500, self._load_stage_2)
        except Exception as e:
            self._show_error(str(e))

    def _load_stage_2(self):
        try:
            # Stage 2: License checking
            self.splash.set_loading_stage(2)
            self.wnd.license_mechanism = self.License_Mechanism(parent = self.wnd, splash = self.splash)

            QTimer.singleShot(500, self._load_stage_3)
        except Exception as e:
            self._show_error(str(e))

    def _load_stage_3(self):
        try:
            # Stage 3: Audio device initialization
            self.splash.set_loading_stage(3)
            inputList = self.flow_audio_manager.AudioEnviroment.inputList(self.wnd.settingDialog)
            outputList = self.flow_audio_manager.AudioEnviroment.outputList(self.wnd.settingDialog)

            if inputList == [] and outputList == []:
                self._show_error('Sound Device Is Empty')
                return

            QTimer.singleShot(500, self._load_stage_4)
        except Exception as e:
            self._show_error(str(e))

    def _load_stage_4(self):
        try:
            # Stage 4: Final initialization
            self.splash.set_loading_stage(4)
            self.wnd.waitForLicenseInitSuccess()
            self.wnd.nodesListWidget.addMyItems()
            self.wnd.settingDialog.onTargetSelect()
            self.wnd.custom_aos_setup()
            self.wnd.control_feature_by_license_tier(self.wnd.license_mechanism.tier)
            QTimer.singleShot(500, self._finish_loading)
            # Track user action "Start Flow Studio"
            self.tracker = TrackManager()
            self.tracker.track_user_action(action=1, license=self.wnd.license_mechanism)
        except Exception as e:
            self._show_error(str(e))

    def _finish_loading(self):
        try:
            self.splash.finished.emit()  # Emit the finished signal
            self.splash.close()  # Explicitly close the splash screen
            self.wnd.show()
        except Exception as e:
            self._show_error(str(e))

    def initialize_application(self):
        try:
            # Stage 0: Initial setup
            QTimer.singleShot(500, self._load_stage_1)
        except Exception as e:
            self._show_error(str(e))


if __name__ == '__main__':
    loader = ApplicationLoader()
    sys.exit(loader.app.exec_())