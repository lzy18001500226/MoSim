#ifndef MOSIM_MWORKS_LIVE_RT0_TIMER_RESOLUTION_H
#define MOSIM_MWORKS_LIVE_RT0_TIMER_RESOLUTION_H

#ifndef _WIN32
#error "The RT0 timer-resolution helper currently targets Windows."
#endif

#include <windows.h>
#include <mmsystem.h>

static int mosim_mworks_live_request_1ms_timer_resolution(void) {
    return timeBeginPeriod(1) == TIMERR_NOERROR ? 1 : 0;
}

#endif
