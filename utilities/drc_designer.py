import numpy as np

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

class DRC_Designer(object):

    def __init__(self, model=LIMITER, threshold=-20, knee=24, maximum=40, minimum=-160, ratio=4, noisegate=-160, threshold_2=-90, ratio_2=1, ratio_3=1, makeup=0):

        self._maximum = maximum
        self._minimum = minimum
        self._model = model
        self._threshold = threshold
        self._threshold_2 = threshold_2
        self._ratio = ratio
        self._ratio_2 = ratio_2
        self._ratio_3 = ratio_3
        self._knee = knee
        self._noisegate = noisegate
        self._makeup = makeup
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
    def ratio_2(self):
        return self._ratio_2

    @ratio_2.setter
    @refresh
    def ratio_2(self, input_data):
        self._ratio_2 = input_data

    @property
    def ratio_3(self):
        return self._ratio_3

    @ratio_3.setter
    @refresh
    def ratio_3(self, input_data):
        self._ratio_3 = input_data

    @property
    def threshold(self):
        return self._threshold

    @threshold.setter
    @refresh
    def threshold(self, input_data):
        self._threshold = input_data

    @property
    def threshold_2(self):
        return self._threshold_2

    @threshold_2.setter
    @refresh
    def threshold_2(self, input_data):
        self._threshold_2 = input_data

    @property
    def noisegate(self):
        return self._noisegate

    @noisegate.setter
    @refresh
    def noisegate(self, input_data):
        self._noisegate = input_data

    @property
    def knee(self):
        return self._knee

    @knee.setter
    @refresh
    def knee(self, input_data):
        self._knee = input_data

    @property
    def makeup(self):
        return self._makeup
    @makeup.setter
    @refresh
    def makeup(self, input_data):
        self._makeup = input_data

    def process(self):
        if self.bypass:
            self.input = [self.minimum, self.maximum]
            self.output = [self.minimum, self.maximum]
            return

        # Xg - T < -W/2
        if self.model == FUSION:
            self.input = [self.noisegate, self.noisegate]
            self.output = [-160, self.noisegate]
        else:
            self.input = [self.minimum, self.threshold - self.knee / 2]
            self.output = [self.minimum, self.threshold - self.knee / 2]

        # |Xg - T| <= W/2
        if not self.knee == 0:
            knee_space = np.linspace(self.threshold - self.knee / 2, self.threshold + self.knee / 2, num=10, endpoint=True)
            if self.model == LIMITER:
                for element in reversed(knee_space):
                    res = ((element - self.threshold + self.knee / 2) ** 2) / (self.knee * 2)
                    self.input.insert(2, element)
                    self.output.insert(2, element - res)
            elif self.model == COMPRESSOR:
                for element in reversed(knee_space):
                    res = ((1 / self.ratio - 1) * (element - self.threshold + self.knee / 2) ** 2) / (self.knee * 2)
                    self.input.insert(2, element)
                    self.output.insert(2, element + res)

        # Xg - T > W/2
        if self.model == LIMITER:
            self.input.append(self.maximum)
            self.output.append(self.threshold)
        elif self.model == COMPRESSOR:
            self.input.append(self.maximum)
            self.output.append((self.maximum - self.threshold) / self.ratio + self.threshold)
        elif self.model == FUSION:

            x0 = self.threshold
            y0 = (self.threshold - self.noisegate) / self.ratio + self.noisegate
            self.input.append(x0)
            self.output.append(y0)

            x1 = self.threshold_2
            y1 = (self.threshold_2 - self.threshold) / self.ratio_2 + (self.threshold - self.noisegate) / self.ratio + self.noisegate
            self.input.append(x1)
            self.output.append(y1)

            x2 = self.maximum
            y2 = (self.maximum - self.threshold_2) / self.ratio_3 + (self.threshold_2 - self.threshold) / self.ratio_2 + (self.threshold - self.noisegate) / self.ratio + self.noisegate
            self.input.append(x2)
            self.output.append(y2)

        # offset output with makeup
        for i in range(len(self.output)):
            self.output[i] = self.output[i] + self.makeup

    def location(self, input):
        if self.model == FUSION:
            if input - self.noisegate < 0:
                output = self.minimum

            elif self.noisegate <= input < self.threshold:
                output = (input - self.noisegate) / self.ratio + self.noisegate

            elif self.threshold <= input < self.threshold_2:
                output = (input - self.threshold) / self.ratio_2 + (self.threshold - self.noisegate) / self.ratio + self.noisegate

            elif self.threshold <= input < self.maximum:
                output = (input - self.threshold_2) / self.ratio_3 + (self.threshold_2 - self.threshold) / self.ratio_2 + (self.threshold - self.noisegate) / self.ratio + self.noisegate


        else:
            if input - self.threshold < -self.knee/2:
                output = input

            elif abs(input - self.threshold) <= self.knee/2:
                if self.model == LIMITER:
                    output = input - (input - self.threshold + self.knee / 2) ** 2 / (2*self.knee + 0.0000001)

                elif self.model == COMPRESSOR:
                    output = input + ((1 / self.ratio - 1) * (input - self.threshold + self.knee / 2) ** 2) / (self.knee * 2  + 0.0000001)


            elif input - self.threshold > self.knee/2:
                if self.model == LIMITER:
                    output = self.threshold

                elif self.model == COMPRESSOR:
                    output = (input - self.threshold) / self.ratio + self.threshold

        return output + self.makeup
    def input_index(self, x):
        for element in self.input:
            if element > x:
                index = self.input.index(element)
                return index