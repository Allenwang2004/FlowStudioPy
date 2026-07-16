import time
from PyQt5.QtCore import QThread, pyqtSignal
from ws4py.client.threadedclient import WebSocketClient
from flowstudio.flow_build_manager import Manager
import json
import requests
import threading

DEBUG = False
manager = Manager()
common_urls, distribution_urls = manager.get_all_url_list()
get_chat_res_url = distribution_urls['get_chat_res_url']
get_design_res_url = distribution_urls['get_design_res_url']
get_history_url = distribution_urls['get_history_url']
get_history_conversation_url = distribution_urls['get_history_conversation_url']
delete_history_conversation_url = distribution_urls['delete_history_conversation_url']
rename_history_conversation_title_url = distribution_urls['rename_history_conversation_title_url']
tag_and_untag_conversation_url = distribution_urls['tag_and_untag_conversation_url']
flow_ai_feedback_thumb_url = distribution_urls['flow_ai_feedback_thumb_url']

class ChatWebSocketClient(WebSocketClient):
    def __init__(self, ws_url, update_data, text, email, token, conversation_id, flw):
        headers = [('token', f'{token}')]
        super().__init__(ws_url, headers=headers)
        self.update_data = update_data
        self.res_text = ''
        self.text = text
        self.email = email
        self.token = token
        self.conversation_id = conversation_id
        self.flw = flw
        self.timeout = 10
        self.timeout_timer = None
        self.msg = ''
        self.first_status = True
        self.first_cmd = True

        self.pause_event = threading.Event()
        self.pause_event.set()

    def start_timeout_timer(self):
        self.timeout_timer = threading.Timer(self.timeout, self.on_timeout)
        self.timeout_timer.start()

    def cancel_timeout_timer(self):
        if self.timeout_timer:
            self.timeout_timer.cancel()
            self.timeout_timer = None

    def on_timeout(self):
        self.update_data.emit(("error", "Waiting for response timeout. Please try again.[failed]"))
        self.close()

    def opened(self):
        self.msg = ''
        self.first_status = True
        self.first_cmd = True
        self.start_timeout_timer()
        time.sleep(1)
        req = ('{"message":"%s",'
               '"user_id":"%s",'
               '"conversation_id":"%s",'
               '"flw":%s}') % (self.text, self.email, self.conversation_id, self.flw)
        print(req)
        self.send(req)

    def received_message(self, resp):
        self.pause_event.wait()
        print(resp)
        self.cancel_timeout_timer()
        try:
            if str(resp) not in ['"CONNECT_SUCCESS"']:
                msg = resp.data.decode()
                res = json.loads(msg)
                msg_type = res.get("type")

                if msg_type == "design_cmd":
                    if res["data"] == "end":
                        self.close()
                    if self.first_cmd:
                        self.first_cmd = False
                        if res["meta"]["source"] == "generated":
                            self.update_data.emit(("design", ""))
                    self.update_data.emit((msg_type, res["data"].strip()))
                elif msg_type in ["status", "routing", "thought", "action", "observation"]:
                    self.update_data.emit((msg_type, res["message"]))
                elif msg_type == "msg":
                    if self.msg == '':
                        self.msg = res["data"]
                        self.update_data.emit((msg_type, self.msg))
                    else:
                        self.update_data.emit((msg_type, res["data"]))
                elif msg_type == "error":
                    self.update_data.emit((msg_type, "error"))
                elif msg_type == "end":
                    self.update_data.emit((msg_type, "end"))
                else:
                    self.update_data.emit(('chatHistoryID', res["id"]))
        except Exception as e:
            print(f"received message fail: {e}")

    def closed(self, code, reason=None):
        self.cancel_timeout_timer()
        print("Closed down:", code, reason)

    def pause(self):
        """暂停"""
        self.pause_event.clear()

    def resume(self):
        """恢复"""
        self.pause_event.set()

class GetChatResWorker(QThread):
    update_data = pyqtSignal(tuple)

    def __init__(self, text, email, token, conversation_id, flw):
        super().__init__()
        self.text = text
        self.email = email
        self.token = token
        self.conversation_id = conversation_id
        self.flw = flw
        self.ws_client = None

    def run(self):
        try:
            # ws_url = f"wss://dev1.tymecho.com/tomcat/flowstudio/websocket/getChatResponse/{address}/{time_stamp}"
            ws_url = "ws://localhost:14080/flowai/ws/getAgentResponse_v4"
            # ws_url = "ws://localhost:8080/flowai/v1/websocket/chat/response"
            self.ws_client = ChatWebSocketClient(
                ws_url,
                self.update_data,
                self.text,
                self.email,
                self.token,
                self.conversation_id,
                self.flw
            )
            self.ws_client.connect()
            self.ws_client.run_forever()
        except Exception as e:
            print(f"Failed to connect: {e}")
            self.update_data.emit(('error', 'Connection failed, please check network connection and try again.[failed]'))

    def pause(self):
        if self.ws_client:
            self.ws_client.pause()

    def resume(self):
        if self.ws_client:
            self.ws_client.resume()

    def stop(self):
        """停止并关闭连接"""
        if self.ws_client:
            self.ws_client.close()

class DesignWebSocketClient(WebSocketClient):
    def __init__(self, ws_url, update_design, message, user_id, token, conversation_id):
        headers = [('token', f'{token}')]
        super().__init__(ws_url, headers=headers)
        self.update_design = update_design
        self.res_text = ''
        self.message = message
        self.user_id = user_id
        self.token = token
        self.conversation_id = conversation_id
        self.timeout = 10
        self.timeout_timer = None

    def start_timeout_timer(self):
        self.timeout_timer = threading.Timer(self.timeout, self.on_timeout)
        self.timeout_timer.start()

    def cancel_timeout_timer(self):
        if self.timeout_timer:
            self.timeout_timer.cancel()
            self.timeout_timer = None

    def on_timeout(self):
        self.update_design.emit("Waiting for response timeout. Please try again.[failed]")
        self.close()

    def opened(self):
        self.start_timeout_timer()
        time.sleep(1)
        req = ('{"message":"%s",'
               '"user_id":"%s",'
               '"conversation_id":"%s"}') % (self.message, self.user_id, self.conversation_id)
        self.send(req)

    def received_message(self, resp):
        self.cancel_timeout_timer()
        try:
            if str(resp) not in ['"CONNECT_SUCCESS"']:
                msg = resp.data.decode()
                res = json.loads(msg)
                msg_type = res.get("type")

                if msg_type == "design_cmd":
                    if res["data"] == "end":
                        self.close()
                    self.update_design.emit((msg_type, res["data"].strip()))
                elif msg_type == "status":
                    self.update_design.emit((msg_type, res["message"]))
                elif msg_type == "msg":
                    self.update_design.emit((msg_type, res["data"]))

        except Exception as e:
            print(f"received message fail: {e}")

    def closed(self, code, reason=None):
        self.cancel_timeout_timer()
        print("Closed down:", code, reason)

class GetDesignResWorker(QThread):
    update_design = pyqtSignal(tuple)

    def __init__(self, user_id, conversation_id, message, token, flw):
        super().__init__()
        self.user_id = user_id
        self.conversation_id = conversation_id
        self.message = message
        self.token = token
        self.flw = flw

    def run(self):
        try:
            # ws_url = f"wss://dev1.tymecho.com/tomcat/flowstudio/websocket/getChatResponse/{address}/{time_stamp}"
            ws_url = f"{get_chat_res_url}".replace('https', 'wss')
            self.ws_client = DesignWebSocketClient(ws_url, self.update_design, self.message, self.user_id, self.token, self.conversation_id)
            self.ws_client.connect()
            self.ws_client.run_forever()
        except Exception as e:
            print(f"Failed to connect: {e}")
            self.update_design.emit('Connection failed, please check network connection and try again.[failed]')

    def stop(self):
        if self.ws_client:
            self.ws_client.close()

    # def run(self):
    #     try:
    #         headers = {
    #             'Token': f'{self.token}',
    #             'Content-Type': 'application/json'
    #         }
    #         res = requests.post(get_design_res_url,
    #                             data=json.dumps({"user_id": self.user_id,
    #                                              "conversation_id": self.conversation_id,
    #                                              "message": self.message,
    #                                              "flw": self.flw
    #                                              }),
    #                             headers=headers)
    #         if res.status_code == 200:
    #             self.update_design.emit((True, json.loads(res.text)['data']))
    #         else:
    #             self.update_design.emit((False, f"Error Occurred: {res.status_code}: {res.text}"))
    #     except Exception as e:
    #         self.update_design.emit((False, f"Error Occurred: {e}"))

class GetFlowAIHistoryWorker(QThread):
    update_history_item = pyqtSignal(list, str)

    def __init__(self, email):
        super().__init__()
        self.email = email

    def run(self):
        try:
            data = {
                'email': self.email
            }
            headers = {"Content-Type": "application/json"}
            raw_data = json.dumps(data)
            response = requests.post(get_history_url, data=raw_data, headers=headers)
            if DEBUG: print("get history success: " + response.text)
            conversations_list = json.loads(response.text)['data']['list']
            history_list = []
            for item in conversations_list:
                history_item = {}
                history_item['create_time'] = item['first_chat_history'][0]['create_time']
                history_item['title'] = item['conversation']['title']
                history_item['user_id'] = item['user_id']
                history_item['conversation_id'] = item['conversation_id']
                history_item['conversation_tag'] = item['conversation']['tag']
                history_list.append(history_item)
            self.update_history_item.emit(history_list, "2a0d4b")
        except Exception as e:
            if DEBUG: print(f"Error occurred while getting history: {e}")
            self.update_history_item.emit('', "2a0d4b")

class FlowAIAPI:
    def get_conversation(self, conversation_id, user_id):
        try:
            data = {
                'conversation_id': conversation_id,
                "user_id": user_id
            }
            headers = {"Content-Type": "application/json"}
            raw_data = json.dumps(data)
            response = requests.post(get_history_conversation_url, data=raw_data, headers=headers)
            if DEBUG: print("get conversation success: " + response.text)
            return json.loads(response.text)['data']['list']
        except Exception as e:
            if DEBUG: print(f"Error occurred while getting conversation: {e}")
            res = [{'role':'FlowAI', 'message':'Error occurred while getting conversation, please try again later.'}]
            return res

    def handle_flow_ai_feedback_thumb(self, conversation_id, user_id, question, thumbType, chatHistoryId, reportType=0, reportDetail=""):
        try:
            data = {
                "conversationId": conversation_id,
                "userId": user_id,
                "question": question,
                "thumbType": thumbType,
                "chatHistoryId": chatHistoryId,
                "reportType": reportType,
                "reportDetail": reportDetail
            }
            headers = {"Content-Type": "application/json"}
            raw_data = json.dumps(data)
            response = requests.post(flow_ai_feedback_thumb_url, data=raw_data, headers=headers)
            if DEBUG: print("handle feedback success: " + response.text)
            return json.loads(response.text)
        except Exception as e:
            if DEBUG: print(f"Error occurred: {e}")

class UnTagConversationWorker(QThread):
    result_signal = pyqtSignal(bool, str)  # Emit success status and message


    def __init__(self, conversation_id, user_id):
        super().__init__()
        self.conversation_id = conversation_id
        self.user_id = user_id


    def run(self):
        try:
            data = {
                'conversation_id': self.conversation_id,
                "user_id": self.user_id,
                "tag": 0
            }
            headers = {"Content-Type": "application/json"}
            raw_data = json.dumps(data)


            response = requests.post(tag_and_untag_conversation_url, data=raw_data, headers=headers)


            if response.status_code == 200:
                self.result_signal.emit(True, "Untag successful")
            else:
                self.result_signal.emit(False, f"Error: {response.status_code} - {response.text}")
        except Exception as e:
            self.result_signal.emit(False, f"Exception: {str(e)}")


class TagConversationWorker(QThread):
    result_signal = pyqtSignal(bool, str)  # Emit success status and message


    def __init__(self, conversation_id, user_id):
        super().__init__()
        self.conversation_id = conversation_id
        self.user_id = user_id


    def run(self):
        try:
            data = {
                'conversation_id': self.conversation_id,
                "user_id": self.user_id,
                "tag": 1
            }
            headers = {"Content-Type": "application/json"}
            raw_data = json.dumps(data)


            response = requests.post(tag_and_untag_conversation_url, data=raw_data, headers=headers)


            if response.status_code == 200:
                self.result_signal.emit(True, "Tag successful")
            else:
                self.result_signal.emit(False, f"Error: {response.status_code} - {response.text}")
        except Exception as e:
            self.result_signal.emit(False, f"Exception: {str(e)}")


class RenameConversationTitleWorker(QThread):
    result_signal = pyqtSignal(bool, str)  # Emit success status and message


    def __init__(self, conversation_id, user_id, title):
        super().__init__()
        self.conversation_id = conversation_id
        self.user_id = user_id
        self.title = title


    def run(self):
        try:
            data = {
                'conversation_id': self.conversation_id,
                "user_id": self.user_id,
                "title": self.title
            }
            headers = {"Content-Type": "application/json"}
            raw_data = json.dumps(data)


            response = requests.post(rename_history_conversation_title_url, data=raw_data, headers=headers)


            if response.status_code == 200:
                self.result_signal.emit(True, "Rename successful")
            else:
                self.result_signal.emit(False, f"Error: {response.status_code} - {response.text}")
        except Exception as e:
            self.result_signal.emit(False, f"Exception: {str(e)}")


class DeleteConversationWorker(QThread):
    result_signal = pyqtSignal(bool, str)  # Emit success status and message


    def __init__(self, conversation_id, user_id):
        super().__init__()
        self.conversation_id = conversation_id
        self.user_id = user_id


    def run(self):
        try:
            data = {
                'conversation_id': self.conversation_id,
                "user_id": self.user_id
            }
            headers = {"Content-Type": "application/json"}
            raw_data = json.dumps(data)


            response = requests.post(delete_history_conversation_url, data=raw_data, headers=headers)


            if response.status_code == 200:
                self.result_signal.emit(True, "Delete successful")
            else:
                self.result_signal.emit(False, f"Error: {response.status_code} - {response.text}")
        except Exception as e:
            self.result_signal.emit(False, f"Exception: {str(e)}")