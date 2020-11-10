class ModFn(object):
    def __init__(self, func, *args, **kwargs):
        self.func = func
        self.args = args
        self.kwargs = kwargs

    def __call__(self, simulation):
        md = self.func(simulation, *self.args, **self.kwargs)

        # Make sure we cast numpy types into normal system types
        for k, v in md.items():
            import numpy as np
            if isinstance(v, (np.int64, np.float64, np.float32, np.uint32, np.int16, np.int32)):
                md[k] = v.item()

        return md
