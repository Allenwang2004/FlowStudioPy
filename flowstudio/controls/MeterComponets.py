# modern_meter_components.py
"""
Modern meter components for audio level visualization.
Reusable components that can be used across different node types.
"""

from PyQt5.QtWidgets import QWidget, QHBoxLayout, QLabel, QGraphicsDropShadowEffect
from PyQt5.QtCore import QPropertyAnimation, QEasingCurve, pyqtProperty, QTimer, QRect, QPointF
from PyQt5.QtGui import (QLinearGradient, QRadialGradient, QFont, QPainter, QBrush, QPen,
                         QColor, QConicalGradient)
from PyQt5.QtCore import Qt



class ModernMeterConfig:
    """Configuration class for modern meter styling."""
    # Modern color palette
    BACKGROUND_COLOR = "#0A0A0F"
    CARD_BACKGROUND = "#1A1A2E"
    ACCENT_COLOR = "#e0e0e0"    # Light gray for text and accents

    # Meter colors (gradient zones)
    SAFE_COLOR = "#00f757"  # Green
    CAUTION_COLOR = "#F59E0B"  # Amber
    WARNING_COLOR = "#EF4444"  # Red
    PEAK_COLOR = "#DC2626"  # Dark red

    # Typography
    FONT_FAMILY = "Segoe UI"
    FONT_SIZE_LARGE = 12
    FONT_SIZE_MEDIUM = 10
    FONT_SIZE_SMALL = 8

    # Dimensions
    METER_WIDTH = 20
    METER_HEIGHT = 160
    SPACING = 3
    MARGIN = 8
    BORDER_RADIUS = 6


class ModernMeterBar(QWidget):
    """
    A modern-styled meter bar widget for audio level visualization.

    Features:
    - Smooth animations
    - Peak hold with decay
    - Color-coded zones (safe/caution/warning/peak)
    - Customizable labels
    - Modern dark theme styling
    """

    def __init__(self, label_text="CH 1", show_label=True, parent=None):
        super().__init__(parent)
        self.config = ModernMeterConfig()
        self.label_text = label_text
        self.show_label = show_label  # Control whether to show the top label

        # Meter state
        self.current_level = -120.0  # dB
        self.peak_level = -120.0
        self.peak_hold_timer = 0

        # Animation
        self.animation_level = -120.0
        self.level_animation = QPropertyAnimation(self, b"animation_level")
        self.level_animation.setDuration(50)
        self.level_animation.setEasingCurve(QEasingCurve.OutCubic)

        # Setup UI
        self.setFixedSize(self.config.METER_WIDTH + 25, self.config.METER_HEIGHT + 60)
        if self.label_text == "AUTO GAIN":
            self.setFixedSize(self.config.METER_WIDTH + 25, self.config.METER_HEIGHT + 70)
        self.setup_styling()

        # Peak hold timer
        self.peak_timer = QTimer()
        self.peak_timer.timeout.connect(self.update_peak_hold)
        self.peak_timer.start(100)

    @pyqtProperty(float)
    def animation_level(self):
        return self._animation_level if hasattr(self, '_animation_level') else -120.0

    @animation_level.setter
    def animation_level(self, value):
        self._animation_level = value
        self.update()

    def setup_styling(self):
        """Setup modern styling with shadows and effects."""
        self.setStyleSheet(f"""
            QWidget {{
                background-color: {self.config.CARD_BACKGROUND};
                border-radius: {self.config.BORDER_RADIUS}px;
                border: 1px solid #2A2A3E;
            }}
        """)

        # Add drop shadow effect
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(10)
        shadow.setColor(QColor(0, 0, 0, 60))
        shadow.setOffset(0, 2)
        self.setGraphicsEffect(shadow)

    def set_label(self, text):
        """Set the label text for this meter."""
        self.label_text = text
        self.update()

    def set_level(self, db_value):
        """Set the meter level with smooth animation."""
        self.current_level = max(-120.0, min(20.0, float(db_value)))

        # Update peak hold
        if self.current_level > self.peak_level:
            self.peak_level = self.current_level
            self.peak_hold_timer = 30  # Hold for 3 seconds at 100ms intervals

        # Animate to new level
        self.level_animation.setStartValue(self.animation_level)
        self.level_animation.setEndValue(self.current_level)
        self.level_animation.start()

    def get_current_level(self):
        """Get the current dB level."""
        return self.current_level

    def get_peak_level(self):
        """Get the current peak level."""
        return self.peak_level

    def reset(self):
        """Reset the meter to minimum level."""
        self.set_level(-120)
        self.peak_level = -120.0

    def update_peak_hold(self):
        """Update peak hold logic."""
        if self.peak_hold_timer > 0:
            self.peak_hold_timer -= 1
        else:
            # Slowly decay peak level
            self.peak_level = max(self.peak_level - 0.5, self.current_level)
        self.update()

    def get_meter_color(self, db_value):
        """Get color based on dB level."""
        if db_value >= -2:
            return self.config.PEAK_COLOR  # Red for -2 dB and above
        elif db_value >= -6:
            return self.config.WARNING_COLOR  # Yellow for -6 to -2 dB
        elif db_value >= -8:
            return self.config.CAUTION_COLOR  # Amber for -8 to -6 dB
        else:
            return self.config.SAFE_COLOR  # Green for below -8 dB

    def db_to_pixel(self, db_value):
        """Convert dB value to pixel position."""
        # Map -120dB to 0dB to 0 to meter_height
        if db_value <= -120:
            return 0
        elif db_value >= 0:
            return self.config.METER_HEIGHT
        else:
            # Logarithmic scaling for better visual representation
            normalized = (db_value + 120) / 120
            return int(normalized * self.config.METER_HEIGHT)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        # Calculate meter area
        meter_rect = QRect(15, 25, self.config.METER_WIDTH, self.config.METER_HEIGHT)

        # Draw background meter track
        self.draw_meter_background(painter, meter_rect)

        # Draw meter fill
        self.draw_meter_fill(painter, meter_rect)

        # Draw peak indicator
        self.draw_peak_indicator(painter, meter_rect)

        # Draw labels
        self.draw_labels(painter, meter_rect)

    def draw_meter_background(self, painter, rect):
        """Draw the meter background track."""
        # Background track with gradient
        gradient = QLinearGradient(0, rect.top(), 0, rect.bottom())
        gradient.setColorAt(0, QColor(60, 60, 80, 100))
        gradient.setColorAt(1, QColor(30, 30, 50, 100))

        painter.setBrush(QBrush(gradient))
        painter.setPen(QPen(QColor(80, 80, 100), 0.5))  # Thin outline
        painter.drawRoundedRect(rect, 3, 3)

        # Inner shadow effect
        inner_rect = rect.adjusted(1, 1, -1, -1)
        inner_gradient = QLinearGradient(0, inner_rect.top(), 0, inner_rect.bottom())
        inner_gradient.setColorAt(0, QColor(20, 20, 30, 150))
        inner_gradient.setColorAt(1, QColor(40, 40, 60, 100))

        painter.setBrush(QBrush(inner_gradient))
        painter.setPen(Qt.NoPen)
        painter.drawRoundedRect(inner_rect, 2, 2)

    def draw_meter_fill(self, painter, rect):
        """Draw the animated meter fill."""
        if self.animation_level <= -120:
            return

        fill_height = self.db_to_pixel(self.animation_level)
        if fill_height <= 0:
            return

        # Create gradient based on level zones
        gradient = QLinearGradient(0, rect.bottom(), 0, rect.top())

        # Add color stops for different zones
        total_height = self.config.METER_HEIGHT

        # Safe zone (bottom) - Green for below -8 dB
        safe_end = self.db_to_pixel(-8) / total_height
        gradient.setColorAt(0, QColor(self.config.SAFE_COLOR))
        gradient.setColorAt(min(safe_end, 1.0), QColor(self.config.SAFE_COLOR))

        # Caution zone - Amber for -8 to -6 dB
        if safe_end < 1.0:
            caution_end = self.db_to_pixel(-6) / total_height
            gradient.setColorAt(min(caution_end, 1.0), QColor(self.config.CAUTION_COLOR))

        # Warning zone - Yellow for -6 to -2 dB
        warning_end = self.db_to_pixel(-2) / total_height
        if warning_end < 1.0:
            gradient.setColorAt(min(warning_end, 1.0), QColor(self.config.WARNING_COLOR))

        # Peak zone (top) - Red for -2 dB and above
        gradient.setColorAt(1.0, QColor(self.config.PEAK_COLOR))

        # Draw the fill
        fill_rect = QRect(rect.left() + 2, rect.bottom() - fill_height,
                          rect.width() - 4, fill_height)

        painter.setBrush(QBrush(gradient))
        painter.setPen(Qt.NoPen)
        painter.drawRoundedRect(fill_rect, 1, 1)

        # Add glow effect for high levels
        if self.animation_level > -6:  # Glow starts at -6 dB instead of -12 dB
            glow_color = QColor(self.get_meter_color(self.animation_level))
            glow_color.setAlpha(50)
            painter.setBrush(QBrush(glow_color))
            glow_rect = fill_rect.adjusted(-1, -1, 1, 1)
            painter.drawRoundedRect(glow_rect, 2, 2)

    def draw_peak_indicator(self, painter, rect):
        """Draw peak hold indicator with thinner line."""
        if self.peak_level <= -120:
            return

        peak_y = rect.bottom() - self.db_to_pixel(self.peak_level)
        peak_color = QColor(self.get_meter_color(self.peak_level))

        # Draw very thin peak line (reduced from 1 to 0.5)
        painter.setPen(QPen(peak_color, 0.5))
        painter.drawLine(rect.left() + 2, peak_y, rect.right() - 2, peak_y)

        # Add subtle glow effect with thinner line (reduced from 2 to 1)
        glow_color = QColor(peak_color)
        glow_color.setAlpha(80)
        painter.setPen(QPen(glow_color, 1))
        painter.drawLine(rect.left() + 2, peak_y, rect.right() - 2, peak_y)

    def draw_labels(self, painter, meter_rect):
        """Draw label and dB value below the meter."""
        # Label (top) - only if show_label is True
        if self.show_label:
            font = QFont(self.config.FONT_FAMILY, self.config.FONT_SIZE_SMALL, QFont.Bold)
            painter.setFont(font)
            painter.setPen(QColor(self.config.ACCENT_COLOR))

            label_rect = QRect(0, 5, self.width(), 15)
            painter.drawText(label_rect, Qt.AlignCenter, self.label_text)

        # dB value below the meter
        font = QFont(self.config.FONT_FAMILY, self.config.FONT_SIZE_SMALL, QFont.Bold)
        painter.setFont(font)

        if self.current_level <= -120:
            level_text = "-∞ dB"
            painter.setPen(QColor(120, 120, 140))
        else:
            level_text = f"{self.current_level:.1f} dB"
            painter.setPen(QColor(self.get_meter_color(self.current_level)))

        # Position dB text below the meter
        db_y = meter_rect.bottom() + 8
        db_rect = QRect(0, db_y, self.width(), 20)
        painter.drawText(db_rect, Qt.AlignCenter, level_text)

        if self.label_text == "AUTO GAIN":
            # LUFS text below dB value
            lufs_font = QFont(self.config.FONT_FAMILY, self.config.FONT_SIZE_SMALL, QFont.Normal)
            painter.setFont(lufs_font)
            if self.current_level <= -120:
                painter.setPen(QColor(120, 120, 140))
            else:
                painter.setPen(QColor(self.get_meter_color(self.current_level)))

            lufs_rect = QRect(0, meter_rect.bottom() + 30, self.width(), 15)
            painter.drawText(lufs_rect, Qt.AlignCenter, "LUFS")


class ModernMeterContainer(QWidget):
    """
    A container widget for multiple meter bars.
    Handles layout and provides easy management of multiple meters.
    """

    def __init__(self, meter_count=1, meter_labels=None, parent=None):
        super().__init__(parent)
        self.config = ModernMeterConfig()
        self.meter_bars = []

        # Setup styling
        self.setup_styling()

        # Create meters
        self.create_meters(meter_count, meter_labels)

        # Setup layout
        self.setup_layout()

    def setup_styling(self):
        """Setup modern dark theme styling."""
        self.setStyleSheet(f"""
            QWidget {{
                background-color: {self.config.BACKGROUND_COLOR};
                color: white;
                font-family: {self.config.FONT_FAMILY};
            }}
        """)

    def create_meters(self, meter_count, meter_labels=None):
        """Create meter bar widgets."""
        self.meter_bars = []

        for i in range(meter_count):
            if meter_labels and i < len(meter_labels):
                label = meter_labels[i]
            else:
                label = f"CH {i + 1}"

            # For multi-meter containers, always show labels
            meter_bar = ModernMeterBar(label, show_label=True, parent=self)
            self.meter_bars.append(meter_bar)

    def setup_layout(self):
        """Setup the horizontal layout for meters."""
        layout = QHBoxLayout(self)
        layout.setContentsMargins(self.config.MARGIN, self.config.MARGIN,
                                  self.config.MARGIN, self.config.MARGIN)
        layout.setSpacing(self.config.SPACING)

        for meter_bar in self.meter_bars:
            layout.addWidget(meter_bar)

        # Calculate and set size
        meter_count = len(self.meter_bars)
        width = (self.config.METER_WIDTH + 25 + self.config.SPACING) * meter_count + self.config.MARGIN * 2
        height = self.config.METER_HEIGHT + 100  # Extra space for labels and controls

        self.setFixedSize(max(width, 150), height)

    def set_level(self, meter_index, db_value):
        """Set the level for a specific meter."""
        if 0 <= meter_index < len(self.meter_bars):
            self.meter_bars[meter_index].set_level(db_value)

    def set_levels(self, db_values):
        """Set levels for all meters from a list."""
        for i, db_value in enumerate(db_values):
            if i < len(self.meter_bars):
                self.meter_bars[i].set_level(db_value)

    def get_level(self, meter_index):
        """Get the current level for a specific meter."""
        if 0 <= meter_index < len(self.meter_bars):
            return self.meter_bars[meter_index].get_current_level()
        return -120.0

    def get_levels(self):
        """Get current levels for all meters."""
        return [meter.get_current_level() for meter in self.meter_bars]

    def reset_all(self):
        """Reset all meters to minimum level."""
        for meter in self.meter_bars:
            meter.reset()

    def set_meter_label(self, meter_index, label):
        """Set the label for a specific meter."""
        if 0 <= meter_index < len(self.meter_bars):
            self.meter_bars[meter_index].set_label(label)

    def get_meter_count(self):
        """Get the number of meters."""
        return len(self.meter_bars)


class ModernMeterGUIBase:
    """
    Base class for creating modern meter GUIs.
    Provides common functionality that can be inherited by specific node implementations.
    """

    def __init__(self):
        self.config = ModernMeterConfig()
        self.isConnected = False
        self.timer = None
        self.client = None

    def setup_base_styling(self, widget):
        """Setup base styling that can be applied to any widget."""
        widget.setStyleSheet(f"""
            QWidget {{
                background-color: {self.config.BACKGROUND_COLOR};
                color: white;
                font-family: {self.config.FONT_FAMILY};
            }}
            QLabel {{
                color: #e0e0e0;
                font-weight: 500;
            }}
            QPushButton {{
                background-color: {self.config.CARD_BACKGROUND};
                border: 1px solid #374151;
                border-radius: 6px;
                padding: 8px 16px;
                font-weight: 500;
            }}
            QPushButton:hover {{
                background-color: #374151;
                border-color: {self.config.ACCENT_COLOR};
            }}
            QPushButton:pressed {{
                background-color: #4B5563;
            }}
            QCheckBox::indicator:unchecked {{
                background-color: #4B5563;
                border: 2px solid #6B7280;
                border-radius: 10px;
            }}
            QCheckBox::indicator:checked {{
                background-color: {self.config.ACCENT_COLOR};
                border: 2px solid {self.config.ACCENT_COLOR};
                border-radius: 10px;
            }}
        """)

    def create_title_label(self, text, parent=None):
        """Create a styled title label."""
        title_label = QLabel(text, parent)
        title_label.setStyleSheet(f"""
            font-size: {self.config.FONT_SIZE_LARGE}px;
            font-weight: bold;
            color: {self.config.ACCENT_COLOR};
            padding: 8px 0px;
        """)
        title_label.setAlignment(Qt.AlignCenter)
        return title_label

    def add_controls_to_layout(self, layout, controls):
        """Add control widgets to a layout with proper styling."""
        controls_widget = QWidget()
        controls_layout = QHBoxLayout(controls_widget)
        controls_layout.setContentsMargins(0, 0, 0, 0)

        controls_layout.addStretch()
        for control in controls:
            controls_layout.addWidget(control)
        controls_layout.addStretch()

        layout.addWidget(controls_widget)


# Example usage and factory functions

def create_single_meter(label="INPUT", show_label=False):
    """Factory function to create a single meter bar without label."""
    return ModernMeterBar(label, show_label)


def create_multi_meter(meter_count, labels=None):
    """Factory function to create a multi-meter container."""
    return ModernMeterContainer(meter_count, labels)


def create_channel_meters(channel_count):
    """Factory function to create meters for audio channels."""
    labels = [f"CH {i + 1}" for i in range(channel_count)]
    return ModernMeterContainer(channel_count, labels)
