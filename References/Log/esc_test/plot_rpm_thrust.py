#!/usr/bin/env python

import numpy as np
import matplotlib.pyplot as plt

if __name__ == "__main__":
  rpm_thrust_coeffs = [
    ("kotleta-duty", [5.85935238e-08, -1.31076936e-04, 2.73896867e-02], "F60"),
    ("kotleta-rpm", [5.89225233e-08, -1.37988721e-04, 9.45800797e-02], "F60"),
  ]
  plt.figure("RPM-thrust curves")
  plt.title("RPM-thrust curves", fontsize=16)

  rpm_range = np.arange(0, 18001, 100)

  for coeffs in rpm_thrust_coeffs:
    label = coeffs[0]
    thrust_range = [coeffs[1][2] + coeffs[1][1] * rpm + coeffs[1][0] * rpm ** 2 for rpm in rpm_range]
    plot_style = "-"
    plt.plot(rpm_range, thrust_range, plot_style, markersize=3, label=label)

  plt.xlabel("RPM")
  plt.ylabel("Thrust (N)")
  plt.grid(True, axis='y')
  plt.tight_layout()
  plt.legend()
  plt.show()
