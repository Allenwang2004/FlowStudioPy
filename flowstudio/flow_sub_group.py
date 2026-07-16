from flowstudio.flow_sub_window import *
from copy import copy


class FLOW_Sub_Group(FLOW_Sub_Window):

    def __init__(self):
        self.title = "New GROUP"
        self.renamed = False
        super().__init__()

    def setTitle(self, is_save_file=False):
        self.setWindowTitle(self.getUserFriendlyFilename(is_save_file))
        if self.window() is not self:
            if self.isModified():
                self.window().findMain().widget().scene.has_been_modified = True

    def getUserFriendlyFilename(self, is_save_file=False) -> str:
        """Get user friendly filename. Used in window title

        :return: just a base name of the file or `'New Graph'`
        :rtype: ``str``
        """
        name = os.path.basename(self.filename) if self.isFilenameSet() else self.title
        if self.renamed and not is_save_file:
            name = self.title
        return name + ("*" if self.isModified() else "")

    def custom_hide(self):
        current_active_sub_window = self.window().mdiArea.activeSubWindow()
        windows = self.window().mdiArea.subWindowList()
        for window in windows:
            if window.widget() == self:
                self.window().setActiveSubWindow(window)
                break
        self.window().closeMdiAreaActiveSubWindowRecursively()
        for window in windows:
            if window == current_active_sub_window:
                self.window().setActiveSubWindow(window)
                break

    def closeEvent(self, event):
        super().closeEvent(event)

    def create_copy(self):
        res = FLOW_Sub_Group()
        res.title = copy(self.title)
        res.renamed = copy(self.renamed)
        res.filename = copy(self.filename)
        res.scene.history.history_stack = copy(self.scene.history.history_stack)
        res.scene.history.history_current_step = copy(self.scene.history.history_current_step)
        res.scene.has_been_modified = copy(self.scene.has_been_modified)
        if hasattr(self, 'already_input_password'):
            res.already_input_password = self.already_input_password
        if hasattr(self, 'correct_password'):
            res.correct_password = self.correct_password
        if hasattr(self, 'encrypted'):
            res.encrypted = self.encrypted
        return res

