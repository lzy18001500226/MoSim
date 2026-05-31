"""
Multimodal Skill Loader for OSWorld Agents.

Handles discovery, loading, and formatting of multimodal skills (text + images)
from the local skills_library. Skills are defined by SKILL.md files and optional
image references in an Images/ subdirectory.

Supports two loading modes:
  - "text_only": Load only the SKILL.md textual content.
  - "multimodal": Load SKILL.md text + referenced images for visual grounding.

Image loading strategy (multimodal mode):
  - Skills text (SKILL.md) is loaded eagerly at task start and injected into
    the system prompt as procedural knowledge. The text already describes
    each state's Visual Grounding and its corresponding Image Reference.
  - Skill images are loaded ON-DEMAND PER IMAGE: the agent reads the skill
    text, compares the current screenshot with the described states, and
    requests only the specific image it needs via `load_skill_image(skill_name,
    image_name)`. This avoids flooding the context window with all images
    upfront and ensures only the relevant visual reference is provided at
    each interaction step.
"""

import json
import logging
import os
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional, Tuple

from mm_agents.utils.qwen_vl_utils import preprocess_image_for_vlm

logger = logging.getLogger("desktopenv.skill_loader")


@dataclass(frozen=True)
class SkillMetadata:
    """Lightweight metadata for a single skill (parsed from SKILL.md frontmatter)."""
    name: str
    description: str
    directory: str  # Absolute path to the skill directory


@dataclass
class SkillContent:
    """Full content of a loaded skill."""
    name: str
    description: str
    text: str  # Full SKILL.md content (without frontmatter)
    image_references: List[str] = field(default_factory=list)  # Relative paths found in text, e.g. ["Images/foo.png"]
    directory: str = ""


@dataclass(frozen=True)
class SkillStateCard:
    """Structured metadata describing when a single skill image is useful."""

    state_id: str = ""
    image_id: str = ""
    image_path: str = ""
    stage: str = ""
    image_role: str = ""
    when_to_use: str = ""
    when_not_to_use: str = ""
    visible_cues: List[str] = field(default_factory=list)
    verification_cue: str = ""
    visual_risk: str = ""
    recommended_verification: str = ""
    non_transferable_parts: List[str] = field(default_factory=list)
    highlight_targets: List[Dict[str, str]] = field(default_factory=list)
    raw: Dict[str, object] = field(default_factory=dict)


@dataclass
class SkillStateCardSet:
    """Container for a skill's state-card schema file."""

    skill_name: str
    schema_version: str
    source_file: str
    card_granularity: str
    domain: str = ""
    generation_method: str = ""
    cards: List[SkillStateCard] = field(default_factory=list)


@dataclass(frozen=True)
class SkillStateView:
    """A single visual view inside a multi-view runtime state bundle."""

    view_type: str = ""
    image_path: str = ""
    use_for: str = ""
    label: str = ""
    raw: Dict[str, object] = field(default_factory=dict)


@dataclass
class SkillStateBundle:
    """Structured metadata describing one state with multiple optional views."""

    state_id: str = ""
    state_name: str = ""
    stage: str = ""
    image_role: str = ""
    when_to_use: str = ""
    when_not_to_use: str = ""
    visible_cues: List[str] = field(default_factory=list)
    verification_cue: str = ""
    visual_risk: str = ""
    preferred_view_order: List[str] = field(default_factory=list)
    visual_evidence_chain: Dict[str, str] = field(default_factory=dict)
    available_views: List[SkillStateView] = field(default_factory=list)
    raw: Dict[str, object] = field(default_factory=dict)


@dataclass
class SkillStateBundleSet:
    """Container for a skill's multi-view runtime bundle schema file."""

    skill_name: str
    schema_version: str
    source_file: str
    card_granularity: str
    domain: str = ""
    generation_method: str = ""
    bundles: List[SkillStateBundle] = field(default_factory=list)


@dataclass
class LoadedSkillStateView:
    """One loaded view image resolved from a state bundle request."""

    view: SkillStateView
    image: Tuple[str, str, str]


@dataclass
class ResolvedSkillStateSelection:
    """Resolved stage-1 request for one state plus one or more loaded views."""

    state: SkillStateBundle
    requested_view_types: List[str] = field(default_factory=list)
    reason: str = ""
    loaded_views: List[LoadedSkillStateView] = field(default_factory=list)


class SkillLoader:
    """
    Local filesystem skill loader for multimodal agents.

    Unlike the terminus SkillDocLoader which operates via container exec,
    this loader reads directly from the local filesystem since skills_library
    is part of the repository.
    """

    def __init__(
        self,
        skills_library_dir: str = "skills_library",
        max_skill_chars: int = 8000,
    ):
        """
        Args:
            skills_library_dir: Path to the skills library directory (relative to project root or absolute).
            max_skill_chars: Maximum characters to load from a single SKILL.md.
        """
        self._skills_dir = Path(skills_library_dir)
        if not self._skills_dir.is_absolute():
            # Resolve relative to project root (where run.py lives)
            project_root = Path(__file__).resolve().parent.parent
            self._skills_dir = project_root / skills_library_dir
        self._max_skill_chars = max_skill_chars
        self._metadata_cache: Dict[str, SkillMetadata] = {}
        self._content_cache: Dict[str, SkillContent] = {}
        self._state_card_cache: Dict[str, Optional[SkillStateCardSet]] = {}
        self._runtime_state_card_cache: Dict[str, Optional[SkillStateCardSet]] = {}
        self._state_bundle_cache: Dict[str, Optional[SkillStateBundleSet]] = {}
        self._runtime_state_bundle_cache: Dict[str, Optional[SkillStateBundleSet]] = {}
        self._skill_id_to_dir: Dict[str, Path] = {}
        self._basename_to_skill_ids: Dict[str, List[str]] = {}
        self._skill_index_built = False

    # ------------------------------------------------------------------ #
    #  Public API
    # ------------------------------------------------------------------ #

    def discover_all_skills(self) -> List[SkillMetadata]:
        """Scan skills_library and return metadata for all available skills."""
        if self._metadata_cache:
            return list(self._metadata_cache.values())

        if not self._skills_dir.exists():
            logger.warning(f"Skills library directory not found: {self._skills_dir}")
            return []

        self._ensure_skill_index()
        metadata_list: List[SkillMetadata] = []
        for skill_id, entry in sorted(self._skill_id_to_dir.items()):
            skill_md = self._find_skill_md(entry)
            if skill_md is None:
                continue
            text = skill_md.read_text(encoding="utf-8")
            frontmatter = self._parse_frontmatter(text)
            meta = SkillMetadata(
                name=frontmatter.get("name", entry.name),
                description=frontmatter.get("description", ""),
                directory=str(entry),
            )
            self._metadata_cache[skill_id] = meta
            metadata_list.append(meta)

        logger.info(f"Discovered {len(metadata_list)} skills in {self._skills_dir}")
        return metadata_list

    def load_skills_for_task(self, skill_names: List[str]) -> List[SkillContent]:
        """
        Load full skill content for the given list of skill directory names.
        These names come from the task JSON's "skills" field.

        Args:
            skill_names: List of skill directory names, e.g. ["Open_Chrome_Extensions_Page", ...]

        Returns:
            List of SkillContent objects with text loaded (images not yet loaded).
        """
        loaded: List[SkillContent] = []
        for name in skill_names:
            content = self._load_skill_content(name)
            if content:
                loaded.append(content)
            else:
                logger.warning(f"Skill '{name}' not found in {self._skills_dir}")
        return loaded

    def load_skill_content(self, skill_name: str) -> Optional[SkillContent]:
        """Load a single skill's SKILL.md content without eagerly loading images."""
        return self._load_skill_content(skill_name)

    def load_state_cards(self, skill_name: str, *, runtime: bool = True) -> Optional[SkillStateCardSet]:
        """
        Load structured state-card metadata for a skill.

        Args:
            skill_name: Skill directory name or relative skill path.
            runtime: Prefer the compact runtime_state_cards.json form when True.

        Returns:
            Parsed SkillStateCardSet, or None if no usable state-card file exists.
        """
        resolved = self._resolve_skill_identifier_and_dir(skill_name)
        if resolved is None:
            logger.warning(f"[SkillLoader] Skill directory not found for identifier: {skill_name}")
            return None
        skill_id, skill_dir = resolved

        cache = self._runtime_state_card_cache if runtime else self._state_card_cache
        if skill_id in cache:
            return cache[skill_id]

        state_path = self._resolve_state_schema_path(skill_dir, runtime=runtime)
        if state_path is None:
            cache[skill_id] = None
            return None

        payload = self._read_state_schema_payload(state_path)
        if payload is None:
            cache[skill_id] = None
            return None

        state_cards: Optional[SkillStateCardSet]
        if isinstance(payload, dict) and isinstance(payload.get("cards"), list):
            state_cards = self._parse_state_card_payload(skill_name=skill_name, state_path=state_path, payload=payload)
        elif isinstance(payload, dict) and isinstance(payload.get("states"), list):
            bundle_set = self._parse_state_bundle_payload(skill_name=skill_name, state_path=state_path, payload=payload)
            state_cards = self._flatten_state_bundles_to_card_set(
                skill_name=skill_name,
                state_path=state_path,
                bundle_set=bundle_set,
            )
        else:
            logger.warning("[SkillLoader] Unsupported state schema in %s", state_path)
            state_cards = None
        cache[skill_id] = state_cards
        return state_cards

    def load_state_bundles(self, skill_name: str, *, runtime: bool = True) -> Optional[SkillStateBundleSet]:
        """
        Load structured multi-view runtime state bundles for a skill.

        Newer multimodal skills use `states -> available_views` rather than the
        older flat `cards` schema. This loader preserves both:
        - native bundle parsing for the new schema
        - one-view fallback conversion for legacy flat cards
        """
        resolved = self._resolve_skill_identifier_and_dir(skill_name)
        if resolved is None:
            logger.warning(f"[SkillLoader] Skill directory not found for identifier: {skill_name}")
            return None
        skill_id, skill_dir = resolved

        cache = self._runtime_state_bundle_cache if runtime else self._state_bundle_cache
        if skill_id in cache:
            return cache[skill_id]

        state_path = self._resolve_state_schema_path(skill_dir, runtime=runtime)
        if state_path is None:
            cache[skill_id] = None
            return None

        payload = self._read_state_schema_payload(state_path)
        if payload is None:
            cache[skill_id] = None
            return None

        state_bundles: Optional[SkillStateBundleSet]
        if isinstance(payload, dict) and isinstance(payload.get("states"), list):
            state_bundles = self._parse_state_bundle_payload(skill_name=skill_name, state_path=state_path, payload=payload)
        elif isinstance(payload, dict) and isinstance(payload.get("cards"), list):
            state_cards = self._parse_state_card_payload(skill_name=skill_name, state_path=state_path, payload=payload)
            state_bundles = self._convert_state_cards_to_bundle_set(
                skill_name=skill_name,
                state_path=state_path,
                state_cards=state_cards,
            )
        else:
            logger.warning("[SkillLoader] Unsupported state schema in %s", state_path)
            state_bundles = None

        cache[skill_id] = state_bundles
        return state_bundles

    def summarize_state_cards_for_preview(
        self,
        state_cards: Optional[SkillStateCardSet],
        *,
        max_cards: int = 3,
        max_when_to_use_chars: int = 140,
    ) -> str:
        """
        Compress runtime state cards into a short preview suitable for the main prompt.
        """
        if state_cards is None or not state_cards.cards:
            return "(no state-card preview)"

        lines: List[str] = []
        for card in state_cards.cards[:max_cards]:
            selector = card.image_id or card.state_id or Path(card.image_path).stem
            stage = card.stage or "unknown stage"
            image_role = card.image_role or "unknown image role"
            when_to_use = self._normalize_preview_sentence(
                card.when_to_use,
                fallback="no recommended usage was provided",
                strip_prefixes=["Use when", "Use it when", "Use this card when", "Match this card when"],
            )
            when_not_to_use = self._normalize_preview_sentence(
                card.when_not_to_use,
                fallback="no exclusion guidance was provided",
                strip_prefixes=["Do not use when", "Avoid using it when", "Skip it if", "Do not use it when"],
            )
            cues = self._normalize_preview_sentence(
                "; ".join(card.visible_cues) if card.visible_cues else "",
                fallback="no visible cues were listed",
                strip_prefixes=[],
            )
            lines.append(
                "  - "
                f'State card "{selector}" corresponds to stage "{stage}" and image role "{image_role}". '
                f"Use it when {when_to_use}. "
                f"Avoid using it when {when_not_to_use}. "
                f"Visible cues include {cues}."
            )
        remaining = len(state_cards.cards) - max_cards
        if remaining > 0:
            lines.append(f"  - ... {remaining} more state cards")
        return "\n".join(lines)

    def summarize_state_bundles_for_preview(
        self,
        state_bundles: Optional[SkillStateBundleSet],
        *,
        max_states: int = 3,
        max_when_to_use_chars: int = 140,
        max_views: int = 4,
    ) -> str:
        """
        Compress multi-view runtime bundles into a short preview suitable for the
        main prompt.
        """
        if state_bundles is None or not state_bundles.bundles:
            return "(no state-bundle preview)"

        lines: List[str] = []
        for bundle in state_bundles.bundles[:max_states]:
            when_to_use = self._truncate_preview_fragment(
                self._normalize_preview_sentence(
                    bundle.when_to_use,
                    fallback="no recommended usage was provided",
                    strip_prefixes=["Use when", "Use it when", "Use this card when", "Match this card when"],
                ),
                max_chars=max_when_to_use_chars,
            )
            visible_cues = self._normalize_preview_sentence(
                "; ".join(bundle.visible_cues) if bundle.visible_cues else "",
                fallback="no visible cues were listed",
                strip_prefixes=[],
            )
            rendered_views = []
            for view in bundle.available_views[:max_views]:
                rendered_views.append(f"{view.view_type or '(unknown view)'}")
            view_text = ", ".join(rendered_views) if rendered_views else "no views"
            lines.append(
                "  - "
                f'State "{bundle.state_id or "(missing)"}" at stage "{bundle.stage or "unknown stage"}": '
                f"use when {when_to_use}. "
                f"Visible cues include {visible_cues}. "
                f"Available views: {view_text}."
            )
        remaining = len(state_bundles.bundles) - max_states
        if remaining > 0:
            lines.append(f"  - ... {remaining} more state bundles")
        return "\n".join(lines)

    def summarize_state_cards_for_main_agent(
        self,
        state_cards: Optional[SkillStateCardSet],
        *,
        max_cards: int = 2,
        max_when_to_use_chars: int = 110,
        max_visible_cues: int = 3,
        max_visible_cue_chars: int = 60,
    ) -> str:
        """
        Render a lightweight main-dialogue preview using only a small amount of
        `when_to_use` and `visible_cues` information from the first few state cards.
        """
        if state_cards is None or not state_cards.cards:
            return "(no state-card hints)"

        lines: List[str] = []
        for card in state_cards.cards[:max_cards]:
            selector = card.image_id or card.state_id or Path(card.image_path).stem
            when_to_use = self._truncate_preview_fragment(
                self._normalize_preview_sentence(
                    card.when_to_use,
                    fallback="no recommended usage was provided",
                    strip_prefixes=["Use when", "Use it when", "Use this card when", "Match this card when"],
                ),
                max_chars=max_when_to_use_chars,
            )
            visible_cues = [
                self._truncate_preview_fragment(str(cue).strip(), max_chars=max_visible_cue_chars)
                for cue in (card.visible_cues or [])[:max_visible_cues]
                if str(cue).strip()
            ]
            cues_text = "; ".join(visible_cues) if visible_cues else "no visible cues were listed"
            lines.append(
                "  - "
                f'State card "{selector}": '
                f"use when {when_to_use}. "
                f"Visible cues: {cues_text}."
            )
        return "\n".join(lines)

    @staticmethod
    def _normalize_preview_sentence(
        text: str,
        *,
        fallback: str,
        strip_prefixes: List[str],
    ) -> str:
        cleaned = str(text or "").strip()
        if not cleaned:
            return fallback
        for prefix in strip_prefixes:
            if cleaned.lower().startswith(prefix.lower()):
                cleaned = cleaned[len(prefix):].strip()
                break
        cleaned = cleaned.lstrip(":,- ").strip()
        cleaned = re.sub(r"\s+", " ", cleaned)
        cleaned = cleaned.rstrip(" .;")
        return cleaned or fallback

    @staticmethod
    def _truncate_preview_fragment(text: str, *, max_chars: int) -> str:
        cleaned = re.sub(r"\s+", " ", str(text or "").strip())
        if len(cleaned) <= max_chars:
            return cleaned
        truncated = cleaned[: max(0, max_chars - 3)].rstrip(" ,;:.")
        return (truncated + "...") if truncated else cleaned[:max_chars]

    def format_state_cards_for_branch(
        self,
        state_cards: Optional[SkillStateCardSet],
        *,
        include_when_not_to_use: bool = True,
        include_visual_risk: bool = True,
    ) -> str:
        """
        Render state cards into a structured text block for multimodal planner branches.
        """
        if state_cards is None or not state_cards.cards:
            return "No structured state cards are available for this skill."

        lines = [
            f"# Runtime State Cards ({state_cards.skill_name})",
            "",
            "These cards summarize which UI state each reference image corresponds to.",
            "Use the cards to decide whether the current screenshot is close enough to any referenced state to justify loading that image.",
            "",
        ]
        for idx, card in enumerate(state_cards.cards, start=1):
            selector = card.image_id or card.state_id or Path(card.image_path).stem
            lines.extend(
                [
                    f"{idx}. state_id: {card.state_id or '(missing)'}",
                    f"   image_id: {selector}",
                    f"   image_path: {card.image_path or '(missing)'}",
                    f"   stage: {card.stage or '(unknown)'}",
                    f"   image_role: {card.image_role or '(unknown)'}",
                    f"   when_to_use: {card.when_to_use or '(missing)'}",
                ]
            )
            if include_when_not_to_use:
                lines.append(f"   when_not_to_use: {card.when_not_to_use or '(missing)'}")
            cues = "; ".join(card.visible_cues) if card.visible_cues else "(none listed)"
            lines.append(f"   visible_cues: {cues}")
            if card.verification_cue:
                lines.append(f"   verification_cue: {card.verification_cue}")
            elif card.recommended_verification:
                lines.append(f"   verification_cue: {card.recommended_verification}")
            if include_visual_risk:
                risk_text = card.visual_risk or "; ".join(card.non_transferable_parts[:2])
                if risk_text:
                    lines.append(f"   visual_risk: {risk_text}")
            lines.append("")
        return "\n".join(lines).rstrip()

    def format_state_bundles_for_branch(
        self,
        state_bundles: Optional[SkillStateBundleSet],
        *,
        include_when_not_to_use: bool = True,
        include_visual_risk: bool = True,
    ) -> str:
        """
        Render multi-view state bundles into a structured text block for v7
        branches. The stage-1 selector sees the available views but does not yet
        receive the underlying images.
        """
        if state_bundles is None or not state_bundles.bundles:
            return "No structured state bundles are available for this skill."

        lines = [
            f"# Runtime State Bundles ({state_bundles.skill_name})",
            "",
            "These bundles summarize which UI state each reference bundle corresponds to.",
            "A single state may expose multiple complementary views such as full_frame, focus_crop, before, or after.",
            "Request only the specific state IDs and view types that are likely to reduce ambiguity for the CURRENT screenshot.",
            "",
        ]
        for idx, bundle in enumerate(state_bundles.bundles, start=1):
            lines.extend(
                [
                    f"{idx}. state_id: {bundle.state_id or '(missing)'}",
                    f"   state_name: {bundle.state_name or '(missing)'}",
                    f"   stage: {bundle.stage or '(unknown)'}",
                    f"   image_role: {bundle.image_role or '(unknown)'}",
                    f"   when_to_use: {bundle.when_to_use or '(missing)'}",
                ]
            )
            if include_when_not_to_use:
                lines.append(f"   when_not_to_use: {bundle.when_not_to_use or '(missing)'}")
            cues = "; ".join(bundle.visible_cues) if bundle.visible_cues else "(none listed)"
            lines.append(f"   visible_cues: {cues}")
            if bundle.verification_cue:
                lines.append(f"   verification_cue: {bundle.verification_cue}")
            if include_visual_risk and bundle.visual_risk:
                lines.append(f"   visual_risk: {bundle.visual_risk}")
            lines.append("   available_views:")
            if bundle.available_views:
                for view in bundle.available_views:
                    lines.append(
                        "   - "
                        f"view_type: {view.view_type or '(unknown)'} | "
                        f"use_for: {view.use_for or '(missing)'} | "
                        f"label: {view.label or '(missing)'}"
                    )
            else:
                lines.append("   - (no views listed)")
            lines.append("")
        return "\n".join(lines).rstrip()

    def resolve_state_card_image_requests(
        self,
        skill_name: str,
        requested_identifiers: List[str],
        *,
        runtime: bool = True,
    ) -> Tuple[List[SkillStateCard], List[str]]:
        """
        Resolve image requests against state-card metadata.

        Supports exact matches against `image_id`, `state_id`, `image_path`, and image basename.
        """
        state_cards = self.load_state_cards(skill_name, runtime=runtime)
        if state_cards is None or not state_cards.cards:
            return [], list(requested_identifiers or [])

        by_key: Dict[str, SkillStateCard] = {}
        for card in state_cards.cards:
            keys = {
                card.image_id,
                card.state_id,
                card.image_path,
                Path(card.image_path).name if card.image_path else "",
                Path(card.image_path).stem if card.image_path else "",
            }
            for key in keys:
                normalized = self._normalize_state_card_selector(key)
                if normalized:
                    by_key.setdefault(normalized, card)

        resolved: List[SkillStateCard] = []
        seen_image_paths: set[str] = set()
        missing: List[str] = []
        for raw_identifier in requested_identifiers or []:
            normalized = self._normalize_state_card_selector(raw_identifier)
            if not normalized:
                continue
            card = by_key.get(normalized)
            if card is None:
                missing.append(str(raw_identifier))
                continue
            if card.image_path and card.image_path not in seen_image_paths:
                resolved.append(card)
                seen_image_paths.add(card.image_path)
        return resolved, missing

    def load_selected_skill_images(
        self,
        skill_name: str,
        requested_identifiers: List[str],
        *,
        runtime: bool = True,
    ) -> Tuple[List[SkillStateCard], List[Tuple[str, str, str]], List[str]]:
        """
        Resolve and load only the requested skill images.
        """
        selected_cards, missing = self.resolve_state_card_image_requests(
            skill_name,
            requested_identifiers,
            runtime=runtime,
        )
        loaded_cards: List[SkillStateCard] = []
        loaded_images: List[Tuple[str, str, str]] = []
        failed_loads: List[str] = []
        for card in selected_cards:
            image_result = self.load_single_skill_image(skill_name, card.image_path or card.image_id)
            if image_result is None:
                failed_loads.append(card.image_id or card.state_id or card.image_path)
                continue
            loaded_cards.append(card)
            loaded_images.append(image_result)
        return loaded_cards, loaded_images, missing + failed_loads

    def resolve_state_view_requests(
        self,
        skill_name: str,
        requested_items: List[Dict[str, object]],
        *,
        runtime: bool = True,
    ) -> Tuple[List[ResolvedSkillStateSelection], List[str]]:
        """
        Resolve stage-1 state/view requests against the bundle metadata.

        Each requested item should contain:
        - `state_id`
        - `views`: list[str]
        - optional `reason`
        """
        state_bundles = self.load_state_bundles(skill_name, runtime=runtime)
        if state_bundles is None or not state_bundles.bundles:
            return [], ["No state bundles are available for this skill."]

        by_state: Dict[str, SkillStateBundle] = {}
        for bundle in state_bundles.bundles:
            normalized = self._normalize_state_card_selector(bundle.state_id)
            if normalized:
                by_state[normalized] = bundle

        merged: Dict[str, ResolvedSkillStateSelection] = {}
        missing: List[str] = []
        for raw_item in requested_items or []:
            if not isinstance(raw_item, dict):
                missing.append(str(raw_item))
                continue
            raw_state_id = str(raw_item.get("state_id", "") or "").strip()
            normalized_state_id = self._normalize_state_card_selector(raw_state_id)
            bundle = by_state.get(normalized_state_id)
            if bundle is None:
                missing.append(f"state_id:{raw_state_id or '(missing)'}")
                continue

            raw_views = raw_item.get("views", [])
            requested_view_types = [
                str(view_type).strip()
                for view_type in raw_views
                if str(view_type).strip()
            ] if isinstance(raw_views, list) else []
            if not requested_view_types:
                default_view = self._select_bundle_default_view(bundle)
                requested_view_types = [default_view.view_type] if default_view is not None else []

            reason = str(raw_item.get("reason", "") or "").strip()
            selection = merged.get(bundle.state_id)
            if selection is None:
                selection = ResolvedSkillStateSelection(
                    state=bundle,
                    requested_view_types=[],
                    reason=reason,
                    loaded_views=[],
                )
                merged[bundle.state_id] = selection
            elif reason and not selection.reason:
                selection.reason = reason

            available_by_view = {
                self._normalize_state_card_selector(view.view_type): view
                for view in bundle.available_views
                if self._normalize_state_card_selector(view.view_type)
            }
            for view_type in requested_view_types:
                normalized_view = self._normalize_state_card_selector(view_type)
                if normalized_view not in available_by_view:
                    missing.append(f"{bundle.state_id}:{view_type}")
                    continue
                if view_type not in selection.requested_view_types:
                    selection.requested_view_types.append(view_type)

        return list(merged.values()), missing

    def load_selected_state_views(
        self,
        skill_name: str,
        requested_items: List[Dict[str, object]],
        *,
        runtime: bool = True,
    ) -> Tuple[List[ResolvedSkillStateSelection], List[str]]:
        """
        Resolve and load only the requested state/view images for v7 branches.
        """
        resolved_selections, missing = self.resolve_state_view_requests(
            skill_name,
            requested_items,
            runtime=runtime,
        )

        loaded_selections: List[ResolvedSkillStateSelection] = []
        failed_loads: List[str] = []
        for selection in resolved_selections:
            available_by_view = {
                self._normalize_state_card_selector(view.view_type): view
                for view in selection.state.available_views
                if self._normalize_state_card_selector(view.view_type)
            }
            loaded_views: List[LoadedSkillStateView] = []
            for requested_view_type in selection.requested_view_types:
                view = available_by_view.get(self._normalize_state_card_selector(requested_view_type))
                if view is None:
                    failed_loads.append(f"{selection.state.state_id}:{requested_view_type}")
                    continue
                image_result = self.load_single_skill_image(skill_name, view.image_path)
                if image_result is None:
                    failed_loads.append(f"{selection.state.state_id}:{requested_view_type}")
                    continue
                loaded_views.append(LoadedSkillStateView(view=view, image=image_result))

            if loaded_views:
                selection.loaded_views = loaded_views
                loaded_selections.append(selection)

        return loaded_selections, missing + failed_loads

    def load_single_skill_image(
        self, skill_name: str, image_name: str
    ) -> Optional[Tuple[str, str, str]]:
        """
        Load a single image by filename from a skill's Images/ directory.

        This is the core method for dynamic per-image loading. The agent reads
        the SKILL.md text (already in its context), identifies which state it
        is in, and requests the specific image referenced in that state.

        Args:
            skill_name: Skill directory name (e.g., "Chrome_Enable_Developer_Mode")
            image_name: Image filename (e.g., "developer_mode_off.png").
                        Can also be a relative path like "Images/developer_mode_off.png".

        Returns:
            (filename, base64_encoded_data, mime_type) tuple, or None if not found.
        """
        resolved = self._resolve_skill_identifier_and_dir(skill_name)
        if resolved is None:
            logger.warning(f"[SkillLoader] Skill directory not found for identifier: {skill_name}")
            return None
        _, skill_dir = resolved

        # Normalise: strip leading "Images/" if provided, then look in Images/
        clean_name = image_name
        if clean_name.startswith("Images/"):
            clean_name = clean_name[len("Images/"):]

        img_path = skill_dir / "Images" / clean_name
        if not img_path.exists():
            # Try case-insensitive fallback in Images directory
            images_dir = skill_dir / "Images"
            if images_dir.exists():
                for f in images_dir.iterdir():
                    if f.name.lower() == clean_name.lower():
                        img_path = f
                        break
            if not img_path.exists():
                logger.warning(f"[SkillLoader] Image not found: {img_path}")
                return None

        try:
            img_bytes = img_path.read_bytes()
            b64, resized_width, resized_height = preprocess_image_for_vlm(img_bytes)
            mime = "image/png"
            logger.info(
                f"[SkillLoader] ✓ Loaded image '{img_path.name}' for skill "
                f"'{skill_name}' ({len(img_bytes):,} bytes -> {resized_width}x{resized_height}, {mime})"
            )
            return img_path.name, b64, mime
        except Exception as e:
            logger.error(f"[SkillLoader] ✗ Failed to load {img_path}: {e}")
            return None

    def load_skill_images(self, skill_name: str) -> List[Tuple[str, str, str]]:
        """
        Load ALL images for a skill (legacy / fallback).
        Discovers images by scanning the Images/ subdirectory.

        Returns:
            List of (filename, base64_encoded_data, mime_type) tuples.
        """
        resolved = self._resolve_skill_identifier_and_dir(skill_name)
        if resolved is None:
            logger.warning(f"[SkillLoader] Skill directory not found for identifier: {skill_name}")
            return []
        _, skill_dir = resolved

        images_dir = skill_dir / "Images"
        if not images_dir.exists():
            for d in skill_dir.iterdir():
                if d.is_dir() and d.name.lower() == "images":
                    images_dir = d
                    break
            else:
                logger.warning(f"[SkillLoader] Images directory not found for skill '{skill_name}'")
                return []

        results: List[Tuple[str, str, str]] = []
        image_extensions = {".png", ".jpg", ".jpeg", ".gif", ".webp", ".bmp"}
        image_files = [f for f in images_dir.iterdir() if f.suffix.lower() in image_extensions]

        for img_file in sorted(image_files):
            try:
                img_bytes = img_file.read_bytes()
                b64, resized_width, resized_height = preprocess_image_for_vlm(img_bytes)
                mime = "image/png"
                results.append((img_file.name, b64, mime))
                logger.debug(
                    "[SkillLoader] Preprocessed skill image '%s' for '%s' -> %sx%s",
                    img_file.name,
                    skill_name,
                    resized_width,
                    resized_height,
                )
            except Exception as e:
                logger.error(f"[SkillLoader] ✗ Failed to load {img_file.name}: {e}")

        logger.info(f"[SkillLoader] Loaded {len(results)} images for skill '{skill_name}'")
        return results

    def get_skill_image_by_reference(self, skill_name: str, image_ref: str) -> Optional[Tuple[str, str]]:
        """
        Load a single image by its reference path as written in SKILL.md.

        Args:
            skill_name: Skill directory name.
            image_ref: Reference path like "Images/developer_mode_off.png".

        Returns:
            (base64_data, mime_type) or None if not found.
        """
        resolved = self._resolve_skill_identifier_and_dir(skill_name)
        if resolved is None:
            return None
        _, skill_dir = resolved
        img_path = skill_dir / image_ref
        if not img_path.exists():
            return None

        try:
            img_bytes = img_path.read_bytes()
            b64, _, _ = preprocess_image_for_vlm(img_bytes)
            mime = "image/png"
            return b64, mime
        except Exception as e:
            logger.error(f"Failed to load image {img_path}: {e}")
            return None

    # ------------------------------------------------------------------ #
    #  Full skill loading (text + all images in one call)
    # ------------------------------------------------------------------ #

    def load_full_skill(self, skill_name: str) -> Optional[Dict]:
        """
        Load a skill's complete content: full SKILL.md text + all images
        from the Images/ directory.

        This is the method used for on-demand skill loading. When the agent
        recognises it needs a particular skill, it calls the `load_skill` tool
        which triggers this method.

        Args:
            skill_name: Skill directory name, e.g. "Chrome_Enable_Developer_Mode"

        Returns:
            A dict with:
              - "content": SkillContent object (text, name, description, etc.)
              - "images": list of (filename, base64_data, mime_type) tuples
            or None if the skill directory does not exist.
        """
        content = self._load_skill_content(skill_name)
        if content is None:
            logger.warning(f"[SkillLoader] Skill '{skill_name}' not found for full load")
            return None

        images = self.load_skill_images(skill_name)
        logger.info(
            f"[SkillLoader] Full-loaded skill '{skill_name}': "
            f"{len(content.text)} chars text, {len(images)} image(s)"
        )
        return {"content": content, "images": images}

    def format_full_skill_for_messages(
        self, skill_name: str, full_skill: Dict
    ) -> List[dict]:
        """
        Format a fully-loaded skill (text + images) into OpenAI-compatible
        message content parts that can be injected as a user message.

        The output contains:
          1. A text part with the full SKILL.md content
          2. For each image: a text label + an image_url part

        Args:
            skill_name: Skill directory name
            full_skill: Dict returned by load_full_skill()

        Returns:
            List of content parts (text + image_url dicts)
        """
        content: SkillContent = full_skill["content"]
        images: List[Tuple[str, str, str]] = full_skill["images"]

        parts: List[dict] = []

        # 1. Full SKILL.md text
        parts.append({
            "type": "text",
            "text": (
                f"# Skill Loaded: {content.name}\n\n"
                f"{content.text}\n\n"
                "Follow the State-Action Mappings above carefully. "
                "The images below are visual references for each state described in the skill."
            ),
        })

        # 2. All images with labels
        if images:
            for filename, b64_data, mime_type in images:
                parts.append({
                    "type": "text",
                    "text": f"[Visual Reference — {filename}]:",
                })
                parts.append({
                    "type": "image_url",
                    "image_url": {
                        "url": f"data:{mime_type};base64,{b64_data}"
                    },
                })

        return parts

    def format_text_only_skill_for_messages(
        self, skill_name: str, full_skill: Dict
    ) -> List[dict]:
        """
        Format a loaded skill as text-only message content.

        This is used when the agent is configured with `skill_mode=text_only`.
        Only the SKILL.md content is injected; no visual reference images are
        included in the prompt.
        """
        content: SkillContent = full_skill["content"]
        return [
            {
                "type": "text",
                "text": (
                    f"# Skill Loaded: {content.name}\n\n"
                    f"{content.text}\n\n"
                    "This skill was loaded in text-only mode. "
                    "Use the procedural instructions above when choosing the next action."
                ),
            }
        ]

    # ------------------------------------------------------------------ #
    #  Formatting helpers for prompt injection
    # ------------------------------------------------------------------ #

    def format_skills_meta_prompt(self, skill_metadatas: List[SkillMetadata]) -> str:
        """
        Build a compact meta-only prompt listing available skills.
        Only includes name + description — NO full SKILL.md content.

        This is injected into the system prompt at the start of a task so the
        agent knows what skills exist and can decide which to load on-demand.
        """
        if not skill_metadatas:
            return ""

        lines = [
            "# Available Skills (Meta Information)",
            "",
            "The following procedural skills are available. Each skill contains "
            "detailed step-by-step instructions (State-Action Mappings) and visual "
            "references (annotated screenshots) for specific UI operations.",
            "",
            "**IMPORTANT**: These skills are NOT loaded yet. You only see their "
            "names and descriptions below. When you recognise that the current task "
            "or UI state requires a specific skill, you MUST proactively load it "
            "using the `load_skill` tool BEFORE attempting the corresponding UI "
            "actions. Loading a skill gives you the full instructions and all "
            "visual reference images.",
            "",
        ]

        for i, meta in enumerate(skill_metadatas, 1):
            dir_name = Path(meta.directory).name
            lines.append(f"{i}. **{meta.name}** (`{dir_name}`) — {meta.description}")

        lines.append("")
        return "\n".join(lines)

    def format_skill_index(self, skill_names: List[str]) -> str:
        """
        Build a concise skill index block for the system prompt.
        Lists available skills with name + description so the agent knows
        what procedural knowledge is available.
        """
        if not skill_names:
            return ""

        all_metadata = self.discover_all_skills()
        meta_map = {Path(m.directory).name: m for m in all_metadata}

        lines = ["# Available Skills", ""]
        lines.append("The following procedural skills are available to guide you. "
                      "Each skill provides step-by-step instructions (State-Action Mappings) for specific UI operations.")
        lines.append("")

        for i, name in enumerate(skill_names, 1):
            meta = meta_map.get(name)
            if meta:
                lines.append(f"{i}. **{meta.name}** - {meta.description}")
            else:
                lines.append(f"{i}. **{name}** - (description not available)")

        lines.append("")
        lines.append("You can request to load a skill's full instructions or visual references using the skill tools below.")
        lines.append("")
        return "\n".join(lines)

    def format_skill_text(self, skill_content: SkillContent) -> str:
        """Format a single skill's full text for injection into context."""
        return (
            f"## Skill: {skill_content.name}\n\n"
            f"{skill_content.text}\n"
        )

    def format_all_skills_text(self, skill_contents: List[SkillContent]) -> str:
        """Format all loaded skills' text into a single block."""
        if not skill_contents:
            return ""

        sections = [
            "# Loaded Skills - Procedural Knowledge\n",
            "Below are detailed step-by-step guides for the skills required by this task. "
            "Follow the State-Action Mappings carefully. When you encounter a described state "
            "in the screenshot, apply the corresponding action.\n",
        ]
        for content in skill_contents:
            sections.append(self.format_skill_text(content))
            sections.append("---\n")

        return "\n".join(sections)

    def format_single_skill_image_for_message(
        self, skill_name: str, image: Tuple[str, str, str]
    ) -> List[dict]:
        """
        Format a single loaded skill image as message content parts (OpenAI-compatible).

        Args:
            skill_name: Name of the skill
            image: (filename, base64_data, mime_type) tuple

        Returns a list of content parts:
        [
            {"type": "text", "text": "Visual reference ..."},
            {"type": "image_url", "image_url": {"url": "data:image/png;base64,..."}},
        ]
        """
        filename, b64_data, mime_type = image
        return [
            {
                "type": "text",
                "text": f"Visual reference for skill '{skill_name}' — [{filename}]:"
            },
            {
                "type": "image_url",
                "image_url": {
                    "url": f"data:{mime_type};base64,{b64_data}"
                }
            },
        ]

    def format_skill_images_for_message(
        self, skill_name: str, images: List[Tuple[str, str, str]]
    ) -> List[dict]:
        """
        Format loaded skill images as message content parts (OpenAI-compatible format).
        Kept for backward compatibility / bulk loading.
        """
        if not images:
            return []

        parts: List[dict] = []
        parts.append({
            "type": "text",
            "text": f"Visual references for skill '{skill_name}':"
        })

        for filename, b64_data, mime_type in images:
            parts.append({
                "type": "text",
                "text": f"[{filename}]:"
            })
            parts.append({
                "type": "image_url",
                "image_url": {
                    "url": f"data:{mime_type};base64,{b64_data}"
                }
            })

        return parts

    # ------------------------------------------------------------------ #
    #  Internal helpers
    # ------------------------------------------------------------------ #

    def _load_skill_content(self, dir_name: str) -> Optional[SkillContent]:
        """Load and cache a single skill's full content."""
        resolved = self._resolve_skill_identifier_and_dir(dir_name)
        if resolved is None:
            return None
        skill_id, skill_dir = resolved

        if skill_id in self._content_cache:
            return self._content_cache[skill_id]

        # Find SKILL.md (case-insensitive)
        skill_md = self._find_skill_md(skill_dir)
        if skill_md is None:
            return None

        raw_text = skill_md.read_text(encoding="utf-8")
        if len(raw_text) > self._max_skill_chars:
            raw_text = raw_text[: self._max_skill_chars] + "\n(Truncated)"

        frontmatter = self._parse_frontmatter(raw_text)
        body = self._strip_frontmatter(raw_text)

        # Extract image references from the text
        image_refs = self._extract_image_references(body)

        content = SkillContent(
            name=frontmatter.get("name", dir_name),
            description=frontmatter.get("description", ""),
            text=body,
            image_references=image_refs,
            directory=str(skill_dir),
        )
        self._content_cache[skill_id] = content
        return content

    @staticmethod
    def _resolve_state_schema_path(skill_dir: Path, *, runtime: bool) -> Optional[Path]:
        preferred_name = "runtime_state_cards.json" if runtime else "state_cards.json"
        fallback_name = "state_cards.json" if runtime else None

        state_path = skill_dir / preferred_name
        if not state_path.exists() and fallback_name:
            state_path = skill_dir / fallback_name
        return state_path if state_path.exists() else None

    @staticmethod
    def _read_state_schema_payload(state_path: Path) -> Optional[Dict[str, object]]:
        try:
            payload = json.loads(state_path.read_text(encoding="utf-8"))
        except Exception as exc:
            logger.error("[SkillLoader] Failed to parse %s: %s", state_path, exc)
            return None
        if not isinstance(payload, dict):
            logger.warning("[SkillLoader] State schema in %s is not a JSON object", state_path)
            return None
        return payload

    def _parse_state_card_payload(
        self,
        *,
        skill_name: str,
        state_path: Path,
        payload: Dict[str, object],
    ) -> Optional[SkillStateCardSet]:
        if not isinstance(payload, dict):
            logger.warning("[SkillLoader] State card payload in %s is not a JSON object", state_path)
            return None
        raw_cards = payload.get("cards", [])
        if not isinstance(raw_cards, list):
            logger.warning("[SkillLoader] State card payload in %s has non-list 'cards'", state_path)
            return None

        cards: List[SkillStateCard] = []
        for item in raw_cards:
            if not isinstance(item, dict):
                continue
            cards.append(
                SkillStateCard(
                    state_id=str(item.get("state_id", "") or "").strip(),
                    image_id=str(item.get("image_id", "") or "").strip(),
                    image_path=str(item.get("image_path", "") or "").strip(),
                    stage=str(item.get("stage", "") or "").strip(),
                    image_role=str(item.get("image_role", "") or "").strip(),
                    when_to_use=str(item.get("when_to_use", "") or "").strip(),
                    when_not_to_use=str(item.get("when_not_to_use", "") or "").strip(),
                    visible_cues=[
                        str(cue).strip()
                        for cue in item.get("visible_cues", [])
                        if str(cue).strip()
                    ]
                    if isinstance(item.get("visible_cues", []), list)
                    else [],
                    verification_cue=str(item.get("verification_cue", "") or "").strip(),
                    visual_risk=str(item.get("visual_risk", "") or "").strip(),
                    recommended_verification=str(item.get("recommended_verification", "") or "").strip(),
                    non_transferable_parts=[
                        str(part).strip()
                        for part in item.get("non_transferable_parts", [])
                        if str(part).strip()
                    ]
                    if isinstance(item.get("non_transferable_parts", []), list)
                    else [],
                    highlight_targets=[
                        target for target in item.get("highlight_targets", [])
                        if isinstance(target, dict)
                    ]
                    if isinstance(item.get("highlight_targets", []), list)
                    else [],
                    raw=dict(item),
                )
            )

        return SkillStateCardSet(
            skill_name=skill_name,
            schema_version=str(payload.get("schema_version", "") or "").strip(),
            source_file=state_path.name,
            card_granularity=str(payload.get("card_granularity", "") or "").strip(),
            domain=str(payload.get("domain", "") or "").strip(),
            generation_method=str(payload.get("generation_method", "") or "").strip(),
            cards=cards,
        )

    def _parse_state_bundle_payload(
        self,
        *,
        skill_name: str,
        state_path: Path,
        payload: Dict[str, object],
    ) -> Optional[SkillStateBundleSet]:
        if not isinstance(payload, dict):
            logger.warning("[SkillLoader] State bundle payload in %s is not a JSON object", state_path)
            return None
        raw_states = payload.get("states", [])
        if not isinstance(raw_states, list):
            logger.warning("[SkillLoader] State bundle payload in %s has non-list 'states'", state_path)
            return None

        bundles: List[SkillStateBundle] = []
        for item in raw_states:
            if not isinstance(item, dict):
                continue
            available_views: List[SkillStateView] = []
            raw_available_views = item.get("available_views", [])
            if isinstance(raw_available_views, list):
                for raw_view in raw_available_views:
                    if not isinstance(raw_view, dict):
                        continue
                    available_views.append(
                        SkillStateView(
                            view_type=str(raw_view.get("view_type", "") or "").strip(),
                            image_path=str(raw_view.get("image_path", "") or "").strip(),
                            use_for=str(raw_view.get("use_for", "") or "").strip(),
                            label=str(raw_view.get("label", "") or "").strip(),
                            raw=dict(raw_view),
                        )
                    )

            visual_evidence_chain = item.get("visual_evidence_chain", {})
            if not isinstance(visual_evidence_chain, dict):
                visual_evidence_chain = {}

            preferred_view_order = item.get("preferred_view_order", [])
            bundles.append(
                SkillStateBundle(
                    state_id=str(item.get("state_id", "") or "").strip(),
                    state_name=str(item.get("state_name", "") or "").strip(),
                    stage=str(item.get("stage", "") or "").strip(),
                    image_role=str(item.get("image_role", "") or "").strip(),
                    when_to_use=str(item.get("when_to_use", "") or "").strip(),
                    when_not_to_use=str(item.get("when_not_to_use", "") or "").strip(),
                    visible_cues=[
                        str(cue).strip()
                        for cue in item.get("visible_cues", [])
                        if str(cue).strip()
                    ]
                    if isinstance(item.get("visible_cues", []), list)
                    else [],
                    verification_cue=str(item.get("verification_cue", "") or "").strip(),
                    visual_risk=str(item.get("visual_risk", "") or "").strip(),
                    preferred_view_order=[
                        str(view_name).strip()
                        for view_name in preferred_view_order
                        if str(view_name).strip()
                    ]
                    if isinstance(preferred_view_order, list)
                    else [],
                    visual_evidence_chain={
                        str(key).strip(): str(value).strip()
                        for key, value in visual_evidence_chain.items()
                        if str(key).strip() and str(value).strip()
                    },
                    available_views=available_views,
                    raw=dict(item),
                )
            )

        return SkillStateBundleSet(
            skill_name=skill_name,
            schema_version=str(payload.get("schema_version", "") or "").strip(),
            source_file=state_path.name,
            card_granularity=str(payload.get("card_granularity", "") or "").strip(),
            domain=str(payload.get("domain", "") or "").strip(),
            generation_method=str(payload.get("generation_method", "") or "").strip(),
            bundles=bundles,
        )

    def _convert_state_cards_to_bundle_set(
        self,
        *,
        skill_name: str,
        state_path: Path,
        state_cards: Optional[SkillStateCardSet],
    ) -> Optional[SkillStateBundleSet]:
        if state_cards is None or not state_cards.cards:
            return None

        bundles: List[SkillStateBundle] = []
        for card in state_cards.cards:
            selector = card.image_id or card.state_id or Path(card.image_path).stem
            label = selector
            available_view = SkillStateView(
                view_type="full_frame",
                image_path=card.image_path,
                use_for="legacy_single_reference",
                label=label,
                raw=dict(card.raw),
            )
            bundles.append(
                SkillStateBundle(
                    state_id=card.state_id or selector,
                    state_name=selector,
                    stage=card.stage,
                    image_role=card.image_role,
                    when_to_use=card.when_to_use,
                    when_not_to_use=card.when_not_to_use,
                    visible_cues=list(card.visible_cues),
                    verification_cue=card.verification_cue or card.recommended_verification,
                    visual_risk=card.visual_risk,
                    preferred_view_order=["full_frame"],
                    visual_evidence_chain={},
                    available_views=[available_view] if card.image_path else [],
                    raw=dict(card.raw),
                )
            )

        return SkillStateBundleSet(
            skill_name=skill_name,
            schema_version=state_cards.schema_version,
            source_file=state_path.name,
            card_granularity=state_cards.card_granularity or "legacy_single_view",
            domain=state_cards.domain,
            generation_method=state_cards.generation_method,
            bundles=bundles,
        )

    def _flatten_state_bundles_to_card_set(
        self,
        *,
        skill_name: str,
        state_path: Path,
        bundle_set: Optional[SkillStateBundleSet],
    ) -> Optional[SkillStateCardSet]:
        if bundle_set is None or not bundle_set.bundles:
            return None

        cards: List[SkillStateCard] = []
        for bundle in bundle_set.bundles:
            default_view = self._select_bundle_default_view(bundle)
            cards.append(
                SkillStateCard(
                    state_id=bundle.state_id,
                    image_id=bundle.state_id,
                    image_path=default_view.image_path if default_view is not None else "",
                    stage=bundle.stage,
                    image_role=bundle.image_role,
                    when_to_use=bundle.when_to_use,
                    when_not_to_use=bundle.when_not_to_use,
                    visible_cues=list(bundle.visible_cues),
                    verification_cue=bundle.verification_cue,
                    visual_risk=bundle.visual_risk,
                    recommended_verification=bundle.verification_cue,
                    non_transferable_parts=[],
                    highlight_targets=[],
                    raw={
                        **dict(bundle.raw),
                        "available_views": [dict(view.raw) for view in bundle.available_views],
                    },
                )
            )

        return SkillStateCardSet(
            skill_name=skill_name,
            schema_version=bundle_set.schema_version,
            source_file=state_path.name,
            card_granularity=bundle_set.card_granularity,
            domain=bundle_set.domain,
            generation_method=bundle_set.generation_method,
            cards=cards,
        )

    @staticmethod
    def _select_bundle_default_view(bundle: SkillStateBundle) -> Optional[SkillStateView]:
        if not bundle.available_views:
            return None

        available_by_type = {
            SkillLoader._normalize_state_card_selector(view.view_type): view
            for view in bundle.available_views
            if SkillLoader._normalize_state_card_selector(view.view_type)
        }
        full_frame = available_by_type.get("full_frame")
        if full_frame is not None:
            return full_frame
        for preferred in bundle.preferred_view_order:
            preferred_view = available_by_type.get(SkillLoader._normalize_state_card_selector(preferred))
            if preferred_view is not None:
                return preferred_view
        return bundle.available_views[0]

    @staticmethod
    def _truncate_text(text: str, max_chars: int) -> str:
        text = " ".join((text or "").split())
        if len(text) <= max_chars:
            return text
        return text[: max_chars - 3].rstrip() + "..."

    @staticmethod
    def _normalize_state_card_selector(selector: object) -> str:
        if selector is None:
            return ""
        normalized = str(selector).strip().replace("\\", "/")
        if normalized.startswith("./"):
            normalized = normalized[2:]
        return normalized

    def _ensure_skill_index(self) -> None:
        """Build an index of available skills for both flat and nested libraries."""
        if self._skill_index_built:
            return

        self._skill_id_to_dir = {}
        self._basename_to_skill_ids = {}

        if not self._skills_dir.exists():
            self._skill_index_built = True
            return

        for root, _, files in os.walk(self._skills_dir):
            if not any(name.lower() == "skill.md" for name in files):
                continue
            skill_dir = Path(root)
            skill_id = skill_dir.relative_to(self._skills_dir).as_posix()
            self._skill_id_to_dir[skill_id] = skill_dir
            self._basename_to_skill_ids.setdefault(skill_dir.name, []).append(skill_id)

        for skill_ids in self._basename_to_skill_ids.values():
            skill_ids.sort()

        self._skill_index_built = True

    def _resolve_skill_identifier_and_dir(self, skill_name: str) -> Optional[Tuple[str, Path]]:
        """Resolve either a flat skill name or a nested relative path to a skill directory."""
        if not skill_name:
            return None

        self._ensure_skill_index()

        normalized = skill_name.strip().replace("\\", "/").strip("/")
        if normalized in self._skill_id_to_dir:
            return normalized, self._skill_id_to_dir[normalized]

        basename = Path(normalized).name
        candidates = self._basename_to_skill_ids.get(basename, [])
        if not candidates:
            return None
        if len(candidates) > 1:
            logger.warning(
                "[SkillLoader] Multiple skills share basename '%s': %s. Using %s",
                basename,
                candidates,
                candidates[0],
            )
        skill_id = candidates[0]
        return skill_id, self._skill_id_to_dir[skill_id]

    @staticmethod
    def _find_skill_md(skill_dir: Path) -> Optional[Path]:
        """Find SKILL.md in a directory with case-insensitive fallback."""
        skill_md = skill_dir / "SKILL.md"
        if skill_md.exists():
            return skill_md
        for f in skill_dir.iterdir():
            if f.name.lower() == "skill.md":
                return f
        return None

    @staticmethod
    def _parse_frontmatter(text: str) -> Dict[str, str]:
        """Parse YAML-like frontmatter from SKILL.md."""
        lines = text.splitlines()
        if not lines or lines[0].strip() != "---":
            return {}

        end_index = None
        for i in range(1, len(lines)):
            if lines[i].strip() == "---":
                end_index = i
                break

        if end_index is None:
            return {}

        metadata: Dict[str, str] = {}
        for line in lines[1:end_index]:
            if ":" not in line:
                continue
            key, value = line.split(":", 1)
            key = key.strip()
            value = value.strip().strip('"').strip("'")
            metadata[key] = value

        return metadata

    @staticmethod
    def _strip_frontmatter(text: str) -> str:
        """Remove YAML frontmatter from text, returning the body."""
        lines = text.splitlines()
        if not lines or lines[0].strip() != "---":
            return text

        end_index = None
        for i in range(1, len(lines)):
            if lines[i].strip() == "---":
                end_index = i
                break

        if end_index is None:
            return text

        return "\n".join(lines[end_index + 1:]).strip()

    @staticmethod
    def _extract_image_references(text: str) -> List[str]:
        """Extract image file references like `Images/foo.png` from SKILL.md body."""
        pattern = r'`?(Images/[^`\s\)]+\.(?:png|jpg|jpeg|gif|webp|bmp))`?'
        return re.findall(pattern, text, re.IGNORECASE)

    @staticmethod
    def _get_mime_type(suffix: str) -> str:
        mime_map = {
            ".png": "image/png",
            ".jpg": "image/jpeg",
            ".jpeg": "image/jpeg",
            ".gif": "image/gif",
            ".webp": "image/webp",
            ".bmp": "image/bmp",
        }
        return mime_map.get(suffix.lower(), "image/png")
