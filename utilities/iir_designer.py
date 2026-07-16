import math
import numpy as np
import scipy.signal

from flowstudio.flow_conf import OP_NODE_PEQ_V2

EULER = np.exp(1)

LOWPASS1 = 0
LOWPASS2 = 1
HIGHPASS1 = 2
HIGHPASS2 = 3
ALLPASS1 = 4
ALLPASS2 = 5
PEAKING = 6
PARAMETRIC = 7
BANDPASS = 8
NOTCH = 9
LOWSHELF = 10
HIGHSHELF = 11
FLAT = 12

def refresh(func):
    def dummy_function(instance, *args):
        func(instance, *args)
        instance.process()
    return dummy_function

class IIR_Designer(object):

    def __init__(self, filter_type: int = LOWPASS1, frequency_cut: float = 1200, sample_rate: float = 44100,
                 Q: float = 0.707, slope: float = 0.1, magnitude: float = 0, gain: float = 0, op_code: int = 0):

        self._filter_type = filter_type
        self._freq = frequency_cut
        self._sr = sample_rate
        self._q = Q
        self._slope = slope
        self._magnitude = magnitude
        self._gain = gain
        self._op_code = op_code

        self._bypass = False

        self._coef = None
        self._w = None
        self._h = None

        self.initCoef()
        self.process()

    def initCoef(self):
        self.a0, self.a1, self.a2, self.b0, self.b1, self.b2 = 0, 0, 0, 0, 0, 0

    @property
    def bypass(self):
        return self._bypass

    @bypass.setter
    @refresh
    def bypass(self, input_data):
        self._bypass = input_data

    @property
    def omega(self):
        return 2 * math.pi * self.freq / self.sr

    @property
    def boost(self):
        return pow(10, (self.magnitude / 20))

    @property
    def sineOmega(self):
        return np.sin(self.omega)

    @property
    def cosineOmega(self):
        return np.cos(self.omega)

    @property
    def filter_type(self):
        return self._filter_type

    @filter_type.setter
    @refresh
    def filter_type(self, input_data):
        self._filter_type = input_data

    @property
    def freq(self):
        return self._freq

    @freq.setter
    @refresh
    def freq(self, input_data):
        self._freq = input_data

    @property
    def sr(self):
        return self._sr

    @property
    def gain(self):
        return pow(10, (self._gain / 20))

    @gain.setter
    @refresh
    def gain(self, input_data):
        self._gain = input_data

    @sr.setter
    @refresh
    def sr(self, input_data):
        self._sr = input_data

    @property
    def q(self):
        return self._q

    @q.setter
    @refresh
    def q(self, input_data):
        self._q = input_data

    @property
    def slope(self):
        return self._slope

    @slope.setter
    @refresh
    def slope(self, input_data):
        # slope should be in the range 0 < slope <= 2
        if input_data >= 2.0:
            self._slope = 2.0
        elif input_data <= 0.1:
            self._slope = 0.1
        else:
            self._slope = input_data

    @property
    def magnitude(self):
        return self._magnitude

    @magnitude.setter
    @refresh
    def magnitude(self, input_data):
        self._magnitude = input_data

    @property
    def op_code(self):
        return self._op_code

    @op_code.setter
    @refresh
    def op_code(self, input_data):
        self._op_code = input_data

    def process(self):

        filter_type = self.filter_type

        if filter_type == FLAT and not self.bypass:
            self.b0 = 1.0
            self.b1 = 0.0
            self.b2 = 0.0

            self.a1 = 0.0
            self.a2 = 0.0

        elif filter_type == LOWPASS1 and not self.bypass:
            self.a1 = pow(EULER, -self.omega)

            self.b0 = (1.0 - self.a1) * self.gain
            self.b1 = 0.0
            self.b2 = 0.0

            self.a1 = -self.a1
            self.a2 = 0.0

        elif filter_type == HIGHPASS1 and not self.bypass:
            self.a1 = pow(EULER, -self.omega)

            self.b0 = (1.0 + self.a1) * self.gain / 2
            self.b1 = -(1.0 + self.a1) * self.gain / 2
            self.b2 = 0.0

            self.a1 = -self.a1
            self.a2 = 0.0

        elif filter_type == ALLPASS1 and not self.bypass:
            self.a1 = pow(EULER, -self.omega)

            self.b0 = -self.a1 * self.gain
            self.b1 = self.gain
            self.b2 = 0.0

            self.a1 = -self.a1
            self.a2 = 0.0

        elif filter_type == LOWPASS2 and not self.bypass:
            alpha = self.sineOmega / (2 * self.q)

            self.a0 = 1 + alpha
            self.a1 = (-2 * self.cosineOmega) / self.a0
            self.a2 = (1 - alpha) / self.a0

            self.b0 = (1 - self.cosineOmega) * self.gain / 2 / self.a0
            self.b1 = (1 - self.cosineOmega) * self.gain / self.a0
            self.b2 = (1 - self.cosineOmega) * self.gain / 2 / self.a0

        elif filter_type == HIGHPASS2 and not self.bypass:
            alpha = self.sineOmega / (2 * self.q)

            self.a0 = 1 + alpha
            self.a1 = (-2 * self.cosineOmega) / self.a0
            self.a2 = (1 - alpha) / self.a0

            self.b0 = (1 + self.cosineOmega) * self.gain / 2 / self.a0
            self.b1 = -(1 + self.cosineOmega) * self.gain / self.a0
            self.b2 = (1 + self.cosineOmega) * self.gain / 2 / self.a0

        elif filter_type == ALLPASS2 and not self.bypass:
            alpha = self.sineOmega / (2 * self.q)

            self.a0 = 1 + alpha
            self.a1 = (-2 * self.cosineOmega) / self.a0
            self.a2 = (1 - alpha) / self.a0

            self.b0 = (1 - alpha) * self.gain / self.a0
            self.b1 = (-2 * self.cosineOmega) * self.gain / self.a0
            self.b2 = (1 + alpha) * self.gain / self.a0

        elif filter_type == PARAMETRIC and not self.bypass:
            A = pow(10.0, (self.magnitude / 40.0))
            alpha = self.sineOmega / (2 * A * self.q)

            self.a0 = 1 + alpha / A
            self.a1 = (-2 * self.cosineOmega) / self.a0
            self.a2 = (1 - alpha / A) / self.a0

            self.b0 = (1 + alpha * A) / self.a0
            self.b1 = -(2 * self.cosineOmega) / self.a0
            self.b2 = (1 - alpha * A) / self.a0

        elif filter_type == PEAKING and not self.bypass:
            A = pow(10.0, (self.magnitude / 40.0))
            alpha = self.sineOmega / (2 * self.q)

            self.a0 = 1 + alpha / A
            self.a1 = (-2 * self.cosineOmega) / self.a0
            self.a2 = (1 - alpha / A) / self.a0

            self.b0 = (1 + alpha * A) / self.a0
            self.b1 = -(2 * self.cosineOmega) / self.a0
            self.b2 = (1 - alpha * A) / self.a0

        elif filter_type == BANDPASS and not self.bypass:
            alpha = self.sineOmega / (2 * self.q)

            self.a0 = 1 + alpha
            self.a1 = (-2.0 * self.cosineOmega) / self.a0
            self.a2 = (1 - alpha) / self.a0

            self.b0 = (alpha * self.gain) / self.a0
            self.b1 = 0.0
            self.b2 = -(alpha * self.gain) / self.a0

        elif filter_type == NOTCH and not self.bypass:
            alpha = self.sineOmega / (2 * self.q)

            self.a0 = 1 + alpha
            self.a1 = (-2.0 * self.cosineOmega) / self.a0
            self.a2 = (1.0 - alpha) / self.a0

            self.b0 = self.gain / self.a0
            self.b1 = (-2.0 * self.cosineOmega * self.gain) / self.a0
            self.b2 = self.gain / self.a0

        elif filter_type == LOWSHELF and not self.bypass:
            A = pow(10.0, (self.magnitude / 40.0))
            if self.op_code == OP_NODE_PEQ_V2:
                alpha = self.sineOmega / (2 * self.q)
            else:
                alpha = (self.sineOmega / 2) * (np.sqrt((A + 1 / A) * (1 / self.slope - 1) + 2))

            self.a0 = (A + 1) + (A - 1) * self.cosineOmega + 2 * np.sqrt(A) * alpha
            self.a1 = (-2 * ((A - 1) + (A + 1) * self.cosineOmega)) / self.a0
            self.a2 = ((A + 1) + (A - 1) * self.cosineOmega - 2 * np.sqrt(A) * alpha) / self.a0

            self.b0 = (A * ((A + 1) - (A - 1) * self.cosineOmega + 2 * np.sqrt(A) * alpha)) / self.a0
            self.b1 = (2 * A * ((A - 1) - (A + 1) * self.cosineOmega)) / self.a0
            self.b2 = (A * ((A + 1) - (A - 1) * self.cosineOmega - 2 * np.sqrt(A) * alpha)) / self.a0

        elif filter_type == HIGHSHELF and not self.bypass:
            A = pow(10.0, (self.magnitude / 40.0))
            if self.op_code == OP_NODE_PEQ_V2:
                alpha = self.sineOmega / (2 * self.q)
            else:
                alpha = (self.sineOmega / 2) * (np.sqrt((A + 1 / A) * (1 / self.slope - 1) + 2))

            self.a0 = (A + 1) - (A - 1) * self.cosineOmega + 2 * np.sqrt(A) * alpha
            self.a1 = (2 * ((A - 1) - (A + 1) * self.cosineOmega)) / self.a0
            self.a2 = ((A + 1) - (A - 1) * self.cosineOmega - 2 * np.sqrt(A) * alpha) / self.a0

            self.b0 = (A * ((A + 1) + (A - 1) * self.cosineOmega + 2 * np.sqrt(A) * alpha)) / self.a0
            self.b1 = (-2 * A * ((A - 1) + (A + 1) * self.cosineOmega)) / self.a0
            self.b2 = (A * ((A + 1) + (A - 1) * self.cosineOmega - 2 * np.sqrt(A) * alpha)) / self.a0

        else:
            self.b0 = 1.0
            self.b1 = 0.0
            self.b2 = 0.0

            self.a1 = 0.0
            self.a2 = 0.0

        numerator = self.coef['b']
        denominator = self.coef['a']
        self._w, self._h = scipy.signal.freqz(numerator, denominator, worN=np.logspace(1, np.log(22000) / np.log(20), num=1024, base=20),whole=False, fs=44100)

    @property
    def coef(self):
        self.a0 = 1.0
        self._coef = {'a': [], 'b': []}
        self._coef['b'] = [self.b0, self.b1, self.b2]
        self._coef['a'] = [self.a0, self.a1, self.a2]
        return self._coef

    @property
    def w(self):
        return self._w

    @property
    def h(self):
        return self._h
