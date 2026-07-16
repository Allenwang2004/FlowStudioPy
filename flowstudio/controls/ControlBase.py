class ControlBase(object):
    required_parameters = []

    @classmethod
    def get_keys_from_required_parameters(cls):
        return [param['key'] for param in cls.required_parameters]
