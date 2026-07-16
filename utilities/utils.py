import os
import sys
import csv
import xlrd
import subprocess
import numpy as np
import openpyxl


def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)

def getFileDialogDirectory():
    """Returns starting directory for ``QFileDialog`` file open/save"""
    return ''

def getFileDialogPROJFilter():
    """Returns starting directory for ``QFileDialog`` file open"""
    return 'PROJ (*.proj);;All files (*)'

def getFileDialogFilter():
    """Returns ``str`` standard file open/save filter for ``QFileDialog``"""
    return 'Graph (*.json);;All files (*)'

def getProfileFilter():
    """Returns ``str`` standard file open/save filter for ``QFileDialog``"""
    return 'Profile (*.profile);;All files (*)'

def getCoefficientFilter():
    """Returns ``str`` standard file open/save filter for ``QFileDialog``"""
    # return 'Filter Coefficient (*.txt *.csv *.xls *.xlsx);;All files (*)'
    return 'Filter Coefficient (*.xls *.xlsx);;All files (*)'

def getWavFilter():
    """Returns ``str`` standard file open/save filter for ``QFileDialog``"""
    return 'Waveform Audio File (*.wav);;All files (*)'

def txt2dict(fname):
    with open(fname) as file:
        dict = {}
        converter = []
        for line in file:
            new_list = line.split()[:2]
            try:
                if isNumeric(new_list[0]):
                    dict['a'] = float(new_list[0])
                else:
                    return []
            except Exception:
                return []

            try:
                if isNumeric(new_list[1]):
                    dict['b'] = float(new_list[1])
                else:
                    return []
            except Exception:
                dict['b'] = 0

            # if type(new_list[0]) == str and type(new_list[1]) == str:
            #     try:
            #         dict['a'] = float(new_list[0])
            #         dict['b'] = float(new_list[1])
            #     except ValueError:
            #         dict['a'] = new_list[0]
            #         dict['b'] = new_list[1]

            converter.append(dict.copy())
        return converter[1:]

def csv2dict(fname):
    with open(fname, newline='') as file:
        file = csv.DictReader(file)
        converter = []
        dict = {}
        for line in file:
            for element in line:
                element_list = element.split()[:2]
                try:
                    if isNumeric(element_list[0]):
                        dict['a'] = float(element_list[0])
                    else:
                        return []
                except Exception:
                    return []

                try:
                    if isNumeric(element_list[1]):
                        dict['b'] = float(element_list[1])
                    else:
                        return []
                except Exception:
                    dict['b'] = 0
            converter.append(dict.copy())
        return converter

def extract_coefficients_from_excel(file_path, disable_denominator = False):
    numerator = list()
    denominator = list()

    workbook = None
    sheets = None
    try:
        if file_path.endswith('.xls'):
            workbook = xlrd.open_workbook(file_path)
            sheets = workbook.sheet_names()
        elif file_path.endswith('.xlsx'):
            workbook = openpyxl.load_workbook(file_path)
            sheets = workbook.sheetnames

        for sheet in sheets:
            current_sheet = None
            if file_path.endswith('.xls'):
                current_sheet = workbook.sheet_by_name(sheet)
            elif file_path.endswith('.xlsx'):
                current_sheet = workbook[sheet]
            if file_path.endswith('.xls'):
                if current_sheet.nrows == 0:
                    continue
            elif file_path.endswith('.xlsx'):
                if current_sheet.max_row == 0:
                    continue
            if file_path.endswith('.xls'):
                for row in range(0, current_sheet.nrows):
                    values = current_sheet.row_values(row)

                    flag, result = isNumeric(values[0])
                    if flag:
                        numerator.append(float(result).__round__(12))
                    else:
                        return False, None

                    if not disable_denominator:
                        if len(values) == 2:
                            flag, result = isNumeric(values[1])
                            if flag:
                                denominator.append(float(result).__round__(12))
                            else:
                                return False, None
                        else:
                            return False, None
            elif file_path.endswith('.xlsx'):
                for row in current_sheet.iter_rows(min_row=1, max_row=current_sheet.max_row, values_only=True):
                    if not row:
                        continue

                    flag, result = isNumeric(row[0])
                    if flag:
                        numerator.append(float(result).__round__(12))
                    else:
                        return False, None

                    if not disable_denominator:
                        if len(row) == 2:
                            flag, result = isNumeric(row[1])
                            if flag:
                                denominator.append(float(result).__round__(12))
                            else:
                                return False, None
                        else:
                            return False, None

        if disable_denominator:
            while len(numerator) < 32:
                numerator.append(0.0)
            return True, [numerator]
        else:
            if any(denominator):
                print(numerator)
                print("-------------------")
                print(denominator)
                return True, [numerator[0:10], denominator[0:10]]

            else:
                return False, None, 'The filter coefficients you provided have a problem, please check again.'
    except:
        return False, None


def isNumeric(input_data: str):
    try:
        result = float(input_data)
        return True, result
    except ValueError:
        return False, None

def circular(array, element, size):
    if len(array) == size:
        array.append(element)
        array.pop(0)
    else:
        array.append(element)
    return array

def getReleaseTime(decay = 100):
    analogTimeConstant = -1.00239343093 # ln(0.367)
    result = np.exp(analogTimeConstant * 0.05 / (decay * 0.001))
    return result

def isEngineAlive(file_name=None):
    cmd = "tasklist /svc | find \"FlowEngine.exe\""
    if file_name is not None:
        cmd = f"tasklist /svc | find \"{file_name}\""
    Process = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE)
    return Process.stdout.read()

def killEngine(file_name=None):
    cmd = "taskkill /IM FlowEngine.exe /F"
    if file_name is not None:
        cmd = f"taskkill /IM {file_name} /F"
    Process = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE)
    return Process.stdout.read()
