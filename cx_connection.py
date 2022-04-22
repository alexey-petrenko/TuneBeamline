import json
import pycx4.qcda as cda


class CXDataExchange:
    def __init__(self, config_file, *chan_types):
        super().__init__()
        config: dict = {}
        with open(config_file, "r") as f:
            config = json.load(f)

        for key in chan_types:
            if key not in config:
                print(f"{key} is absent in config file")
                return

        self.bpm_vals = {cname: 0.0 for name, cname in config['bpm'].items()}
        self.bpm_chans = {cname: cda.DChan(cname) for name, cname in config['bpm'].items()}
        for name, chans in self.bpm_chans.items():
            chans.valueMeasured.connect(self.upt_beam_coor)

        self.cor_vals = {cname: 0.0 for name, cname in config['cor'].items()}
        self.cor_chans = {cname: cda.DChan(cname) for name, cname in config['cor'].items()}
        for name, chans in self.cor_chans.items():
            chans.valueMeasured.connect(self.upt_cor_vals)

        print("exchange is ok")

    def upt_beam_coor(self, chan):
        self.bpm_vals[chan.name] = chan.val

    def upt_cor_vals(self, chan):
        self.cor_vals[chan.name] = chan.val

    def get_beam_coor(self):
        return self.bpm_vals

    def get_cor_vals(self):
        return self.cor_vals

    def set_cor_vals(self, vals):
        for cname in vals:
            self.cor_chans[cname].setValue(vals[cname])


# if __name__ == '__main__':
#     w = CXDataExchange('/home/vbalakin/PycharmProjects/accel_packages/TuneBeamline/cx_data_config.json', 'bpm', 'cor')
#     cda.main_loop()
