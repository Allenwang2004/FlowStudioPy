import ast
import copy
import json
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5 import QtCore, sip
import time

from flowstudio.controls.Toggle import SwitchButton
from flowstudio.flow_conf import OP_NODE_SUBPATCH, OP_NODE_ADC
from flowstudio.flow_file_converter import FLOW_File_Convert
from flowstudio.functions.special_components import SelectableTextEdit
from flowstudio.functions.thread_worker import GetChatResWorker, GetDesignResWorker, GetFlowAIHistoryWorker, FlowAIAPI, \
    DeleteConversationWorker, TagConversationWorker, UnTagConversationWorker, RenameConversationTitleWorker
from flowstudio.flow_sub_window import FLOW_Sub_Window
from flowstudio.functions.track_worker import TrackManager
from template.flow_ai_dialog import Ui_flow_ai_dialog


class FeedbackDialog(QDialog):
    def __init__(self, parent):
        super().__init__(parent)
        self.selected_category = None
        self.comment_text = ""
        self.setup_ui()

    def setup_ui(self):
        self.setWindowTitle("Feedback")
        self.setModal(True)
        self.setFixedSize(520, 400)
        
        self.setStyleSheet("""
            QDialog {
                background-color: #ffffff;
            }
        """)
        
        main_layout = QVBoxLayout()
        self.setLayout(main_layout)
        main_layout.setSpacing(20)
        main_layout.setContentsMargins(24, 24, 24, 24)
        
        top_layout = QHBoxLayout()
        
        title_label = QLabel("Feedback")
        title_label.setStyleSheet("""
            color: #1f2937;
            font-size: 18px;
            font-weight: 600;
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', system-ui, sans-serif;
            background-color: transparent;
            margin-left: 8px;
        """)
        
        top_layout.addWidget(title_label)
        top_layout.addStretch()
        
        main_layout.addLayout(top_layout)
        
        content_title = QLabel("Help us improve - What went wrong?")
        content_title.setStyleSheet("""
            color: #374151;
            font-size: 16px;
            font-weight: 500;
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', system-ui, sans-serif;
            background-color: transparent;
            border: none;
            padding: 0px;
            margin: 0px;
        """)
        main_layout.addWidget(content_title)
        
        category_label = QLabel("What type of issue do you wish to report? (optional)")
        category_label.setStyleSheet("""
            color: #6b7280;
            font-size: 14px;
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', system-ui, sans-serif;
            background-color: transparent;
            border: none;
            padding: 0px;
            margin: 0px;
        """)
        main_layout.addWidget(category_label)
        
        self.category_combo = QComboBox()
        self.category_combo.setStyleSheet("""
            QComboBox {
                padding: 12px 16px;
                border: 1px solid #d1d5db;
                border-radius: 6px;
                background-color: #ffffff;
                color: #374151;
                font-size: 14px;
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', system-ui, sans-serif;
                min-height: 20px;
            }
            QComboBox:hover {
                border-color: #9ca3af;
            }
            QComboBox:focus {
                border-color: #3b82f6;
                outline: none;
            }
            QComboBox::drop-down {
                border: none;
                width: 20px;
                padding-right: 10px;
            }
            QComboBox::down-arrow {
                image: none;
                border-left: 4px solid transparent;
                border-right: 4px solid transparent;
                border-top: 4px solid #6b7280;
                margin-right: 8px;
            }
            QComboBox QAbstractItemView {
                border: 1px solid #d1d5db;
                border-radius: 6px;
                background-color: #ffffff;
                selection-background-color: #f3f4f6;
                color: #374151;
                padding: 4px;
            }
            QComboBox QAbstractItemView::item {
                padding: 8px 12px;
                border: none;
                min-height: 20px;
            }
            QComboBox QAbstractItemView::item:hover {
                background-color: #f9fafb;
            }
            QComboBox QAbstractItemView::item:selected {
                background-color: #eff6ff;
                color: #1d4ed8;
            }
        """)
        
        categories = [
            ("0", "Select..."),
            ("1", "Incorrect Answer"),
            ("2", "Incomplete Answer"),
            ("3", "Unclear UI Instructions"),
            ("4", "Mismatch with Flow Studio Functionality"),
            ("5", "Misunderstood Question"),
            ("6", "Unusable Command / Code Error"),
            ("7", "UI Performance / Responsiveness Issue"),
            ("8", "Other (please specify)")
        ]
        
        for value, display_text in categories:
            self.category_combo.addItem(display_text, value)
        
        self.category_combo.setCurrentIndex(0)
        main_layout.addWidget(self.category_combo)
        
        comment_label = QLabel("Please provide details: (optional)")
        comment_label.setStyleSheet("""
            color: #6b7280;
            font-size: 14px;
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', system-ui, sans-serif;
            background-color: transparent;
            border: none;
            padding: 0px;
            margin: 0px;
        """)
        main_layout.addWidget(comment_label)
        
        self.comment_text_edit = QTextEdit()
        self.comment_text_edit.setPlaceholderText("What was unsatisfying about this response?")
        self.comment_text_edit.setStyleSheet("""
            QTextEdit {
                border: 1px solid #d1d5db;
                border-radius: 6px;
                background-color: #ffffff;
                color: #374151;
                padding: 12px;
                font-size: 14px;
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', system-ui, sans-serif;
                line-height: 1.5;
            }
            QTextEdit:focus {
                border-color: #3b82f6;
                outline: none;
            }
        """)
        self.comment_text_edit.setMaximumHeight(100)
        self.comment_text_edit.setMinimumHeight(80)
        main_layout.addWidget(self.comment_text_edit)
        
        
        main_layout.addStretch()
        
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        
        cancel_btn = QPushButton("Cancel")
        cancel_btn.setFixedSize(80, 36)
        cancel_btn.setStyleSheet("""
            QPushButton {
                background-color: #ffffff;
                color: #374151;
                border: 1px solid #d1d5db;
                border-radius: 6px;
                padding: 8px 16px;
                font-size: 14px;
                font-weight: 500;
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', system-ui, sans-serif;
            }
            QPushButton:hover {
                background-color: #f9fafb;
                border-color: #9ca3af;
            }
            QPushButton:pressed {
                background-color: #f3f4f6;
            }
        """)
        cancel_btn.clicked.connect(self.reject)
        
        self.submit_btn = QPushButton("Submit")
        self.submit_btn.setFixedSize(80, 36)
        self.submit_btn.setStyleSheet("""
            QPushButton {
                background-color: #3b82f6;
                color: #ffffff;
                border: none;
                border-radius: 6px;
                padding: 8px 16px;
                font-size: 14px;
                font-weight: 500;
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', system-ui, sans-serif;
            }
            QPushButton:hover {
                background-color: #2563eb;
            }
            QPushButton:pressed {
                background-color: #1d4ed8;
            }
            QPushButton:disabled {
                background-color: #e5e7eb;
                color: #9ca3af;
            }
        """)
        self.submit_btn.clicked.connect(self.accept_feedback)
        self.submit_btn.setEnabled(False)

        button_layout.addWidget(cancel_btn)
        button_layout.addSpacing(12)
        button_layout.addWidget(self.submit_btn)
        
        main_layout.addLayout(button_layout)

        self.category_combo.currentIndexChanged.connect(self.on_category_changed)


    def on_category_changed(self, index):
        self.submit_btn.setEnabled(index > 0)

    def accept_feedback(self):
        try:
            current_index = self.category_combo.currentIndex()
            if current_index > 0:
                self.selected_category = self.category_combo.currentData()
            else:
                self.selected_category = None
                
            self.comment_text = self.comment_text_edit.toPlainText().strip()
            self.accept()
        except Exception as e:
            print(f"Error in accept_feedback: {e}")
            self.accept()
        
    def get_feedback_data(self):
        return {
            "category": self.selected_category,
            "comment": self.comment_text
        }

class FlowAIDialogManager:
    
    def __init__(self, parent_window):
        self.parent = parent_window
        self.history_list = []
        self.has_flow_ai_dialog = False
        self.flow_ai_dialog = None
        self.flow_ai_mode = 0
        self.flow_ai_dialog_resize = False
        self.flow_ai_chat_text_edit_list = []
        self.get_chat_res_worker = None
        self.get_design_res_worker = None
        self._block_text_edit_signal = False
        
        self.form_factor_btn_list = []
        self.signal_path_btn_list = []
        self.complexity_btn_list = []
        self.feedback_widget_list = []

        self.accumulated_delay = 0
        self.interval_ms = 100

        self.current_ai_status = ""
        self.current_ai_msg = ""
        self.frist_add_cmd = True

        self.current_chat_history_id = 0

    def open_flow_ai_dialog(self):
        if self.flow_ai_dialog != None and not self.has_flow_ai_dialog:
            self.flow_ai_dialog.setVisible(True)
            self.has_flow_ai_dialog = True
            self.flow_ai_dialog_geometry()
            return

        if not self.has_flow_ai_dialog:
            self.flow_ai_timestamp = int(time.time() * 1000)
            self.flow_ai_dialog = QDialog(self.parent)
            self.flow_ai = Ui_flow_ai_dialog()
            self.flow_ai.setupUi(self.flow_ai_dialog)
            self.flow_ai.top_bar_widget.setLayout(self.flow_ai.top_bar_layout)
            self.flow_ai.tab_widget.setStyleSheet("QTabBar::tab { height: 0px; width: 0px; }"
                                                  "QTabWidget::pane{border:none;"
                                                  "background-color: rgba(0, 0, 0, 0);}")
            self.flow_ai_dialog.setWindowFlags(Qt.FramelessWindowHint)

            self.fine_tune_toggle = SwitchButton()
            self.fine_tune_toggle.setChecked(True)
            self.flow_ai.fine_tune_horizontalLayout.addWidget(self.fine_tune_toggle)
            self.flow_ai.fine_tune_horizontalLayout.addStretch()

            self.has_flow_ai_dialog = True
            self.flow_ai_dialog_geometry()
            self.flow_ai_dialog.setVisible(True)
            self.flow_ai.history_item_scrollArea.setVisible(False)
            self.flow_ai.mode_list_widget.setVisible(False)
            self.flow_ai.generate_res_label.setVisible(False)

            self.create_chat_loading()

            if self.flow_ai_mode == 0:
                self.select_chat_mode()
            else:
                self.select_design_mode()

            self._setup_ui_components()
            self._connect_signals()

            # Track user action "Launch the Flow AI Agent"
            self.tracker = TrackManager()
            self.tracker.track_user_action(action=9, license=self.parent.license_mechanism)
            
        else:
            self.flow_ai_dialog.setVisible(False)
            self.has_flow_ai_dialog = False

    def create_chat_loading(self):
        self.loading_gif = QLabel()
        self.movie = QMovie("../resources/loading.gif")
        self.loading_gif.setMovie(self.movie)
        self.loading_gif.setAlignment(Qt.AlignCenter)
        self.loading_gif.setFixedSize(20, 20)
        self.loading_gif.setScaledContents(True)
        self.loading_label = QLabel()
        self.toggle_loading(False)
        self.flow_ai.loading_horizontalLayout.setAlignment(Qt.AlignCenter)
        self.flow_ai.loading_horizontalLayout.addWidget(self.loading_gif)
        self.flow_ai.loading_horizontalLayout.addWidget(self.loading_label)

    def toggle_loading(self, is_loading):
        if is_loading:
            self.flow_ai.generate_btn.setEnabled(False)
            self.flow_ai.generate_res_label.setVisible(False)
            self.loading_label.setVisible(True)
            self.loading_gif.setVisible(True)
            self.movie.start()
            self.loading_label.setText("Generating...")
            self.flow_ai.generate_res_label.setText("")
        else:
            self.flow_ai.generate_btn.setEnabled(True)
            self.flow_ai.generate_res_label.setVisible(True)
            self.loading_label.setVisible(False)
            self.loading_gif.setVisible(False)
            self.movie.stop()


    def _setup_ui_components(self):
        # history dialog setLayout
        self.flow_ai.scrollAreaWidgetContents_2.setLayout(self.flow_ai.history_item_verticalLayout)
        self.flow_ai.history_item_scrollArea.setWidget(self.flow_ai.scrollAreaWidgetContents_2)

        # chat event handle
        self.flow_ai.scrollAreaWidgetContents.setLayout(self.flow_ai.chat_panel_verticalLayout)
        self.flow_ai.chat_panel.setWidget(self.flow_ai.scrollAreaWidgetContents)

        # design event handle
        self.flow_ai.scrollAreaWidgetContents_3.setLayout(self.flow_ai.design_tab_verticalLayout)
        self.flow_ai.design_panel.setWidget(self.flow_ai.scrollAreaWidgetContents_3)

    def _setup_drag_line(self):
        """設置拖拽線的 objectName"""
        if hasattr(self.flow_ai, 'drag_line'):
            self.flow_ai.drag_line.setObjectName('drag_line')

    def _connect_signals(self):
        """連接所有信號"""
        # history button click event
        self.flow_ai.history.clicked.connect(self.display_history_dialog)
        
        # new project button click event
        self.flow_ai.new_project.clicked.connect(self.create_new_project)
        
        # mode list click event
        self.flow_ai.mode_icon.clicked.connect(self.mode_list_widget_visible)
        self.flow_ai.mode_label.clicked.connect(self.mode_list_widget_visible)
        self.flow_ai.mode_down.clicked.connect(self.mode_list_widget_visible)
        self.flow_ai.chat_icon.clicked.connect(self.select_chat_mode)
        self.flow_ai.chat_label.clicked.connect(self.select_chat_mode)
        self.flow_ai.chat_des.clicked.connect(self.select_chat_mode)
        self.flow_ai.chat_tick.clicked.connect(self.select_chat_mode)
        self.flow_ai.design_icon.clicked.connect(self.select_design_mode)
        self.flow_ai.design_label.clicked.connect(self.select_design_mode)
        self.flow_ai.design_des.clicked.connect(self.select_design_mode)
        self.flow_ai.design_tick.clicked.connect(self.select_design_mode)

        # chat events
        self.flow_ai.send.clicked.connect(lambda: self.chat_send_msg(self.flow_ai.user_input_box.toPlainText(), "send"))
        self.flow_ai.stop.clicked.connect(self.stop_update_chat_res_box)
        self.flow_ai.example_1.clicked.connect(lambda: self.chat_send_msg(self.flow_ai.example_1.text().replace("\n", "")))
        self.flow_ai.example_2.clicked.connect(lambda: self.chat_send_msg(self.flow_ai.example_2.text().replace("\n", "")))
        self.flow_ai.example_3.clicked.connect(lambda: self.chat_send_msg(self.flow_ai.example_3.text().replace("\n", "")))
        self.flow_ai.example_4.clicked.connect(lambda: self.chat_send_msg(self.flow_ai.example_4.text().replace("\n", "")))
        self.flow_ai.user_input_box.textChanged.connect(self.input_box_text_change)
        self.flow_ai.user_input_box.enterPressed.connect(lambda: self.chat_send_msg(self.flow_ai.user_input_box.toPlainText(), "send"))

        # design events
        self._setup_form_factor_buttons()
        self._setup_signal_path_buttons()
        self._setup_complexity_buttons()
        
        self.flow_ai.describe_textEdit.textChanged.connect(self.describe_textedit_change)
        self.flow_ai.generate_btn.clicked.connect(self.generate_flow_project)
        
        # 設置預設選項
        self.flow_ai.headset_button.click()
        self.flow_ai.playback_btn.click()
        self.flow_ai.basic_btn.click()

    def _setup_form_factor_buttons(self):
        """設置外型因子按鈕"""
        self.form_factor_btn_list = [
            [self.flow_ai.headset_button, "headset"],
            [self.flow_ai.speaker_button, "speaker"],
            [self.flow_ai.mic_button, "mic"],
            [self.flow_ai.pc_button, "pc"]]
        for btn, name1 in self.form_factor_btn_list:
            btn.clicked.connect(lambda _, name=name1: self.foctor_btn_click(name, self.form_factor_btn_list))

    def _setup_signal_path_buttons(self):
        """設置信號路徑按鈕"""
        self.signal_path_btn_list = [
            [self.flow_ai.playback_btn, "playback"],
            [self.flow_ai.recording_btn, "recording"]]
        for btn, name1 in self.signal_path_btn_list:
            btn.clicked.connect(lambda _, name=name1: self.signal_path_complexity_btn_click(name, self.signal_path_btn_list))

    def _setup_complexity_buttons(self):
        """設置複雜度按鈕"""
        self.complexity_btn_list = [
            [self.flow_ai.basic_btn, "basic"],
            [self.flow_ai.advanced_btn, "advanced"]]
        for btn, name1 in self.complexity_btn_list:
            btn.clicked.connect(lambda _, name=name1: self.signal_path_complexity_btn_click(name, self.complexity_btn_list))

    def flow_ai_dialog_geometry(self):
        """設置 Flow AI 對話框的幾何位置"""
        if hasattr(self, 'has_flow_ai_dialog') and self.has_flow_ai_dialog:
            if self.parent.mdiArea.subWindowList() == []:
                ai_dialog_height = self.parent.window().mdiArea.height()
            else:
                ai_dialog_height = self.parent.window().mdiArea.height() - 20

            self.flow_ai_dialog.setMinimumWidth(550)
            self.flow_ai_dialog.setMaximumWidth(self.parent.width())
            self.flow_ai_dialog.setGeometry(self.parent.geometry().width() - self.flow_ai_dialog.width(),
                                            self.parent.editorDock.height() + self.parent.menuBar().height(),
                                            self.flow_ai_dialog.width(),
                                            ai_dialog_height)
            self.flow_ai.drag_line.setFixedHeight(ai_dialog_height)
            new_width = self.flow_ai_dialog.width()
            self.flow_ai.top_bar_widget.setFixedWidth(new_width)
            self.flow_ai.mode_list_widget.move((new_width - self.flow_ai.mode_list_widget.width()) / 2,
                                               self.flow_ai.mode_list_widget.y())
            self.flow_ai.tab_widget.setFixedHeight(ai_dialog_height - self.flow_ai.top_bar_widget.height())
            self.flow_ai.tab_widget.setFixedWidth(new_width)
            self.flow_ai.chat_panel.setFixedHeight(
                ai_dialog_height - self.flow_ai.input_edit_widget.height() - self.flow_ai.top_bar_widget.height() - 50)
            self.flow_ai.chat_panel.setFixedWidth(new_width)
            self.flow_ai.design_panel.setFixedHeight(
                ai_dialog_height - self.flow_ai.top_bar_widget.height() - 30)
            self.flow_ai.design_panel.setFixedWidth(new_width)
            self.flow_ai.input_edit_widget.setGeometry(10,
                                                 self.flow_ai.chat_panel.height() + self.flow_ai.top_bar_widget.height() - 20,
                                                 new_width - 20,
                                                 self.flow_ai.input_edit_widget.height())
            self.flow_ai.user_input_box.setFixedWidth(new_width - 110)
            self.flow_ai.send.move(self.flow_ai.user_input_box.x() + self.flow_ai.user_input_box.width(),
                                   self.flow_ai.send.y())

            user_input_box_pos = self.flow_ai.user_input_box.mapTo(self.flow_ai.chat_tab, QPoint(0, 0))
            self.flow_ai.design_label_2.setGeometry(
                user_input_box_pos.x() + 25,
                user_input_box_pos.y() + self.flow_ai.user_input_box.height() + 10,
                self.flow_ai.user_input_box.width(),
                20
            )
            self.flow_ai.design_label_2.setVisible(True)

            self.flow_ai.stop.move(self.flow_ai.user_input_box.x() + self.flow_ai.user_input_box.width(),
                                   self.flow_ai.send.y())
            self.input_box_text_change()

            self.flow_ai.history_item_scrollArea.setGeometry(0,
                                                             self.flow_ai.top_bar_widget.height(),
                                                             new_width,
                                                             ai_dialog_height - self.flow_ai.top_bar_widget.height())

    def mode_list_widget_visible(self):
        """切換模式列表可見性"""
        if self.flow_ai.mode_list_widget.isVisible():
            self.flow_ai.mode_list_widget.setVisible(False)
        else:
            self.flow_ai.mode_list_widget.setVisible(True)

        if self.flow_ai_mode == 0:
            self.flow_ai.chat_tick.setIcon(QIcon('../resources/tick.png'))
            self.flow_ai.design_tick.setIcon(QIcon())
        else:
            self.flow_ai.chat_tick.setIcon(QIcon())
            self.flow_ai.design_tick.setIcon(QIcon('../resources/tick.png'))

    def select_chat_mode(self):
        """選擇聊天模式"""
        self.flow_ai.mode_list_widget.setVisible(False)
        self.flow_ai_mode = 0
        self.flow_ai.mode_icon.setIcon(QIcon('../resources/chat.png'))
        self.flow_ai.mode_label.setText('Chat')
        self.flow_ai.top_bar_widget.setStyleSheet('background-color: #2a0d4b;')
        self.flow_ai.tab_widget.setCurrentIndex(0)

    def select_design_mode(self):
        """選擇設計模式"""
        self.flow_ai.mode_list_widget.setVisible(False)
        self.flow_ai_mode = 1
        self.flow_ai.mode_icon.setIcon(QIcon('../resources/design.png'))
        self.flow_ai.mode_label.setText('Design')
        self.flow_ai.top_bar_widget.setStyleSheet('background-color: #14316a;')
        self.flow_ai.tab_widget.setCurrentIndex(1)

    def set_example_status(self, bool):
        self.flow_ai.example_1.setVisible(bool)
        self.flow_ai.example_2.setVisible(bool)
        self.flow_ai.example_3.setVisible(bool)
        self.flow_ai.example_4.setVisible(bool)

    def clear_layout(self, layout):
        """清除佈局"""
        if isinstance(layout, QSpacerItem):
            self.flow_ai.chat_panel_verticalLayout.removeItem(layout)
            del layout
            return

        if layout is not None:
            while layout.count():
                item = layout.takeAt(0)
                widget = item.widget()
                if widget is not None:
                    widget.deleteLater()
                else:
                    sub_layout = item.layout()
                    if sub_layout is not None:
                        self.clear_layout(sub_layout)
            layout.deleteLater()

    def display_history_dialog(self):
        item_list = list(range(self.flow_ai.history_item_verticalLayout.count()))
        for i in item_list:
            item = self.flow_ai.history_item_verticalLayout.itemAt(i)
            self.clear_layout(item)

        has_display = self.flow_ai.history_item_scrollArea.isVisible()
        self.flow_ai.history_item_scrollArea.setVisible(not has_display)
        self.flow_ai.mode_icon.setVisible(has_display)
        self.flow_ai.mode_down.setVisible(has_display)
        self.flow_ai.mode_label.setVisible(has_display)
        self.flow_ai.new_project.setVisible(has_display)
        self.flow_ai.mode_list_widget.setVisible(False)

        if has_display: return

        self.flow_ai.history_item_verticalLayout.setAlignment(Qt.AlignTop)

        if self.flow_ai_mode == 0:
            self.history_loading_layout = QVBoxLayout()
            self.history_loading = QLabel()
            self.history_movie = QMovie("../resources/loading.gif")
            self.history_loading.setMovie(self.history_movie)
            self.history_loading.setAlignment(Qt.AlignCenter)
            self.history_loading.setFixedSize(60, 60)
            self.history_loading.setScaledContents(True)
            self.history_loading_label = QLabel('Loading...')
            self.history_loading_label.setStyleSheet("""QLabel {
                    font-family: 'Calibri';
                    font-size: 16pt;
                }
            """)
            self.history_loading_layout.addStretch()
            self.history_loading_layout.addWidget(self.history_loading, alignment=Qt.AlignCenter)
            self.history_loading_layout.addWidget(self.history_loading_label, alignment=Qt.AlignCenter)
            self.history_loading_layout.addStretch()
            self.flow_ai.history_item_verticalLayout.addLayout(self.history_loading_layout)
            self.history_movie.start()
            self.history_loading.setVisible(True)

            email = self.parent.encrypt(self.parent.license_mechanism.user['email']).decode("utf-8")
            self.get_chat_history_worker = GetFlowAIHistoryWorker(email)
            self.get_chat_history_worker.update_history_item.connect(self.display_history_item)
            self.get_chat_history_worker.start()

            # Track user action "View the conversation history"
            self.tracker = TrackManager()
            self.tracker.track_user_action(action=11, license=self.parent.license_mechanism)
        else:
            print("Design Mode history TO DO.")

    def display_history_item(self, history_list, colors):
        # 清理旧的布局内容
        while self.flow_ai.history_item_verticalLayout.count():
            item = self.flow_ai.history_item_verticalLayout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
            elif item.layout():
                self.clear_layout(item.layout())

        # 更新 history_list
        self.history_list = history_list  # Update the history_list
        #self.clear_layout(self.history_loading_layout)
        self.history_movie.stop()
        # Ensure the loading label exists and is not deleted
        if hasattr(self, 'history_loading') and not sip.isdeleted(self.history_loading):
            self.history_loading.setVisible(False)
        if hasattr(self, 'history_loading_label') and not sip.isdeleted(self.history_loading_label):
            self.history_loading_label.setVisible(False)

        # Clear the loading layout if it exists
        if hasattr(self, 'history_loading_layout') and not sip.isdeleted(self.history_loading_layout):
            self.clear_layout(self.history_loading_layout)

        style = """
                font-family: Calibri;
                font-size: 14pt;
                color: white;
                border: none;
                text-align: left top;
                padding: 0;
                """
        layout = QVBoxLayout()
        if history_list != []:
            for item in reversed(history_list):
                item_date = QLabel()
                item_date.setText(item['create_time'].split(" ")[0])
                item_date.setStyleSheet("color: #7a7f7f;"
                                        "font-family: Calibri;"
                                        "font-size: 12pt;"
                                        )

                item_title = QPushButton(item['title'])
                item_title.setCursor(QCursor(Qt.PointingHandCursor))
                item_title.clicked.connect(lambda _, current_item=item: self.click_history_item(current_item))
                item_title.setStyleSheet(style)

                # Create a QLabel for the tag icon
                tag_label = QLabel()
                tag_label.setFixedSize(32, 32)  # Ensure QLabel size matches the icon
                pixmap = QPixmap("../resources/tag.png")
                tag_label.setPixmap(pixmap.scaled(16, 16, Qt.KeepAspectRatio, Qt.SmoothTransformation))

                if item['conversation_tag'] == 1:
                    tag_label.setVisible(True)
                else:
                    tag_label.setVisible(False)

                # Add three-dot button
                menu_btn = QPushButton()
                menu_btn.setCursor(Qt.PointingHandCursor)
                menu_btn.setIcon(QIcon("../resources/three-dots.png"))  # Replace with your icon path
                menu_btn.setIconSize(QtCore.QSize(32, 32))
                menu_btn.setStyleSheet("border: none; background: transparent;")

                # 綁定點擊事件
                menu_btn.clicked.connect(lambda _, current_item=item: self.show_context_menu(menu_btn, current_item))

                # 创建水平布局，将标题和按钮放在同一行
                title_layout = QHBoxLayout()
                title_layout.addWidget(item_title)
                title_layout.addStretch()  # 添加拉伸以将按钮推到末尾
                title_layout.addWidget(tag_label)  # Add the tag icon
                title_layout.addWidget(menu_btn)

                # Add spacer to leave some space after the button
                spacer = QSpacerItem(10, 0, QSizePolicy.Fixed, QSizePolicy.Minimum)  # Adjust width as needed
                title_layout.addItem(spacer)

                layout1 = QVBoxLayout()
                layout1.addWidget(item_date)
                layout1.addLayout(title_layout)
                layout1.setSpacing(2)
                layout.addLayout(layout1)
        else:
            msg = 'Connection error. Please try again later.'
            if history_list == []:
                msg = 'Data Not Available'
            item_title = QPushButton(msg)
            item_title.setStyleSheet(style)
            layout.addWidget(item_title)

        self.flow_ai.history_item_verticalLayout.addLayout(layout)
        self.flow_ai.history_item_verticalLayout.setContentsMargins(30, 10, 0, 15)
        self.flow_ai.scrollAreaWidgetContents_2.setStyleSheet(f"background-color: #{colors};"
                                                              "border: none;")
        self.flow_ai.history_item_scrollArea.setStyleSheet(
            self.flow_ai.history_item_scrollArea.styleSheet() +
            ("""QScrollBar:vertical {
                        border-width: 0px;
                        border: none;
                        background: #%s;
                        width: 10px;
                        margin: 0px 0px 0px 0px;
                    }""" % colors)
        )

    def click_history_item(self, item):
        self.flow_ai.history_item_scrollArea.setVisible(False)
        self.flow_ai.mode_icon.setVisible(True)
        self.flow_ai.mode_down.setVisible(True)
        self.flow_ai.mode_label.setVisible(True)
        self.flow_ai.new_project.setVisible(True)
        self.set_example_status(False)
        # Clear previous chat messages
        item_list = list(range(self.flow_ai.chat_panel_verticalLayout.count()))
        item_list.reverse()
        for i in item_list:
            if i <= 1: continue
            item1 = self.flow_ai.chat_panel_verticalLayout.itemAt(i)
            self.clear_layout(item1)
        self.flow_ai_chat_text_edit_list.clear()
        # Display the selected chat history
        self.flow_ai_timestamp = item["conversation_id"]
        conversation_id = self.parent.encrypt(item["conversation_id"]).decode("utf-8")
        user_id = self.parent.encrypt(item["user_id"]).decode("utf-8")
        response = FlowAIAPI().get_conversation(conversation_id, user_id)

        user_question = ''
        for conversation in reversed(response):
            if conversation['role'] == "User":
                self.flow_ai.chat_panel_verticalLayout.addLayout(self.chat_user_template(conversation['message']))
                user_question = conversation['message']
            else:
                print('conversation', conversation)
                print(item)
                self.flow_ai.chat_panel_verticalLayout.addLayout(self.chat_ai_template(conversation=conversation, user_question=user_question))
                chat_box = self.flow_ai_chat_text_edit_list[-1]
                chat_box.setFont(QFont("Calibri", 12))
                chat_box.setMarkdown(conversation['message'])
                document = chat_box.document()
                margin = document.documentMargin()
                ideal_width = chat_box.width() - 2 * margin
                document.setTextWidth(ideal_width)
                height = document.documentLayout().documentSize().height()
                chat_box.setFixedHeight(int(height) + 5)
                for widget in self.feedback_widget_list:
                    widget.setVisible(True)


        # Track user action "Check a specific history record"
        self.tracker = TrackManager()
        self.tracker.track_user_action(action=12, license=self.parent.license_mechanism)

    def show_context_menu(self, widget, current_item):
        print(current_item)

        menu = QMenu(widget)
        delete_action = QAction("Delete", menu)
        rename_action = QAction("Rename", menu)
        if current_item['conversation_tag'] == 1:
            tag_action = QAction("UnTag", menu)
        else:
            tag_action = QAction("Tag", menu)

        menu.addAction(delete_action)
        menu.addAction(rename_action)
        menu.addAction(tag_action)

        # 连接删除操作
        delete_action.triggered.connect(lambda: self.confirm_delete(current_item))

        # 连接重命名操作
        rename_action.triggered.connect(lambda: self.rename_dialog(current_item))

        # 连接tag untag操作
        tag_action.triggered.connect(lambda: self.tag_operation(current_item))

        # 获取鼠标点击的全局坐标
        global_pos = QCursor.pos()
        menu.exec_(global_pos)

    def confirm_delete(self, current_item):
        reply = QMessageBox.question(
            self.flow_ai_dialog,
            "Confirm Deletion",
            "Are you sure you want to delete this conversation?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        if reply == QMessageBox.Yes:
            self.delete_history_item(current_item)

    def delete_history_item(self, current_item):
        # 删除逻辑
        print(f"Deleting item: {current_item}")
        # 在这里实现删除操作，例如从布局中移除
        # Remove the item from the history list
        self.history_list = [item for item in self.history_list if item != current_item]
        # Refresh the history display
        self.display_history_item(self.history_list, "2a0d4b")

        conversation_id = self.parent.encrypt(current_item["conversation_id"]).decode("utf-8")
        user_id = self.parent.encrypt(current_item["user_id"]).decode("utf-8")
        self.worker = DeleteConversationWorker(conversation_id, user_id)
        self.worker.start()

    def rename_dialog(self, current_item):
        dialog = QInputDialog(self.flow_ai_dialog)
        dialog.setWindowTitle("Rename conversation")
        dialog.setLabelText("Enter the new title:")
        dialog.setTextValue(current_item.get("title", ""))
        dialog.resize(400, 200)  # Set a larger size for the dialog
        dialog.setStyleSheet("""
               QDialog {
                   background-color: #f9fafb;
                   border-radius: 12px;
                   border: 1px solid #e5e7eb;
                   box-shadow: 0px 4px 10px rgba(0, 0, 0, 0.1);
               }
               QLabel {
                   font-size: 14px;
                   color: #374151;
                   font-family: 'Segoe UI', sans-serif;
               }
               QLineEdit {
                   font-size: 14px;
                   padding: 10px;
                   border: 1px solid #d1d5db;
                   border-radius: 8px;
                   background-color: #ffffff;
                   color: #374151;
               }
               QLineEdit:focus {
                   border-color: #3b82f6;
                   outline: none;
               }
               QPushButton {
                   font-size: 14px;
                   padding: 8px 16px;
                   border-radius: 8px;
                   font-weight: 500;
                   font-family: 'Segoe UI', sans-serif;
               }
               QPushButton:hover {
                   background-color: #2563eb;
                   color: #ffffff;
               }
               QPushButton:pressed {
                   background-color: #1d4ed8;
               }
               QPushButton:disabled {
                   background-color: #e5e7eb;
                   color: #9ca3af;
               }
           """)
        if dialog.exec_() == QDialog.Accepted:
            new_name = dialog.textValue().strip()
            if new_name:
                current_item["title"] = new_name
                self.display_history_item(self.history_list, "2a0d4b")  # Refresh the display
                self.rename_history_item(current_item)

    def rename_history_item(self, current_item):
        # 改名逻辑
        print(f"Rename item: {current_item}")

        conversation_id = self.parent.encrypt(current_item["conversation_id"]).decode("utf-8")
        user_id = self.parent.encrypt(current_item["user_id"]).decode("utf-8")
        title = self.parent.encrypt(current_item["title"]).decode("utf-8")
        self.worker = RenameConversationTitleWorker(conversation_id, user_id, title)
        self.worker.start()

    def tag_operation(self, current_item):
        # Check the current tag status
        if current_item['conversation_tag'] == 1:
            # Untag the conversation
            conversation_id = self.parent.encrypt(current_item["conversation_id"]).decode("utf-8")
            user_id = self.parent.encrypt(current_item["user_id"]).decode("utf-8")
            current_item['conversation_tag'] = 0  # Update the tag status locally
            # Start the untag worker
            self.worker = UnTagConversationWorker(conversation_id, user_id)
            self.worker.start()
        else:
            # Tag the conversation
            conversation_id = self.parent.encrypt(current_item["conversation_id"]).decode("utf-8")
            user_id = self.parent.encrypt(current_item["user_id"]).decode("utf-8")
            current_item['conversation_tag'] = 1  # Update the tag status locally
            # Start the untag worker
            self.worker = TagConversationWorker(conversation_id, user_id)
            self.worker.start()

        # Refresh the history display
        self.display_history_item(self.history_list, "2a0d4b")
    def create_new_project(self):
        self.flow_ai_timestamp = int(time.time() * 1000)
        self.flow_ai.mode_list_widget.setVisible(False)
        self.feedback_widget_list = []
        self.stop_update_chat_res_box()

        if self.flow_ai_mode == 0:
            self.flow_ai_chat_text_edit_list.clear()
            self.set_example_status(True)
            item_list = list(range(self.flow_ai.chat_panel_verticalLayout.count()))
            item_list.reverse()
            for i in item_list:
                if i <= 1: continue
                item1 = self.flow_ai.chat_panel_verticalLayout.itemAt(i)
                self.clear_layout(item1)
            self.flow_ai_chat_text_edit_list.clear()
            if hasattr(self.flow_ai, "design_label_2"):
                self.flow_ai.design_label_2.setVisible(True)
        if self.flow_ai_mode == 1:
            self.flow_ai.headset_button.click()
            self.flow_ai.playback_btn.click()
            self.flow_ai.basic_btn.click()
            self.flow_ai.describe_textEdit.clear()
            self.flow_ai.generate_res_label.setVisible(False)

    def chat_user_template(self, text):
        """創建用戶訊息模板"""
        user_box = SelectableTextEdit(text)
        user_box.setFont(QFont("Calibri", 12))
        user_box.setStyleSheet("background-color: rgba(0, 0, 0, 0);")
        user_box.setReadOnly(True)
        user_box.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        user_box.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

        # Calculate box dimensions
        fm = QFontMetrics(user_box.font())
        box_width = fm.horizontalAdvance(user_box.toPlainText()) + 12
        max_width = self.flow_ai_dialog.width() - 80
        user_box.setFixedWidth(min(box_width, max_width))

        document = user_box.document()
        document.setTextWidth(user_box.width())
        user_box.setFixedHeight(document.size().height() + 5)

        # Layout for user message
        layout = QHBoxLayout()
        layout.addStretch(1)
        layout.addWidget(user_box)

        self.flow_ai_chat_text_edit_list.append(user_box)
        return layout

    def chat_ai_template(self, conversation=None, user_question=''):
        """創建 AI 回應模板"""
        self.create_chat_loading()

        # Common styles
        transparent_style = "background-color: rgba(0, 0, 0, 0);"
        button_style = """border: none; color: white; background-color: rgba(0, 0, 0, 0);"""

        # Chat box
        text = "Response generation in progress. Please wait..."
        chat_box = SelectableTextEdit(text)
        chat_box.setFont(QFont("Calibri", 12))
        chat_box.setStyleSheet(transparent_style)
        chat_box.setReadOnly(True)
        chat_box.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        chat_box.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        chat_box.setFixedWidth(self.flow_ai_dialog.width() - 70)
        chat_box.setFixedHeight(40)
        chat_box.document().setDocumentMargin(0)

        # AI icon
        icon = QLabel()
        icon.setAlignment(Qt.AlignTop)
        icon.setFixedWidth(30)
        icon.setFixedHeight(30)
        icon.setStyleSheet(transparent_style)
        icon.setPixmap(QPixmap('../resources/res_ai.png'))


        # Copy button
        copy_btn = QPushButton()
        copy_btn.setCursor(Qt.PointingHandCursor)
        copy_btn.setIcon(QIcon("../resources/ai_copy.png"))
        copy_btn.setIconSize(QtCore.QSize(16, 16))
        copy_btn.setStyleSheet(button_style)
        copy_btn.setToolTip("copy")

        def copy_chat_box_text():
            clipboard = QApplication.clipboard()
            clipboard.setText(chat_box.toPlainText())
        copy_btn.clicked.connect(copy_chat_box_text)

        # Feedback button
        # Thumb Up
        thumb_up_btn = QPushButton()
        thumb_up_btn.setCursor(Qt.PointingHandCursor)
        thumb_up_btn.setIcon(QIcon("../resources/thumbs-up.png"))
        thumb_up_btn.setIconSize(QtCore.QSize(16, 16))
        thumb_up_btn.setStyleSheet(button_style)
        thumb_up_btn.setToolTip("Good Response")

        def handle_thumb_up():
            self.handle_feedback_positive(conversation, user_question, thumb_up_btn, thumb_down_btn)
        thumb_up_btn.clicked.connect(handle_thumb_up)

        # Thumb Down
        thumb_down_btn = QPushButton()
        thumb_down_btn.setCursor(Qt.PointingHandCursor)
        thumb_down_btn.setIcon(QIcon("../resources/thumbs-down.png"))
        thumb_down_btn.setIconSize(QtCore.QSize(16, 16))
        thumb_down_btn.setStyleSheet(button_style)
        thumb_down_btn.setToolTip("Bad Response")


        def handle_thumb_down():
            self.handle_feedback_negative(conversation, user_question, thumb_down_btn, thumb_up_btn)
        thumb_down_btn.clicked.connect(handle_thumb_down)

        copy_btn.setVisible(False)
        thumb_up_btn.setVisible(False)
        thumb_down_btn.setVisible(False)
        self.feedback_widget_list.append(copy_btn)
        self.feedback_widget_list.append(thumb_up_btn)
        self.feedback_widget_list.append(thumb_down_btn)

        button_layout = QHBoxLayout()
        button_layout.addWidget(copy_btn)
        button_layout.addWidget(thumb_up_btn)
        button_layout.addWidget(thumb_down_btn)
        button_layout.addStretch(1)
        button_layout.setSpacing(8)
        button_layout.setContentsMargins(0, 5, 0, 0)

        if conversation != None:
            if conversation['flowAiFeedback'] != None:
                if conversation['flowAiFeedback']['thumb_type'] == 1:
                    self.handle_feedback_button_states(thumb_up_btn, thumb_down_btn)
                else:
                    self.handle_feedback_button_states(thumb_down_btn, thumb_up_btn)

        chat_layout = QVBoxLayout()
        chat_layout.addWidget(chat_box)
        chat_layout.addWidget(self.loading_gif)
        chat_layout.addLayout(button_layout)
        chat_layout.addStretch(1)
        chat_layout.setContentsMargins(5, 0, 0, 0)
        chat_layout.setSpacing(4)

        # Layouts
        icon_layout = QVBoxLayout()
        icon_layout.addWidget(icon)
        icon_layout.addStretch(1)
        icon_layout.setContentsMargins(0, 0, 0, 0)

        main_layout = QHBoxLayout()
        main_layout.addLayout(icon_layout)
        main_layout.addLayout(chat_layout)
        main_layout.setSpacing(0)
        main_layout.setContentsMargins(0, 0, 0, 10)

        self.flow_ai_chat_text_edit_list.append(chat_box)
        return main_layout

    def chat_send_msg(self, text, msg_type="example"):
        """處理發送聊天訊息"""
        # Delete Stretch
        item_count = self.flow_ai.chat_panel_verticalLayout.count()
        target_index = item_count - 1
        item = self.flow_ai.chat_panel_verticalLayout.itemAt(target_index)
        if isinstance(item, QSpacerItem):
            self.flow_ai.chat_panel_verticalLayout.removeItem(item)
            del item

        self.accumulated_delay = 0
        self.current_ai_status = ""
        self.current_ai_msg = ""
        self.frist_add_cmd = True
        self.flow_ai.mode_list_widget.setVisible(False)

        ori_text = text
        if text == "":
            return
        else:
            text = text.replace("\n", " ")
            text = text.replace("\\n", " ")
            text = text.replace("\"", "''")
            text = text.replace("\\", " ")
            text = text.replace("\t", " ")
        self.set_example_status(False)

        self.flow_ai.example_1.setVisible(False)
        self.flow_ai.example_2.setVisible(False)
        self.flow_ai.example_3.setVisible(False)
        self.flow_ai.example_4.setVisible(False)

        # Add user and AI message templates
        self.flow_ai.chat_panel_verticalLayout.addLayout(self.chat_user_template(ori_text))
        self.flow_ai.chat_panel_verticalLayout.addLayout(self.chat_ai_template(user_question=ori_text))
        self.flow_ai.chat_panel_verticalLayout.addStretch(1)

        def scroll_once():
            scrollbar = self.flow_ai.chat_panel.verticalScrollBar()
            scrollbar.setValue(scrollbar.maximum())
            scrollbar.rangeChanged.disconnect(scroll_once)
        self.flow_ai.chat_panel.verticalScrollBar().rangeChanged.connect(scroll_once)

        if msg_type == "send":
            self.flow_ai.user_input_box.clear()
        self.flow_ai.send.hide()

        # flw
        current_window = self.parent.getCurrentNodeEditorWidget()
        nodes_in_main = self.parent.findMain().widget().scene.nodes
        for node in nodes_in_main:
            if node.op_code == OP_NODE_SUBPATCH:
                self.parent.open_subwindow_in_subpatch_recursively(node.title)
                self.parent.setActiveSubWindow(current_window.parent())
        raw_data = json.dumps(self.parent.findMain().widget().scene.serialize(), indent=4)
        data = json.loads(raw_data)
        converter = FLOW_File_Convert(copy.deepcopy(data), windows=self.parent.mdiArea.subWindowList())
        result, not_support_nodes = converter.process()
        flw = json.dumps(result)

        if self.parent.license_mechanism.user is None:
            # Use default test user for local testing
            email = "test@localhost"
            token = "test_token"
        else:
            email = self.parent.license_mechanism.user['email']
            token = self.parent.license_mechanism.token

        # Start worker for AI response
        # email = 'local@test'
        # token = self.parent.license_mechanism.token if self.parent.license_mechanism.user is not None else "test_token"
            
        self.get_chat_res_worker = GetChatResWorker(text, email, token, self.flow_ai_timestamp, flw)
        self.get_chat_res_worker.update_data.connect(self.update_chat_res_box)
        self.get_chat_res_worker.start()

        # Track user action "Send a message to the Agent"
        self.tracker = TrackManager()
        self.tracker.track_user_action(action=10, license=self.parent.license_mechanism)

    def update_chat_res_box(self, res):
        self.loading_gif.setVisible(True)
        self.movie.start()
        """更新聊天回應框"""
        if res[0] in ["msg", "status"]:
            if res[0] == "status":
                text = res[1]
                styled_text = f'<div style="font-style: italic;color: #999;">{text}</div>'
                self.current_ai_status += styled_text
            elif res[0] == "msg":
                self.current_ai_msg += res[1]
            chat_box = self.flow_ai_chat_text_edit_list[-1]
            chat_box.setFont(QFont("Calibri", 12))
            chat_box.setMarkdown(self.current_ai_status + self.current_ai_msg)
            document = chat_box.document()
            document.setTextWidth(chat_box.width())
            height = document.size().height() + 5
            chat_box.setFixedHeight(height)
        elif res[0] == "design_cmd":
            if res[1] == "end":
                self.stop_update_chat_res_box()
            else:
                self.mainWindow = self.parent.findMain()
                delay = self.accumulated_delay
                QTimer.singleShot(delay, lambda: self.execute_single_command(res[1], self.mainWindow))
                self.accumulated_delay += self.interval_ms
        elif res[0] == "end":
            self.stop_update_chat_res_box()
        elif res[0] == "chatHistoryID":
            self.current_chat_history_id = res[1]
        elif res[0] == "design":
            if self.parent.window().isModified():
                self.get_chat_res_worker.pause()
                res = QMessageBox.warning(
                    self.parent,
                    "About to lose your work?",
                    "The document has been modified.\n Do you want to save your changes?",
                    QMessageBox.Save | QMessageBox.Discard | QMessageBox.Cancel
                )
                if res == QMessageBox.Save:
                    self.parent.onFileSave()
                    self.parent.onFileNew()
                    self.get_chat_res_worker.resume()
                elif res == QMessageBox.Discard:
                    self.parent.skip_save_check = True
                    self.parent.onFileNew()
                    self.parent.skip_save_check = False
                    self.get_chat_res_worker.resume()
                elif res == QMessageBox.Cancel:
                    self.stop_update_chat_res_box()
                    return

        # self.stop_update_chat_res_box()
        # # "[DONE]" is success reply
        # if "[DONE]" in text:
        #     self.stop_update_chat_res_box()
        #     return
        #
        # if not self.flow_ai_chat_text_edit_list:
        #     # List is empty, nothing to update
        #     return
        #
        # chat_box = self.flow_ai_chat_text_edit_list[-1]
        # chat_box.setFont(QFont("Calibri", 12))
        # if '[failed]' in text:
        #     chat_box.setText(text.replace('[failed]', ''))
        #     self.stop_update_chat_res_box()
        #     return
        # chat_box.setMarkdown(text)
        # document = chat_box.document()
        # document.setTextWidth(chat_box.width())
        # height = document.size().height() + 5
        # chat_box.setFixedHeight(height)
        # # "input_value=" is send error input
        # if "input_value=" in text:
        #     self.stop_update_chat_res_box()
        #     return

    def stop_update_chat_res_box(self):
        """停止更新聊天回應框"""
        self.flow_ai.send.show()
        if hasattr(self, "get_chat_res_worker") and self.get_chat_res_worker is not None:
            self.get_chat_res_worker.stop()
        self.loading_gif.setVisible(False)
        self.movie.stop()

        for widget in self.feedback_widget_list:
            widget.setVisible(True)

        # item = {'conversation_id': str(self.flow_ai_timestamp),
        #         'user_id': self.parent.license_mechanism.user['email']}
        # self.click_history_item(item)

    def chat_ai_res_copy(self, text):
        """AI 回應複製處理"""
        print(text)

    def handle_feedback_positive(self, conversation, user_question, clicked_btn, other_btn):
        """處理正面反饋 - 保留點擊的按鈕並設為disabled"""
        try:
            conversation_id = self.parent.encrypt(str(self.flow_ai_timestamp)).decode("utf-8")
            user_id = self.parent.encrypt(self.parent.license_mechanism.user['email']).decode("utf-8")
            question = self.parent.encrypt(user_question).decode("utf-8")
            thumbType = 1
            if conversation is None:
                chatHistoryId = self.current_chat_history_id
            else:
                chatHistoryId = conversation['id']
            response = FlowAIAPI().handle_flow_ai_feedback_thumb(conversation_id, user_id, question, thumbType, chatHistoryId)

            self.handle_feedback_button_states(clicked_btn, other_btn)

        except Exception as e:
            print(f"Error handling positive feedback: {e}")

    def handle_feedback_negative(self, conversation, user_question, clicked_btn, other_btn):
        """處理負面反饋 - 保留點擊的按鈕並設為disabled"""
        try:
            feedback_dialog = FeedbackDialog(self.flow_ai_dialog)
            
            if feedback_dialog.exec_() == QDialog.Accepted:
                feedback_data = feedback_dialog.get_feedback_data()

                conversation_id = self.parent.encrypt(str(self.flow_ai_timestamp)).decode("utf-8")
                user_id = self.parent.encrypt(self.parent.license_mechanism.user['email']).decode("utf-8")
                question = self.parent.encrypt(user_question).decode("utf-8")
                thumbType = 2
                if conversation is None:
                    chatHistoryId = self.current_chat_history_id
                else:
                    chatHistoryId = conversation['id']
                reportType = feedback_data.get("category")
                reportDetail = self.parent.encrypt(feedback_data.get("comment")).decode("utf-8")
                response = FlowAIAPI().handle_flow_ai_feedback_thumb(conversation_id, user_id, question, thumbType,
                                                                     chatHistoryId, reportType, reportDetail)

                # 處理按鈕狀態
                self.handle_feedback_button_states(clicked_btn, other_btn)

                # 顯示簡潔的感謝訊息
                msg = QMessageBox(self.flow_ai_dialog)
                msg.setWindowTitle("Feedback")
                msg.setText("Thank you for your feedback! We'll use it to improve our AI.")
                msg.setIcon(QMessageBox.Information)
                msg.setStandardButtons(QMessageBox.Ok)
                msg.setStyleSheet("""
                    QMessageBox {
                        background-color: #ffffff;
                    }
                    QMessageBox QLabel {
                        color: #374151;
                        background-color: transparent;
                        font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', system-ui, sans-serif;
                    }
                    QMessageBox QPushButton {
                        background-color: #3b82f6;
                        color: #ffffff;
                        border: none;
                        padding: 8px 16px;
                        border-radius: 6px;
                        min-width: 60px;
                        font-weight: 500;
                    }
                    QMessageBox QPushButton:hover {
                        background-color: #2563eb;
                    }
                """)
                msg.exec_()
                
        except Exception as e:
            print(f"Error handling negative feedback: {e}")
            # 如果出現錯誤，至少顯示一個簡單的錯誤訊息
            msg = QMessageBox(self.flow_ai_dialog)
            msg.setWindowTitle("Error")
            msg.setText("Sorry, there was an error processing your feedback. Please try again.")
            msg.setIcon(QMessageBox.Critical)
            msg.setStandardButtons(QMessageBox.Ok)
            msg.setStyleSheet("""
                QMessageBox {
                    background-color: #ffffff;
                }
                QMessageBox QLabel {
                    color: #374151;
                    background-color: transparent;
                }
            """)
            msg.exec_()

    def handle_feedback_button_states(self, clicked_btn, other_btn):
        """處理反饋按鈕狀態 - 保留點擊的按鈕並設為disabled，隱藏另一個"""
        try:
            # 隱藏未點擊的按鈕
            other_btn.hide()
            
            # 將點擊的按鈕設為disabled並添加半透明樣式
            clicked_btn.setEnabled(False)
            clicked_btn.setCursor(Qt.ArrowCursor)

            clicked_btn.setStyleSheet("""
                QPushButton {
                    border: none; 
                    color: rgba(255, 255, 255, 0.5);
                    background-color: rgba(128, 128, 128, 0.3);
                    border-radius: 4px;
                }
                QPushButton:disabled {
                    color: rgba(255, 255, 255, 0.5);
                    background-color: rgba(128, 128, 128, 0.3);
                    border-radius: 4px;
                }
                QPushButton:hover:disabled {
                    color: rgba(255, 255, 255, 0.5);
                    background-color: rgba(128, 128, 128, 0.3);
                    border-radius: 4px;
                }
                QToolTip {
                    background-color: #333333;
                    color: #ffffff;
                    border: 1px solid #555555;
                    padding: 4px 8px;
                    border-radius: 4px;
                    font-size: 12px;
                }
            """)

            current_tooltip = clicked_btn.toolTip()
            if "Good Response" in current_tooltip:
                clicked_btn.setToolTip("Positive feedback submitted")
                clicked_btn.setIcon(QIcon("../resources/thumbs-up-fill.png"))
            elif "Bad Response" in current_tooltip:
                clicked_btn.setToolTip("Negative feedback submitted")
                clicked_btn.setIcon(QIcon("../resources/thumbs-down-fill.png"))
                
            clicked_btn.update()
            clicked_btn.repaint()
                
        except Exception as e:
            print(f"Error handling feedback button states: {e}")

    def input_box_text_change(self):
        """輸入框文字變更處理"""
        if self.flow_ai.user_input_box.toPlainText() == "":
            self.flow_ai.send.setEnabled(False)
        else:
            self.flow_ai.send.setEnabled(True)

        document = self.flow_ai.user_input_box.document()
        document.setTextWidth(self.flow_ai.user_input_box.width() - 10)
        height = document.size().height()
        if height < 30: height = 30
        if height > 170: height = 170
        height_gap = height - self.flow_ai.user_input_box.height()
        self.flow_ai.user_input_box.setFixedHeight(height)
        self.flow_ai.input_edit_widget.setGeometry(self.flow_ai.input_edit_widget.x(),
                                                   self.flow_ai.input_edit_widget.y() - height_gap,
                                                   self.flow_ai.input_edit_widget.width(),
                                                   self.flow_ai.user_input_box.height() + 20)
        self.flow_ai.send.setFixedHeight(self.flow_ai.input_edit_widget.height() - 10)
        self.flow_ai.chat_panel.setFixedHeight(self.flow_ai.chat_panel.height() - height_gap)

    def foctor_btn_click(self, text, btn_list):
        """外型因子按鈕點擊處理"""
        print(text)
        self.flow_ai.mode_list_widget.setVisible(False)
        
        # 根據名稱找到對應的按鈕
        clicked_button = None
        for button, name in btn_list:
            if name == text:
                clicked_button = button
                break
        
        # 更新所有按鈕的樣式
        for button, name in btn_list:
            if button == clicked_button:
                button.setStyleSheet("""border: 2px solid #a8a8a8;
                                        border-radius: 12px;
                                        background-color: #14316a;""")
            else:
                button.setStyleSheet("""border: 2px solid #a8a8a8;
                                        border-radius: 12px;""")

    def signal_path_complexity_btn_click(self, text, btn_list):
        """信號路徑/複雜度按鈕點擊處理"""
        print(text)
        self.flow_ai.mode_list_widget.setVisible(False)
        
        # 根據名稱找到對應的按鈕
        clicked_button = None
        for button, name in btn_list:
            if name == text:
                clicked_button = button
                break
        
        # 更新所有按鈕的樣式
        for button, name in btn_list:
            if button == clicked_button:
                button.setStyleSheet("""color: white;
                                        font: 14pt "Calibri";
                                        border: 2px solid #a8a8a8;
                                        border-radius: 12px;
                                        background-color: #14316a;""")
            else:
                button.setStyleSheet("""color: white;
                                        font: 14pt "Calibri";
                                        border: 2px solid #a8a8a8;
                                        border-radius: 12px;""")

    def describe_textedit_change(self):
        """描述文字編輯變更處理"""
        if self._block_text_edit_signal:
            return

        self._block_text_edit_signal = True
        try:
            text = self.flow_ai.describe_textEdit.toPlainText()
            count = len(text)
            if count >= 100:
                self.flow_ai.describe_textEdit.setPlainText(text[:100])
                self.flow_ai.describe_textEdit.moveCursor(QTextCursor.End)
            char_count = len(self.flow_ai.describe_textEdit.toPlainText())
            self.flow_ai.count_limit_label.setText(f'{char_count}/100')
        finally:
            self._block_text_edit_signal = False

    def update_flow_project_by_design(self, res):
        """根據設計更新流程專案"""
        if res[0] == "status":
            self.loading_label.setText(res[1])
        elif res[0] == "design_cmd":
            if res[1] == "end":
                self.toggle_loading(False)
            else:
                self.mainWindow = self.parent.findMain()
                delay = self.accumulated_delay
                QTimer.singleShot(delay, lambda: self.execute_single_command(res[1], self.mainWindow))
                self.accumulated_delay += self.interval_ms
        elif res[0] == "msg":
            self.flow_ai.generate_res_label.setText(res[1])

    def execute_single_command(self, cmd, mainWindow):
        """执行单个命令"""
        try:
            nodes = mainWindow.widget().scene.nodes
            edges = mainWindow.widget().scene.edges

            parts = cmd.split('/')
            action = parts[0]

            if action == "add":
                code = int(parts[1])
                designator = int(parts[2])
                x = int(parts[3])
                y = int(parts[4])

                if code == OP_NODE_ADC and self.frist_add_cmd:
                    self.frist_add_cmd = False
                    mainWindow.widget().view.setViewTopLeft(x - 30, y - 30)

                if len(parts) > 5 and parts[5].strip():
                    parameters = ast.literal_eval(parts[5])
                else:
                    parameters = None

                if parameters is None:
                    parameters = {'num_channels': 1, 'num_in_channels': 1, 'num_out_channels': 1, 'num_bands': 1,
                                  'num_taps': 1, 'configure': '2.0'}
                parameters['control'] = False
                designators = []
                for node in nodes:
                    if node.op_code == code:
                        designators.append(node.designator)

                if designator in designators: return

                new_node = mainWindow.widget().initNewNodeCondition(code, parameters)
                new_node.designator = designator
                new_node.setPos(x, y)
                new_node.title = new_node.title + '_' + str(designator)

                if code == OP_NODE_SUBPATCH:
                    self.parent.onEnterGroupFile(new_node)
                    new_node.cwd = new_node.title
                    self.parent.mdiArea.setActiveSubWindow(self.parent.findMain())

                mainWindow.widget().scene.history.storeHistory(
                    f"Created {new_node.__class__.__name__}-{new_node.title}", setModified=True)
            elif action == "delete":
                code = int(parts[1])
                designator = int(parts[2])
                for node in nodes:
                    if node.op_code == code and node.designator == designator:
                        node.grNode.setSelected(True)
                        node.scene.getView().window().onEditDelete()
                        break
            elif action in ["connect", "connectControl"]:
                code_1 = int(parts[1])
                designator_1 = int(parts[2])
                port_1 = int(parts[3])
                code_2 = int(parts[4])
                designator_2 = int(parts[5])
                port_2 = int(parts[6])

                start_socket = None
                end_socket = None

                for node in nodes:
                    if node.op_code == code_1 and node.designator == designator_1:
                        if action == "connect":
                            start_socket = node.outputs[port_1]
                        else:
                            start_socket = node.outctrls[port_1]
                        continue
                    if node.op_code == code_2 and node.designator == designator_2:
                        if action == "connect":
                            end_socket = node.inputs[port_2]
                        else:
                            end_socket = node.inctrls[port_2]
                        continue

                mainWindow.widget().view.dragging.add_edge(start_socket=start_socket,
                                                           end_socket=end_socket,
                                                           ignore_message_box=True,
                                                           ignore_drag_edge=True)
            elif action == "disconnect":
                code_1 = int(parts[1])
                designator_1 = int(parts[2])
                port_1 = int(parts[3])
                code_2 = int(parts[4])
                designator_2 = int(parts[5])
                port_2 = int(parts[6])

                for edge in edges:
                    if (edge.start_socket.node.op_code == code_1 and
                            edge.start_socket.node.designator == designator_1 and
                            edge.start_socket.index == port_1 and
                            edge.end_socket.node.op_code == code_2 and
                            edge.end_socket.node.designator == designator_2 and
                            edge.end_socket.index == port_2):
                        edge.grEdge.setSelected(True)
                        edge.scene.getView().window().onEditDelete()
                        break
            elif action == "set":
                code = int(parts[1])
                designator = int(parts[2])
                parameter_name = parts[3]
                parameter_value = parts[4]

                for node in nodes:
                    if node.op_code == code and node.designator == designator:
                        for widget_label in node.manager.widgetSet:
                            if widget_label == parameter_name:
                                widget = node.manager.widgetSet[widget_label]
                                if type(widget.widget_value) is int:
                                    widget.widget_value = int(parameter_value)
                                elif type(widget.widget_value) is float:
                                    widget.widget_value = float(parameter_value)
                                elif type(widget.widget_value) is list:
                                    parameter_value = json.loads(parameter_value.replace('\\"', '"'))
                                    widget.widget_value = parameter_value
                                node.manager.parameterStored()
            elif action == "move":
                code = int(parts[1])
                designator = int(parts[2])
                x = int(parts[3])
                y = int(parts[4])

                for node in nodes:
                    if node.op_code == code and node.designator == designator:
                        node.grNode.setPos(x, y)
                        break
                mainWindow.widget().scene.history.storeHistory("Node moved", setModified=True)
        except Exception as e:
            print(f"Critical error executing command: {cmd}")
            print(f"Error details: {str(e)}")

    def generate_flow_project(self):
        """生成流程專案"""
        self.accumulated_delay = 0
        # self.flow_ai.describe_textEdit.setText("8 in 8 out")
        self.flow_ai.generate_res_label.setVisible(True)
        if self.flow_ai.describe_textEdit.toPlainText() == "":
            self.flow_ai.generate_res_label.setText("Please enter your target design description")
            return False
        self.toggle_loading(True)
        self.parent.window().onFileNew()

        # request parameters
        email = 'local@test'
        user_id = self.parent.encrypt(email).decode("utf-8")
        conversation_id = self.parent.encrypt(str(self.flow_ai_timestamp)).decode("utf-8")
        text = self.flow_ai.describe_textEdit.toPlainText()
        message = text
        token = self.parent.license_mechanism.token

        flw = ""
        if self.fine_tune_toggle.isChecked():
            current_window = self.parent.getCurrentNodeEditorWidget()
            nodes_in_main = self.parent.findMain().widget().scene.nodes
            for node in nodes_in_main:
                if node.op_code == OP_NODE_SUBPATCH:
                    self.parent.open_subwindow_in_subpatch_recursively(node.title)
                    self.parent.setActiveSubWindow(current_window.parent())
            raw_data = json.dumps(self.parent.findMain().widget().scene.serialize(), indent=4)
            data = json.loads(raw_data)
            converter = FLOW_File_Convert(copy.deepcopy(data), windows=self.parent.mdiArea.subWindowList())
            result, not_support_nodes = converter.process()
            flw = result
        else:
            flw = ""

        # get design json data
        self.get_design_res_worker = GetDesignResWorker(user_id, conversation_id, message, token, flw)
        self.get_design_res_worker.update_design.connect(self.update_flow_project_by_design)
        self.get_design_res_worker.start()


    # 鼠標事件處理方法
    def handle_mouse_press(self, event):
        """處理鼠標按下事件"""
        if not hasattr(self, 'flow_ai_dialog') or self.flow_ai_dialog is None:
            return False
            
        # 檢查是否點擊在 flow_ai_dialog 區域內
        if not self.flow_ai_dialog.isVisible():
            return False
            
        # 將事件座標轉換為 flow_ai_dialog 的局部座標
        local_pos = self.flow_ai_dialog.mapFromGlobal(event.globalPos())
        
        # 檢查是否在 dialog 範圍內
        if not self.flow_ai_dialog.rect().contains(local_pos):
            return False
            
        # 在 flow_ai_dialog 內查找被點擊的控件
        clicked_widget = self.flow_ai_dialog.childAt(local_pos)
        
        # 檢查是否點擊了 drag_line
        if clicked_widget and clicked_widget.objectName() == 'drag_line':
            self.flow_ai_dialog_resize = True
            return True
        
        # 如果直接檢查 drag_line 控件（備用方案）
        if hasattr(self.flow_ai, 'drag_line') and clicked_widget == self.flow_ai.drag_line:
            self.flow_ai_dialog_resize = True
            return True
        
        self.flow_ai_dialog_resize = False
        return False

    def handle_mouse_release(self, event):
        """處理鼠標釋放事件"""
        if self.flow_ai_dialog_resize:
            self.flow_ai_dialog_resize = False
            return True
        return False

    def handle_mouse_move(self, event):
        """處理鼠標移動事件（用於調整對話框大小）"""
        if not self.flow_ai_dialog_resize:
            return False
            
        if self.flow_ai_dialog_resize:
            if self.parent.findMain() == None:
                ai_dialog_height = self.parent.window().mdiArea.height()
            else:
                ai_dialog_height = self.parent.window().mdiArea.height() - 20
            new_pos = event.pos().x()
            pos = self.flow_ai_dialog.x()
            increase = new_pos - pos
            new_width = self.flow_ai_dialog.width() - increase
            if new_width > 1000: new_width = 1000
            if new_width < 550: new_width = 550
            self.flow_ai_dialog.setFixedWidth(new_width)
            self.flow_ai_dialog_geometry()
            
            for item in self.flow_ai_chat_text_edit_list:
                fm = QFontMetrics(item.font())
                box_width = fm.horizontalAdvance(item.toPlainText()) + 20
                max_width = self.flow_ai_dialog.width() - 80
                if box_width >= max_width:
                    item.setFixedWidth(max_width)
                else:
                    item.setFixedWidth(box_width)

                document = item.document()
                document.setTextWidth(item.width())
                height = document.size().height() + 5
                item.setFixedHeight(height)

