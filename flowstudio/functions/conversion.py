class Conversion(object):
    def str_to_binary(self, input_str):
        return ' '.join(format(ord(x), 'b') for x in input_str)

    def binary_to_str(self, input_binary):
        ls = input_binary.split(' ')
        instr = ''
        for x in ls:
            instr += chr(int(x, 2))
        return instr
