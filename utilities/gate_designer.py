import numpy as np
from flowstudio.flow_conf import Debug

COMPRESSOR = 0
LIMITER = 1
NOISEGATE = 2
CLIPPER = 3
EXPANDER = 4
FUSION = 5

def refresh(func):
    def dummy_function(instance, *args):
        func(instance, *args)
        instance.process()
    return dummy_function

class GATE_Designer(object):

    def __init__(self, model=LIMITER, threshold=-20, knee=0, maximum=20, minimum=-120, ratio=1):

        self._maximum = maximum
        self._minimum = minimum
        self._model = model
        self._threshold = threshold
        self._ratio = ratio
        self._knee = knee
        self._bypass = False

        self.input = None
        self.output = None

        if model == FUSION:
            self.knee = 0

        self.process()

    @property
    def model(self):
        return self._model

    @property
    def maximum(self):
        return self._maximum

    @property
    def minimum(self):
        return self._minimum

    @property
    def bypass(self):
        return self._bypass

    @bypass.setter
    @refresh
    def bypass(self, input_data):
        self._bypass = input_data

    @property
    def ratio(self):
        return self._ratio

    @ratio.setter
    @refresh
    def ratio(self, input_data):
        self._ratio = input_data

    @property
    def threshold(self):
        return self._threshold

    @threshold.setter
    @refresh
    def threshold(self, input_data):
        self._threshold = input_data

    @property
    def knee(self):
        return self._knee

    @knee.setter
    @refresh
    def knee(self, input_data):
        self._knee = input_data

    def process(self):
        if self.bypass:
            self.input = [self.minimum, self.maximum]
            self.output = [self.minimum, self.maximum]
            return

        # Xg - T < -W/2
        self.input = [self.minimum, self.threshold - self.knee / 2]
        self.output = [(self.minimum - self.threshold) * self.ratio + self.threshold, self.threshold - self.knee / 2]
        if Debug.DEBUG_COMMON.value:
            print('in ', self.input)
            print('out', self.output)
        # |Xg - T| <= W/2
        if not self.knee == 0:
            knee_space = np.linspace(self.threshold - self.knee / 2, self.threshold + self.knee / 2, num=10, endpoint=True)
            print('knee space', knee_space)
            for element in reversed(knee_space):
                res = ((1 - self.ratio) * (element - self.threshold - self.knee / 2) ** 2) / (self.knee * 2)
                # print('res:', res)
                self.input.insert(1, element)
                self.output.insert(1, element + res)
            self.input.pop()
            self.output.pop()
        if Debug.DEBUG_COMMON.value:
            print('in + knee ', self.input)
            print('out + knee', self.output)
        # # Xg - T > W/2
        self.input.append(self.maximum)
        self.output.append(self.maximum)



    def location(self, input):
        THcondition = 2.0 * (input - self.threshold)
        if THcondition >= self.knee:
            output = input
            return output

        elif THcondition <= self.knee and THcondition >= -self.knee:
            output = input + ((1 - self.ratio) * (input - self.threshold - self.knee / 2) ** 2) / (self.knee * 2 + 0.0000001)
            return output

        elif THcondition < -self.knee:
            output = (input - self.threshold) * self.ratio + self.threshold

            return output

    def input_index(self, x):
        for element in self.input:
            if element > x:
                index = self.input.index(element)
                return index