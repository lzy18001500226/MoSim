# CoSim Source Migration Manifest 2026-06-14

Status: raw-content preservation manifest.

In the 2026-06 rebuild, previously root-level CoSim research files were moved
into the blueprint's `research/raw/` tree without editing their content. The
old material is preserved as trace-back input, not treated as deleted.

| Raw file | SHA256 | Intended reviewed decision destination |
|---|---|---|
| `固定翼仿真.md` | `7988065513207BFFB01A57A893C1478A5D93F1449D68BB528F6AE727E1C75C8F` | fixed-wing, JSBSim/ArduPilot, ducted model-aircraft notes |
| `AirSim.md` | `B4626D7534A11BCD38ACF4CB0BB1C2A4D55D89F530FC4CF8700EC06A028AE90B` | AirSim / UE simulator architecture |
| `Bullet.md` | `E7418FA2887FF581CFAE2A14D9A2944979001DDC0FB79DF9B29B5D6D36AD0219` | RL/contact physics optional backends |
| `CARLA.md` | `7CA493B1606B43219F875CC7ADDF1E09E72C4BCED43B33BEFBB5E5DB70BDCDCB` | ground-vehicle and traffic reference only |
| `CoSim设计.md` | `A9450223065ED9FA0BBB64F2438F84B6E3FC8A8447BBA06839ADC2D557DC920D` | platform blueprint input |
| `Cosys-AirSim.md` | `27E7961C4CD0DB449FBACAA19EBAC775218F57EDBA3CC4051ECE6CAADBCE4C1F` | AirSim / UE5 sensor extension |
| `Flightmare.md` | `9CBB910B957E00FCF955A04A7EF0B1F8F5CD4A5D764D35BD73D567B8A237C77B` | multirotor RL and decoupled rendering |
| `Gazebo.md` | `E3B0C44298FC1C149AFBF4C8996FB92427AE41E4649B934CA495991B7852B855` | empty placeholder; replace through reviewed Gazebo research decision |
| `Genesis.md` | `404FEB70869B2C8F274BE56011D623A1A7E93612795425262518184B3AD0DB5F` | RL / differentiable / GPU simulation |
| `Isaac.md` | `46DDDB21C2E351D902B2D82A223AA20A35B04CAEDE733B89A44D0192BE2B9502` | Isaac Sim/Lab and sensor/RL route |
| `JSBSim.md` | `2A3135AB30ACE2D16B9080622AEC8C9BCA12B3EC8DAFAFE687483EEFED265848` | fixed-wing truth backend |
| `Lidar SLAM.md` | `3C3B4EF58E724A9552843D03E2E8AC6490ED2FF7E6B691B6B7425E297F04B7BA` | SLAM / local-map route |
| `MAV层.md` | `03307B14C95676975A7817F89E84E480906BC2DE6A37BA1C33BBC2BFC7833A55` | MAVLink/QGC/MAVSDK command layer |
| `MuJoCo.md` | `8B617CB57E20821D272A12B49F3B6F31AC36274AB543D6C828F20DBDA3A25467` | RL/control physics backend |
| `MuJoCo生态` | `EDB25B102C2623C6C24C7CD980A09F4FB864F6DDE6B549BBBCA4750893500EBB` | MJX/Playground/MPC notes |
| `Planner.md` | `D461FFB9EB020FEAA2224E636CFC09E7549CB3D61608D9F6678F5C26344E06AD` | planner / ESDF / local map |
| `Project AirSim.md` | `246EE104E466A5228A25FE7F2331F26130D7215668939D75DD50DA6C7097AD23` | Project AirSim platform architecture |
| `Prometheus.md` | `BD211D0D5FFFEF241A8AFFD937D358DDB63F1435E7172CA9C878CBC7C7BA0AF5` | autonomous UAV system and control middleware |
| `PX4-Autopilot.md` | `78B4A00A548E255612101D15BDABB9998D647DC59159E32A28CE5608CC6822BF` | PX4 flight-control backend |
| `rclUE.md` | `3333B984F829C4B913FA4EB9828D1141476C7858183994BCCA62F590E834FAB6` | UE / ROS2 integration |
| `ROS2.md` | `FFD9E36CAB1628D5ECC6DD5FA3BDA69C7EF88479018F6FCD34C07C3B82529C9A` | ROS2 algorithm bus |
| `RotorS.md` | `6FFFE03B1B3A37FEC7D253DF7603EB50B9200C97C264B62C5FE2522EFD1EDE9B` | Gazebo multirotor model/plugin reference |
| `Webots.md` | `1C16CBA0B7ED139ED5726813F4A220B513C1520782EBC86A4B11BBE14699513A` | optional education/general simulator reference |
| `XTDrone.md` | `EAF86D99C87406438CCB6849C7401877E02614DB864966B275D68ADBC5A78177` | PX4 + ROS + Gazebo multi-UAV system reference |

## Preservation Rule

Future edits should update reviewed decision or architecture documents. Raw
files should remain stable unless a later task explicitly imports a corrected
source note.
