from utilities.iir_designer import *

LOW = 0
HIGH = 1

Butterworth6 = 0
Butterworth12 = 1
Butterworth18 = 2
Butterworth24 = 3
Butterworth30 = 4
Butterworth36 = 5
Bessel6 = 6
Bessel12 = 7
Bessel18 = 8
Bessel24 = 9
Bessel30 = 10
Bessel36 = 11
LR12 = 12
LR24 = 13
LR36 = 14
LR48 = 15

def refresh(func):
    def dummy_function(instance, *args):
        func(instance, *args)
        instance.process()
    return dummy_function

class Crossover_Designer(object):

    def __init__(self, frequency_cut: float = 1200, filter_topology = Butterworth6, filter_type = LOW):
        self.master = []

        self._freq = frequency_cut
        self._filter_topology = filter_topology
        self._filter_type = filter_type

        for index in range(4):
            self.master.append(IIR_Designer())

        self.process()

    @property
    def freq(self):
        return self._freq

    @freq.setter
    @refresh
    def freq(self, input_data):
        self._freq = input_data

    @property
    def filter_topology(self):
        return self._filter_topology

    @filter_topology.setter
    @refresh
    def filter_topology(self, input_data):
        self._filter_topology = input_data

    @property
    def filter_type(self):
        return self._filter_type

    @filter_type.setter
    @refresh
    def filter_type(self, input_data):
        self._filter_type = input_data

    @property
    def bypass(self):
        return [self.master[0].bypass, self.master[1].bypass, self.master[2].bypass, self.master[3].bypass]

    @bypass.setter
    def bypass(self, input_data):
        for index in range(4):
            self.master[index].bypass = input_data

    def process(self):

        filter_topology = self.filter_topology
        filter_type = self.filter_type

        if filter_topology == Butterworth6:
            self.Butterworth_6(filter_type)
        elif filter_topology == Butterworth12:
            self.Butterworth_12(filter_type)
        elif filter_topology == Butterworth18:
            self.Butterworth_18(filter_type)
        elif filter_topology == Butterworth24:
            self.Butterworth_24(filter_type)
        elif filter_topology == Butterworth30:
            self.Butterworth_30(filter_type)
        elif filter_topology == Butterworth36:
            self.Butterworth_36(filter_type)
        elif filter_topology == Bessel6:
            self.Bessel_6(filter_type)
        elif filter_topology == Bessel12:
            self.Bessel_12(filter_type)
        elif filter_topology == Bessel18:
            self.Bessel_18(filter_type)
        elif filter_topology == Bessel24:
            self.Bessel_24(filter_type)
        elif filter_topology == Bessel30:
            self.Bessel_30(filter_type)
        elif filter_topology == Bessel36:
            self.Bessel_36(filter_type)
        elif filter_topology == LR12:
            self.LinkwitzRiley_12(filter_type)
        elif filter_topology == LR24:
            self.LinkwitzRiley_24(filter_type)
        elif filter_topology == LR36:
            self.LinkwitzRiley_36(filter_type)
        elif filter_topology == LR48:
            self.LinkwitzRiley_48(filter_type)
        else:
            return

    def Butterworth_6(self, filter_type):
        if filter_type == LOW:
            target = LOWPASS1
        elif filter_type == HIGH:
            target = HIGHPASS1
        else:
            return

        self.master[0].filter_type = target
        self.master[1].filter_type = FLAT
        self.master[2].filter_type = FLAT
        self.master[3].filter_type = FLAT

        self.master[0].q = 0.707
        self.master[1].q = 0.707
        self.master[2].q = 0.707
        self.master[3].q = 0.707

        self.master[0].freq = self.freq
        self.master[1].freq = self.freq
        self.master[2].freq = self.freq
        self.master[3].freq = self.freq

    def Butterworth_12(self, filter_type):
        if filter_type == LOW:
            target = LOWPASS2
        elif filter_type == HIGH:
            target = HIGHPASS2
        else:
            return

        self.master[0].filter_type = target
        self.master[1].filter_type = FLAT
        self.master[2].filter_type = FLAT
        self.master[3].filter_type = FLAT

        self.master[0].q = 0.707
        self.master[1].q = 0.707
        self.master[2].q = 0.707
        self.master[3].q = 0.707

        self.master[0].freq = self.freq
        self.master[1].freq = self.freq
        self.master[2].freq = self.freq
        self.master[3].freq = self.freq

    def Butterworth_18(self, filter_type):
        if filter_type == LOW:
            target1 = LOWPASS1
            target2 = LOWPASS2
        elif filter_type == HIGH:
            target1 = HIGHPASS1
            target2 = HIGHPASS2
        else:
            return

        self.master[0].filter_type = target1
        self.master[1].filter_type = target2
        self.master[2].filter_type = FLAT
        self.master[3].filter_type = FLAT

        self.master[0].q = 0.707
        self.master[1].q = 1
        self.master[2].q = 0.707
        self.master[3].q = 0.707

        self.master[0].freq = self.freq
        self.master[1].freq = self.freq
        self.master[2].freq = self.freq
        self.master[3].freq = self.freq

    def Butterworth_24(self, filter_type):
        if filter_type == LOW:
            target1 = LOWPASS2
            target2 = LOWPASS2
        elif filter_type == HIGH:
            target1 = HIGHPASS2
            target2 = HIGHPASS2
        else:
            return

        self.master[0].filter_type = target1
        self.master[1].filter_type = target2
        self.master[2].filter_type = FLAT
        self.master[3].filter_type = FLAT

        self.master[0].q = 0.54
        self.master[1].q = 1.31
        self.master[2].q = 0.707
        self.master[3].q = 0.707

        self.master[0].freq = self.freq
        self.master[1].freq = self.freq
        self.master[2].freq = self.freq
        self.master[3].freq = self.freq

    def Butterworth_30(self, filter_type):
        if filter_type == LOW:
            target1 = LOWPASS1
            target2 = LOWPASS2
            target3 = LOWPASS2
        elif filter_type == HIGH:
            target1 = HIGHPASS1
            target2 = HIGHPASS2
            target3 = HIGHPASS2
        else:
            return

        self.master[0].filter_type = target1
        self.master[1].filter_type = target2
        self.master[2].filter_type = target3
        self.master[3].filter_type = FLAT

        self.master[0].q = 0.707
        self.master[1].q = 0.62
        self.master[2].q = 1.62
        self.master[3].q = 0.707

        self.master[0].freq = self.freq
        self.master[1].freq = self.freq
        self.master[2].freq = self.freq
        self.master[3].freq = self.freq

    def Butterworth_36(self, filter_type):
        if filter_type == LOW:
            target1 = LOWPASS2
            target2 = LOWPASS2
            target3 = LOWPASS2
        elif filter_type == HIGH:
            target1 = HIGHPASS2
            target2 = HIGHPASS2
            target3 = HIGHPASS2
        else:
            return

        self.master[0].filter_type = target1
        self.master[1].filter_type = target2
        self.master[2].filter_type = target3
        self.master[3].filter_type = FLAT

        self.master[0].q = 0.52
        self.master[1].q = 0.71
        self.master[2].q = 1.93
        self.master[3].q = 0.707

        self.master[0].freq = self.freq
        self.master[1].freq = self.freq
        self.master[2].freq = self.freq
        self.master[3].freq = self.freq

    def Bessel_6(self, filter_type):
        if filter_type == LOW:
            target1 = LOWPASS1
        elif filter_type == HIGH:
            target1 = HIGHPASS1
        else:
            return

        self.master[0].filter_type = target1
        self.master[1].filter_type = FLAT
        self.master[2].filter_type = FLAT
        self.master[3].filter_type = FLAT

        self.master[0].q = 0.707
        self.master[1].q = 0.707
        self.master[2].q = 0.707
        self.master[3].q = 0.707

        self.master[0].freq = self.freq
        self.master[1].freq = self.freq
        self.master[2].freq = self.freq
        self.master[3].freq = self.freq

    def Bessel_12(self, filter_type):
        if filter_type == LOW:
            target1 = LOWPASS2
        elif filter_type == HIGH:
            target1 = HIGHPASS2
        else:
            return

        self.master[0].filter_type = target1
        self.master[1].filter_type = FLAT
        self.master[2].filter_type = FLAT
        self.master[3].filter_type = FLAT

        self.master[0].q = 0.58
        self.master[1].q = 0.707
        self.master[2].q = 0.707
        self.master[3].q = 0.707

        self.master[0].freq = self.freq
        self.master[1].freq = self.freq * 1.27
        self.master[2].freq = self.freq
        self.master[3].freq = self.freq

    def Bessel_18(self, filter_type):
        if filter_type == LOW:
            target1 = LOWPASS1
            target2 = LOWPASS2
        elif filter_type == HIGH:
            target1 = HIGHPASS1
            target2 = HIGHPASS2
        else:
            return

        self.master[0].filter_type = target1
        self.master[1].filter_type = target2
        self.master[2].filter_type = FLAT
        self.master[3].filter_type = FLAT

        self.master[0].q = 0.707
        self.master[1].q = 0.69
        self.master[2].q = 0.707
        self.master[3].q = 0.707

        self.master[0].freq = self.freq * 1.32
        self.master[1].freq = self.freq * 1.45
        self.master[2].freq = self.freq
        self.master[3].freq = self.freq

    def Bessel_24(self, filter_type):
        if filter_type == LOW:
            target1 = LOWPASS2
            target2 = LOWPASS2
        elif filter_type == HIGH:
            target1 = HIGHPASS2
            target2 = HIGHPASS2
        else:
            return

        self.master[0].filter_type = target1
        self.master[1].filter_type = target2
        self.master[2].filter_type = FLAT
        self.master[3].filter_type = FLAT

        self.master[0].q = 0.81
        self.master[1].q = 0.52
        self.master[2].q = 0.707
        self.master[3].q = 0.707

        self.master[0].freq = self.freq * 1.60
        self.master[1].freq = self.freq * 1.43
        self.master[2].freq = self.freq
        self.master[3].freq = self.freq

    def Bessel_30(self, filter_type):
        if filter_type == LOW:
            target1 = LOWPASS1
            target2 = LOWPASS2
            target3 = LOWPASS2
        elif filter_type == HIGH:
            target1 = HIGHPASS1
            target2 = HIGHPASS2
            target3 = HIGHPASS2
        else:
            return

        self.master[0].filter_type = target1
        self.master[1].filter_type = target2
        self.master[2].filter_type = target3
        self.master[3].filter_type = FLAT

        self.master[0].q = 0.707
        self.master[1].q = 0.92
        self.master[2].q = 0.56
        self.master[3].q = 0.707

        self.master[0].freq = self.freq * 1.50
        self.master[1].freq = self.freq * 1.76
        self.master[2].freq = self.freq * 1.56
        self.master[3].freq = self.freq

    def Bessel_36(self, filter_type):
        if filter_type == LOW:
            target1 = LOWPASS2
            target2 = LOWPASS2
            target3 = LOWPASS2
        elif filter_type == HIGH:
            target1 = HIGHPASS2
            target2 = HIGHPASS2
            target3 = HIGHPASS2
        else:
            return

        self.master[0].filter_type = target1
        self.master[1].filter_type = target2
        self.master[2].filter_type = target3
        self.master[3].filter_type = FLAT

        self.master[0].q = 1.02
        self.master[1].q = 0.61
        self.master[2].q = 0.51
        self.master[3].q = 0.707

        self.master[0].freq = self.freq * 1.90
        self.master[1].freq = self.freq * 1.69
        self.master[2].freq = self.freq * 1.6
        self.master[3].freq = self.freq

    def LinkwitzRiley_12(self, filter_type):
        if filter_type == LOW:
            target1 = LOWPASS2
        elif filter_type == HIGH:
            target1 = HIGHPASS2
        else:
            return

        self.master[0].filter_type = target1
        self.master[1].filter_type = FLAT
        self.master[2].filter_type = FLAT
        self.master[3].filter_type = FLAT

        self.master[0].q = 0.5
        self.master[1].q = 0.707
        self.master[2].q = 0.707
        self.master[3].q = 0.707

        self.master[0].freq = self.freq
        self.master[1].freq = self.freq
        self.master[2].freq = self.freq
        self.master[3].freq = self.freq

    def LinkwitzRiley_24(self, filter_type):
        if filter_type == LOW:
            target1 = LOWPASS2
            target2 = LOWPASS2
        elif filter_type == HIGH:
            target1 = HIGHPASS2
            target2 = HIGHPASS2
        else:
            return

        self.master[0].filter_type = target1
        self.master[1].filter_type = target2
        self.master[2].filter_type = FLAT
        self.master[3].filter_type = FLAT

        self.master[0].q = 0.71
        self.master[1].q = 0.71
        self.master[2].q = 0.707
        self.master[3].q = 0.707

        self.master[0].freq = self.freq
        self.master[1].freq = self.freq
        self.master[2].freq = self.freq
        self.master[3].freq = self.freq

    def LinkwitzRiley_36(self, filter_type):
        if filter_type == LOW:
            target1 = LOWPASS2
            target2 = LOWPASS2
            target3 = LOWPASS2
        elif filter_type == HIGH:
            target1 = HIGHPASS2
            target2 = HIGHPASS2
            target3 = HIGHPASS2
        else:
            return

        self.master[0].filter_type = target1
        self.master[1].filter_type = target2
        self.master[2].filter_type = target3
        self.master[3].filter_type = FLAT

        self.master[0].q = 0.5
        self.master[1].q = 1
        self.master[2].q = 1
        self.master[3].q = 0.707

        self.master[0].freq = self.freq
        self.master[1].freq = self.freq
        self.master[2].freq = self.freq
        self.master[3].freq = self.freq

    def LinkwitzRiley_48(self, filter_type):
        if filter_type == LOW:
            target1 = LOWPASS2
            target2 = LOWPASS2
            target3 = LOWPASS2
            target4 = LOWPASS2
        elif filter_type == HIGH:
            target1 = HIGHPASS2
            target2 = HIGHPASS2
            target3 = HIGHPASS2
            target4 = HIGHPASS2
        else:
            return

        self.master[0].filter_type = target1
        self.master[1].filter_type = target2
        self.master[2].filter_type = target3
        self.master[3].filter_type = target4

        self.master[0].q = 0.54
        self.master[1].q = 1.34
        self.master[2].q = 0.5
        self.master[3].q = 1.34

        self.master[0].freq = self.freq
        self.master[1].freq = self.freq
        self.master[2].freq = self.freq
        self.master[3].freq = self.freq

    @property
    def w(self):
        return self.master[0].w, self.master[1].w, self.master[2].w, self.master[3].w

    @property
    def h(self):
        return self.master[0].h, self.master[1].h, self.master[2].h, self.master[3].h
