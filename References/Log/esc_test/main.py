import argparse
import os
import sys

from collections import namedtuple

import numpy as np
import matplotlib.pyplot as plt

import scipy.signal

from formats import gf2N
from quantities import *
from tests import tests
from util import filter_nan, first_greater_than

def show_freq(ts, s):
  print("Frequency of %s = %f Hz" % (s, len(ts) / (ts[-1] - ts[0])))

if __name__ == "__main__":
  parser = argparse.ArgumentParser()
  parser.add_argument("testname", default=None, nargs="?", type=str, help="Test key for which to plot data. Plots last if not specified.")
  parser.add_argument("--rpm-trigger", required=False, default=500.0, type=float, help="RPM value after which test is considered started")
  parser.add_argument("--max-step-changes", required=False, default=40, type=int, help="Number of step changes after which no vertical lines are drawn")
  parser.add_argument("--max-thrust-for-torque-fit", required=False, default=5, type=int, help="Maximum thrust (in Newtons) to consider when fitting the linear thrust to torque curve (moment scale)")
  parser.add_argument("--save-format", default="png", type=str, help="File format to save plots in")
  parser.add_argument("--plot-extra", required=False, action='store_true', help="Plot additional quantities")
  parser.add_argument("--plot-debug", required=False, action='store_true', help="Show debug plots")
  parser.add_argument("--save", required=False, action='store_true', help="Save plots to disk")
  args = parser.parse_args()

  outputs = []

  Plot = namedtuple('Plot', ["name", "x", "y", "data"])

  class Line:
    def __init__(self, name, x, y, style, nosourcelab=False, **kwargs):
      self.name = name
      self.x = x
      self.y = y
      self.style = style
      self.nosourcelab = nosourcelab
      self.kwargs = kwargs

  class Output:
    def __init__(self):
      self.data = []

  step_changes = None

  keys = [t.key for t in tests]

  if args.testname is None:
    test = tests[-1]
    print("No testname given, defaulting to", test.key)
  else:
    if args.testname not in keys:
      print("No test found matching name: \"%s\"" % args.testname)
      print("Options are:")
      for k in keys:
        print("\t%s" % k)
      sys.exit(1)

    test = tests[keys.index(args.testname)]

  print(test)

  for source in test.sources:
    source.read()
    data = source.data

    output = Output()
    output.source = source

    timestamps = data[TIME]
    timestamps -= timestamps[0]
    rpms = data[RPM]

    # Use RPMs as a trigger to sync up different data sources.
    timestamps -= timestamps[first_greater_than(args.rpm_trigger, rpms)]

    print(source, end=" ")
    show_freq(timestamps, "RPM")

    # Plot everything vs. time.
    for quantity, vals in data.items():
      if quantity.extra and not args.plot_extra:
        print("\tSkipping", quantity)
        continue

      if quantity == TIME:
        continue

      output.data.append(Plot(quantity.name, TIME, quantity, [Line("", *filter_nan(timestamps, vals), ".-")]))

    rpm_plot = Plot("RPM", TIME, RPM, [])
    output.data.append(rpm_plot)

    filt_rpms = scipy.signal.medfilt(rpms, 37)
    #filt_rpms = scipy.signal.wiener(rpms, 37)
    err_rpm = rpms - filt_rpms
    abs_err_rpm = np.square(err_rpm)
    var_rpm = np.sqrt(scipy.signal.medfilt(abs_err_rpm, 181))
    #var_rpm = np.sqrt(scipy.signal.wiener(abs_err_rpm, 181))
    rpm_plot.data.append(Line("Filtered", timestamps, filt_rpms, "-"))

    if args.plot_extra:
      output.data.append(Plot("RPM Variance", TIME, RPM, [Line("", timestamps, var_rpm, "-")]))
      output.data.append(Plot("RPM Variance vs RPM", RPM, RPM, [Line("", rpms, var_rpm, "x")]))

    if DUTY in data:
      changes = np.nonzero(np.diff(data[DUTY]))
      if len(changes) < args.max_step_changes:
        step_changes = timestamps[changes]

    if VOLTAGE in data and CURRENT in data and args.plot_extra:
      start_voltage = data[VOLTAGE][0]
      good_points = np.logical_and(data[CURRENT] > 0.05, data[VOLTAGE] <= start_voltage)
      resist = (start_voltage - data[VOLTAGE]) / data[CURRENT]
      output.data.append(Plot("Voltage Supply Resistance", TIME, RESISTANCE, [Line("", data[TIME][good_points], resist[good_points], "-")]))

    if THRUST in data:
      thrust = data[THRUST]
      interp_thrust = np.interp(timestamps, *filter_nan(data[TIME], thrust))
      output.data.append(Plot("Thrust vs. RPM", RPM, THRUST, [Line("", filt_rpms, interp_thrust, "x")]))

      interp_torque = np.interp(timestamps, *filter_nan(data[TIME], data[TORQUE]))
      output.data.append(Plot("Torque vs. Thrust", THRUST, TORQUE, [Line("", interp_thrust, interp_torque, "-")]))

      # Process RCBenchmark data to produce RPM-Thrust curve

      # Step point detection parameters (I converted them to Newtons - Alex)
      high_thrust_value = 20 * gf2N
      thrust_diff_thresh = 0.05 * gf2N
      rpm_diff_thresh = 2
      thrust_thresh_2 = 8 * gf2N

      if source.display_name == "RCBench":
        # record only the good RPMs
        filt_rpms_diff = np.diff(filt_rpms);
        thrust_diff = np.diff(interp_thrust);

        if args.plot_debug:
          output.data.append(Plot("First order RPM", TIME, RPM, [Line("", timestamps[1:], filt_rpms_diff, "x")]))
          output.data.append(Plot("First order thrust", TIME, THRUST, [Line("", timestamps[1:], thrust_diff, "x")]))

        rpms_sanitized = []
        filt_rpms_sanitized = []
        thrust_sanitized = []
        torque_sanitized = []
        timestamps_sanitized = []
        for i in range(0, len(thrust_diff)):
          if abs(thrust_diff[i]) <= thrust_diff_thresh and abs(filt_rpms_diff[i]) <= rpm_diff_thresh:
            rpms_sanitized.append(rpms[i])
            filt_rpms_sanitized.append(filt_rpms[i])
            thrust_sanitized.append(interp_thrust[i])
            torque_sanitized.append(interp_torque[i])
            timestamps_sanitized.append(timestamps[i])

        if args.plot_debug:
          output.data.append(Plot("Thrust vs. RPM", RPM, THRUST, [Line("RPM Sanitized", rpms_sanitized, thrust_sanitized, "x")]))
          output.data.append(Plot("Thrust vs. RPM", RPM, THRUST, [Line("Filtered RPM Sanitized", filt_rpms_sanitized, thrust_sanitized, "x")]))
          output.data.append(Plot("Torque vs. RPM", RPM, TORQUE, [Line("Filtered RPM Sanitized", filt_rpms_sanitized, torque_sanitized, "x")]))
          output.data.append(Plot("RPM", TIME, RPM, [Line("RPMs sanitized", timestamps_sanitized, rpms_sanitized, "x")]))
          output.data.append(Plot("RPM", TIME, RPM, [Line("Filtered RPMs sanitized", timestamps_sanitized, filt_rpms_sanitized, "x")]))
          output.data.append(Plot("Thrust", TIME, THRUST, [Line("Thrust interp", timestamps, interp_thrust, "x-")]))
          output.data.append(Plot("Thrust", TIME, THRUST, [Line("Thrust sanitized", timestamps_sanitized, thrust_sanitized, "x")]))

        high_values = interp_thrust > high_thrust_value
        max_thrust_index = np.argmax(interp_thrust) + 100
        start_time = timestamps[high_values][0]
        end_time = timestamps[max_thrust_index]
        print("Start time: %.2f, end time: %.2f" % (start_time, end_time))

        ### set starting and end points for this data
        setpoint = []
        for i in range(1, len(timestamps_sanitized)):
          if timestamps_sanitized[i] < start_time or timestamps_sanitized[i] > end_time:
            continue
          if thrust_sanitized[i] - thrust_sanitized[i-1] > thrust_thresh_2:
            setpoint.append(timestamps_sanitized[i-1])
            setpoint.append(timestamps_sanitized[i])
        setpoint.append(end_time)
        setpoint.pop(0);

        #setpoint = []
        extra_filt = scipy.signal.medfilt(rpms, 301)
        diffs = np.diff(extra_filt)

        setpoint = []
        last_t = 0

        for i, d in enumerate(diffs):
          if d > 25 and timestamps[i] - last_t > 1.0:
            setpoint.append(timestamps[i-1])
            setpoint.append(timestamps[i])
            last_t = timestamps[i]
        setpoint.append(end_time)
        setpoint.pop(0);

        if args.plot_debug:
          rpm_plot.data.append(Line("Extra Filtered", timestamps, extra_filt, "-"))
          output.data.append(Plot("First order RPM", TIME, RPM, [Line("extra filt", timestamps[1:], np.diff(extra_filt), "-")]))

        #inds = scipy.signal.argrelextrema(np.diff(extra_filt), np.greater)
        #print(inds)
        #setpoint = timestamps[inds]
        #print(setpoint)

        ### double sanitize the data, if you want.

        rpms_double_sanitized = []
        filt_rpms_double_sanitized = []
        thrust_double_sanitized = []
        timestamps_double_sanitized = []

        j = 0
        rpms_section = []
        raw_rpms_section = []
        thrust_section = []
        torque_section = []
        rpms_avg = [0]
        thrust_avg = [0]
        torque_avg = [0]

        var_rpms_rpm = []
        var_rpms_var = []

        for i in range(0, len(timestamps_sanitized)):
          t = timestamps_sanitized[i]
          if t < start_time or t > end_time:
            continue

          if t > setpoint[j] and t < setpoint[j+1]:
            rpms_double_sanitized.append(rpms_sanitized[i])
            filt_rpms_double_sanitized.append(filt_rpms_sanitized[i])
            thrust_double_sanitized.append(thrust_sanitized[i])
            timestamps_double_sanitized.append(t)
            thrust_section.append(thrust_sanitized[i])
            torque_section.append(torque_sanitized[i])
            rpms_section.append(filt_rpms_sanitized[i])
            raw_rpms_section.append(rpms_sanitized[i])

          if timestamps_sanitized[i+1] > setpoint[j+1]:
            j = j + 2

            rpm_mean = np.mean(rpms_section)
            raw_mean = np.mean(raw_rpms_section)

            #output.data.append(Plot("Set point %d" % (j/2), TIME, RPM, [Line("Filtered", list(range(len(rpms_section))), rpms_section, "x")]))
            #output.data.append(Plot("Set point %d" % (j/2), TIME, RPM, [Line("Raw", list(range(len(rpms_section))), raw_rpms_section, "x")]))
            #output.data.append(Plot("Set point %d" % (j/2), TIME, RPM, [Line("Mean", [0, len(rpms_section)], [rpm_mean, rpm_mean], "-")]))
            #output.data.append(Plot("Set point %d" % (j/2), TIME, RPM, [Line("Raw Mean", [0, len(rpms_section)], [raw_mean, raw_mean], "-")]))

            rpms_avg.append(rpm_mean)

            #raw_var = np.std(raw_rpms_section)
            raw_var = np.std(rpms_section)

            var_rpms_rpm.append(raw_mean)
            var_rpms_var.append(raw_var)

            thrust_avg.append(np.mean(thrust_section))
            torque_avg.append(np.mean(torque_section))
            rpms_section = []
            raw_rpms_section = []
            thrust_section = []
            torque_section = []
            if j >= len(setpoint):
              break

        rpm_thrust_coeffs = np.polyfit(rpms_avg, thrust_avg, 2)
        print("RPM Coeffs: ")
        print(rpm_thrust_coeffs)
        print("RPM-Thrust Curve: Thrust = %.10f * RPM^2 + %.10f * RPM + %.10f" % ( rpm_thrust_coeffs[0], rpm_thrust_coeffs[1], rpm_thrust_coeffs[2]) )
        model_lab = "$T = ${:.3e}$r^2 + ${:.3e}$r + ${:.2e}".format(rpm_thrust_coeffs[0], rpm_thrust_coeffs[1], rpm_thrust_coeffs[2])

        thrust_avg = np.array(thrust_avg)
        torque_avg = np.array(torque_avg)
        inds = thrust_avg < args.max_thrust_for_torque_fit
        thrusts_fit = thrust_avg[inds]
        torques_fit = torque_avg[inds]

        #thrust_torque_coeffs = np.polyfit(thrust_avg, torque_avg, 1)
        thrust_torque_coeff = np.linalg.lstsq(np.array((thrusts_fit,)).T, torques_fit, rcond=None)[0][0]
        print("Moment Scale:", thrust_torque_coeff)
        torque_model_lab = "$\\tau = %0.4fT$" % thrust_torque_coeff

        maxrpm = np.max(rpms)
        rpm_range = np.arange(0, maxrpm, 10)
        thrust_range = [rpm_thrust_coeffs[2] + rpm_thrust_coeffs[1] * rpm + rpm_thrust_coeffs[0] * rpm ** 2 for rpm in rpm_range]
        output.data.append(Plot("Thrust Model", RPM, THRUST, [Line("Sanitized", filt_rpms_double_sanitized, thrust_double_sanitized, ".")]))
        output.data.append(Plot("Thrust Model", RPM, THRUST, [Line("Averaged", rpms_avg, thrust_avg, ".", markersize=10)]))
        output.data.append(Plot("Thrust Model", RPM, THRUST, [Line("Thrust Model Fit " + model_lab, rpm_range, thrust_range, "-", nosourcelab=True)]))
        output.data.append(Plot("Thrust vs. RPM", RPM, THRUST, [Line("Thrust Model Fit", rpm_range, thrust_range, "-")]))

        thrusts = np.arange(0, max(thrust_avg), 0.1)
        torques = thrust_torque_coeff * thrusts
        output.data.append(Plot("Torque vs. Thrust", THRUST, TORQUE, [Line("Averaged", thrust_avg, torque_avg, "x")]))
        output.data.append(Plot("Torque vs. Thrust", THRUST, TORQUE, [Line("Torque Model Fit " + torque_model_lab, thrusts, torques, "-", nosourcelab=True)]))

        if args.plot_debug:
          output.data.append(Plot("RPM", TIME, RPM, [Line("RPMs double sanitized", timestamps_double_sanitized, rpms_double_sanitized, "x")]))
          output.data.append(Plot("RPM", TIME, RPM, [Line("Filtered RPMs double sanitized", timestamps_double_sanitized, filt_rpms_double_sanitized, "x")]))
          output.data.append(Plot("Thrust", TIME, THRUST, [Line("Thrust double sanitized", timestamps_double_sanitized, thrust_double_sanitized, "x")]))

        if args.plot_extra:
          output.data.append(Plot("RPM Variance vs RPM", RPM, RPM, [Line("Filtered", var_rpms_rpm, var_rpms_var, "-")]))

    outputs.append(output)

  if args.save:
    dir_name = os.path.join("media", test.key)
    if not os.path.exists(dir_name):
      os.mkdir(dir_name)

  for output in outputs:
    for plot_name, x_quant, y_quant, lines in output.data:
      plt.figure(plot_name)
      plt.title(plot_name, fontsize=16)
      for line in lines:
        label = line.name
        if not line.nosourcelab:
          label += " %s (%s)" % (output.source.display_name, output.source.filename)
        plt.plot(line.x, line.y, line.style, label=label, **line.kwargs)

      if step_changes is not None and x_quant == TIME:
        for change in step_changes:
          plt.axvline(change, linestyle='--', color='black', linewidth=0.3)

      plt.xlabel(x_quant)
      plt.ylabel(y_quant)
      plt.grid(True, axis='y')
      plt.tight_layout()
      plt.legend()

      if args.save:
        plt_name = test.key + "-" + plot_name.replace(" ", "_")
        plt.savefig(os.path.join(dir_name, "%s.%s" % (plt_name, args.save_format)))

  plt.show()
