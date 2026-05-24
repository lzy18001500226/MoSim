# QPSK Modulation-Demodulation System with BER Analysis
# Using TYCommunication library

from mworks.sysplorer import *

StartSysplorer()

print("Creating QPSK BER Analysis Model...")

# Create new Sysblock model
ModelingPy.NewModel("QPSK_BER_Analysis", "Sysblock")
ModelingPy.OpenModel("QPSK_BER_Analysis")

# Add Bernoulli Binary Generator (signal source)
ModelingPy.AddComponent("TYCommunication.PHYComponents.SourcesAndSinks.BernoulliBinaryGenerator", "QPSK_BER_Analysis", "dataSource", 0, 0, 60, 40)
ModelingPy.SetModelParamValue("QPSK_BER_Analysis", "dataSource", "Probability", "0.5")
ModelingPy.SetModelParamValue("QPSK_BER_Analysis", "dataSource", "SampleRate", "1")

# Add QPSK Modulator
ModelingPy.AddComponent("TYCommunication.PHYComponents.Modulation.QPSKModulatorBaseband", "QPSK_BER_Analysis", "qpskModulator", 120, 0, 60, 40)
ModelingPy.SetModelParamValue("QPSK_BER_Analysis", "qpskModulator", "PhaseOffset", "0")

# Add Raised Cosine Transmit Filter
ModelingPy.AddComponent("TYCommunication.PHYComponents.Filtering.RaisedCosineTransmitFilter", "QPSK_BER_Analysis", "txFilter", 220, 0, 60, 40)
ModelingPy.SetModelParamValue("QPSK_BER_Analysis", "txFilter", "RolloffFactor", "0.5")
ModelingPy.SetModelParamValue("QPSK_BER_Analysis", "txFilter", "FilterSpanInSymbols", "10")

# Add AWGN Channel
ModelingPy.AddComponent("TYCommunication.PropagationAndChannelModels.AWGNChannel", "QPSK_BER_Analysis", "awgnChannel", 320, 0, 60, 40)
ModelingPy.SetModelParamValue("QPSK_BER_Analysis", "awgnChannel", "SignalPower", "1")

# Add Raised Cosine Receive Filter
ModelingPy.AddComponent("TYCommunication.PHYComponents.Filtering.RaisedCosineReceiveFilter", "QPSK_BER_Analysis", "rxFilter", 420, 0, 60, 40)
ModelingPy.SetModelParamValue("QPSK_BER_Analysis", "rxFilter", "RolloffFactor", "0.5")
ModelingPy.SetModelParamValue("QPSK_BER_Analysis", "rxFilter", "FilterSpanInSymbols", "10")

# Add QPSK Demodulator
ModelingPy.AddComponent("TYCommunication.PHYComponents.Modulation.QPSKDemodulatorBaseband", "QPSK_BER_Analysis", "qpskDemodulator", 520, 0, 60, 40)
ModelingPy.SetModelParamValue("QPSK_BER_Analysis", "qpskDemodulator", "PhaseOffset", "0")

# Add Error Rate Calculation
ModelingPy.AddComponent("TYCommunication.TestAndMeasurement.ErrorRateCalculation", "QPSK_BER_Analysis", "errorRate", 620, 0, 60, 40)

# Add Display for BER output
ModelingPy.AddComponent("SysplorerEmbeddedCoder.Utilities.Display", "QPSK_BER_Analysis", "displayBER", 620, 70, 60, 30)

# Connect ports
ModelingPy.ConnectPort("QPSK_BER_Analysis", "dataSource.bin", "qpskModulator.in")
ModelingPy.ConnectPort("QPSK_BER_Analysis", "qpskModulator.out", "txFilter.in")
ModelingPy.ConnectPort("QPSK_BER_Analysis", "txFilter.out", "awgnChannel.in")
ModelingPy.ConnectPort("QPSK_BER_Analysis", "awgnChannel.out", "rxFilter.in")
ModelingPy.ConnectPort("QPSK_BER_Analysis", "rxFilter.out", "qpskDemodulator.in")
ModelingPy.ConnectPort("QPSK_BER_Analysis", "qpskDemodulator.out", "errorRate.rx")
ModelingPy.ConnectPort("QPSK_BER_Analysis", "dataSource.bin", "errorRate.tx")
ModelingPy.ConnectPort("QPSK_BER_Analysis", "errorRate.output", "displayBER.input")

# Save model
ModelingPy.SaveModel("QPSK_BER_Analysis")


