import math
import ctypes
from PyQt5.QtWidgets import QApplication, QWidget
from PyQt5.QtCore import Qt, QTimer, QRect, pyqtSignal
from PyQt5.QtGui import QColor, QPainter, QFont, QPixmap


class SplashScreen(QWidget):
    finished = pyqtSignal()

    def __init__(self, app_icon=None):
        # Set Windows taskbar icon
        try:
            myappid = 'flowstudio.app'
            ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)
        except Exception as e:
            print(f"Failed to set app ID: {e}")

        super().__init__()
        self.setWindowFlag(Qt.FramelessWindowHint)
        self.setAttribute(Qt.WA_TranslucentBackground)

        # Set fixed window size to 600x600
        self.window_size = 600
        self.setFixedSize(self.window_size, self.window_size)

        # Load and scale background image
        self.background = QPixmap("../resources/splash.png")
        self.background = self.background.scaled(
            self.window_size,
            self.window_size,
            Qt.KeepAspectRatio,
            Qt.SmoothTransformation
        )

        # Calculate image position
        self.image_x = (self.window_size - self.background.width()) // 2
        self.image_y = 0

        # Set overlay dimensions
        self.overlay_height = 100  # Increased height for status text
        self.overlay_y = self.window_size - self.overlay_height

        # Initialize loading states
        self.loading_stages = [
            "Initializing",
            "Loading Core Modules",
            "Checking License",
            "Loading Audio Devices",
            "Starting Application"
        ]
        self.current_stage = 0
        self.stage_progress = 0
        self.total_progress = 0

        # Animation properties
        self.dots_opacity = 0
        self.dots_timer = 0

        # Center splash screen
        screen = QApplication.primaryScreen().geometry()
        self.move(
            screen.center().x() - self.width() // 2,
            screen.center().y() - self.height() // 2
        )

        # Setup animation timer
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_progress)
        self.timer.start(30)

        # self.setWindowFlag(Qt.WindowStaysOnTopHint)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        # Draw background
        painter.drawPixmap(self.image_x, self.image_y, self.background)

        # Draw version text if available
        try:
            import flowstudio.flow_build_manager
            version = "v" + flowstudio.flow_build_manager.VERSION
            painter.setFont(QFont("Calibri", 12))
            painter.setPen(QColor("#FFFFFF"))
            painter.drawText(
                self.image_x + 15,
                27,
                version
            )
        except ImportError as e:
            import logging
            logging.error(f"Failed to import flow_build_manager: {e}")
            version = "vUnknown"
            painter.setFont(QFont("Calibri", 12))
            painter.setPen(QColor("#FFFFFF"))
            painter.drawText(
                self.image_x + 15,
                27,
                version
            )

        # Draw overlay
        overlay_rect = QRect(
            self.image_x,
            self.overlay_y,
            self.background.width(),
            self.overlay_height
        )
        painter.fillRect(overlay_rect, QColor(0, 0, 0, 100))

        # Draw progress bar
        progress_margin = 20
        progress_height = 4
        progress_y = self.overlay_y + 40

        # Background
        painter.setPen(Qt.NoPen)
        painter.setBrush(QColor(255, 255, 255, 50))
        progress_width = self.background.width() - (progress_margin * 2)
        painter.drawRect(
            self.image_x + progress_margin,
            progress_y,
            progress_width,
            progress_height
        )

        # Progress fill
        progress_fill = int(progress_width * (self.total_progress / 100))
        painter.setBrush(QColor('#e270e4'))
        painter.drawRect(
            self.image_x + progress_margin,
            progress_y,
            progress_fill,
            progress_height
        )

        # Draw current stage text
        painter.setFont(QFont("Calibri", 12))
        current_text = self.loading_stages[self.current_stage]
        text_rect = painter.fontMetrics().boundingRect(current_text)

        # Calculate positions for centered text
        dots = "..."
        dots_rect = painter.fontMetrics().boundingRect(dots)
        total_width = text_rect.width() + dots_rect.width()
        text_x = self.image_x + (self.background.width() - total_width) // 2
        text_y = self.overlay_y + 25

        # Draw stage text
        painter.setPen(QColor("#FFFFFF"))
        painter.drawText(text_x, text_y, current_text)

        # Draw animated dots
        dots_color = QColor(255, 255, 255, int(self.dots_opacity))
        painter.setPen(dots_color)
        painter.drawText(text_x + text_rect.width(), text_y, dots)

    def update_progress(self):
        # Only update dots animation when not finished
        self.dots_timer += 1
        if self.dots_timer >= 60:
            self.dots_timer = 0
        self.dots_opacity = abs(255 * math.sin(self.dots_timer * math.pi / 60))

        self.update()

    def set_loading_stage(self, stage_index):
        """Manually set the current loading stage"""
        if 0 <= stage_index < len(self.loading_stages):
            self.current_stage = stage_index
            self.stage_progress = 0
            self.total_progress = (stage_index * 100) / len(self.loading_stages)

            # If we're at the last stage, update to 100%
            if stage_index == len(self.loading_stages) - 1:
                self.total_progress = 100

            self.update()
            QApplication.processEvents()