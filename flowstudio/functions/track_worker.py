import json
import requests
from PyQt5.QtCore import QThread, pyqtSignal, QObject
from flowstudio.flow_build_manager import Manager

DEBUG = False

class TrackWorker(QThread):
    success_signal = pyqtSignal(str)
    error_signal = pyqtSignal(str)

    manager = Manager()
    common_urls, distribution_urls = manager.get_all_url_list()
    create_user_action_url = distribution_urls['create_user_action_url']

    def __init__(self, action, address, email):
        super().__init__()
        self.action = action
        self.address = address
        self.email = email
        self.action_text = {1: "Start Flow Studio",
                            2: "Close Flow Studio",
                            3: "Drag AO To Canvas",
                            4: "Save Project",
                            5: "Open Project",
                            6: "Connect To Engine (PC)",
                            7: "Launch Signal Flow Diff",
                            8: "Launch Custom AO Builder",
                            9: "Launch the Flow AI Agent",
                            10: "Send a message to the Agent",
                            11: "View the conversation history",
                            12: "Check a specific history record"
                            }

    def run(self):
        try:
            data = {
                "address": self.address,
                "action": self.action,
                "email": self.email,
                "content": self.action_text[self.action]
            }
            headers = {"Content-Type": "application/json"}
            raw_data = json.dumps(data)

            response = requests.post(self.create_user_action_url, data=raw_data, headers=headers, timeout=5)
            self.success_signal.emit(f"Create '{self.action_text[self.action]}' action: " + response.text)
        except Exception as e:
            if DEBUG: print("Error:", str(e))
            self.error_signal.emit(f"Create '{self.action_text[self.action]}' action failed: {str(e)}")
        finally:
            self.stop()

    def stop(self):
        if self.isRunning():
            self.quit()
            self.wait()

    def __del__(self):
        if DEBUG: print(f"TrackWorker deleted (action={self.action_text[self.action]})")


class TrackManager(QObject):
    def __init__(self):
        super().__init__()
        self.worker = None

    def track_user_action(self, action, license):
        if self.worker and self.worker.isRunning():
            self.worker.stop()
        address = license.address
        user = license.user
        if user is None:
            email = ''
        else:
            email = user['email']
        self.worker = TrackWorker(action, address, email)
        self.worker.success_signal.connect(self.handle_success)
        self.worker.error_signal.connect(self.handle_error)
        self.worker.finished.connect(self.worker.deleteLater)
        self.worker.start()

    def handle_success(self, msg):
        if DEBUG: print(msg)
        self.cleanup()

    def handle_error(self, err):
        if DEBUG: print(err)
        self.cleanup()

    def cleanup(self):
        if self.worker and self.worker.isRunning():
            self.worker.stop()
            self.worker = None