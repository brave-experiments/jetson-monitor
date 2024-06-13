import glob
import os


class OrinNanoDispatcher:

    units = {
        'temp': 'mC',
        'voltage': 'mV',
        'power': 'mW',
        'current': 'mA',
        'freq': 'Hz'
    }

    def __init__(self, dummy=False):
        self.file_associations = {
            'voltage': '/sys/bus/i2c/drivers/ina3221/1-0040/hwmon/hwmon3/in?_input',
            'current': '/sys/bus/i2c/drivers/ina3221/1-0040/hwmon/hwmon3/curr?_input',
            'temps': '/sys/devices/virtual/thermal/thermal_zone*',
        }

        if dummy:
            for k in self.file_associations.keys():
                self.file_associations[k] = f'../dummy_files/orin_nano/{self.file_associations[k]}'

    def get_power_figs(self, metrics, subsystems=['all']):
        ret = {}
        # 3 rails
        # 1. VDD_IN
        # 2. VDD_CPU_GPU_CV
        # 3. VDD_SOC
        for idx in range(1, 4):
            name = ''
            voltage = ''
            current = ''
            curr_path = self.file_associations['current'].replace('?', str(idx))
            volt_path = self.file_associations['voltage'].replace('?', str(idx))
            name_path = self.file_associations['voltage'].replace('?', str(idx)).replace('input', 'label')
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
