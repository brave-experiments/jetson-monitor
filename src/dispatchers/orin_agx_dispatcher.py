import glob
import os


class OrinAGXDispatcher:

    units = {
        'temp': 'mC',
        'voltage': 'mV',
        'power': 'mW',
        'current': 'mA',
        'freq': 'Hz'
    }

    def __init__(self, dummy=False):
        self.file_associations = {
            'voltage': '/sys/bus/i2c/drivers/ina3221/1-004?/hwmon/hwmon?/in?_input',
            'current': '/sys/bus/i2c/drivers/ina3221/1-004?/hwmon/hwmon?/curr?_input',
            'temps': '/sys/devices/virtual/thermal/thermal_zone*',
        }

        if dummy:
            for k in self.file_associations.keys():
                self.file_associations[k] = f'../dummy_files/orin_nano/{self.file_associations[k]}'

    def get_power_figs(self, metrics, subsystems=['all']):
        ret = {}
        # 2 hwmons x 3 rails
        #   - 0.1 VDD_GPU_SOC: GPU
        #   - 0.2 VDD_CPU_CV: CPU
        #   - 0.3 VIN_SYS_5V0: SoC
        #   - 1.1 NC: CV cores
        #   - 1.2 VDDQ_VDD2_1V8AO: DDR
        #   - 1.3 NC: IO

        related_files = sorted(glob.glob(self.file_associations['voltage'].replace('?', '*')))
        abs_path_prefix = '/' if related_files[0].startswith('/') else ''
        files = [p.split('/') for p in related_files]
        path_prefix = '/'.join(files[0][:-4])
        channel_hwmons = list({'_'.join((f[-4], f[-2])) for f in files})

        for ch_hw in channel_hwmons:
            ch, hw = ch_hw.split('_')
            ch_hw_path = f"{ch}/hwmon/{hw}"
            for idx in range(1, 4):
                name = ''
                voltage = ''
                current = ''
                curr_path_suffix = os.path.split(
                    self.file_associations['current'])[-1].replace('?', str(idx))
                volt_path_suffix = os.path.split(
                    self.file_associations['voltage'])[-1].replace('?', str(idx))
                name_path_suffix = os.path.split(
                    self.file_associations['voltage'])[-1].replace('?', str(idx)).replace('input',
                                                                                          'label')
                curr_path = os.path.join(abs_path_prefix, path_prefix, ch_hw_path, curr_path_suffix)
                volt_path = os.path.join(abs_path_prefix, path_prefix, ch_hw_path, volt_path_suffix)
                name_path = os.path.join(abs_path_prefix, path_prefix, ch_hw_path, name_path_suffix)
                with open(name_path, 'r', encoding='utf-8') as f:
                    name = f.read().strip()
                with open(curr_path, 'r', encoding='utf-8') as f:
                    current = int(f.read().strip())
                with open(volt_path, 'r', encoding='utf-8') as f:
                    voltage = int(f.read().strip())
                ret[name] = {'voltage': f"{voltage} {self.units['voltage']}",
                             'current': f"{current} {self.units['current']}",
                             'power': f"{voltage * current/1000} {self.units['power']}"}

        fk = list(ret.keys())[0]
        _metrics = [m for m in metrics if m in ret[fk].keys()]
        if metrics == ['all']:
            _metrics = list(ret[fk].keys())

        if subsystems == ['all']:
            ret = {f"{m}_{k}": v[m] for k, v in ret.items() for m in _metrics}
        else:
            ret = {f"{m}_{k}": v[m] for k, v in ret.items() for s in subsystems if s in k.lower() for m in _metrics}

        return ret


    def get_temps(self, subsystems=['all']):
        path = self.file_associations['temps']
        ret = {}
        all_zones = sorted(glob.glob(path))

        for zone in all_zones:
            with open(os.path.join(zone, 'type'), 'r', encoding='utf-8') as f:
                key = f.readline().rstrip()
            if 'CV' in key:
                continue
            with open(os.path.join(zone, 'temp'), 'r', encoding='utf-8') as f:
                value = int(f.readline().rstrip(''))
                value = f"{value} {self.units['temp']}"
            if subsystems == ['all']:
                ret[f"{key}"] = value
            else:
                for s in subsystems:
                    if s in key.lower():
                        ret[f"{key}"] = value

        return ret
