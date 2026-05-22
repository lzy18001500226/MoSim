# esc\_test

This is a Python package used to plot and analyze data collected for the purpose of characterizing a particular propeller, motor, and ESC configuration (e.g. for quadrotors).

[main.py](main.py) computes two models:

* a quadratic model describing thrust as a function of motor RPM
* a linear model describing torque as a function of thrust

The data sources currently supported are:

* [RCBenchmark](https://gitlab.com/TytoRobotics/RCbenchmarkGUI) logs
* AutoQuad logs, from the [ESC32 Configuration Utility](http://autoquad.org/wiki/wiki/aq-esc32/esc32-configuration-utility)

Additional sources can be used by adding an appropriate class to [formats.py](formats.py).

Sample data from 6 tests is included, all with the three-bladed 7-inch DALPROP T7056.

* ESC32v3 with T-Motor F40 Pro III 1600 kv (esc32v3-f40)
* Kotleta 20 with F60 Pro II 1750 kv (duty cycle commands, kotleta-f60-duty)
* Kotleta 20 with F60 Pro II 1750 kv (closed-loop RPM commands, kotleta-f60-rpm)
* ESC32v3 with F60 Pro II 1750 kv (esc32v3-f60)
* ESC32v2 with F60 Pro II 1750 kv (esc32v2-f60)
* Aikon BLHeli32 4-in-1 with F80 Pro 1900 kv (aikon-f80)

You can add your own data by editing [tests_sample.py](tests_sample.py) or creating Test objects and adding them to [tests.py](tests.py).

The relationship between RPM and thrust should really only be a function of the propeller and it should be independent of the ESC and motor.
So for all six tests above, the RPM to thrust curves should be fairly similar.
However, the command and voltage to RPM (and thus to thrust) relationship will depend on the ESC and motor as well.

Written with the help of [Xuning Yang](http://xuningyang.com).

# Usage

Dependencies are numpy, scipy, and matplotlib.

Run `python main.py <TEST>` where TEST is a test name found in [tests_sample.py](tests_sample.py).

Run `python main.py --help` to see additional options.
In particular, `--plot-debug` can be used to plot additional intermediate quantities used in the model computation and `--plot-extra` will plot additional measurements that may be interesting.

[plot_rpm_thrust.py](plot_rpm_thrust.py) is a helper script to compare motor thrust models from different tests.

# Sample Output

Plots can be optionally saved to the `media` folder by passing `--save` to [main.py](main.py).

<p align="center">
  <img src="https://github.com/alspitz/esc_test/blob/master/media/kotleta-f60-rpm/kotleta-f60-rpm-Current.png?raw=true" alt="Current from kotleta-f60-rpm"/>
  <img src="https://github.com/alspitz/esc_test/blob/master/media/kotleta-f60-rpm/kotleta-f60-rpm-Voltage.png?raw=true" alt="Voltage from kotleta-f60-rpm"/>
  <img src="https://github.com/alspitz/esc_test/blob/master/media/kotleta-f60-rpm/kotleta-f60-rpm-Thrust_Model.png?raw=true" alt="Thrust model from kotleta-f60-rpm"/>
  <img src="https://github.com/alspitz/esc_test/blob/master/media/kotleta-f60-rpm/kotleta-f60-rpm-Torque_vs._Thrust.png?raw=true" alt="Torque model from kotleta-f60-rpm"/>
</p>
