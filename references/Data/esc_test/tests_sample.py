from testutil import Test
from formats import AutoQuadECU, RCBenchmark

"""
  All tests performed using a three-bladed 7-inch DALPROP T7056.
"""

tests = []

tests.append(Test(
    RCBenchmark("Log_2019-11-05_171350.csv"),
    AutoQuadECU("f40_steps_5-2.csv"),
    key="esc32v3-f40",
    description="""
    ESC32v3, F40 Pro III 1600kv, 7 inch clear prop, after resoldering on RPM probe
    2019-11-05

    Manually set duty cycle steps of 5 from AutoQuadECU
    power supply at 16.00 V
    """
))

tests.append(Test(
    RCBenchmark("Log_2019-11-07_174807.csv"),
    key="kotleta-f60-duty",
    description="""
    Holybro Kotleta 20 w/ Sapog firmware, F60 Pro II 1750kv, 7-inch clear prop
    Steps of 0.05 through Sapog CLI interface
    Power supply set to 16.00 V.
    """
))

tests.append(Test(
    RCBenchmark("Log_2019-11-07_175456.csv"),
    key="kotleta-f60-rpm",
    description="""
    Holybro Kotleta 20 w/ Sapog firmware, F60 Pro II 1750kv, 7-inch clear prop
    RPM steps of 500 from 2500 to 13500. (maxed out at 13100).
    Power supply set to 16.00 V.
    """
))

tests.append(Test(
    RCBenchmark("Log_2019-11-07_184325.csv"),
    AutoQuadECU("esc32v3_f60-1.csv"),
    key="esc32v3-f60",
    description="""
    ESC32v3 F60 Pro II 1750kv, 7-inch clear prop
    bullet connectors
    duty cycle steps from 15 to 100 in steps of 5 from AutoQuad ECU
    Power supply set to 16.00 V.
    """
))

tests.append(Test(
    RCBenchmark("Log_2019-11-07_211050.csv"),
    key="esc32v2-f60",
    description="""
    ESC32v2 F60 Pro II 1750kv, 7-inch clear prop
    bullet connectors
    duty cycle steps from 10 to 100 in steps of 5 from CLI
    Power supply set to 16.00 V, current limit of 40.0 A
    Sample rate was increased to 130 +
    """
))

tests.append(Test(
    RCBenchmark("Log_2019-11-09_181347.csv"),
    key="aikon-f80",
    description="""
    Aikon BLHeli32 4 in 1 ESC, F80 Pro 1900kv, 7-inch clear prop
    soldered on
    pwm steps from 1050 to 1950 via RCBenchmark, using added textbox entry support
    power supply set to 16.00 V
    Sample rate was 140+
    """
))
