class Quantity:
  def __init__(self, name, unit, extra=False):
    self.name = name
    self.unit = unit
    self.extra = extra

  def __str__(self):
    return "{name} ({unit})".format(name=self.name, unit=self.unit)

Q = Quantity
TIME = Q("Time", "s")
RPM = Q("RPM", "min$^{-1}$")
DUTY = Q("Duty", "%")
THRUST = Q("Thrust", "N")
TORQUE = Q("Torque", "Nm")
VOLTAGE = Q("Voltage", "V")
CURRENT = Q("Current", "A")
VIBRATION = Q("Vibration", "g", extra=True)
RESISTANCE = Q("Resistance", "$\Omega$", extra=True)

MOTOR_VOLTAGE = Q("Motor Voltage", "V", extra=True)
COMM_PERIOD = Q("Commutation Period", "$\mu$s", extra=True)
ELECTRICAL_POWER = Q("Electrical Power", "W", extra=True)
MECHANICAL_POWER = Q("Mechanical Power", "W", extra=True)
MOTOR_EFFICIENCY = Q("Motor Efficiency", "%", extra=True)
PROP_MECH_EFF = Q("Prop. Mech. Eff.", "gf/W", extra=True)
OVERALL_EFF = Q("Overall Eff.", "gf/W", extra=True)
ACC_X = Q("Acc. X", "g", extra=True)
ACC_Y = Q("Acc. Y", "g", extra=True)
ACC_Z = Q("Acc. Z", "g", extra=True)
