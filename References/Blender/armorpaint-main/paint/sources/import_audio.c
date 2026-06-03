
#include "global.h"

void import_audio_run(char *path) {

#ifdef IRON_AUDIO
    sound_t *s = data_get_sound(path);
    iron_a1_play_sound(s->sound_, false, 1, false);

	string_array_t *ar   = string_split(path, PATH_SEP);
	char           *name = ar->buffer[ar->length - 1];
	console_info(string("%s %s", tr("Audio imported:"), name));
#endif

}
