import datetime
import os

import numpy as np

from quantities import *

gf2N = 9.80665 / 1000

dirpath = os.path.dirname(os.path.realpath(__file__))

class Source:
  def __init__(self, filename):
    self.filename = filename

  def __str__(self):
    return self.__class__.__name__

class CSVSource(Source):
  def read(self):
    mat = np.genfromtxt(os.path.join(self.base_dir, self.filename), delimiter=',', skip_header=1, converters=self.converters)
    self.data = { quant : mat[:, index] for (quant, index) in self.quantity_map.items() }

    # Convert thrust from grams to Newtons
    if THRUST in self.data:
      self.data[THRUST] *= gf2N

    # Ensure torque is always positive.
    if TORQUE in self.data:
      self.data[TORQUE] = np.abs(self.data[TORQUE])

class AutoQuadECU(CSVSource):
  base_dir = os.path.join(dirpath, "data", "autoquad")
  converters = {0 : lambda x: datetime.datetime.strptime(x.decode('utf-8'), '%Y-%m-%d %H:%M:%S:%f').timestamp()}
  display_name = "ESC"
  plot_style = '-'

  quantity_map = {
    TIME : 0,
    CURRENT : 1,
    VOLTAGE : 2,
    MOTOR_VOLTAGE : 3,
    RPM : 4,
    DUTY : 5,
    COMM_PERIOD : 6
  }

class RCBenchmark(CSVSource):
  base_dir = os.path.join(dirpath, "data", "rcbench")
  converters = {}
  display_name = "RCBench"
  plot_style = 'o-'

  quantity_map = {
    TIME : 0,
    ACC_X : 5,
    ACC_Y : 6,
    ACC_Z : 7,
    TORQUE : 8,
    THRUST : 9,
    VOLTAGE : 10,
    CURRENT : 11,
    RPM : 12,
    ELECTRICAL_POWER : 14,
    MECHANICAL_POWER : 15,
    MOTOR_EFFICIENCY : 16,
    PROP_MECH_EFF : 17,
    OVERALL_EFF : 18,
    VIBRATION : 19
  }
