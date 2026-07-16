import ast
import copy
import json
import os
from PyQt5.QtWidgets import QDialog
from PyQt5.QtWebEngineWidgets import QWebEngineView, QWebEngineScript
from PyQt5.QtWebChannel import QWebChannel
from PyQt5.QtCore import QObject, QUrl, Qt, QTimer, pyqtSlot, pyqtSignal, QThread
from flowstudio.flow_conf import OP_NODE_SUBPATCH, OP_NODE_ADC
from flowstudio.flow_file_converter import FLOW_File_Convert

from flowstudio.functions.thread_worker import GetChatResWorker

SHOW_WEB_DEBUG_TOOLS = False

RUN_MOCK_WORKER = False

MOCK_LOGS_1 = [
    { 'type': 'routing', 'content': 'Routing to Respond Agent: user asked about PEQ in Flow Studio.'},
    { 'type': 'thought', 'content': 'I need to explain PEQ. Let me look up the documentation first.'},
    { 'type': 'action', 'content': 'using tool: Flow object RAG (PEQ)'},
    { 'type': 'observation', 'content': 'PEQ is a powerful audio processing tool based on IIR biquad filters, supporting Bell, Shelf, and Pass filter types.'},

    # 模拟一下重复循环（根据你的数据）
    { 'type': 'routing', 'content': 'Routing to Respond Agent: user asked about PEQ in Flow Studio.'},
    { 'type': 'thought', 'content': 'I need to explain PEQ. Let me look up the documentation first.'},
    { 'type': 'action', 'content': 'using tool: Flow object RAG (PEQ)'},
    { 'type': 'observation', 'content': 'PEQ is a powerful audio processing tool based on IIR biquad filters, supporting Bell, Shelf, and Pass filter types.'},

    { 'type': 'summary', 'content': 'PEQ documentation retrieved. I should also build an example flow.'},

    # 这里是发给 UI 显示的 Markdown 消息 (msg 类型)
    { 'type': 'msg', 'content': 'Now I understand PEQ. Let me also ask Canvas Agent to build an example flow for you to try.\n\n'},

    { 'type': 'routing', 'content': 'Routing to Canvas Agent: build a simple PEQ demo signal flow.'},
    { 'type': 'thought', 'content': 'I will use the signal flow proposal generator first.'},
    { 'type': 'action', 'content': 'using tool: signal flow proposal generator (PEQ demo)'},
    { 'type': 'observation', 'content': '2 input channels → stereo PEQ → 2 output nodes. Simple and clean.'},
    { 'type': 'thought', 'content': 'Proposal looks good. Building the structure graph.'},
    { 'type': 'action', 'content': 'using tool: topology (proposal → JSON graph)'},
    { 'type': 'observation', 'content': 'JSON graph with nodes and edges returned.'},
    { 'type': 'action', 'content': 'using tool: cmd_gen (graph → verified commands)'},
    { 'type': 'observation', 'content': 'Verified command list generated.'},
    { 'type': 'summary', 'content': 'Canvas flow built and commands are ready.'},

    { 'type': 'msg', 'content': '## PEQ in Flow Studio\n\nPEQ is based on **Infinite Impulse Response (IIR) biquad filters**, making it highly efficient for real-time audio applications.'},
    { 'type': 'msg', 'content': '\n\n**Supported filter types:**\n- **Bell / Peaking** – boost or cut at a centre frequency with configurable Q'},
    { 'type': 'msg', 'content': '\n- **Low / High Shelf** – smooth roll-off shaping at band edges\n- **Low Pass / High Pass** – cut frequencies above or below the cutoff'},
    { 'type': 'msg', 'content': '\n\n## Example Flow\n\nHere is the demo flow: two input channels feed through a stereo PEQ block then route to two output nodes.' },

    {'type': 'end', 'content': '' }
]

MOCK_LOGS_DESIGN_CMD = [
    {'type': 'routing', 'content': 'Routing to Respond Agent: user asked about PEQ in Flow Studio.'},
    {'type': 'thought', 'content': 'I need to explain PEQ. Let me look up the documentation first.'},
    {'type': 'action', 'content': 'using tool: Flow object RAG (PEQ)'},
    {'type': 'observation',
     'content': 'PEQ is a powerful audio processing tool based on IIR biquad filters, supporting Bell, Shelf, and Pass filter types.'},

    # 模拟一下重复循环（根据你的数据）
    {'type': 'routing', 'content': 'Routing to Respond Agent: user asked about PEQ in Flow Studio.'},
    {'type': 'thought', 'content': 'I need to explain PEQ. Let me look up the documentation first.'},
    {'type': 'action', 'content': 'using tool: Flow object RAG (PEQ)'},
    {'type': 'observation',
     'content': 'PEQ is a powerful audio processing tool based on IIR biquad filters, supporting Bell, Shelf, and Pass filter types.'},

    {'type': 'summary', 'content': 'PEQ documentation retrieved. I should also build an example flow.'},

    # 这里是发给 UI 显示的 Markdown 消息 (msg 类型)
    {'type': 'msg',
     'content': 'Now I understand PEQ. Let me also ask Canvas Agent to build an example flow for you to try.\n\n'},

    {'type': 'routing', 'content': 'Routing to Canvas Agent: build a simple PEQ demo signal flow.'},
    {'type': 'thought', 'content': 'I will use the signal flow proposal generator first.'},
    {'type': 'action', 'content': 'using tool: signal flow proposal generator (PEQ demo)'},
    {'type': 'observation', 'content': '2 input channels → stereo PEQ → 2 output nodes. Simple and clean.'},
    {'type': 'thought', 'content': 'Proposal looks good. Building the structure graph.'},
    {'type': 'action', 'content': 'using tool: topology (proposal → JSON graph)'},
    {'type': 'observation', 'content': 'JSON graph with nodes and edges returned.'},
    {'type': 'action', 'content': 'using tool: cmd_gen (graph → verified commands)'},
    {'type': 'observation', 'content': 'Verified command list generated.'},
    {'type': 'summary', 'content': 'Canvas flow built and commands are ready.'},

    {'type': 'msg',
     'content': '## PEQ in Flow Studio\n\nPEQ is based on **Infinite Impulse Response (IIR) biquad filters**, making it highly efficient for real-time audio applications.'},
    {'type': 'msg',
     'content': '\n\n**Supported filter types:**\n- **Bell / Peaking** – boost or cut at a centre frequency with configurable Q'},
    {'type': 'msg',
     'content': '\n- **Low / High Shelf** – smooth roll-off shaping at band edges\n- **Low Pass / High Pass** – cut frequencies above or below the cutoff'},
    {'type': 'msg',
     'content': '\n\n## Example Flow\n\nHere is the demo flow: two input channels feed through a stereo PEQ block then route to two output nodes.'},

    { 'type': 'design_cmd', 'content': 'add/11/1/0/0'},
    { 'type': 'design_cmd', 'content': 'add/32/1/200/0'},
    { 'type': 'design_cmd', 'content': 'add/32/2/500/0'},
    { 'type': 'design_cmd', 'content': 'add/12/1/800/0'},
    { 'type': 'design_cmd', 'content': 'connect/11/1/0/32/1/0'},
    { 'type': 'design_cmd', 'content': 'connect/32/1/0/32/2/0'},
    { 'type': 'design_cmd', 'content': 'connect/32/2/0/12/1/0'},

    {'type': 'end', 'content': ''}
]

class MockGetChatResWorker(QThread):
    update_data = pyqtSignal(tuple)

    def __init__(self, text, email, token, conversation_id, flw):
        super().__init__()
        self.text = text
        self.email = email
        self.token = token
        self.conversation_id = conversation_id
        self.flw = flw

        if text == "mock_1":
            self.logs = MOCK_LOGS_1
        elif text == "mock_design_cmd":
            self.logs = MOCK_LOGS_DESIGN_CMD
        else:
            self.logs = MOCK_LOGS_1

        self._current_index = 0
        self._timer = None
        self._is_paused = False

    def run(self):
        print(f"[Mock Worker] Starting stream for: {self.text}")

        # 使用 QTimer 模拟逐条推送
        self._timer = QTimer()
        self._timer.timeout.connect(self.send_next_log)
        self._timer.start(200)  # 每 200ms 推一条，模拟打字机效果

        self.exec_()  # 进入事件循环

    def send_next_log(self):
        if self._is_paused:
            return

        if self._current_index < len(self.logs):
            log_item = self.logs[self._current_index]

            # 构造 tuple: (type, content)
            # 你的 UI 应该根据这个 type 来决定是显示在“调试面板”还是“聊天窗口”
            data_tuple = (log_item['type'], log_item['content'])

            self.update_data.emit(data_tuple)
            self._current_index += 1
        else:
            # 发完了
            if self._timer:
                self._timer.stop()
            self.quit()

    def pause(self):
        print("[Mock Worker] Paused")
        self._is_paused = True

    def resume(self):
        print("[Mock Worker] Resumed")
        self._is_paused = False

    def stop(self):
        print("[Mock Worker] Stopped")
        if self._timer:
            self._timer.stop()
        self.quit()

class FlowAIBridge(QObject):
    """Exposed to Vue via QWebChannel"""

    # PyQt5 → Vue signals
    messageReceived = pyqtSignal(str, str)   # (type, content)

    def __init__(self, manager: 'FlowAIWebManager'):
        super().__init__()
        self.manager = manager

    @pyqtSlot(str, str, str)
    def sendMessage(self, text: str, conversation_id: str, flw):
        """Called by Vue to start a chat"""
        self.manager.start_ws(text, conversation_id)

    @pyqtSlot()
    def stopStream(self):
        """Called by Vue to stop streaming"""
        print('[Bridge] stopStream called')
        self.manager.stop_ws()


class FlowAIWebManager:

    DIST_PATH = os.path.abspath(
        os.path.join(os.path.dirname(__file__), '..', 'resources', 'flow-ai-index.html')
    )
    MIN_WIDTH     = 400
    MAX_WIDTH     = 900
    DEFAULT_WIDTH = 550
    DRAG_LINE_WIDTH = 6

    def __init__(self, parent_window):
        self.parent = parent_window
        self.dialog   = None
        self.web_view = None
        self.bridge   = None
        self.channel  = None
        self.ws_worker = None
        self.frist_add_cmd = True
        self._visible      = False
        self._width        = self.DEFAULT_WIDTH
        self._dragging     = False
        self._drag_start_x = 0
        self._drag_start_w = 0
        self._current_route = '/ai'
        self.accumulated_delay = 0
        self.interval_ms = 100

    # ── public API ────────────────────────────────────────────

    def preload(self):
        """Call on app start to warm up Chromium — avoids first-open freeze"""
        self._create_dialog()
        self.dialog.setVisible(False)

    def toggle(self, route='/ai'):
        if self._visible:
            self.close()
        else:
            self.open(route)

    def open(self, route='/ai'):
        self._current_route = route
        if self.dialog is None:
            QTimer.singleShot(0, self._create_dialog)
            return
        self._visible = True
        self.dialog.setVisible(True)
        self.update_geometry()

    def close(self):
        self._visible = False
        if self.dialog:
            self.dialog.setVisible(False)

    def update_geometry(self):
        if not self._visible or self.dialog is None:
            return
        parent = self.parent
        mdi_h  = parent.mdiArea.height()
        if parent.mdiArea.subWindowList():
            mdi_h -= 20
        top  = parent.editorDock.height() + parent.menuBar().height()
        left = parent.geometry().width() - self._width
        self.dialog.setGeometry(left, top, self._width, mdi_h)
        self.web_view.resize(self._width, mdi_h)

    # ── mouse events (forwarded from FLOW_Window) ─────────────

    def handle_mouse_press(self, event) -> bool:
        if not self._visible or self.dialog is None:
            return False
        local = self.dialog.mapFromGlobal(event.globalPos())
        if 0 <= local.x() <= self.DRAG_LINE_WIDTH and self.dialog.rect().contains(local):
            self._dragging     = True
            self._drag_start_x = event.globalPos().x()
            self._drag_start_w = self._width
            return True
        return False

    def handle_mouse_release(self, event) -> bool:
        if self._dragging:
            self._dragging = False
            return True
        return False

    def handle_mouse_move(self, event) -> bool:
        if not self._dragging:
            return False
        delta     = self._drag_start_x - event.globalPos().x()
        new_width = max(self.MIN_WIDTH, min(self.MAX_WIDTH, self._drag_start_w + delta))
        self._width = new_width
        self.update_geometry()
        return True

    # ── WebSocket ─────────────────────────────────────────────

    def start_ws(self, text: str, conversation_id: str):
        self.stop_ws()
        self.frist_add_cmd = True
        self.accumulated_delay = 0
        lm = self.parent.license_mechanism
        email = lm.user['email'] if lm.user else ''
        token = lm.token if hasattr(lm, 'token') else ''

        # Serialize the current .xml scene and pass to the backend
        flw = '""'
        try:
            current_window = self.parent.getCurrentNodeEditorWidget()
            nodes_in_main = self.parent.findMain().widget().scene.nodes
            for node in nodes_in_main:
                if node.op_code == OP_NODE_SUBPATCH:
                    self.parent.open_subwindow_in_subpatch_recursively(node.title)
                    self.parent.setActiveSubWindow(current_window.parent())
            raw_data = json.dumps(self.parent.findMain().widget().scene.serialize(), indent=4)
            data = json.loads(raw_data)
            converter = FLOW_File_Convert(copy.deepcopy(data), windows=self.parent.mdiArea.subWindowList())
            result, _ = converter.process()
            flw = json.dumps(result)
        except Exception as e:
            print(f'[FlowAIWeb] Failed to serialize scene: {e}')

        print(f'[FlowAIWeb] start_ws  email={email}  conv={conversation_id}')

        if RUN_MOCK_WORKER:
            self.ws_worker = MockGetChatResWorker(text, email, token, conversation_id, flw)
        else:
            self.ws_worker = GetChatResWorker(text, email, token, conversation_id, flw)
        self.ws_worker.update_data.connect(self._on_ws_data)
        self.ws_worker.start()

    def stop_ws(self):
        if self.ws_worker:
            self.ws_worker.stop()
            self.ws_worker = None

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

    def _on_ws_data(self, res: tuple):
        msg_type, content = res
        print(f'[FlowAIWeb] ws data  type={msg_type}  content={str(content)[:80]}')
        if msg_type != "design_cmd":
            if self.bridge:
                delay = self.accumulated_delay
                QTimer.singleShot(delay, lambda: self.bridge.messageReceived.emit(msg_type, str(content)))
                self.accumulated_delay += self.interval_ms
        else:
            if content == "end":
                delay = self.accumulated_delay
                QTimer.singleShot(delay, lambda: self.stop_ws())
                self.accumulated_delay += self.interval_ms
            else:
                mainWindow = self.parent.findMain()
                delay = self.accumulated_delay
                QTimer.singleShot(delay, lambda: self.execute_single_command(content, mainWindow))
                self.accumulated_delay += self.interval_ms

        # 收到 end 或 error 时自动清理 worker
        if msg_type in ('end', 'error'):
            delay = self.accumulated_delay
            QTimer.singleShot(delay, lambda: self.stop_ws())
            self.accumulated_delay += self.interval_ms

    # ── internal ──────────────────────────────────────────────

    def _create_dialog(self):
        self.dialog = QDialog(self.parent)
        self.dialog.setWindowFlags(Qt.FramelessWindowHint)

        self.web_view = QWebEngineView(self.dialog)

        # QWebChannel
        self.bridge  = FlowAIBridge(self)
        self.channel = QWebChannel()
        self.channel.registerObject('bridge', self.bridge)
        self.web_view.page().setWebChannel(self.channel)

        # Inject initial route before Vue mounts
        self._inject_script(
            name='initial_route',
            code=f"window.__INITIAL_ROUTE__ = '{self._current_route}';",
        )

        # Inject user info (for display only — auth is handled by PyQt5)
        self._inject_user()

        # Dev tools (remove for production)
        if SHOW_WEB_DEBUG_TOOLS:
            self.dev_view = QWebEngineView()
            self.dev_view.setWindowTitle('DevTools - FlowAI')
            self.dev_view.resize(1200, 800)
            self.web_view.page().setDevToolsPage(self.dev_view.page())
            self.dev_view.show()

        self.web_view.load(QUrl.fromLocalFile(self.DIST_PATH))

        self._visible = True
        self.dialog.setVisible(True)
        self.update_geometry()

    def _inject_script(self, name: str, code: str):
        page_scripts = self.web_view.page().scripts()
        for s in page_scripts.findScripts(name):
            page_scripts.remove(s)
        script = QWebEngineScript()
        script.setName(name)
        script.setSourceCode(code)
        script.setInjectionPoint(QWebEngineScript.DocumentCreation)
        script.setWorldId(QWebEngineScript.MainWorld)
        page_scripts.insert(script)

    def _inject_user(self):
        lm = self.parent.license_mechanism
        user_data = {
            'email': lm.user['email'] if lm.user else '',
            'env':   'dev',
            'tier':  lm.tier if hasattr(lm, 'tier') else 'pro',
        }
        self._inject_script('flow_user', f"window.__FLOW_USER__ = {json.dumps(user_data)};")