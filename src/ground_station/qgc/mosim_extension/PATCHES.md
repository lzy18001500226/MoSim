# MoSim Extension Source Promotion

The current MoSim extension was promoted from the retained
`apps/flight_console/mosim/custom` snapshot into the canonical
`src/ground_station/qgc/mosim_extension/custom` tree. The old tree remains
unchanged as a rollback copy.

The canonical tree includes the Factory map resources, QML layers, and both
the operator and compatibility bridge implementations used by the current
ground-station build. `Scripts/ui/materialize_qgc_custom_overlay.py` reads
only this canonical tree and writes the generated overlay to
`src/ground_station/qgc/qgroundcontrol/custom`.

This promotion does not alter the imported QGroundControl source payload,
change its license status, or claim full QGC executable/runtime validation.
