# 📚 Released MMSkills Subset

This directory contains the public MMSkills subset released with the repository. Each skill is a self-contained multimodal package for a recurring Ubuntu desktop workflow.

## Package Structure

```text
<domain>/<skill_name>/
├── SKILL.md                  # Procedure, applicability, transfer limits, verification cues
├── runtime_state_cards.json  # Compact state metadata loaded by the runtime agent
├── state_cards.json          # Audit-grade state metadata for inspection
├── plan.json                 # Generated plan metadata, when available
└── Images/                   # Full frames, focus crops, before/after references
```

## Skill Inventory

| Domain | Count | Released skills |
|--------|------:|-----------------|
| Chrome | 3 | Configure default search engine and preferences; manage bookmarks, reading list, and shortcuts; search web and open target result |
| GIMP | 1 | Save projects and export edited images |
| LibreOffice Calc | 3 | Create chart on target sheet; sort and filter tables; use formulas and functions |
| LibreOffice Impress | 2 | Insert and configure images/audio/media; manage slide structure, ordering, and layouts |
| LibreOffice Writer | 2 | Find and replace text or formatting; save, export, and use templates |
| OS | 2 | Manage files and archives; query system state in Terminal |
| Thunderbird | 1 | Compose, format, and send emails |
| VLC | 1 | Open local media and verify playback surface |
| VS Code | 1 | Search and replace project content |

## Exact Directories

- `chrome/CHROME_Configure_Default_Search_Engine_And_Search_Preferences`
- `chrome/CHROME_Manage_Bookmarks_Reading_List_And_Shortcuts`
- `chrome/CHROME_Search_Web_And_Open_Target_Result`
- `gimp/GIMP_GIMP_Save_Projects_and_Export_Edited_Images`
- `libreoffice_calc/LIBREOFFICECALC_Create_Chart_on_Target_Sheet_with_Exact_Title_and_Type`
- `libreoffice_calc/LIBREOFFICECALC_Sort_and_Filter_Calc_Tables`
- `libreoffice_calc/LIBREOFFICECALC_Use_Formulas_and_Functions_in_Calc_Cells`
- `libreoffice_impress/LIBREOFFICEIMPRESS_Insert_and_Configure_Images_Audio_and_Interactive_Media`
- `libreoffice_impress/LIBREOFFICEIMPRESS_Manage_Slide_Structure_Ordering_and_Layouts`
- `libreoffice_writer/LIBREOFFICEWRITER_Find_and_Replace_Text_or_Formatting`
- `libreoffice_writer/LIBREOFFICEWRITER_Save_Export_and_Template_Writer_Documents`
- `os/OS_Manage_Files_and_Archives_in_Files`
- `os/OS_Query_System_State_in_Terminal`
- `thunderbird/THUNDERBIRD_Compose_Format_and_Send_Thunderbird_Emails`
- `vlc/VLC_Open_Local_Media_And_Verify_Playback_Surface`
- `vs_code/VSCODE_Search_and_Replace_Project_Content`

## Notes for Contributors

- Keep each skill focused on one reusable workflow.
- Prefer compact runtime state cards over broad visual dumps.
- Add only visual references that are referenced by state cards.
- Update `task_skill_mappings/task_skill_mapping.json` when a new skill should be selected automatically for released OSWorld tasks.
