import json
import winreg


def add_ampersand_before_and(string):
    indexes = [i for i, char in enumerate(string) if char == '&']
    for index in reversed(indexes):
        string = string[:index] + '&' + string[index:]
    return string



def is_valid_json(file_path):
    try:
        with open(file_path, 'r') as file:
            json.load(file)
        return True
    except (ValueError, json.JSONDecodeError):
        return False

def is_program_installed(search_text):
    registry_paths = [
        r"SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall",
        r"SOFTWARE\WOW6432Node\Microsoft\Windows\CurrentVersion\Uninstall"
    ]

    for registry_path in registry_paths:
        try:
            reg_key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, registry_path)
            for i in range(0, winreg.QueryInfoKey(reg_key)[0]):
                sub_key_name = winreg.EnumKey(reg_key, i)
                sub_key = winreg.OpenKey(reg_key, sub_key_name)
                try:
                    program_name = winreg.QueryValueEx(sub_key, "DisplayName")[0]
                    if search_text.lower() in program_name.lower():
                        return True
                except FileNotFoundError:
                    pass
                finally:
                    sub_key.Close()
            reg_key.Close()
        except FileNotFoundError:
            pass

    return False

