import os
import subprocess
import platform

import paramiko
import shutil

from PyQt5.QtWidgets import QMessageBox


def sshGetConnect(username: str, hostname: str, verified_text: str):
    system32 = os.path.join(os.environ['SystemRoot'],'SysNative' if platform.architecture()[0] == '32bit' else 'System32')
    scp_path = os.path.join(system32, 'OpenSSH/scp.exe')

    destination = username + '@' + hostname
    # commands = [scp_path, '-T', destination, "uname"]
    commands = [scp_path, destination, "uname"]
    # destination = username + '@' + hostname
    # commands = ['adb.exe', '-T', destination, "uname"]

    try:
        process = subprocess.run(commands, timeout=8, stdout=subprocess.PIPE)
    except Exception as e:
        print("sshGetConnect Errors:", e)
        return False

    try:
        result = process.stdout.decode().rstrip()
    except Exception:
        return False

    if result == verified_text:
        return True
    else:
        return False

def adbGetConnect():
    commands = ['adb.exe', 'devices', '-l']

    try:
        process = subprocess.run(commands, timeout=8, stdout=subprocess.PIPE)
    except Exception as e:
        print("adbGetConnect Errors: ", e)
        return False

    try:
        result = process.stdout.decode().rsplit('\n')
        ListOfDevicesAttached = result[0].rstrip()
        deviceProduct = result[1].rstrip()
    except Exception:
        return False

    if ListOfDevicesAttached == "List of devices attached":
        if "qcs40x-qsap" in deviceProduct:
            return True
        else:
            return False
    else:
        return False

def sshGetUpload(username: str, hostname: str, remoteDir: str, localPath: str):
    system32 = os.path.join(os.environ['SystemRoot'],'SysNative' if platform.architecture()[0] == '32bit' else 'System32')
    scp_path = os.path.join(system32, 'OpenSSH/scp.exe')

    if localPath.split('.')[-1] == 'proj':
        remotepath = remoteDir + "default.proj"
    else:
        remotepath = remoteDir + localPath.split('/')[-1]

    destination = username + '@' + hostname + ':' + remotepath
    commands = [scp_path, localPath, destination]
    process = subprocess.Popen(commands, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    # process.wait()
    result = repr(process.stderr.readline())
    process.stdout.close()

    if result == str(b''):
        return True
    else:
        return False

def sshGetDownload(username: str, hostname: str, remoteDir: str, localPath: str):
    system32 = os.path.join(os.environ['SystemRoot'],'SysNative' if platform.architecture()[0] == '32bit' else 'System32')
    scp_path = os.path.join(system32, 'OpenSSH/scp.exe')

    destination = username + '@' + hostname + ':' + remoteDir + '/default.proj'
    commands = [scp_path, '-r', destination, localPath+'/default.proj']
    process = subprocess.Popen(commands, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    # process.wait()
    result = repr(process.stderr.readline())
    process.stdout.close()

    if result == str(b''):
        return True
    else:
        return False

def adbGetUpload(remoteDir: str, localPath: str):
    if localPath.split('.')[-1] == 'proj':
        remotepath = remoteDir + "default.proj"
    else:
        remotepath = remoteDir + localPath.split('/')[-1]
    local = localPath
    commands = ['adb.exe', 'push', local, remotepath]

    try:
        process = subprocess.run(commands, timeout=8, stdout=subprocess.PIPE)
    except Exception as e:
        print("adbGetUpload Errors: ",e)
        return False

    try:
        result = process.stdout.decode().rsplit('\n')
        if '1 file pushed' in result[0]:
            return True
        else:
            return False
    except Exception:
        return False

def adbGetDownload(remoteDir: str, localPath: str):
    remote = remoteDir + '/default.proj'
    local = localPath + '/default.proj'
    commands = ['adb.exe', 'pull', remote, local]

    try:
        process = subprocess.run(commands, timeout=8, stdout=subprocess.PIPE)
    except Exception as e:
        print("adbGetDownload Errors: ",e)
        return False

    try:
        result = process.stdout.decode().rsplit('\n')
        if '1 file pulled' in result[0]:
            return True
        else:
            return False
    except Exception:
        return False


def sshGetUploadHasPassword(username: str, password:str, hostname: str, remoteDir: str, localPath: str):
    try:
        trans = paramiko.Transport((hostname, 22))

        trans.connect(username=username, password=password)

        sftp = paramiko.SFTPClient.from_transport(trans)
        if localPath.split('.')[-1] == 'proj':
            remotepath=remoteDir + "default.proj"
        else:
            remotepath=remoteDir + localPath.split('/')[-1]
        sftp.put(localpath=localPath, remotepath=remotepath)

        trans.close()
        return True
    except Exception:
        return False

def raspberry_pi_copy_file(window, username: str, password:str, hostname: str, remoteDir: str, localPath: str):
    # if localPath.split('.')[-1] == 'proj': return True
    #
    # ssh = paramiko.SSHClient()
    # ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    # try:
    #     ssh.connect(hostname, username=username, password=password)
    #     stdin, stdout, stderr = ssh.exec_command("cd %s;"
    #                                              "rm default_config.flw" % remoteDir)
    #     result = stdout.read().decode()
    #     error = stderr.read().decode()
    #     # print('result', result)
    #     # print('error', error)
    #     if error != '':
    #         QMessageBox.about(window, "SSH Note", "%s" % error)
    #         print(error)
    #         return
    # except paramiko.AuthenticationException:
    #     statement = "Authentication failed, please check username and password"
    #     QMessageBox.about(window, "SSH Note", "%s" % statement)
    # except paramiko.SSHException as sshException:
    #     statement = "Unable to establish SSH connection: %s" % sshException
    #     QMessageBox.about(window, "SSH Note", "%s" % statement)
    # except Exception as e:
    #     statement = "Error occurred: %s" % e
    #     QMessageBox.about(window, "SSH Note", "%s" % statement)
    # finally:
    #     ssh.close()
    #
    # try:
    #
    #     trans = paramiko.Transport((hostname, 22))
    #
    #     trans.connect(username=username, password=password)
    #
    #     sftp = paramiko.SFTPClient.from_transport(trans)
    #
    #     sftp.put(localpath=localPath, remotepath=remoteDir + '/default_config.flw')
    #
    #     trans.close()
    #     return True
    # except Exception as e:
    #     QMessageBox.about(window, "SFTP Note", "%s" % e)
    #     return False

    try:
        path = "C:/FlowAPO/Config"
        try:
            os.makedirs(path)
        except OSError as error:
            print(error)


        shutil.copy2(localPath, "C:\\FlowAPO\\Config\\")


        return True
    except Exception as error:
        print(error)
        return False

def sshGetDownloadHasPassword(username: str, password:str, hostname: str, remoteDir: str, localPath: str):
    try:
        trans = paramiko.Transport((hostname, 22))

        trans.connect(username=username, password=password)

        sftp = paramiko.SFTPClient.from_transport(trans)

        sftp.get(remotepath=remoteDir + '/default.proj', localpath=localPath+'/default.proj')
        trans.close()
        return True
    except Exception:
        return False

def windowsCopyConfigFile(srcpath: str):
    try:
        path = "C:/FlowAPO/Config"
        try:
            os.makedirs(path)
        except OSError as error:
            print(error)


        shutil.copy2(srcpath, "C:\\FlowAPO\\Config\\")


        return True
    except Exception as error:
        print(error)
        return False