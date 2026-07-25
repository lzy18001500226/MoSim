# MWORKS Formal Model Root

For review and reproduction, load exactly one file:

```text
Models/MoSimQuadrotorModel/package.mo
```

This package contains the project-owned plant, controller implementations,
scenarios, resources, runners, and live-integration sources. Do not load an
individual controller file, an external official package, or any retired
package as a second root.

Before a review or run, validate the source layout:

```text
python Scripts/quality/consolidate_mosimquad_model_root.py --check
```

The check proves only source ownership and in-root resource resolution. Model
checks, simulations, performance, code generation, and Gazebo runtime still
need their respective evidence gates.
