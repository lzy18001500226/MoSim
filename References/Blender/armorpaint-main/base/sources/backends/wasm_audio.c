
#ifdef IRON_AUDIO

#include <iron_audio.h>
#include <stdlib.h>

static iron_a2_buffer_t a2_buffer;
static bool             initialized = false;

void iron_a2_init() {
	if (initialized) {
		return;
	}

	iron_a2_internal_init();
	initialized = true;
}

void iron_a2_shutdown() {}

static uint32_t samples_per_second = 44100;

uint32_t iron_a2_samples_per_second(void) {
	return samples_per_second;
}

#endif
