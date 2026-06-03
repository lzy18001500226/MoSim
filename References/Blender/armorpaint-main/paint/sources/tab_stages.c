
#include "global.h"

typedef struct slot_stage {
	char *name;
} slot_stage_t;

any_array_t  *project_stages               = NULL;
int           selected_stage               = 0;
bool          tab_stages_show_context_menu = false;
slot_stage_t *tab_stages_context_stage     = NULL;

void tab_stages_context_menu_delete(void *_) {
	array_remove(project_stages, tab_stages_context_stage);
	if (selected_stage >= project_stages->length) {
		selected_stage = project_stages->length - 1;
	}
}

void tab_stages_context_menu_draw() {
	ui->enabled = project_stages->length > 1;
	if (ui_menu_button(tr("Delete"), "delete", ICON_DELETE)) {
		sys_notify_on_next_frame(&tab_stages_context_menu_delete, NULL);
	}
	ui->enabled = true;
}

void tab_stages_draw(ui_handle_t *htab) {
	if (ui_tab(htab, tr("Stages"), false, -1, false)) {

		ui_begin_sticky();
		f32_array_t *row = f32_array_create_from_raw(
		    (f32[]){
		        -70,
		    },
		    1);
		ui_row(row);
		if (ui_icon_button("New", ICON_PLUS, UI_ALIGN_CENTER)) {
			slot_stage_t *s = GC_ALLOC_INIT(slot_stage_t, {.name = string("%s %s", tr("Stage"), i32_to_string(project_stages->length + 1))});
			any_array_push(project_stages, s);
			selected_stage = project_stages->length - 1;
		}
		// if (ui_button(tr("Nodes"), UI_ALIGN_CENTER, "")) {}
		ui_end_sticky();

		if (project_stages == NULL) {
			project_stages = any_array_create(0);
			gc_root(project_stages);

			slot_stage_t *s = GC_ALLOC_INIT(slot_stage_t, {.name = "Stage 1"});
			any_array_push(project_stages, s);
		}

		for (i32 i = 0; i < project_stages->length; ++i) {
			slot_stage_t *s              = project_stages->buffer[i];
			tab_stages_show_context_menu = false;
			if (i == selected_stage) {
				ui_fill(0, 0, ui->_window_w, ui->ops->theme->ELEMENT_H, ui->ops->theme->HIGHLIGHT_COL);
			}
			ui_text(s->name, UI_ALIGN_LEFT, 0x00000000);
			if (ui->is_released) {
				selected_stage = i;
			}
			if (ui->is_hovered && ui->input_released_r) {
				gc_unroot(tab_stages_context_stage);
				tab_stages_context_stage = s;
				gc_root(tab_stages_context_stage);
				tab_stages_show_context_menu = true;
			}
			ui_fill(0, 0, (ui->_window_w / (float)UI_SCALE() - 2), 1 * UI_SCALE(), ui->ops->theme->SEPARATOR_COL);
			if (tab_stages_show_context_menu) {
				ui_menu_draw(&tab_stages_context_menu_draw, -1, -1);
			}
		}
	}
}
