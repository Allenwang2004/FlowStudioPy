import time

from flowstudio.flow_conf import *
from flowstudio.flow_node_base import *

@register_node(OP_NODE_DIRAC)
class FLOW_Node_DIRAC(FLOW_Node):
    icon = '../resources/dirac-ao-icon.png'
    op_code = OP_NODE_DIRAC
    op_title = "DIRAC"
    content_label_objname = "DIRAC"
    display_name = 'Dirac Live Processor'
    info = 'DIRAC Info'
    expandable = True
    linkType = 1
    type_ao_addition = TypeAOAddition.SPECIAL_ACTION.value
    ch_dict = {
        '2.0': [0, 1],
        '5.1.2': [0, 1, 2, 3, 4, 5, 8, 9],
        '7.1.4': [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11]
    }

    def __init__(self, scene, configure):
        channel_num = 0
        self.inputs = []
        self.outputs = []
        for i in configure.split('.'):
            channel_num += int(i)
        for i in range(channel_num):
            self.inputs.append(1)
            self.outputs.append(1)

        super().__init__(scene, inputs=self.inputs, outputs=self.outputs)
        self.initControl()
        self.eval()

        self.manager.widgetSet['configure'].comboBox.setCurrentText(configure)

        self.tab_change()
        input_textedit_list = self.manager.widgetSet['inputinfo'].textedit_list
        input_combobox_list = self.manager.widgetSet['inputinfo'].combobox_list
        speaker_index_list = self.manager.widgetSet['speakerinfo'].index_list
        speaker_textedit_list = self.manager.widgetSet['speakerinfo'].textedit_list
        speaker_combobox_list = self.manager.widgetSet['speakerinfo'].combobox_list
        speaker_combobox_id_list = self.manager.widgetSet['speakerinfo'].combobox_id_list
        result = [item for item in self.ch_dict['7.1.4'] if item not in self.ch_dict[configure]]
        for i in result:
            input_textedit_list[i].hide()
            input_combobox_list[i].hide()
            speaker_index_list[i].hide()
            speaker_textedit_list[i].hide()
            speaker_combobox_list[i].hide()
            speaker_combobox_id_list[i].hide()
        self.page_update()
        self.manager.widgetSet['configure'].valueChanged.connect(self.configure_change)
        self.manager.widgetSet['infotab'].valueChanged.connect(self.tab_change)
        self.manager.widgetSet['infotab'].save.clicked.connect(self.update_data_to_ssh)

    def initInnerClasses(self):
        self.manager = FLOW_Ctrl_Manager(self.content_label_objname)
        self.content = FLOW_Content(self)
        self.grNode = FLOW_GraphicsNode(self)

    def configure_change(self):
        input_textedit_list = self.manager.widgetSet['inputinfo'].textedit_list
        input_combobox_list = self.manager.widgetSet['inputinfo'].combobox_list
        speaker_index_list = self.manager.widgetSet['speakerinfo'].index_list
        speaker_textedit_list = self.manager.widgetSet['speakerinfo'].textedit_list
        speaker_combobox_list = self.manager.widgetSet['speakerinfo'].combobox_list
        speaker_combobox_id_list = self.manager.widgetSet['speakerinfo'].combobox_id_list
        channel_num = 0
        configure = self.manager.widgetSet['configure'].widget_value[0]
        for i in configure.split('.'):
            channel_num += int(i)
        num = channel_num - len(self.inputlist)

        if num > 0:
            for i in range(num):
                self.addChannel()
            for item in self.ch_dict[configure]:
                input_textedit_list[item].show()
                input_combobox_list[item].show()
                speaker_index_list[item].show()
                speaker_textedit_list[item].show()
                speaker_combobox_list[item].show()
                speaker_combobox_id_list[item].show()
        elif num < 0:
            for i in range(abs(num)):
                self.reduceChannel()
            result = [item for item in self.ch_dict['7.1.4'] if item not in self.ch_dict[configure]]
            for i in result:
                input_textedit_list[i].hide()
                input_combobox_list[i].hide()
                speaker_index_list[i].hide()
                speaker_textedit_list[i].hide()
                speaker_combobox_list[i].hide()
                speaker_combobox_id_list[i].hide()

        self.page_update()

    def page_update(self):
        if self.manager.widgetSet['infotab'].widget_value == 0:
            self.manager.widgetSet['inputinfo'].hide()
            self.manager.widgetSet['inputinfo'].show()
        else:
            self.manager.widgetSet['speakerinfo'].hide()
            self.manager.widgetSet['speakerinfo'].show()

    def tab_change(self):
        if self.manager.widgetSet['infotab'].widget_value == 0:
            self.manager.widgetSet['speakerinfo'].hide()
            self.manager.widgetSet['inputinfo'].show()
        else:
            self.manager.widgetSet['speakerinfo'].show()
            self.manager.widgetSet['inputinfo'].hide()

    def update_data_to_ssh(self):
        self.manager.widgetSet['inputinfo'].label.setText('')
        self.manager.widgetSet['speakerinfo'].label.setText('')

        hostname = self.cSocket.addr
        username = self.manager.widgetSet['username'].widget_value
        password = self.manager.widgetSet['password'].widget_value
        devicename = self.manager.widgetSet['devicename'].widget_value

        if self.cSocket.target == Target.RASP.value:
            sudo = "echo " + password + "| sudo -S"
            # cmd_stop = 'sudo /opt/dirac/concord/scripts/stop_services.sh'
            # cmd_start = 'sudo /opt/dirac/concord/scripts/start_services.sh'
        elif self.cSocket.target == Target.FLOW_APO.value:
            sudo = ''
            # cmd_stop = '/etc/init.d/S94dirac stop'
            # cmd_start = '/etc/init.d/S94dirac start'
        else:
            statement = "Please choose platform: Flow APO or Raspberry Pi"
            QMessageBox.about(self.scene.getView().window(), "Note", "%s" % statement)
            return

        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

        try:
            ssh.connect(hostname, username=username, password=password)

            # device name
            stdin, stdout, stderr = ssh.exec_command("cd /opt/dirac/concord/bin;"
                                                     "%s ./concord cli --config 'deviceInfo/name=\"%s\"'" % (sudo, devicename))
            result = stdout.read().decode()
            error = stderr.read().decode()
            # print(result, 'result')
            # print(error, 'error')
            if result == '':
                statement = "device name error：%s" % error
                QMessageBox.about(self.scene.getView().window(), "Dirac SSH Note", "%s" % statement)
                return
            # else:
            #     print('device name: ', result)

            # input info
            input_textedit_list = self.manager.widgetSet['inputinfo'].textedit_list
            input_combobox_list = self.manager.widgetSet['inputinfo'].combobox_list
            inputInfo = []
            for i in range(len(self.inputlist)):
                inputInfo.append({"index": i, "name": input_textedit_list[i].text(), "type": input_combobox_list[i].currentText()})
            json_str = json.dumps(inputInfo, indent=4)
            stdin, stdout, stderr = ssh.exec_command("""cd /opt/dirac/concord/bin;
                                                     %s ./concord cli --config 'inputInfo=%s'""" % (sudo, json_str))
            result = stdout.read().decode()
            error = stderr.read().decode()
            # print(result, 'result')
            # print(error, 'error')
            if result == '':
                statement = "input info error：%s" % error
                QMessageBox.about(self.scene.getView().window(), "Dirac SSH Note", "%s" % statement)
                return
            # else:
            #     print('input info:', result)

            # speaker info
            index_list = self.manager.widgetSet['speakerinfo'].index_list
            speaker_textedit_list = self.manager.widgetSet['speakerinfo'].textedit_list
            speaker_combobox_list = self.manager.widgetSet['speakerinfo'].combobox_list
            speaker_combobox_id_list = self.manager.widgetSet['speakerinfo'].combobox_id_list
            speakerInfo = []
            for i in range(len(self.inputlist)):
                speakerInfo.append(
                    {"associated_input": {"i": index_list[i].currentText()}, "group_id": speaker_combobox_id_list[i].currentText(),
                     "name": speaker_textedit_list[i].text(), "type": speaker_combobox_list[i].currentText()})
            json_str = json.dumps(speakerInfo, indent=4)
            stdin, stdout, stderr = ssh.exec_command("""cd /opt/dirac/concord/bin;
                                                    %s ./concord cli --config 'speakerInfo=%s'""" % (sudo, json_str))
            result = stdout.read().decode()
            error = stderr.read().decode()
            # print(result, 'result')
            # print(error, 'error')
            if result == '':
                statement = "speaker info error：%s" % error
                QMessageBox.about(self.scene.getView().window(), "Dirac SSH Note", "%s" % statement)
                return
            # else:
            #     print('speaker info:', result)

            self.timer = QTimer()
            self.timer.timeout.connect(self.updaue_info)
            self.info = ['',
                         "Changing Device Name to %s ... success \n" % devicename,
                         "Updating Input Info ... success \n",
                         "Updating Speaker Info ... success \n",
                         "Please reboot the device to apply the above configurations... \n"]
            self.index = 0
            self.timer.start(500)
        except paramiko.AuthenticationException:
            statement = "Authentication failed, please check username and password"
            QMessageBox.about(self.scene.getView().window(), "Dirac SSH Note", "%s" % statement)
        except paramiko.SSHException as sshException:
            statement = "Unable to establish SSH connection: %s" % sshException
            QMessageBox.about(self.scene.getView().window(), "Dirac SSH Note", "%s" % statement)
        except Exception as e:
            statement = "Error occurred: %s" % e
            QMessageBox.about(self.scene.getView().window(), "Dirac SSH Note", "%s" % statement)
        finally:
            ssh.close()


    def updaue_info(self):
        if self.index < len(self.info):
            text = ''
            for i in range(self.index):
                text += self.info[i+1]
            self.manager.widgetSet['inputinfo'].label.setText(text)
            self.manager.widgetSet['speakerinfo'].label.setText(text)
            self.index += 1
            self.page_update()
        else:
            self.timer.stop()
