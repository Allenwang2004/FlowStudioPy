class change_channel_implementation():
    def VQE_change_channel(self, manager, mic_num):
        for i in range(1, manager.config['UrocMicSetup'].parameters['pMax']):
            manager.widgetSet['UrocMicSetup'].comboBox.model().item(i).setEnabled(False)

        if mic_num == 1:
            manager.widgetSet['UrocMicSetup'].comboBox.model().item(1).setEnabled(True)
        elif mic_num == 2:
            manager.widgetSet['UrocMicSetup'].comboBox.model().item(2).setEnabled(True)
        elif mic_num == 3:
            manager.widgetSet['UrocMicSetup'].comboBox.model().item(7).setEnabled(True)
            manager.widgetSet['UrocMicSetup'].comboBox.model().item(13).setEnabled(True)
        elif mic_num == 4:
            manager.widgetSet['UrocMicSetup'].comboBox.model().item(3).setEnabled(True)
            manager.widgetSet['UrocMicSetup'].comboBox.model().item(4).setEnabled(True)
            manager.widgetSet['UrocMicSetup'].comboBox.model().item(10).setEnabled(True)
            manager.widgetSet['UrocMicSetup'].comboBox.model().item(11).setEnabled(True)
        elif mic_num == 5:
            manager.widgetSet['UrocMicSetup'].comboBox.model().item(14).setEnabled(True)
        elif mic_num == 6:
            manager.widgetSet['UrocMicSetup'].comboBox.model().item(6).setEnabled(True)
            manager.widgetSet['UrocMicSetup'].comboBox.model().item(12).setEnabled(True)
        elif mic_num == 7:
            manager.widgetSet['UrocMicSetup'].comboBox.model().item(9).setEnabled(True)
        elif mic_num == 8:
            manager.widgetSet['UrocMicSetup'].comboBox.model().item(5).setEnabled(True)
            manager.widgetSet['UrocMicSetup'].comboBox.model().item(8).setEnabled(True)
