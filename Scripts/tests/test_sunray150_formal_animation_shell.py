from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
ASSEMBLY = ROOT / "Models" / "MoSimQuadrotorModel" / "Vehicle" / "Sunray150Assembly.mo"
SHELL = ROOT / "Models" / "MoSimQuadrotorModel" / "Vehicle" / "Sunray150VisualShell.mo"


def test_formal_assembly_binds_a_massless_animation_shell() -> None:
    assembly = ASSEMBLY.read_text(encoding="utf-8")
    shell = SHELL.read_text(encoding="utf-8")

    assert "Sunray150VisualShell visual_shell(profile = profile)" in assembly
    assert "connect(physical.body.frame_a, visual_shell.frame_a);" in assembly
    assert "connect(rotor_speed, visual_shell.rotor_speed);" in assembly
    assert "sunray150_dae_mid360_realistic_material_audit_gazebo_body_static.obj" in shell
    assert "sunray150_mid360_body.stl" not in shell
    assert "axisRotation(1, Modelica.Constants.pi / 2, 0)" in shell
    assert "sunray150_mid360_propeller.stl" not in shell
    assert "sunray150_propeller_rotor_0_link_local.stl" in shell
    assert "sunray150_propeller_rotor_2_link_local.stl" in shell
    assert "sunray150_propeller_rotor_1_link_local.stl" in shell
    assert "sunray150_propeller_rotor_3_link_local.stl" in shell
    assert "propeller_visual[4]" not in shell
    assert "propeller_front_right_visual" in shell
    assert "propeller_front_left_visual" in shell
    assert "propeller_back_left_visual" in shell
    assert "propeller_back_right_visual" in shell
    assert "profile.mworks_rotor_center_m[3, 1]" in shell
    assert "each extra = 0" not in shell
    assert "der(rotor_phase[i]) = rotor_speed[i];" in shell
    assert "frame_a.f = zeros(3);" in shell
    assert "frame_a.t = zeros(3);" in shell
    assert "Modelica.Mechanics.MultiBody.Parts.Body" not in shell
    assert "PhysicalWrenchAdapter physical" not in shell
