from flowstudio.flow_conf import *
from flowstudio.flow_node_base import *
from template.add_password import Ui_addPasswordDialog
from template.remove_password import Ui_removePasswordDialog
from template.modify_password import Ui_modifyPasswordDialog
import json
from flowstudio.functions.aes_operation import AESOperation
import base64
from flowstudio.flow_sub_group import FLOW_Sub_Group


@register_node(OP_NODE_SUBPATCH)
class FLOW_Node_SUBPATCH(FLOW_Node):
    # icon = "icons/in.png"
    op_code = OP_NODE_SUBPATCH
    op_title = "SUBPATCH"
    content_label_objname = "SUBPATCH"
    display_name = 'Subpatch'
    info = 'A group block that can combine multiple AO in a sub canvas'
    expandable = False
    expand = True
    type_ao_addition = TypeAOAddition.DYNAMIC_NUM_INPUTS_AND_OUTPUTS.value

    def __init__(self, scene, num_input_sockets, num_output_sockets):
        self.inputs = []
        self.outputs = []
        for i in range(num_input_sockets):
            self.inputs.append(1)
        for i in range(num_output_sockets):
            self.outputs.append(1)
        super().__init__(scene, inputs=self.inputs, outputs=self.outputs, rule_check_mode=-2)
        self.eval()
        self.cwd = None  # 有這個欄位代表會產生子視窗

    def serialize(self):
        res = super().serialize()
        res['cwd'] = self.cwd
        return res

    def deserialize(self, data, hashmap=None, restore_id=True):
        if hashmap is None:
            hashmap = {}
        res = super().deserialize(data, hashmap, restore_id)
        self.cwd = data['cwd']
        return res

    # 看encrypted欄位是true or false
    def is_encrypted(self):
        windows = self.scene.getView().window().mdiArea.subWindowList()
        result = None
        for window in windows:
            window_name = window.widget().getPrettyFilename()
            if window_name == self.title:
                if hasattr(window.widget(), 'encrypted'):
                    result = window.widget().encrypted
                else:
                    result = False
        if result is None:
            for ele in self.scene.getView().window().sub_patchs:
                if ele.title == self.title + '.json' or ele.title == self.title:
                    if hasattr(ele, 'encrypted'):
                        result = ele.encrypted
                    else:
                        result = False
        return result

    def add_password(self):
        qdialog = QDialog(self.scene.getView().window())
        self.addPasswordDialog = Ui_addPasswordDialog()
        self.addPasswordDialog.setupUi(qdialog)
        qdialog.setWindowTitle("Add Password")
        self.addPasswordDialog.buttonBox.clicked.connect(self.onAddPasswordDialogOption)
        for gui_widget in FLOW_Window_Connection.show_window_objects:
            gui_widget.hide()
        qdialog.exec_()
        for gui_widget in FLOW_Window_Connection.show_window_objects:
            gui_widget.show()

    def lock(self, password):
        """
            lock this subpatch with the password provided

            :param password: str, the password to lock subpatch

            :return: bool, If the task is completed successfully,
                the function will return True. If not, the function will return False.
        """
        try:
            current_window = self.scene.getView().window().getCurrentNodeEditorWidget()
            def dfs_encrypt_subpatch(subpatch_name, windows):
                is_subpatch_inside = False
                for sub_window in windows:
                    sub_window_name = sub_window.widget().getPrettyFilename()
                    if subpatch_name == sub_window_name:
                        sub_window.widget().encrypted = True
                        sub_window.widget().already_input_password = True
                        sub_window.widget().correct_password = password
                        subpatchs_inside = []
                        for node in sub_window.widget().scene.nodes:
                            if node.op_code == OP_NODE_SUBPATCH:
                                # 假如底下的subpatch沒有加密, 則要一起加密
                                if not node.is_encrypted():
                                    is_subpatch_inside = True
                                    subpatchs_inside.append(node.title)
                if not is_subpatch_inside:
                    return
                for subpatch_inside in subpatchs_inside:
                    dfs_encrypt_subpatch(subpatch_inside, windows)

            self.scene.getView().window().open_subwindow_in_subpatch_recursively(self.title)
            self.scene.getView().window().setActiveSubWindow(current_window.parent())
            windows = self.scene.getView().window().mdiArea.subWindowList()
            dfs_encrypt_subpatch(self.title, windows)
            for sub_window in windows:
                if hasattr(sub_window.widget(), 'close_if_no_problem'):
                    if sub_window.widget().close_if_no_problem:
                        self.scene.getView().window().close_sub_window(sub_window)
            self.scene.getView().window().setActiveSubWindow(current_window.parent())
            self.scene.getView().window().findMain().widget().scene.has_been_modified = True
            self.scene.getView().window().statusBar().showMessage('Added password successfully.', 3000)
            self.scene.history.storeHistory(f"AddPassword {self.__class__.__name__}-{self.title}", setModified=True)
            return True
        except:
            return False

    def onAddPasswordDialogOption(self, button):
        curr_btn = self.addPasswordDialog.buttonBox.standardButton(button)
        if curr_btn == QDialogButtonBox.Ok:
            input_password = self.addPasswordDialog.lineEditPassword.text()
            input_confirm_password = self.addPasswordDialog.lineEditConfirmPassword.text()
            if input_password == '':
                QMessageBox.warning(self.scene.getView().window(), 'Please input password',
                                    f'Please input password')
            elif input_confirm_password == '':
                QMessageBox.warning(self.scene.getView().window(), 'Please confirm password',
                                    f'Please confirm password')
            elif input_password != input_confirm_password:
                QMessageBox.warning(self.scene.getView().window(), 'Warning',
                                    f'Password is not same as confirmed password')
            else:
                if not self.lock(password=input_password):
                    QMessageBox.warning(self.scene.getView().window(), 'Warning',
                                        f'Something went wrong, please try again.')
        elif curr_btn == QDialogButtonBox.Cancel:
            pass

    def remove_password(self):
        qdialog = QDialog(self.scene.getView().window())
        self.removePasswordDialog = Ui_removePasswordDialog()
        self.removePasswordDialog.setupUi(qdialog)
        qdialog.setWindowTitle("Remove Password")
        self.removePasswordDialog.buttonBox.clicked.connect(self.onRemovePasswordDialogOption)
        for gui_widget in FLOW_Window_Connection.show_window_objects:
            gui_widget.hide()
        qdialog.exec_()
        for gui_widget in FLOW_Window_Connection.show_window_objects:
            gui_widget.show()

    def delete_password(self, input_password, ignore_message_box=False):
        """
            remove the password of this subpatch by providing password,
            if the provided password is incorrect, the removal will not be allowed.

            :param input_password: str, given password
            :param ignore_message_box: Optional. Default: False.
            A boolean value indicating whether to ignore showing the message box or not.
        """
        current_window = self.scene.getView().window().getCurrentNodeEditorWidget()
        self.scene.getView().window().open_subwindow_in_subpatch_recursively(self.title)
        self.scene.getView().window().setActiveSubWindow(current_window.parent())
        windows = self.scene.getView().window().mdiArea.subWindowList()
        correct_password = None
        for sub_window in windows:
            sub_window_name = sub_window.widget().getPrettyFilename()
            if self.title == sub_window_name:
                correct_password = sub_window.widget().correct_password
            if hasattr(sub_window.widget(), 'close_if_no_problem'):
                if sub_window.widget().close_if_no_problem and current_window.parent() != sub_window:
                    self.scene.getView().window().close_sub_window(sub_window)
        if input_password == '':
            if not ignore_message_box:
                QMessageBox.warning(self.scene.getView().window(), 'Please input password',
                                    f'Please input password')
        elif input_password != correct_password:
            if not ignore_message_box:
                QMessageBox.warning(self.scene.getView().window(), 'Warning',
                                    f'Input password is not correct.')
        elif input_password == correct_password:
            def dfs_decrypt_subpatch(subpatch_name, input_password, windows):
                is_subpatch_inside = False
                for sub_window in windows:
                    sub_window_name = sub_window.widget().getPrettyFilename()
                    if subpatch_name == sub_window_name:
                        if hasattr(sub_window.widget(), 'correct_password'):
                            if sub_window.widget().correct_password != input_password:
                                return
                            delattr(sub_window.widget(), 'correct_password')
                        if hasattr(sub_window.widget(), 'encrypted'):
                            delattr(sub_window.widget(), 'encrypted')
                        if hasattr(sub_window.widget(), 'already_input_password'):
                            delattr(sub_window.widget(), 'already_input_password')
                        subpatchs_inside = []
                        for node in sub_window.widget().scene.nodes:
                            if node.op_code == OP_NODE_SUBPATCH:
                                is_subpatch_inside = True
                                subpatchs_inside.append(node.title)
                if not is_subpatch_inside:
                    return
                for subpatch_inside in subpatchs_inside:
                    dfs_decrypt_subpatch(subpatch_inside, input_password, windows)
            self.scene.getView().window().open_subwindow_in_subpatch_recursively(self.title)
            self.scene.getView().window().setActiveSubWindow(current_window.parent())
            windows = self.scene.getView().window().mdiArea.subWindowList()
            dfs_decrypt_subpatch(self.title, input_password, windows)
            for sub_window in windows:
                if hasattr(sub_window.widget(), 'close_if_no_problem'):
                    if sub_window.widget().close_if_no_problem and current_window.parent() != sub_window:
                        self.scene.getView().window().close_sub_window(sub_window)
            self.scene.getView().window().setActiveSubWindow(current_window.parent())
            self.scene.getView().window().statusBar().showMessage('Removed password successfully.', 3000)
            self.scene.history.storeHistory(f"RemovePassword {self.__class__.__name__}-{self.title}", setModified=True)
            # In order to enable the "undo" feature, the password needs to be stored in the history stamp
            self.scene.history.history_stack[self.scene.history.history_current_step]['password'] = input_password
            self.scene.getView().window().setActiveSubWindow(current_window.parent())

    def onRemovePasswordDialogOption(self, button):
        """
            Executes the appropriate action based on the button clicked in the remove password dialog.

            Args:
                button: The button clicked in the remove password dialog.
        """
        curr_btn = self.removePasswordDialog.buttonBox.standardButton(button)
        if curr_btn == QDialogButtonBox.Ok:
            input_password = self.removePasswordDialog.lineEditPassword.text()
            self.delete_password(input_password)
        elif curr_btn == QDialogButtonBox.Cancel:
            pass

    def modify_password(self):
        """
            Opens a dialog window to modify the password.
        """
        qdialog = QDialog(self.scene.getView().window())
        self.modifyPasswordDialog = Ui_modifyPasswordDialog()
        self.modifyPasswordDialog.setupUi(qdialog)
        qdialog.setWindowTitle("Modify Password")
        self.modifyPasswordDialog.buttonBox.clicked.connect(self.onModifyPasswordDialogOption)
        for gui_widget in FLOW_Window_Connection.show_window_objects:
            gui_widget.hide()
        qdialog.exec_()
        for gui_widget in FLOW_Window_Connection.show_window_objects:
            gui_widget.show()

    def change_password(self, input_original_password, input_new_password, input_confirm_password,
                        ignore_message_box=False):
        """
            change the password of this subpatch.

            :param input_original_password: str, given original password
            :param input_new_password: str, given new password
            :param input_confirm_password: str, given new password
            :param ignore_message_box: Optional. Default: False.
            A boolean value indicating whether to ignore showing the message box or not.
        """
        current_window = self.scene.getView().window().getCurrentNodeEditorWidget()
        self.scene.getView().window().open_subwindow_in_subpatch_recursively(self.title)
        self.scene.getView().window().setActiveSubWindow(current_window.parent())
        windows = self.scene.getView().window().mdiArea.subWindowList()
        correct_password = None
        for sub_window in windows:
            sub_window_name = sub_window.widget().getPrettyFilename()
            if self.title == sub_window_name:
                correct_password = sub_window.widget().correct_password
            if hasattr(sub_window.widget(), 'close_if_no_problem'):
                if sub_window.widget().close_if_no_problem and current_window.parent() != sub_window:
                    self.scene.getView().window().close_sub_window(sub_window)
        self.scene.getView().window().setActiveSubWindow(current_window.parent())
        if input_original_password == '':
            if not ignore_message_box:
                QMessageBox.warning(self.scene.getView().window(), 'Please input original password',
                                    f'Please input original password')
        elif input_original_password != correct_password:
            if not ignore_message_box:
                QMessageBox.warning(self.scene.getView().window(), 'Warning',
                                    f'Input original password is not correct.')
        else:
            if input_new_password == '':
                if not ignore_message_box:
                    QMessageBox.warning(self.scene.getView().window(), 'Please input new password',
                                        f'Please input new password')
            elif input_new_password == input_original_password:
                if not ignore_message_box:
                    QMessageBox.warning(self.scene.getView().window(),
                                        'Please input new password which is not same as original password',
                                        f'Please input new password which is not same as original password')
            elif input_new_password != input_confirm_password:
                if not ignore_message_box:
                    QMessageBox.warning(self.scene.getView().window(), 'Warning',
                                        f'Password is not same as confirmed password')
            elif input_new_password == input_confirm_password:
                def dfs_modify_password(subpatch_name, input_original_password, input_new_password, windows):
                    is_subpatch_inside = False
                    for sub_window in windows:
                        sub_window_name = sub_window.widget().getPrettyFilename()
                        if subpatch_name == sub_window_name:
                            if hasattr(sub_window.widget(), 'correct_password'):
                                if sub_window.widget().correct_password != input_original_password:
                                    return
                                sub_window.widget().correct_password = input_new_password
                            subpatchs_inside = []
                            for node in sub_window.widget().scene.nodes:
                                if node.op_code == OP_NODE_SUBPATCH:
                                    is_subpatch_inside = True
                                    subpatchs_inside.append(node.title)
                    if not is_subpatch_inside:
                        return
                    for subpatch_inside in subpatchs_inside:
                        dfs_modify_password(subpatch_inside, input_original_password, input_new_password, windows)

                self.scene.getView().window().open_subwindow_in_subpatch_recursively(self.title)
                self.scene.getView().window().setActiveSubWindow(current_window.parent())
                windows = self.scene.getView().window().mdiArea.subWindowList()
                dfs_modify_password(self.title, input_original_password, input_new_password, windows)
                for sub_window in windows:
                    if hasattr(sub_window.widget(), 'close_if_no_problem'):
                        if sub_window.widget().close_if_no_problem and current_window.parent() != sub_window:
                            self.scene.getView().window().close_sub_window(sub_window)
                self.scene.getView().window().setActiveSubWindow(current_window.parent())
                self.scene.history.storeHistory(
                    f"ModifyPassword {self.__class__.__name__}-{self.title} {input_original_password} to {input_new_password}",
                    setModified=True)
                self.scene.getView().window().statusBar().showMessage('Modified password successfully.', 3000)
        self.scene.getView().window().setActiveSubWindow(current_window.parent())

    def onModifyPasswordDialogOption(self, button):
        """
            Executes the appropriate action based on the button clicked in the modify password dialog.

            Args:
                button: The button clicked in the modify password dialog.
        """
        curr_btn = self.modifyPasswordDialog.buttonBox.standardButton(button)
        if curr_btn == QDialogButtonBox.Ok:
            input_original_password = self.modifyPasswordDialog.lineEditOriginalPassword.text()
            input_new_password = self.modifyPasswordDialog.lineEditNewPassword.text()
            input_confirm_password = self.modifyPasswordDialog.lineEditConfirmPassword.text()
            self.change_password(input_original_password, input_new_password, input_confirm_password)
        elif curr_btn == QDialogButtonBox.Cancel:
            pass
