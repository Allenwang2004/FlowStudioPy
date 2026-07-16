from collections import OrderedDict

from flowstudio.controls.ControlValueShow import ControlValueShow
from flowstudio.controls.LabelToggle import LabelToggle
from flowstudio.controls.MultiTypeInput import MultiTypeInput
from flowstudio.flow_conf_list import AUDIO_OBJECT

# --------- Control I/O ---------
HW_IN = OrderedDict()
HW_OUT = OrderedDict()


# --------- Arithmetic ---------
ADD = OrderedDict()

CONSTANT = OrderedDict()
CONSTANT['constant'] = MultiTypeInput('Constant', 50)

MULTIPLY = OrderedDict()
INVERSE = OrderedDict()


# --------- Math Function ---------
POWER = OrderedDict()
POWER['exponent'] = MultiTypeInput('Exponent', 60)

SQRT = OrderedDict()
SQRT['radix'] = MultiTypeInput('Radix', 40)

LOG = OrderedDict()
LOG['base'] = MultiTypeInput('Base', 40)

EXP = OrderedDict()
EXP['base'] = MultiTypeInput('Base', 40)


# --------- Non Linear Processing ---------
CLAMP = OrderedDict()
CLAMP['Clamp'] = MultiTypeInput('Clamp Value', 70)
CLAMP['Toggle'] = LabelToggle('Min', 'Max',  25)

THRESHOLD = OrderedDict()
THRESHOLD['LevelHigh'] = MultiTypeInput('Level High', 60, True)
THRESHOLD['LevelLow'] = MultiTypeInput('Level Low', 60, True)
THRESHOLD['HysteresisMode'] = MultiTypeInput('Hysteresis Mode', 95, False)

LOOKUP_TABLE = OrderedDict()


# --------- Logical ---------
OR = OrderedDict()
AND = OrderedDict()
XOR = OrderedDict()
NOT = OrderedDict()


# --------- Misc ---------
DELAY = OrderedDict()
DELAY['n_frames'] = MultiTypeInput('N frames', 50, True)

METER = OrderedDict()
METER['value'] = ControlValueShow('Value:')


AUDIO_OBJECT['HW_IN'] = HW_IN
AUDIO_OBJECT['HW_OUT'] = HW_OUT

AUDIO_OBJECT['ADD'] = ADD
AUDIO_OBJECT['CONSTANT'] = CONSTANT
AUDIO_OBJECT['MULTIPLY'] = MULTIPLY
AUDIO_OBJECT['INVERSE'] = INVERSE

AUDIO_OBJECT['POWER'] = POWER
AUDIO_OBJECT['CO_SQRT'] = SQRT
AUDIO_OBJECT['LOG'] = LOG
AUDIO_OBJECT['EXP'] = EXP

AUDIO_OBJECT['CLAMP'] = CLAMP
AUDIO_OBJECT['THRESHOLD'] = THRESHOLD
AUDIO_OBJECT['LOOKUP_TABLE'] = LOOKUP_TABLE

AUDIO_OBJECT['OR'] = OR
AUDIO_OBJECT['AND'] = AND
AUDIO_OBJECT['XOR'] = XOR
AUDIO_OBJECT['NOT'] = NOT

AUDIO_OBJECT['CO_DELAY'] = DELAY
AUDIO_OBJECT['CO_METER'] = METER

