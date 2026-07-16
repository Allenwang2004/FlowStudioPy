import json
import pickle
from binascii import a2b_hex
from functools import partial
from subprocess import run
from PyQt5.QtCore import QTimer, QPropertyAnimation, Qt
import requests
import datetime
from datetime import timedelta
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QMessageBox, QWidget, QLabel, QDialog
from Crypto.Cipher import AES
from flowstudio.flow_conf import FLOW_NODES, CATE_AO_MAPPING
from flowstudio.flow_build_manager import Manager, VERSION
import wmi
from collections import defaultdict

from flowstudio.functions.CallbackHandle import LocalServer
from template.user_expired_box import Ui_user_expired_box

DEBUG = False


class License_Mechanism:
    manager = Manager()
    common_urls, distribution_urls = manager.get_all_url_list()
    remainOffSecond = 0
    remainTime = 0
    permanent=False
    version="0.28"
    address=""
    email=""
    ip = ""
    verifyCode=0
    loginTime=0
    quitTime=0
    # get_license_key_by_address_url = f"{API_BASE_URL}public/user/getLicenceKeyByAddress"
    # license_check_url = f'{SERVER_SIDE_BASE_URL}common/licencecheck/v2'
    # register_url = f"{API_BASE_URL}register/v2"
    # sendCode_url = f"{API_BASE_URL}sendCode/v2"
    # downloadLatestExt_url = "https://tym-flowdsp.s3.ap-southeast-1.amazonaws.com/FlowStudio0.28.1.exe"
    add_project_info_url = common_urls['add_project_info_url']
    get_info_by_technical_provider_name_url = common_urls['get_info_by_technical_provider_name_url']
    get_all_features_by_token_url = common_urls['get_all_features_by_token_url']
    get_all_features_by_app_and_type_name = common_urls['get_all_features_by_app_and_type_name']
    # check_tracking_by_licence_key_url = url_list['check_tracking_by_licence_key_url']
    create_record_url = distribution_urls['create_record_url']
    create_user_action_url = distribution_urls['create_user_action_url']
    get_user_first_record_url = distribution_urls['get_user_first_record_url']
    check_user_token_url = distribution_urls['check_user_token_url']
    version_check_url = distribution_urls['version_check_url']
    user_login_url = distribution_urls['user_login_url']
    portal_url = distribution_urls['portal_url']
    mode=1 #0 is inline, 1 is offline
    interval_send_verification_code = 120  # interval(secs) between ability to click button of sending verification code
    # license type: "Free","Pro","Premium"
    tier = "Free"
    remain_time = 0
    no_login_free_time = 30
    # trial、login、token valid
    expire_type = 'trial'

    def __init__(self, parent: 'QWidget' = None, is_testing=True, splash = None):
        # init data
        self.is_tracking = False
        self.is_online = True
        self.is_testing = is_testing
        self.address = self.get_CPU_info() + self.get_mac_address()
        self.ip = self.get_user_ip()
        self.loginTime = datetime.datetime.now()
        self.tipBox=TipBox(parent)
        self.parent_window = parent
        self.splash = splash
        self.remain_time = 0
        self.token = ''
        self.tier = "Free"
        self.user = None
        self.user_expired_prompt_dialog = None
        self.custom_ao_list = []
        self.license_data = self.pickleReadFile()
        self.check_user_metadata(token=self.license_data['token'])

        if DEBUG: print("license_data=", self.license_data)

        # Create a timer to check the user's metadata every hour
        self.check_user_data_timer = QTimer()
        self.check_user_data_timer.timeout.connect(partial(self.check_user_metadata, 'local_token'))
        self.check_user_data_timer.start(3600000)  # 1 hour


    def check_user_metadata(self, token):
        if self.is_testing:
            self.test_initialize()
            return

        if token == 'local_token':
            self.license_data = self.pickleReadFile()
            token = self.license_data['token']

        if DEBUG: print('token', token)
        self.token = token

        # version check
        res = self.version_check()
        if not res:
            self.offline_mode()
            return

        # step 1: find tier and remain_time
        # If the token does not exist, the expiration time is the first creation record + self.no_Logic_free_time
        # If the token exists, use the token to query the user's expiration time
        if token == '' or token is None:
            res = self.check_user_free_time()
            if not res:
                self.offline_mode()
                return
        else:
            res = self.CheckUserToken(token)
            if not res:
                self.offline_mode()
                return

        # step 2: find available AO
        # Free Tier: All AO can be used
        # Pro/Premium Tier: The available AO depends on the user's AO permissions
        feature_permission_data = {'AO': []}
        ao_info_data = {}
        technical_provider_info_data = {}
        ao_info_data = self.get_ao_info_res()

        if self.tier == "Free":
            for key, value in FLOW_NODES.items():
                feature_permission_data['AO'].append(key)
        else:
            # self.is_tracking = self.is_in_tracking_list(license_key)
            feature_permission_data = self.get_feature_permission_res(token)
            # technical_provider_info_data = self.get_technical_provider_info_res()

        if (feature_permission_data is None or ao_info_data is None):
            self.offline_mode()
            return

        for company in CATE_AO_MAPPING['Technology Provider']:
            company_db_name = company.db_name
            company_info = company.info
            technical_provider_info_data[company_db_name] = company_info

        # step 3: Store data locally
        self.feature_permission_data = feature_permission_data
        self.technical_provider_info_data = technical_provider_info_data
        self.ao_info_data = ao_info_data
        self.parent_window.write_local_license(self.feature_permission_data, self.technical_provider_info_data,
                                               self.ao_info_data, self.token, self.user, self.tier, self.remain_time)
        self.license_data = self.pickleReadFile()

        # step 4: Set the usage functions for different tiers
        if self.parent_window.isVisible():
            self.parent_window.control_feature_by_license_tier(self.tier)

        # step5: check remain time
        self.check_user_remain_time()
        self.is_online = True

    def check_user_remain_time(self):
        if self.remain_time.total_seconds() < 0:
            if hasattr(self.parent_window, 'user_pane_dialog') and self.parent_window.user_pane_dialog:
                self.parent_window.UserPaneSwitch()
            if self.user_expired_prompt_dialog is None:
                self.UserExpiredPrompt()
            else:
                if self.expire_type == 'login':
                    self.user_expired_prompt_dialog.setWindowTitle("License Expired")
                    self.user_expired_prompt.label.setText('🚨 Sorry, Your license has expired!')
                    self.user_expired_prompt.label_msg.setText('Please contact TYM to renew your Flow Studio license.')

                if self.expire_type == 'token valid':
                    self.user_expired_prompt_dialog.setWindowTitle("Token Valid")
                    self.user_expired_prompt.label.setText('🚨 Your session token has expired!')
                    self.user_expired_prompt.label_msg.setText('Please sign in your account again or contact us')
        else:
            if self.user_expired_prompt_dialog is not None:
                self.user_expired_prompt_dialog.deleteLater()
                self.user_expired_prompt_dialog = None


    def test_initialize(self):
        if DEBUG: print("is_testing mode, skip check_user_metadata")
        self.tier = "Pro"
        self.remain_time = timedelta(days=30)
        self.expire_type = 'trial'
        self.user = None
        feature_permission_data = {'AO': []}
        ao_info_data = {}
        for key, value in FLOW_NODES.items():
            feature_permission_data['AO'].append(key)
            ao_info_data[key] = value.info
        technical_provider_info_data = {}
        for company in CATE_AO_MAPPING['Technology Provider']:
            company_db_name = company.db_name
            company_info = company.info
            technical_provider_info_data[company_db_name] = company_info
        self.feature_permission_data = feature_permission_data
        self.technical_provider_info_data = technical_provider_info_data
        self.ao_info_data = ao_info_data

    def offline_mode(self):
        print("Enter offline mode")
        self.is_online = False
        if self.license_data['feature_permission_data'] == '{"AO": []}':
            QMessageBox.warning(self.parent_window, 'Initialization Information',
                                'Initialization failed on first launch. Please verify network connectivity and restart the application.')
            if self.splash:
                self.splash.close()
            if self.parent_window:
                self.parent_window.close()
            return
        else:
            feature_permission_data = {k: v for k, v in
                                       json.loads(self.license_data['feature_permission_data']).items()}
            self.feature_permission_data = feature_permission_data
            technical_provider_info_data = {k: v for k, v in
                                            json.loads(self.license_data['technical_provider_info_data']).items()}
            self.technical_provider_info_data = technical_provider_info_data
            ao_info_data = {int(k): v for k, v in json.loads(self.license_data['ao_info_data']).items()}
            self.ao_info_data = ao_info_data
            self.token = self.license_data['token']
            self.user = self.license_data['user']
            self.tier = self.license_data['tier']
            self.remain_time = self.license_data['remain_time']
            # Set the usage functions for different tiers
            if self.parent_window.isVisible():
                self.parent_window.control_feature_by_license_tier(self.tier)
                # Calculate available time in offline mode
                self.remain_time = self.remain_time - timedelta(minutes=60)
                self.parent_window.write_local_license(self.feature_permission_data, self.technical_provider_info_data,
                                                       self.ao_info_data, self.token, self.user, self.tier,
                                                       self.remain_time)
            # check user remain time
            self.check_user_remain_time()

    def StartLoginServer(self):
        local_server_thread = LocalServer(parent=self.parent_window)
        local_server_thread.callback_token.connect(self.check_user_metadata)
        local_server_thread.callback_port.connect(self.OpenLoginURL)
        local_server_thread.start()

    def OpenLoginURL(self, port):
        import webbrowser
        url = self.user_login_url + port
        webbrowser.open(url)

    def OpenContactUsEmail(self):
        import webbrowser
        from urllib.parse import quote
        import textwrap

        recipient = "support@flow-dsp.com"
        subject = "My problem for Flow Studio"
        raw_body = ""

        body = textwrap.dedent(raw_body)
        body = body.strip()
        body = body.replace("\n", "\r\n")
        encoded_body = quote(body)
        encoded_subject = quote(subject)
        mailto_url = f"mailto:{recipient}?subject={encoded_subject}&body={encoded_body}"
        webbrowser.open(mailto_url)

    def PromptClose(self):
        self.user_expired_prompt_dialog.deleteLater()
        if self.splash:
            self.splash.close()
        if self.parent_window and self.parent_window.isVisible():
            self.parent_window.close()


    def UserExpiredPrompt(self):
        self.user_expired_prompt_dialog = QDialog(self.parent_window)
        self.user_expired_prompt = Ui_user_expired_box()
        self.user_expired_prompt.setupUi(self.user_expired_prompt_dialog)
        self.user_expired_prompt_dialog.setWindowFlag(Qt.WindowCloseButtonHint, False)
        if self.expire_type == 'trial':
            self.user_expired_prompt_dialog.setWindowTitle("License Expired")
            self.user_expired_prompt.label.setText('🚨 Your trial has expired!')
            self.user_expired_prompt.label_msg.setText('Please sign up your account or contact us')

        if self.expire_type == 'login':
            self.user_expired_prompt_dialog.setWindowTitle("License Expired")
            self.user_expired_prompt.label.setText('🚨 Sorry, Your license has expired!')
            self.user_expired_prompt.label_msg.setText('Please contact TYM to renew your Flow Studio license.')

        if self.expire_type == 'token valid':
            self.user_expired_prompt_dialog.setWindowTitle("Token Valid")
            self.user_expired_prompt.label.setText('🚨 Your session token has expired!')
            self.user_expired_prompt.label_msg.setText('Please sign in your account again or contact us')

        self.user_expired_prompt.signin.clicked.connect(self.StartLoginServer)
        self.user_expired_prompt.contactus.clicked.connect(self.OpenContactUsEmail)
        self.user_expired_prompt.close.clicked.connect(self.PromptClose)
        self.user_expired_prompt_dialog.exec_()

    #get cpu serial number
    def get_CPU_info(self):
        cp = wmi.WMI().Win32_Processor()
        return cp[0].ProcessorId

    def get_mac_address(self):
        cmd = 'wmic path Win32_NetworkAdapter where "PNPDeviceID like "%PCI%" AND AdapterTypeID="0"" get name, MacAddress'
        data = run(cmd, capture_output=True, shell=True)
        output = data.stdout.splitlines()
        res = {}
        for line in output:
            line = line.decode('utf-8')
            strings = line.split(' ')
            if len(strings) >= 2:
                if strings[0].lower() != 'macaddress':
                    mac_address = strings[0]
                    name = ''
                    for i in range(1, len(strings)):
                        if strings[i] != '':
                            if name == '':
                                name += strings[i]
                            else:
                                name += ' ' + strings[i]
                    res[name] = mac_address

        if len(res.keys()) == 1:
            return list(res.values())[0]
        else:
            for key, value in res.items():
                if 'Ether' in key:
                    return value
            else:
                return self.get_serial_number_of_physical_disk()

    # get C disk-id
    def get_serial_number_of_physical_disk(self):
        c = wmi.WMI()
        for physical_disk in c.Win32_DiskDrive():
            for partition in physical_disk.associators("Win32_DiskDriveToDiskPartition"):
                for logical_disk in partition.associators("Win32_LogicalDiskToPartition"):
                    if logical_disk.Caption == 'C:':
                        return physical_disk.SerialNumber
                    else:
                        continue

    def pickleReadFile(self):
        pickle_open = open(self.parent_window.license_file_path, 'rb')
        local_data = pickle.load(pickle_open)
        decrypt_bytes = self.decryptFunction(local_data)
        decrypt_dict=eval(decrypt_bytes)
        pickle_open.close()
        return decrypt_dict


    # def is_in_tracking_list(self, license_key):
    #     """
    #         Check if a license is in the tracking list.
    #
    #         Parameters:
    #             license_key (str): The license key to be checked.
    #
    #         Returns:
    #             bool: True if the license is in the tracking list, False otherwise.
    #     """
    #     try:
    #         res = requests.post(self.check_tracking_by_licence_key_url,
    #                             data=json.dumps({"licenceKey": self.parent_window.encrypt(license_key).decode("utf-8")}),
    #                             headers={
    #                                 'Content-type': 'application/json'
    #                             },
    #                             timeout=4)
    #         if res.status_code == 200:
    #             return json.loads(res.text)['data']
    #         else:
    #             return False
    #     except Exception:
    #         return False


    def get_feature_permission_res(self, token):
        """
            Retrieves feature permissions associated with a given license key.

            Args:
                token (str): The token to use for fetching feature permissions.

            Returns:
                dict or None: A dictionary containing feature permissions categorized by feature types,
                or None if an error occurs.

            Note:
                This function sends an HTTP POST request to retrieve feature permissions based on the provided
                license key. It categorizes the permissions by feature types and returns them as a dictionary.
                If the request is successful (HTTP status code 200), the dictionary is returned.
                If error or exception occurs, None is returned.

        """
        if DEBUG: print("---Get Feature Permission---")
        from flowstudio.flow_conf import AO_TYPE_NAME
        try:
            headers = {
                'Token': f'{token}',  # Ensure the token is correctly formatted
                'Content-Type': 'application/json'  # Other optional headers
            }
            res = requests.post(self.get_all_features_by_token_url,
                                headers=headers,
                                timeout=4)
            if DEBUG: print("get_feature_permission_res: " + res.text)
            if res.status_code == 200:
                features_dict = defaultdict(list)
                feature_list = json.loads(res.text)['data']['featureList']

                for feature in feature_list:
                    type_name = feature['type']['name']
                    try:
                        feature_code = int(feature['code']) if type_name == AO_TYPE_NAME else feature['code']
                    except ValueError:
                        continue
                    features_dict[type_name].append(feature_code)
                return features_dict
            else:
                QMessageBox.warning(self.parent_window, 'Initialization Failed',
                                    'Failed to retrieve license information. <br>Please contact support@flow-dsp.com for support.')
                return None
        except Exception as e:
            return None

    def get_technical_provider_info_res(self):
        """
            Retrieves technical provider info using the specified API endpoint.

            This method iterates through the list of technology providers defined in the
            CATE_AO_MAPPING for 'Technology Provider'. For each provider, it sends a POST
            request to the API endpoint with the technical provider's name as the payload.
            If the request is successful (status code 200), the information is extracted
            from the response and stored in a dictionary. The final result is a dictionary
            containing technical provider information keyed by their respective names in database.

            Returns:
                dict or None: A dictionary containing technical provider information, where
                keys are names in database, and values are the extracted information. Returns
                None if an exception occurs during the process.
        """
        from flowstudio.flow_conf import CATE_AO_MAPPING
        try:
            company_info = {}
            for company in CATE_AO_MAPPING['Technology Provider']:
                company_db_name = company.db_name
                res = requests.post(self.get_info_by_technical_provider_name_url,
                                    data=json.dumps({'customer_name': company_db_name}),
                                    headers={
                                        'Content-type': 'application/json'
                                    },
                                    timeout=4)
                if res.status_code == 200:
                    company_info[company_db_name] = json.loads(res.text)['data']['info']
                else:
                    return None
            return company_info
        except Exception as e:
            return None

    def get_ao_info_res(self):
        """
            Retrieves information of all audio objects using the specified API endpoint.

            This method sends a POST request to the API endpoint, providing the application name,
            operating system, and AO type name as parameters. The response contains information
            about all AOs.

            Returns:
                dict or None: A dict containing AO information, where keys are
                AO codes (integers), and values are the corresponding
                AO information. Returns None if an exception occurs during the process.
        """
        if DEBUG: print("---Get AO Info---")
        from flowstudio.flow_conf import FLOW_NODES, APP_NAME, OS_NAME, AO_TYPE_NAME
        try:
            res = requests.post(self.get_all_features_by_app_and_type_name,
                                data=json.dumps({'appName': APP_NAME,
                                                 'os': OS_NAME,
                                                 'typeName': AO_TYPE_NAME}),
                                headers={
                                    'Content-type': 'application/json'
                                },
                                timeout=4)
            if DEBUG: print("get_ao_info_res: " + res.text)
            if res.status_code == 200:
                ao_info = defaultdict(str)
                aos = json.loads(res.text)['data']
                for ao in aos:
                    try:
                        ao_code = int(ao['code'])
                        if ao_code in FLOW_NODES:
                            ao_info[ao_code] = ao['info'] if ao['info'] else ''
                    except ValueError:
                        continue
                return ao_info
            else:
                return None
        except Exception as e:
            return None


    # Every time the application is closed, a message will be sent to record usage information
    def createUserRecord(self):
        if DEBUG: print("---Create User Record---")
        try:
            self.quitTime = datetime.datetime.now()
            if (self.quitTime - self.loginTime).total_seconds() < 60:
                return

            if self.user is None:
                email = ''
            else:
                email = self.user['email']

            data = {
                "address": self.parent_window.encrypt(self.address).decode("utf-8"),
                "ip": self.parent_window.encrypt(self.ip).decode("utf-8"),
                "login_time": self.parent_window.encrypt(str(self.loginTime)).decode("utf-8"),
                "logout_time": self.parent_window.encrypt(str(self.quitTime)).decode("utf-8"),
                "email": self.parent_window.encrypt(str(email)).decode("utf-8")
            }

            headers = {'Token': f'{self.token}',
                       "Content-Type": "application/json"}
            raw_data = json.dumps(data)
            response = requests.post(self.create_record_url, data=raw_data, headers=headers)

            if DEBUG: print("Create User Record: " + response.text)
        except Exception as e:
            if DEBUG: print("Create User Record Failed", str(e))

    # Track user action 'Close FlowStudio'
    def recordUserCloseAction(self):
        if DEBUG: print("---Close FlowStudio Action---")
        try:
            if self.user is None:
                email = ''
            else:
                email = self.user['email']

            data = {
                "address": self.address,
                "email": email,
                "action": 2
            }

            headers = {"Content-Type": "application/json"}
            raw_data = json.dumps(data)
            response = requests.post(self.create_user_action_url, data=raw_data, headers=headers)

            if DEBUG: print("Create User Action: " + response.text)
        except Exception as e:
            if DEBUG: print("Create User Action Failed", str(e))

    # Retrieve user first records, Check the free usage time of users
    def check_user_free_time(self):
        if DEBUG: print("---Get First Record---")
        try:
            data = {
                "address": self.parent_window.encrypt(self.address).decode("utf-8")
            }

            headers = {"Content-Type": "application/json"}
            raw_data = json.dumps(data)
            response = requests.post(self.get_user_first_record_url, data=raw_data, headers=headers)
            if DEBUG: print("Get First Record: " + response.text)
            response_data = json.loads(response.text)
            # Check the free usage time of users
            if response_data['ResultCode'] == 20000000:
                given_date = datetime.datetime.strptime(response_data['data']['create_time'], "%Y-%m-%d %H:%M:%S")
            else:
                given_date = datetime.datetime.strptime(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"), "%Y-%m-%d %H:%M:%S")
            expiration_date = given_date + timedelta(days=self.no_login_free_time)
            current_date = datetime.datetime.now()
            remaining_time = expiration_date - current_date
            self.remain_time = remaining_time
            self.tier = 'Free'
            self.expire_type = 'trial'
            self.user = None
            return True
        except Exception as e:
            if DEBUG: print('Get First Record Failed ', str(e))
            return False

    # Retrieve user information using tokens
    def CheckUserToken(self, token):
        if DEBUG: print("---Check User Token---")
        member_type_to_tier = {
            1: 'Free',
            2: 'Pro',
            3: 'Premium'
        }

        try:
            data = {
                "token": self.parent_window.encrypt(token).decode("utf-8")
            }

            headers = {"Content-Type": "application/json"}
            raw_data = json.dumps(data)
            response = requests.post(self.check_user_token_url, data=raw_data, headers=headers)
            if DEBUG: print("Check User Token: " + response.text)
            response_data = json.loads(response.text)

            # Token is not valid
            if response_data['ResultCode'] == 40020041:
                self.expire_type = 'token valid'
                self.UserExpiredPrompt()
                return True

            if int(response_data['data']['userLicence']['expire_time'].split('-')[0]) > 9999:
                self.remain_time = datetime.timedelta(days=9999)
            else:
                expiration_date = datetime.datetime.strptime(response_data['data']['userLicence']['expire_time'],
                                                             "%Y-%m-%d %H:%M:%S")
                current_date = datetime.datetime.now()
                remaining_time = expiration_date - current_date

                self.remain_time = remaining_time
            self.tier = member_type_to_tier.get(response_data['data']['userLicence']['member_type'], 'Unknown')
            self.expire_type = 'login'
            # if self.remain_time.total_seconds() < 0:
            #     self.tipBox.check_user_free_time_not_available()
            #     return False

            self.user = response_data['data']
            return True
        except Exception as e:
            if DEBUG: print('Check User Token Failed ', str(e))
            return False

    # Check if the version is available
    def version_check(self):
        if DEBUG: print("---Version Check---")
        try:
            data = {
                "version_code": self.parent_window.encrypt(VERSION).decode("utf-8")
            }

            headers = {"Content-Type": "application/json"}
            raw_data = json.dumps(data)
            response = requests.post(self.version_check_url, data=raw_data, headers=headers)
            if DEBUG: print("Version Check Record: " + response.text)
            response_data = json.loads(response.text)
            if response_data['ResultCode'] != 20000000:
                self.tipBox.version_check_fail(self.portal_url)
                if self.splash:
                    self.splash.close()
                return None
            return True
        except Exception as e:
            if DEBUG: print('Version Check Failed ', str(e))
            return False

    def unpad(self, text):
        return text[0:-ord(text[-1:])]

    # decrypt function
    def decryptFunction(self,encrypt_data):
        cryptos = AES.new(self.parent_window.encrypt_key.encode("utf8"),
                          self.parent_window.encrypt_mode,
                          self.parent_window.encrypt_iv.encode("utf8"))
        plain_data=cryptos.decrypt(a2b_hex(encrypt_data))
        return self.unpad(plain_data)

    # get user ip
    def get_user_ip(self):
        apis = [
            "https://api.ipify.org",
            "https://ipinfo.io/ip",
            "https://ifconfig.me/ip",
            "https://ident.me",
            "http://myexternalip.com/raw",
            "https://ipecho.net/plain"
        ]
        for api in apis:
            try:
                response = requests.get(api, timeout=5)
                if response.status_code == 200:
                    if DEBUG: print("IP:", response.text.strip())
                    return response.text.strip()
            except Exception as e:
                if DEBUG: print(f"try {api} fail: {str(e)}")
                return "unknown"

class TipBox:
    def __init__(self,parent):
        self.parent=parent

    # def offlinePromptMinuteBox(self,minute):
    #     return QMessageBox.information(self.parent,"offline remain minute","you just remain %d minute use, please notice." % minute)

    # def inlinePromptDayBox(self,day):
    #     return QMessageBox.information(self.parent,"inline remain day","you just remain %d day use,please notice." % day)

    def downloadLatestExeBox(self,url):
        return QMessageBox.about(self.parent,"download latest install package"," you current version isn't latest, please visit %s download latest install package" % url)

    def offlinePromptExhaustMinute(self):
        return QMessageBox.warning(self.parent, "available time exhausted",
                                   "sorry, your available time has run out,you can try to connect to the Internet or contact tym to buy permanent access.")

    def inlinePromptExhaustTime(self):
        return QMessageBox.warning(self.parent, 'Your license has expired',
                                   'Please contact Tymphany to renew your Flow Studio license.')

    def inlinePromptNoResponse(self):
        return QMessageBox.warning(self.parent, 'No response',
                                   "Unable to retrieve license-related information from the server. Would you like to use offline mode?",
                                   QMessageBox.Apply | QMessageBox.Cancel)

    def check_user_free_time_available(self, remaining_time):
        msg_box = QMessageBox(self.parent)
        msg_box.setWindowTitle('Initialization Information')
        msg_box.setIcon(QMessageBox.NoIcon)
        msg_box.setStyleSheet("""
            QMessageBox QLabel {
                width: 300px;
                font-size: 18px !important;
            }
        """)
        msg_box.setText(f"""
            <div style="text-align: center;">
                <p>Welcome to Flow Studio</p>
                🚨 Your trial has expired {remaining_time}!
            </div>
        """)
        msg_box.exec_()
        return msg_box

    def check_user_free_time_not_available(self):
        msg_box = QMessageBox(self.parent)
        msg_box.setWindowTitle('Initialization Information')
        msg_box.setIcon(QMessageBox.NoIcon)
        msg_box.setText("""
        <div style="font-size: 14px;">
             <b>🚨 Your trial has expired!</b><br>
             Please Contact TYM.<br>
             Note: New users get one year free when signing up now!<br><br>
        </div>
        """)
        msg_box.exec_()
        return msg_box

    def init_data_fail(self):
        return QMessageBox.warning(self.parent, 'Offline Mode Activated',
                                   "Reminder: Flow Studio is currently running in Offline Mode. <br>"
                                   "This may be due to a temporary server issue or loss of internet connection.")

    def version_check_fail(self, URL):
        msg_box = QMessageBox(self.parent)
        msg_box.setWindowTitle('Version Check Failed')
        msg_box.setIcon(QMessageBox.Warning)
        msg_box.setTextFormat(Qt.RichText)
        msg_box.setTextInteractionFlags(Qt.TextBrowserInteraction)
        message = (
            'The current version is no longer available.<br/>'
            'Please upgrade to the latest version by visiting: '
            f'<a href="{URL}" style="text-decoration:none;">'
            'portal'
            '</a>'
        )
        msg_box.setText(message)
        msg_box.exec_()
        return msg_box

    # def registerPromptFail(self):
    #     return QMessageBox.warning(self.parent,"register fail", " sorry, you register is fail, please try again.")

class lowerRightCornerWidget(QWidget):
    def __init__(self,parent,mode,time):
        super().__init__()
        self.parentWidget = parent
        self.setWindowTitle('Important Notice: Limited Access Period Remaining')
        self.setStyleSheet("background:#F8F8FF;")
        self.setFixedSize(500, 80)
        self.setWindowIcon(QIcon("../resources/main-theme.png"))
        self.move(self.parentWidget.width()-270,self.parentWidget.height()-160)
        if not mode:
            self.time = time // 60
            self.mode = 'minutes' if self.time > 1 else 'minute'
            self.status="offline mode"
        else:
            self.time = time // 60 // 60 // 24
            self.mode = 'days' if self.time > 1 else 'day'
            self.status="online mode"
        self.setUi()
        self.show()
        self.doAnimation()

    def setUi(self):
        self.label=QLabel(self)
        self.label.setText("<html><head/><body><p><span style=\" font:Calibri; font-size:12pt;\">"
                           "&nbsp;&nbsp;Dear user, <br/>"
                           "&nbsp;&nbsp;&nbsp; You are currently in %s, and you only have <b> %d %s </b> left to use.<br/>"
                           "&nbsp;&nbsp;&nbsp; Please take note.</span></p></body></html>"
                           % (self.status, self.time, self.mode))

    def doAnimation(self):
        animation=QPropertyAnimation(self.parentWidget)
        animation.setTargetObject(self)
        animation.setPropertyName(b'windowOpacity')
        animation.setDuration(5000)
        animation.setStartValue(1)
        animation.setEndValue(0)
        animation.finished.connect(self.close)
        animation.start()