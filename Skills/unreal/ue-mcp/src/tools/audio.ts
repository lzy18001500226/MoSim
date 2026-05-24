import { z } from "zod";
import { categoryTool, bp, type ToolDef } from "../types.js";
import { Vec3 } from "../schemas.js";

export const audioTool: ToolDef = categoryTool(
  "audio",
  "Audio: sound assets, playback, ambient sounds, SoundCues, MetaSounds.",
  {
    list:              bp("List sound assets. Params: directory?, recursive?", "list_sound_assets"),
    play_at_location:  bp("Play sound. Params: soundPath, location, volumeMultiplier?, pitchMultiplier?", "play_sound_at_location"),
    spawn_ambient:     bp("Place ambient sound. Params: soundPath, location, label?", "spawn_ambient_sound"),
    create_cue:        bp("Create SoundCue. Params: name, packagePath?, soundWavePath?", "create_sound_cue"),
    create_metasound:  bp("Create MetaSoundSource. Params: name, packagePath?", "create_metasound_source"),
  },
  undefined,
  {
    directory: z.string().optional(), recursive: z.boolean().optional(),
    soundPath: z.string().optional(),
    location: Vec3.optional(),
    volumeMultiplier: z.number().optional(),
    pitchMultiplier: z.number().optional(),
    label: z.string().optional(),
    name: z.string().optional(),
    packagePath: z.string().optional(),
    soundWavePath: z.string().optional(),
  },
);
