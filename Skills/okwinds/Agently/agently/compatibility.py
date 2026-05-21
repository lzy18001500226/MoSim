from __future__ import annotations

from copy import deepcopy
from typing import Any


CURRENT_COMPATIBILITY_SCHEMA_VERSION = 1
CURRENT_FRAMEWORK_VERSION = "4.1.2.3"
CURRENT_RELEASE_TRAIN = "2026-05-4.1.2.3"

DEVTOOLS_RUNTIME_PROTOCOL = "agently-devtools.observation-runtime.v1"
SKILLS_AUTHORING_PROTOCOL = "agently-skills.authoring.v1"
SKILLS_DEVTOOLS_GUIDANCE_PROTOCOL = "agently-skills.devtools-guidance.v1"
DOCS_PUBLIC_SURFACE_PROTOCOL = "agently-docs.public-surface.v1"

_CURRENT_RELEASE_MANIFEST: dict[str, Any] = {
    "schema_version": CURRENT_COMPATIBILITY_SCHEMA_VERSION,
    "framework": "agently",
    "framework_version": CURRENT_FRAMEWORK_VERSION,
    "release_train": CURRENT_RELEASE_TRAIN,
    "released_at": "2026-05-21",
    "notes": (
        "This manifest is the offline compatibility surface for the installed "
        "Agently package. Historical release manifests live in the source "
        "repository compatibility registry."
    ),
    "companions": {
        "devtools": {
            "companion_package": "agently-devtools",
            "runtime_protocol": DEVTOOLS_RUNTIME_PROTOCOL,
            "event_naming": {
                "preferred_event_type": "ObservationEvent",
                "legacy_event_type": "RuntimeEvent",
                "legacy_compatibility": "Agently 4.1.x",
                "replacement_line": "Agently 4.2",
            },
            "recommended_version_specifier": ">=0.1.4,<0.2.0",
        },
        "skills": {
            "repository": "Agently-Skills",
            "authoring_protocol": SKILLS_AUTHORING_PROTOCOL,
            "devtools_guidance_protocol": SKILLS_DEVTOOLS_GUIDANCE_PROTOCOL,
            "catalog_generation": "v2",
            "recommended_bundle": "app",
            "recommended_ref": "main",
            "legacy_generations": [
                {
                    "generation": "v1",
                    "last_supported_framework_version": "4.1.1",
                    "status": "frozen",
                }
            ],
        },
        "docs": {
            "repository": "docs",
            "public_surface_protocol": DOCS_PUBLIC_SURFACE_PROTOCOL,
        },
    },
}


def get_current_release_manifest() -> dict[str, Any]:
    return deepcopy(_CURRENT_RELEASE_MANIFEST)


def get_devtools_compatibility_manifest() -> dict[str, Any]:
    manifest = get_current_release_manifest()
    devtools = deepcopy(manifest["companions"]["devtools"])
    devtools["framework_version"] = manifest["framework_version"]
    devtools["release_train"] = manifest["release_train"]
    return devtools


def get_skills_compatibility_manifest() -> dict[str, Any]:
    manifest = get_current_release_manifest()
    skills = deepcopy(manifest["companions"]["skills"])
    skills["framework_version"] = manifest["framework_version"]
    skills["release_train"] = manifest["release_train"]
    return skills


__all__ = [
    "CURRENT_COMPATIBILITY_SCHEMA_VERSION",
    "CURRENT_FRAMEWORK_VERSION",
    "CURRENT_RELEASE_TRAIN",
    "DEVTOOLS_RUNTIME_PROTOCOL",
    "SKILLS_AUTHORING_PROTOCOL",
    "SKILLS_DEVTOOLS_GUIDANCE_PROTOCOL",
    "DOCS_PUBLIC_SURFACE_PROTOCOL",
    "get_current_release_manifest",
    "get_devtools_compatibility_manifest",
    "get_skills_compatibility_manifest",
]
