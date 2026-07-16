import enum
from flowstudio.flow_conf import register_node_now

@enum.unique
class SocketType(enum.Enum):
    BOOL = 7
    INT = 8
    FLOAT = 9
    STRING = 10

def register_node_co(op_code):
    def decorator(original_class):
        register_node_now(op_code, original_class)
        return original_class

    return decorator


# --------- Control I/O ---------
OP_NODE_CO_HW_IN = 10001
OP_NODE_CO_HW_OUT = 10002

# --------- Arithmetic ---------
OP_NODE_CO_CONSTANT = 10003
OP_NODE_CO_ADD = 10004
OP_NODE_CO_MULTIPLY = 10005
OP_NODE_CO_INVERSE = 10006

# --------- Math Function ---------
OP_NODE_CO_POWER = 10007
OP_NODE_CO_SQRT = 10008
OP_NODE_CO_LOG = 10009
OP_NODE_CO_EXP = 10010

# --------- Non Linear Processing ---------
OP_NODE_CO_CLAMP = 10011
OP_NODE_CO_THRESHOLD = 10016
OP_NODE_CO_LOOKUP_TABLE = 10017

# --------- Logical ---------
OP_NODE_CO_OR = 10012
OP_NODE_CO_AND = 10013
OP_NODE_CO_XOR = 10014
OP_NODE_CO_NOT = 10015

# --------- Misc ---------
OP_NODE_CO_DELAY = 10018
OP_NODE_CO_METER = 10019

from flowstudio.nodes.control import HW_IN, HW_OUT
from flowstudio.nodes.control import ADD, CONSTANT, MULTIPLY, INVERSE
from flowstudio.nodes.control import POWER, SQRT, LOG, EXP
from flowstudio.nodes.control import CLAMP, THRESHOLD, LOOKUP_TABLE
from flowstudio.nodes.control import OR, AND, XOR,NOT
from flowstudio.nodes.control import DELAY, METER

CATE_CONTROL_MAPPING = {
    'Control I/O': [OP_NODE_CO_HW_IN, OP_NODE_CO_HW_OUT],
    'Arithmetic': [OP_NODE_CO_CONSTANT, OP_NODE_CO_ADD, OP_NODE_CO_MULTIPLY, OP_NODE_CO_INVERSE],
    'Math Function': [OP_NODE_CO_POWER, OP_NODE_CO_SQRT, OP_NODE_CO_LOG, OP_NODE_CO_EXP],
    'Non Linear Processing': [OP_NODE_CO_CLAMP, OP_NODE_CO_THRESHOLD, OP_NODE_CO_LOOKUP_TABLE],
    'Logical': [OP_NODE_CO_OR, OP_NODE_CO_AND, OP_NODE_CO_XOR, OP_NODE_CO_NOT],
    'Misc': [OP_NODE_CO_DELAY, OP_NODE_CO_METER],
}

NOT_SUPPORT_COS = [
    OP_NODE_CO_INVERSE, OP_NODE_CO_POWER, OP_NODE_CO_SQRT, OP_NODE_CO_LOG, OP_NODE_CO_EXP, OP_NODE_CO_CLAMP,
    OP_NODE_CO_THRESHOLD, OP_NODE_CO_LOOKUP_TABLE, OP_NODE_CO_DELAY
]
