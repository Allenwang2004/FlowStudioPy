import enum
import os
APP_NAME = 'Flow Studio'
OS_NAME = 'Windows'
AO_TYPE_NAME = 'AO'
LISTBOX_MIMETYPE = "application/x-item"

SECRET_KEY = 'j9kf*pn_k5iz$dh*c(&k^kp-lyv=tvl^b9j=$@w(6bsfx=(b%k'

RESULT_CODE_ADDRESS_NOT_EXIST = 40020071

class Debug(enum.Enum):
    DEBUG_Low_Level = False
    DEBUG_COMMON = False
    DEBUG_TWEAKER = False
    DEBUG_THREAD = False
    DEBUG_SERIALIZE = False

@enum.unique
class Target(enum.Enum):
    PC = 0
    IMX = 1
    LINUX = 2
    AMLOGIC = 3
    LINKPLAY = 4
    RASP = 5
    QCS = 6
    CORTEX_M_USB = 7  # this represents Cortex-M
    CORTEX_M_UART = 71
    AIROHA_AB1585_UART = 8  # this represents Airoha AB1585
    AIROHA_USB = 81
    AIROHA_AB1565_UART = 9  # this represents Airoha AB1565
    FLOW_APO = 10
    FLOW_EVK_UART = 11  # this represents Flow EVK
    FLOW_EVK_USB = 100
    GX8008C_USB = 12
    S7 = 13


@enum.unique
class TypeAOAddition(enum.Enum):
    FIXED = 1
    DYNAMIC_NUM_CHANNELS = 2
    DYNAMIC_NUM_INPUTS_AND_OUTPUTS = 3
    DYNAMIC_NUM_BANDS_AND_CHANNELS = 4
    DYNAMIC_NUM_TAPS = 5
    DYNAMIC_NUM_OUTPUTS_AND_FOUR_TIMES_INPUTS = 6
    SPECIAL_ACTION = 7
    DYNAMIC_SOCKET_TYPE = 8
    DYNAMIC_SOCKET_TYPE_AND_SOCKET_NUM = 9

@enum.unique
class ControlType(enum.Enum):
    SWITCH = 0
    LOAD_FILE = 1
    LABEL = 2
    BUTTON = 3
    MENU = 4
    MUX_MENU = 5
    SPECIAL_FLOAT_SPINBOX = 6
    LINEAR_INT_SLIDER_AND_SPINBOX = 7
    LOGARITHMIC_INT_SLIDER_AND_SPINBOX = 8
    LINEAR_FLOAT_SLIDER_AND_SPINBOX = 9
    LOGARITHMIC_FLOAT_SLIDER_AND_SPINBOX = 10
    FLOAT_SPINBOX = 11
    TAP_MENU = 12
    DISABLE_MENU = 13
    LABEL_VALUE = 14


AO_ADDITION_TYPES_FOR_OA = [('fixed number of channels', TypeAOAddition.FIXED.value),
                            ('dynamic number of channels', TypeAOAddition.DYNAMIC_NUM_CHANNELS.value),
                            # ('dynamic number of input channels and output channels',
                            #  TypeAOAddition.DYNAMIC_NUM_INPUTS_AND_OUTPUTS.value),
                            # ('dynamic number of bands and channels',
                            #  TypeAOAddition.DYNAMIC_NUM_BANDS_AND_CHANNELS.value),
                            # ('dynamic number of taps', TypeAOAddition.DYNAMIC_NUM_TAPS.value)
                            ]

CONTROL_TYPES_FOR_OA = [('Switch', ControlType.SWITCH.value),
                        ('Menu', ControlType.MENU.value),
                        ('Linear Int Slider and SpinBox', ControlType.LINEAR_INT_SLIDER_AND_SPINBOX.value),
                        ('Log Int Slider and SpinBox', ControlType.LOGARITHMIC_INT_SLIDER_AND_SPINBOX.value),
                        ('Linear Float Slider and SpinBox', ControlType.LINEAR_FLOAT_SLIDER_AND_SPINBOX.value),
                        ('Log Float Slider and SpinBox', ControlType.LOGARITHMIC_FLOAT_SLIDER_AND_SPINBOX.value),
                        # ('File Loader', ControlType.LOAD_FILE.value),
                        # ('Label', ControlType.LABEL.value),
                        # ('SpinBox', ControlType.FLOAT_SPINBOX.value),
                        # ('Tap Menu', ControlType.TAP_MENU.value)
                        ]


class Company(object):
    def __init__(self, name, db_name, icon_path=None, description='', ao_list=None, info=''):
        """
            Initialize a new Company object.

            Args:
                name (str): The name of the company, which will be displayed in Flow Studio.
                db_name (str): The name of the company which is stored in DB.
                icon_path (str, optional): The file path to the company's icon. Default is None.
                description(str, optional): The description of the company.
                ao_list (list or dict, optional): A list of associated audio objects. Or a dict which contains category and corresponding audio objects. Default is an empty list ([]).
                info(str, optional): The info of the company.

            Returns:
                Company: A new Company object.

            Example:
                # Create a Company object named "ABC Inc."
                abc_company = Company('ABC Inc.', 'ABC Inc.')
        """
        self.name = name
        self.db_name = db_name
        self.icon_path = icon_path
        self.description = description
        self.ao_list = ao_list if ao_list is not None else []
        self.info = info


@enum.unique
class ExportType(enum.Enum):
    COMMAND = 1
    RAW_COMMAND = 2


OP_NODE_INLET = -1
OP_NODE_OUTLET = -2

OP_NODE_INPUT = 1
OP_NODE_OUTPUT = 2
OP_NODE_ADD = 3
OP_NODE_SUB = 4
OP_NODE_MUL = 5
OP_NODE_DIV = 6
OP_NODE_DUMP = 7
OP_NODE_VISUALIZER = 8
OP_NODE_FEEDBACK = 10



OP_NODE_ADC = 11
OP_NODE_DAC = 12
OP_NODE_WAVPLAYER = 13
OP_NODE_TONEGEN = 14
OP_NODE_NOISEGEN = 15
OP_NODE_CHIRP = 16
OP_NODE_XPATIAL = 17

OP_NODE_ADDER = 21
OP_NODE_NEGATOR = 22
OP_NODE_ABS = 23
OP_NODE_SQRT = 24
OP_NODE_RMS = -25
OP_NODE_MOVAV = -26
OP_NODE_MULTIPLIER = 27
OP_NODE_SUBTRACTOR = 28

OP_NODE_BIQUAD = 31

OP_NODE_PEQ = 32
OP_NODE_PEQ_V2 = 39
OP_NODE_LPF = 33
OP_NODE_HPF = 34
OP_NODE_XOVER = 35
OP_NODE_IIRCOEF = 36
OP_NODE_FIR = 37
OP_NODE_LMS = 38
OP_NODE_BIQUAD_LOAD = 3100
OP_NODE_FIR_LOAD = 3101
OP_NODE_GAME_EQ = 3102

OP_NODE_GAIN = 41
OP_NODE_GAIN_ST = 42
OP_NODE_SMART_GAIN = 43
OP_NODE_ATTEN = 44
OP_NODE_ATTEN_ST = 45
OP_NODE_MUTE = 46
OP_NODE_LOUDNESS = 47
OP_NODE_POLARITY = 48
OP_NODE_QUICK_GAIN = 49

OP_NODE_LIMITER = 51
OP_NODE_LIMITER_MB = 52
OP_NODE_COMP = 53
OP_NODE_COMP_Combo = 54
OP_NODE_CLIPPER = 55
OP_NODE_GATE = 56
OP_NODE_SMART_GATE = 57
OP_NODE_AUTO_COMP = 58
OP_NODE_DYNAMIC_FILTER = 59
OP_NODE_DYNAMIC_EQ = 501


OP_NODE_MERGER = 61
OP_NODE_MIXER8 = 62
OP_NODE_MIXER = 66
OP_NODE_MUX = 63
OP_NODE_DRYWET = 64
OP_NODE_MUX_ST = 65

OP_NODE_DELAY = 70
OP_NODE_DELAY_Intp = 71
OP_NODE_MULTITAP = 72
OP_NODE_LONG_APF = 73
OP_NODE_LPF_COMB_FILTER = 74
# OP_NODE_REVERB = 75
OP_NODE_REVERB_V2 = 76
OP_NODE_IR = 77
# OP_NODE_IR_ST = 78
OP_NODE_CHORUS = 79
OP_NODE_DIRAC = 80

OP_NODE_BEAMFORMING = 81
OP_NODE_CROSSFEED = 82
OP_NODE_VAD = 83
OP_NODE_DBASS = 84
OP_NODE_VAD_IABSE = 96
OP_NODE_DEESSER = 86
OP_NODE_VBASS = 87
OP_NODE_AGC = 88
OP_NODE_DLOUDNESS = 89
OP_NODE_AEC = 85
OP_NODE_AI_NR = 801
OP_NODE_NOISEREDUCTION = 802
OP_NODE_SPATIALIZER = 803
OP_NODE_SMART_EQ = 804
OP_NODE_CLIPFIX = 805
OP_NODE_AI_BF = 806
OP_NODE_AI_NR_48K = 807
OP_NODE_AI_NR_UC = 808
OP_NODE_COHBF = 809
OP_NODE_CTC = 94
OP_NODE_AFS = 905

OP_NODE_ROOM_FIX = -4

OP_NODE_SUBPATCH = 90
OP_NODE_METER = 91
OP_NODE_SPECTRUM = 92
OP_NODE_RTA = 93
OP_NODE_BPM = -5
OP_NODE_COMMENT = 95
OP_NODE_BEAMFORMING_2ch = 97
OP_NODE_BEAMFORMING_3ch = 98
OP_NODE_VEP = 99
OP_NODE_CustomEQ = 104
OP_NODE_PHASEVOCODER = 910

OP_NODE_DLFQ = 103

OP_NODE_ABS_FP = 1000
OP_NODE_IN_FP = 1001
OP_NODE_HPF_FP = 1002
OP_NODE_OUT_FP = 1003
OP_NODE_COMP_FP = 1004
OP_NODE_PEQ_FP = 1005
OP_NODE_LIMITER_FP = 1006
OP_NODE_MUX_FP = 1007
OP_NODE_MUTE_FP = 1008
OP_NODE_GAIN_FP = 1009
OP_NODE_METER_FP = 1010
OP_NODE_DBASS_FP = 1011

OP_NODE_MUL_FP = 1012
OP_NODE_SQRT_FP = 1013
OP_NODE_ADDER_FP = 1014

OP_NODE_MIXER_FP = 1015

OP_NODE_LPF_FP = 1016
OP_NODE_FIR_FP = 1017
OP_NODE_XOVER_FP = 1018
OP_NODE_IIRCOEF_FP = 1019

OP_NODE_DELAY_FP = 1020

OP_NODE_COMP_Combo_FP = 1021
OP_NODE_CLIPPER_FP = 1022




OP_NODE_NTTS_IML = 900
OP_NODE_CINGO = 9
OP_NODE_CINGO_SPK = 904
OP_NODE_UPHEAR_VIRT = 902
OP_NODE_UPHEAR_VQE = 901
OP_NODE_NTTS_AGC = 903

OP_NODE_SRC = 906
# OP_NODE_AI_ZIP = 1101
OP_NODE_AI_ZIP = 1101
OP_NODE_AI_ZIP_DE = 1102

OP_NODE_BD_SOUND = 1201

FLOW_NODES = {}
FLOW_NODES_TYPES = {}
FLOW_NODES_DISPLAY_NAMES = {}
CONTROLS_MAPPING = {}

# AOS_ONLY_ALLOW_PC_SIXTEEN_K_SR = [OP_NODE_AI_NR, OP_NODE_AI_BF, OP_NODE_VEP]
AOS_ONLY_ALLOW_PC_SIXTEEN_K_SR = [OP_NODE_AI_NR, OP_NODE_AI_NR_UC]
AOS_ONLY_ALLOW_FORTY_EIGHT_K_SR = [OP_NODE_AI_NR_48K, OP_NODE_VAD, OP_NODE_AI_ZIP]
# AOS_ONLY_ALLOW_SIXTEEN_K_AND_FORTY_EIGHT_K_SR = [OP_NODE_COHBF]
# aos_temporarily_no_support = [OP_NODE_AEC, OP_NODE_AI_NR, OP_NODE_AI_NR_UC, OP_NODE_AI_BF, OP_NODE_MULTITAP, OP_NODE_PEQ_V2, OP_NODE_DYNAMIC_FILTER]

class ConfException(Exception): pass
class InvalidNodeRegistration(ConfException): pass
class OpCodeNotRegistered(ConfException): pass
class OpTypeNotRegistered(ConfException): pass

def register_node_now(op_code, class_reference):
    if op_code in FLOW_NODES:
        raise InvalidNodeRegistration("Duplicite node registration of '%s'. There is already %s" %(op_code, FLOW_NODES[op_code]))
    FLOW_NODES[op_code] = class_reference
    FLOW_NODES_TYPES[class_reference.content_label_objname] = class_reference
    FLOW_NODES_DISPLAY_NAMES[class_reference.display_name] = class_reference

def register_node(op_code):
    def decorator(original_class):
        register_node_now(op_code, original_class)
        return original_class

    return decorator


def register_control_now(control_id, class_reference):
    CONTROLS_MAPPING[control_id] = class_reference


def register_control(control_id):
    def decorator(original_class):
        register_control_now(control_id, original_class)
        return original_class

    return decorator


def get_class_from_opcode(op_code):
    if op_code not in FLOW_NODES: raise OpCodeNotRegistered("OpCode '%d' is not registered" % op_code)
    return FLOW_NODES[op_code]

def get_class_from_type(op_type):
    if op_type not in FLOW_NODES_TYPES: raise OpTypeNotRegistered("OpTypr '%d' is not registered" % op_type)
    return FLOW_NODES_TYPES[op_type]


# region import all controls and register them
from flowstudio.controls import Button, FileLoader, Label, LinearFloatSliderAndSpinBox, LinearIntSliderAndSpinBox, \
    LogFloatSliderAndSpinBox, LogIntSliderAndSpinBox, Menu, MuxMenu, SpecialFloatSpinBox, SpinBox, Switch, TapMenu
# endregion

# import all nodes and register them



from flowstudio.nodes import IN, OUT, WAVPLAYER, TONEGEN, NOISEGEN, CHIRP, DUMP, VISUALIZER, FEEDBACK, XPATIAL, DLFQ, CustomEQ
from flowstudio.nodes import NEGATOR, ABS, SQRT, RMS, MOVAV, MULTIPLIER, ADDER, MERGER, SUBTRACTOR
from flowstudio.nodes import BIQUAD, PEQ, LPF, HPF, IIRCOEF, XOVER, FIR, PEQ_V2, BIQUAD_LOAD, FIR_LOAD, GAME_EQ
from flowstudio.nodes import GAIN, GAIN_ST, SMART_GAIN, ATTEN, ATTEN_ST, MUTE, MIXER8, MIXER, DRYWET, LOUDNESS, \
                             MUX, MUX_ST, POLARITY, QUICK_GAIN
from flowstudio.nodes import LIMITER, LIMITER_MB, CLIPPER, COMP, COMP_Combo, GATE, SMART_GATE, AGC, SRC, AUTO_COMP, \
                             DYNAMIC_FILTER
from flowstudio.nodes import DELAY,  MULTITAP, DELAY_Intp, LONG_APF, LPF_COMB_FILTER, REVERB_V2, IR, CHORUS, VEP, DIRAC
from flowstudio.nodes import (CROSSFEED, SPECTRUM, METER, RTA, COMMENT, BPM, ROOM_FIX_S, VAD, DEESSER, VBASS, DBASS, DLOUDNESS, DYNAMIC_EQ,
                              BEAMFORMING, BEAMFORMING_2ch, BEAMFORMING_3ch, VAD_IABSE, AI_NR, AI_NR_UC, AI_NR_48K, AI_BF, NOISEREDUCTION, CLIPFIX)
from flowstudio.nodes import SPATIALIZER, SMART_EQ, CTC, COHBF, AFS, PHASEVOCODER
from flowstudio.nodes import INLET, OUTLET, SUBPATCH, AEC
from flowstudio.nodes import INLET, OUTLET, SUBPATCH
from flowstudio.nodes import IN_FP, OUT_FP, MUX_FP, LIMITER_FP, METER_FP, ABS_FP, PEQ_FP, HPF_FP, LPF_FP, GAIN_FP, \
                             COMP_FP, MUTE_FP, DBASS_FP, DELAY_FP, XOVER_FP, ADDER_FP, IIRCOEF_FP, MIXER_FP, FIR_FP, \
                             COMP_Combo_FP, MUL_FP, SQRT_FP, CLIPPER_FP
from flowstudio.nodes import NTTS_IML, NTTS_AGC, CINGO, CINGO_SPK, UPHEAR_VQE, UPHEAR_VIRT
from flowstudio.nodes import AIZip, AIZipDE
from flowstudio.nodes import BD_SOUND
# Hide Ao
# LMS  VAD_IABSE

import flowstudio.flow_conf_co

NOT_SUPPORT_AOS_IN_CORTEX_M = [OP_NODE_WAVPLAYER, OP_NODE_RTA, OP_NODE_MULTITAP, OP_NODE_LPF_COMB_FILTER,
                               OP_NODE_LONG_APF, OP_NODE_REVERB_V2, OP_NODE_SPECTRUM, OP_NODE_IR, OP_NODE_AI_BF,
                               OP_NODE_AI_NR, OP_NODE_AI_NR_UC, OP_NODE_CLIPFIX, OP_NODE_NTTS_IML, OP_NODE_NTTS_AGC, OP_NODE_VAD, OP_NODE_CINGO, OP_NODE_CINGO_SPK,
                               OP_NODE_UPHEAR_VQE]
NOT_SUPPORT_AO_IN_AIROHA = [OP_NODE_WAVPLAYER, OP_NODE_RTA, OP_NODE_SPECTRUM, OP_NODE_IR,
                            OP_NODE_VAD]

CATE_AO_MAPPING = {
    'I/O': [OP_NODE_ADC, OP_NODE_IN_FP, OP_NODE_DAC, OP_NODE_OUT_FP, OP_NODE_WAVPLAYER, OP_NODE_TONEGEN,
            OP_NODE_NOISEGEN, OP_NODE_CHIRP, OP_NODE_DUMP, OP_NODE_VISUALIZER, OP_NODE_FEEDBACK, OP_NODE_XPATIAL],
    'Maths': [OP_NODE_ADDER, OP_NODE_ADDER_FP, OP_NODE_NEGATOR, OP_NODE_ABS, OP_NODE_ABS_FP, OP_NODE_SQRT, OP_NODE_SQRT_FP,
              OP_NODE_MULTIPLIER, OP_NODE_MUL_FP, OP_NODE_SUBTRACTOR],
    'Filters': [OP_NODE_BIQUAD, OP_NODE_PEQ, OP_NODE_PEQ_V2, OP_NODE_PEQ_FP, OP_NODE_LPF, OP_NODE_LPF_FP, OP_NODE_HPF, OP_NODE_HPF_FP, OP_NODE_XOVER,
                OP_NODE_XOVER_FP, OP_NODE_IIRCOEF, OP_NODE_FIR, OP_NODE_FIR_FP, OP_NODE_GAME_EQ],
    'Gains': [OP_NODE_GAIN, OP_NODE_GAIN_FP, OP_NODE_SMART_GAIN, OP_NODE_ATTEN,
              OP_NODE_MUTE, OP_NODE_MUTE_FP, OP_NODE_LOUDNESS, OP_NODE_POLARITY, OP_NODE_QUICK_GAIN],
    'Dynamics': [OP_NODE_LIMITER, OP_NODE_LIMITER_FP, OP_NODE_LIMITER_MB, OP_NODE_COMP, OP_NODE_COMP_FP,
                 OP_NODE_COMP_Combo, OP_NODE_COMP_Combo_FP, OP_NODE_CLIPPER, OP_NODE_CLIPPER_FP,
                 OP_NODE_GATE, OP_NODE_SMART_GATE, OP_NODE_AUTO_COMP],
    'Routing & Mixing': [OP_NODE_MERGER, OP_NODE_MUX, OP_NODE_MUX_FP, OP_NODE_DRYWET, OP_NODE_MIXER, OP_NODE_MIXER_FP],
    'Effects': [OP_NODE_DELAY, OP_NODE_DELAY_FP, OP_NODE_DELAY_Intp, OP_NODE_MULTITAP, OP_NODE_LONG_APF, OP_NODE_LPF_COMB_FILTER,
                OP_NODE_REVERB_V2, OP_NODE_IR, OP_NODE_CHORUS],
    'Metering': [OP_NODE_METER, OP_NODE_METER_FP, OP_NODE_SPECTRUM, OP_NODE_RTA],
    'MISCs': [OP_NODE_SUBPATCH, OP_NODE_COMMENT, OP_NODE_BIQUAD_LOAD, OP_NODE_FIR_LOAD],
    'Technology Provider': [Company(name='Fraunhofer IIS',
                                    db_name='Fraunhofer',
                                    icon_path='../resources/fraunhofer-icon.png',
                                    ao_list=[OP_NODE_CINGO, OP_NODE_CINGO_SPK, OP_NODE_UPHEAR_VQE, OP_NODE_UPHEAR_VIRT],
                                    info="About Fraunhofer IIS:<br><br>For over 35 years, the institute’s Audio and Media Technologies division has been shaping the globally deployed standards and technologies in the fields of audio and moving picture production. Starting with the creation of mp3 and continuing with the co-development of AAC and the Digital Cinema Initiative test plan, almost all consumer electronic devices, computers and mobile phones are equipped with systems and technologies from Erlangen today. Meanwhile, a new generation of best-in-class media technologies – such as MPEG-H Audio, xHE-AAC, EVS, LC3/LC3plus, Symphoria, Sonamic, Cingo and upHear – is elevating the user experience to new heights. Always taking into account the demands of the market, Fraunhofer IIS develops technology that makes memorable moments.<br><br><a href='https://www.iis.fraunhofer.de/'>https://www.iis.fraunhofer.de/</a>"),
                            # Company(name='NamiTech',
                            #         icon_path='../resources/namitech-icon.png',
                            #         ao_list=[]),
                            Company(name='NTT sonority',
                                    db_name='NTT',
                                    icon_path='../resources/ntt-sonority-icon.png',
                                    ao_list=[OP_NODE_NTTS_IML, OP_NODE_NTTS_AGC],
                                    info="<a href='https://ntt-sonority.com/en/'>https://ntt-sonority.com/en/</a>"),
                            Company(name='Dirac',
                                    db_name='Dirac',
                                    icon_path='../resources/Dirac.png',
                                    ao_list=[OP_NODE_DIRAC],
                                    info="About Dirac:<br><br>A global audio tech company with headquarters in Uppsala, Sweden, and R&D facilities in Copenhagen, Denmark, and Bangalore, India, with representation in Greater China, Germany, Japan, Korea, and the United States. With a strong focus on the automotive and home audio industries, we collaborate with leading audio innovators and manufacturers to enhance dynamics, clarity, and immersive sound experiences in any environment.<br><br><a href='https://www.dirac.com/'>https://www.dirac.com/</a>"),
                            Company(name='Aizip',
                                    db_name='AI ZIP',
                                    icon_path='../resources/aizip.png',
                                    ao_list=[OP_NODE_AI_ZIP, OP_NODE_AI_ZIP_DE],
                                    info="About Aizip:<br><br>Based in Silicon Valley, Aizip is a leader in model design of AI for IoT (AIoT). With its breakthrough neural network architecture and proprietary automated design tools, Aizip has demonstrated a wide range of deep neural networks (DNN) with superior performance. Since its founding in 2020, Aizip has designed and delivered TinyML models to its diverse customers worldwide.<br><br><a href='https://aizip.ai/'>https://aizip.ai/</a>"),
                            Company(name='BdSound',
                                    db_name='BdSound',
                                    icon_path='../resources/BdSound.png',
                                    ao_list=[OP_NODE_BD_SOUND],
                                    info="About BdSound:<br><br>BdSound is an Italian audio technology company specializing in developing advanced voice and sound processing solutions for various industries.<br>BdSound Provides proprietary Intellectual Property (IP), software, and engineering services related to acoustic and audio technologies. They operate primarily as a Business-to-Business (B2B) provider.<br><br><a href='https://www.bdsound.com/'>https://www.bdsound.com/</a>"),
                            Company(name='THX',
                                    db_name='THX',
                                    icon_path='../resources/THX.png',
                                    ao_list=[],
                                    info="About THX:<br><br>Started in the cinema, and today take that same experience anywhere and everywhere—in the cinema, at home, or on the go. Whether it’s a live event, a movie, or a new entertainment experience or device not yet invented, we’ll be there to ensure you get the truest rendering of the artist’s vision.<br><br><a href='https://thx.com/'>https://thx.com/</a>"),
                            # Company(name='Alango',
                            #         db_name='Alango',
                            #         icon_path='../resources/Alango.png',
                            #         ao_list=[],
                            #         info=''),
                            Company(name='Namitech',
                                    db_name='Namitech',
                                    icon_path='../resources/namitech-icon.png',
                                    ao_list=[],
                                    info="<a href='https://www.namitech.io/'>https://www.namitech.io/</a>"),
                            Company(name='Flow DSP',
                                    db_name='TYM',
                                    icon_path='../resources/main-theme.ico',
                                    ao_list={
                                        'Advanced Playback': [OP_NODE_CROSSFEED, OP_NODE_VBASS, OP_NODE_DBASS,
                                                              OP_NODE_DBASS_FP, OP_NODE_DLOUDNESS, OP_NODE_DYNAMIC_EQ,
                                                              OP_NODE_DYNAMIC_FILTER, OP_NODE_CTC, OP_NODE_SPATIALIZER, OP_NODE_AFS, OP_NODE_CustomEQ, OP_NODE_DLFQ],
                                        'AI DeepTalk': [OP_NODE_VAD, OP_NODE_VAD_IABSE, OP_NODE_AEC,
                                                        OP_NODE_NOISEREDUCTION, OP_NODE_AI_NR, OP_NODE_AI_NR_UC, OP_NODE_AI_NR_48K,
                                                        OP_NODE_COHBF, OP_NODE_BEAMFORMING, OP_NODE_BEAMFORMING_2ch,
                                                        OP_NODE_BEAMFORMING_3ch, OP_NODE_VEP],
                                        '': [OP_NODE_CLIPFIX, OP_NODE_SMART_EQ, OP_NODE_DEESSER, OP_NODE_AGC, OP_NODE_SRC, OP_NODE_PHASEVOCODER]
                                    },
                                    info="About Tymphany:<br><br>The most vertically integrated audio manufacturers in the world, now providing innovative audio IP solutions.<br><br><a href='https://tymphany.com/'>https://tymphany.com/</a>"),
                            ]
}

FIXED_POINT_AOS = []  # fixed point AOs
FLOAT_POINT_AOS = []  # float point AOs
for key, value in FLOW_NODES.items():
    if value.is_float_point:
        FLOAT_POINT_AOS.append(key)
    else:
        FIXED_POINT_AOS.append(key)


NOT_SUPPORT_AOS = {
    Target.PC.value: [OP_NODE_AI_BF, *FIXED_POINT_AOS, OP_NODE_CLIPFIX, OP_NODE_VEP, OP_NODE_DIRAC],

    Target.IMX.value: [*FIXED_POINT_AOS, OP_NODE_VISUALIZER, OP_NODE_DUMP, OP_NODE_CLIPFIX, OP_NODE_NTTS_IML,
                       OP_NODE_NTTS_AGC, OP_NODE_UPHEAR_VIRT, OP_NODE_AI_NR_48K, OP_NODE_VEP, OP_NODE_CINGO, OP_NODE_CINGO_SPK, OP_NODE_UPHEAR_VQE, OP_NODE_DIRAC, OP_NODE_COHBF,
                       OP_NODE_AI_ZIP, OP_NODE_AI_ZIP_DE, OP_NODE_SRC, OP_NODE_BD_SOUND],

    Target.LINUX.value: [*FIXED_POINT_AOS, OP_NODE_VISUALIZER, OP_NODE_DUMP, OP_NODE_CLIPFIX, OP_NODE_NTTS_IML,
                         OP_NODE_NTTS_AGC, OP_NODE_UPHEAR_VIRT, OP_NODE_AI_NR_48K, OP_NODE_VEP, OP_NODE_DIRAC, OP_NODE_COHBF, OP_NODE_AI_ZIP, OP_NODE_AI_ZIP_DE, OP_NODE_SRC,
                         OP_NODE_BD_SOUND],

    Target.AMLOGIC.value: [*FIXED_POINT_AOS, OP_NODE_VISUALIZER, OP_NODE_DUMP, OP_NODE_CLIPFIX, OP_NODE_NTTS_IML,
                           OP_NODE_NTTS_AGC, OP_NODE_UPHEAR_VIRT, OP_NODE_AI_NR_48K, OP_NODE_VEP, OP_NODE_DIRAC,
                           OP_NODE_CINGO, OP_NODE_CINGO_SPK, OP_NODE_UPHEAR_VQE, OP_NODE_COHBF,  OP_NODE_AI_ZIP,
                           OP_NODE_SRC, OP_NODE_BD_SOUND],

    Target.LINKPLAY.value: [*FIXED_POINT_AOS, OP_NODE_VISUALIZER, OP_NODE_DUMP, OP_NODE_CLIPFIX, OP_NODE_NTTS_IML,
                            OP_NODE_NTTS_AGC, OP_NODE_UPHEAR_VIRT, OP_NODE_AI_NR_48K, OP_NODE_VEP, OP_NODE_DIRAC, OP_NODE_COHBF, OP_NODE_AI_ZIP, OP_NODE_AI_ZIP_DE,OP_NODE_SRC,
                            OP_NODE_BD_SOUND],

    Target.RASP.value: [*FIXED_POINT_AOS, OP_NODE_VISUALIZER, OP_NODE_DUMP, OP_NODE_CLIPFIX, OP_NODE_NTTS_IML,
                        OP_NODE_NTTS_AGC, OP_NODE_UPHEAR_VIRT, OP_NODE_AI_NR_48K, OP_NODE_VEP, OP_NODE_CINGO, OP_NODE_CINGO_SPK, OP_NODE_UPHEAR_VQE, OP_NODE_UPHEAR_VIRT,
                        OP_NODE_COHBF,OP_NODE_AI_ZIP, OP_NODE_AI_ZIP_DE,OP_NODE_SRC, OP_NODE_BD_SOUND],

    Target.QCS.value: [*FIXED_POINT_AOS, OP_NODE_VISUALIZER, OP_NODE_DUMP, OP_NODE_CLIPFIX, OP_NODE_NTTS_IML,
                       OP_NODE_NTTS_AGC, OP_NODE_UPHEAR_VIRT, OP_NODE_VEP, OP_NODE_AI_NR_48K, OP_NODE_DIRAC,
                       OP_NODE_CINGO, OP_NODE_CINGO_SPK, OP_NODE_UPHEAR_VQE, OP_NODE_COHBF, OP_NODE_SRC, OP_NODE_BD_SOUND],

    Target.CORTEX_M_USB.value: [*NOT_SUPPORT_AOS_IN_CORTEX_M, *FIXED_POINT_AOS, OP_NODE_VISUALIZER, OP_NODE_DUMP,
                                OP_NODE_UPHEAR_VIRT, OP_NODE_AI_NR_48K, OP_NODE_VEP, OP_NODE_DIRAC, OP_NODE_AI_ZIP, OP_NODE_AI_ZIP_DE ,OP_NODE_SRC,
                                OP_NODE_BD_SOUND],

    Target.AIROHA_AB1585_UART.value: [*NOT_SUPPORT_AO_IN_AIROHA, *FIXED_POINT_AOS, OP_NODE_VISUALIZER, OP_NODE_DUMP, OP_NODE_UPHEAR_VQE,
                                      OP_NODE_UPHEAR_VIRT, OP_NODE_DIRAC, OP_NODE_AI_BF, OP_NODE_MULTITAP, OP_NODE_PEQ_V2, OP_NODE_DYNAMIC_FILTER, OP_NODE_AI_ZIP,
                                      OP_NODE_AI_ZIP_DE, OP_NODE_SRC, OP_NODE_BD_SOUND],
    
    Target.AIROHA_AB1565_UART.value: [*FLOAT_POINT_AOS, OP_NODE_VISUALIZER, OP_NODE_DUMP, OP_NODE_CLIPFIX,
                                      OP_NODE_NTTS_IML, OP_NODE_NTTS_AGC, OP_NODE_UPHEAR_VIRT, OP_NODE_VEP, OP_NODE_AI_NR_48K, OP_NODE_DIRAC, OP_NODE_COHBF, OP_NODE_AI_ZIP,
                                      OP_NODE_AI_ZIP_DE, OP_NODE_SRC, OP_NODE_BD_SOUND],

    Target.FLOW_APO.value: [*FIXED_POINT_AOS, OP_NODE_VISUALIZER, OP_NODE_CLIPFIX, OP_NODE_NTTS_IML, OP_NODE_NTTS_AGC, OP_NODE_VEP,
                            OP_NODE_UPHEAR_VIRT, OP_NODE_AI_NR_48K, OP_NODE_VEP,OP_NODE_SRC],

    Target.FLOW_EVK_UART.value: [*NOT_SUPPORT_AO_IN_AIROHA, *FIXED_POINT_AOS, OP_NODE_VISUALIZER, OP_NODE_DUMP,
                                 OP_NODE_CLIPFIX, OP_NODE_NTTS_IML, OP_NODE_NTTS_AGC, OP_NODE_UPHEAR_VIRT, OP_NODE_AI_NR_48K, OP_NODE_VEP, OP_NODE_DIRAC, OP_NODE_CINGO, OP_NODE_CINGO_SPK, OP_NODE_UPHEAR_VQE, OP_NODE_COHBF,
                                 OP_NODE_AI_ZIP, OP_NODE_AI_ZIP_DE ,OP_NODE_SRC, OP_NODE_BD_SOUND],

    Target.GX8008C_USB.value: [*NOT_SUPPORT_AO_IN_AIROHA, *FIXED_POINT_AOS, OP_NODE_VISUALIZER, OP_NODE_DUMP,
                               OP_NODE_CLIPFIX, OP_NODE_NTTS_IML, OP_NODE_NTTS_AGC, OP_NODE_UPHEAR_VIRT, OP_NODE_AI_NR_48K, OP_NODE_VEP, OP_NODE_DIRAC, OP_NODE_CINGO, OP_NODE_CINGO_SPK, OP_NODE_UPHEAR_VQE, OP_NODE_COHBF,
                               OP_NODE_AI_ZIP, OP_NODE_AI_ZIP_DE, OP_NODE_SRC, OP_NODE_BD_SOUND]
}
