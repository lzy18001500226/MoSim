# px4ctrl Default Generated Backend

This directory contains the source-controlled payload required to build the
default `legacy_px4ctrl` backend from the project-local `src` tree.

## Provenance

- Generated C source was copied byte-for-byte from the historical MWORKS
  evidence payload:
  `Results/sunray_ros1/px4ctrl_mworks_goal5_m4a_cfunction_20260629_092411/px4ctrl_core_cfunction_codegen_strict/PX4CTRL_Core_CFunction_Sysblock`.
- The platform-independent `px4ctrl_core.cpp` and `px4ctrl_core.h` were copied
  byte-for-byte from the retained golden-slice source at
  `Scripts/sunray/px4ctrl_golden_slice`.
- Only the default backend was migrated. G9, G10, P1-P10, and other optional
  generated backends are intentionally absent. Selecting one fails at CMake
  configure time instead of falling back to an evidence or script directory.

## Payload Hashes

| SHA-256 | Project-local file |
| --- | --- |
| `B9A190CDCA0EC0367BFA0B0E060030397C47FE94E69D6461FE38E159AF6E9B17` | `legacy_px4ctrl/PX4CTRL_Core_CFunction_Sysblock.c` |
| `86D783702F252640E7EBD70C337E9DC1CA2A539CCCA7863BFA69C1F0045D5AD0` | `legacy_px4ctrl/PX4CTRL_Core_CFunction_Sysblock.h` |
| `01D34FF47409993594DE4B413523655AEA47D10CE52203A5BAB785DCE7BD8672` | `legacy_px4ctrl/PX4CTRL_Core_CFunction_Sysblock_data.c` |
| `30E82CE0D735FBE4932EC7D8DDC3248A3F7BF5C4CE596F5348641F0AC80A89FB` | `legacy_px4ctrl/PX4CTRL_Core_CFunction_Sysblock_private.h` |
| `625117392AA7C09CE9A3E2FC73AC9DCA93E404E7487A008C9EB30B3CC5B4F4D3` | `legacy_px4ctrl/PX4CTRL_Core_CFunction_Sysblock_extern_include.h` |
| `1B23333E7C982C1D8E454DD306BFB5C206AFAD93FCC9EAF6095BC5032FF62F66` | `legacy_px4ctrl/mwb_runtime.h` |
| `003304DEF70C00103611235CF9DA266466630D9D817F38D61D965CAFF991CDEE` | `legacy_px4ctrl/mwb_types.h` |
| `155AAFA68C77F8161DE905CE4579AA4C6F077F8924560442954A4F7985B0D9D8` | `legacy_px4ctrl/extern_inc/momodel_extern_ince1.c` |
| `483DCD1A0794563BBDCF1EA936C7A1994275BEE4F9EE974ECDCD2AA04DF84066` | `golden_slice/px4ctrl_core.cpp` |
| `121303483B50758B7D727024CE8CADFA0A8AB8F9516BD9764D61D8CEF406CA35` | `golden_slice/px4ctrl_core.h` |

`mwb_main.c`, trace JSON, and result metadata were not copied because the
ROS1 `px4ctrl_node` target neither compiles nor includes them. They remain
historical evidence only and are not runtime inputs.
