---
        name: Open Local Media And Verify Playback Surface
        description: Use VLC's shortest local-open path to bring a Desktop or filesystem file onto the VLC playback surface, then verify by visible title, frame, or timeline instead of drifting into preferences or unrelated dialogs.
        ---

        # Open Local Media And Verify Playback Surface

        ## When This Skill Is Applicable

        Use this skill when the task stays inside VLC and matches one of these flows:

        - Open a video or audio file from the desktop, Downloads, or another local folder.
        - Pick one requested file from the VLC system chooser.
        - Verify that the requested local title or real media frame is the one already playing or paused in VLC.
        - Recover from a mistaken local-open detour such as an `Open URL` dialog when the requested media is already on the playback surface.

        Do not use this skill when the task is primarily about persistent settings, saved output paths, toolbar customization, or unsupported streaming/DRM behavior that VLC cannot visibly prove in the current session.

        ## Text-First Procedure

        1. Check first whether the requested media is already visible in VLC; if it is, verify and stop instead of reopening anything.
        2. If the media is not open yet, use the shortest visible local-open path: existing chooser, `Media > Open File...`, or another direct local-file entry point already on screen.
        3. If an unexpected modal such as `Open URL` appears while the requested media is already playing, close the blocker and return to verification instead of entering another open flow.
        4. Finish only when a visible title, real video frame, or nonzero timeline proves the requested local media is on the VLC surface.

        ## Visual State Card Usage

        This package keeps two image-card files:

        - `state_cards.json`: full audit cards with detailed rationale.
        - `runtime_state_cards.json`: compact cards for runtime loading.

        Load only the card whose `when_to_use` matches the live screenshot.

        - `Images/open_local_media_picker.png`: open_local_media_picker
        - `Images/select_requested_local_source.png`: select_requested_local_source
        - `Images/playback_surface_shows_requested_media.png`: playback_surface_shows_requested_media

        ## Visual Transfer Limits

        - Red boxes mark action regions. Green boxes mark result or verification regions.
        - Use stored screenshots as state evidence only. Do not transfer literal coordinates, example filenames, URLs, or example slider values into a different run.
