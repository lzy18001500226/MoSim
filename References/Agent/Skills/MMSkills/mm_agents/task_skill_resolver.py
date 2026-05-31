import json
import logging
from pathlib import Path
from typing import Dict, List, Optional, Sequence, Tuple

from mm_agents.skill_loader import SkillLoader

logger = logging.getLogger("desktopenv.task_skill_resolver")

_RESOLVER_CACHE: Dict[Tuple[Optional[str], str, Optional[int]], "TaskSkillResolver"] = {}


class TaskSkillResolver:
    """Resolve external task->skills mappings into concrete skill directory names."""

    _PRIORITY_ORDER = {
        "P0": 0,
        "P1": 1,
        "P2": 2,
        "P3": 3,
    }

    def __init__(
        self,
        skills_library_dir: str,
        mapping_root: Optional[str] = None,
        top_k: Optional[int] = 6,
    ) -> None:
        self._skills_library_dir = skills_library_dir
        self._mapping_root = self._resolve_path(mapping_root) if mapping_root else None
        self._top_k = top_k if top_k and top_k > 0 else None
        self._domain_mapping_cache: Dict[str, Optional[dict]] = {}
        self._global_mapping_cache: Optional[dict] = None
        self._all_skill_dirs: set[str] = set()
        self._name_to_dirs: Dict[str, List[str]] = {}
        self._normalized_name_to_dirs: Dict[str, List[str]] = {}
        self._index_built = False

    def resolve_task_skills(
        self,
        *,
        domain: Optional[str],
        task_id: Optional[str],
        fallback_skill_names: Optional[Sequence[str]] = None,
    ) -> List[str]:
        """Return concrete skill directory names for the current task."""
        source_names: List[str] = []
        source = "task_json"

        if domain and task_id:
            mapped_entries = self._lookup_mapped_entries(domain, task_id)
            if mapped_entries is not None:
                source_names = self._select_top_skills(mapped_entries)
                source = "external_mapping"

        if not source_names and fallback_skill_names:
            source_names = list(fallback_skill_names)

        resolved_names: List[str] = []
        for raw_name in source_names:
            directory_name = self._resolve_skill_directory_name(raw_name, domain)
            if directory_name:
                if directory_name not in resolved_names:
                    resolved_names.append(directory_name)
                continue
            logger.warning(
                "Could not resolve skill '%s' for domain '%s' in task '%s'",
                raw_name,
                domain,
                task_id,
            )

        if resolved_names:
            logger.info(
                "[Skills] Resolved %d skill(s) for %s/%s from %s: %s",
                len(resolved_names),
                domain,
                task_id,
                source,
                resolved_names,
            )
        elif source_names:
            logger.warning(
                "[Skills] No concrete skill directories resolved for %s/%s from %s",
                domain,
                task_id,
                source,
            )
        elif (
            self._mapping_root
            and domain
            and not self._domain_mapping_file_exists(domain)
            and not (self._global_mapping_file() and self._global_mapping_file().exists())
        ):
            logger.info(
                "[Skills] No mapping file for domain '%s' under %s; continuing without task-specific skills",
                domain,
                self._mapping_root,
            )

        return resolved_names

    def _lookup_mapped_entries(self, domain: str, task_id: str) -> Optional[List[dict]]:
        mapping = self._load_domain_mapping(domain)
        if not mapping:
            return None

        if "task_to_skills" in mapping:
            task_entry = mapping.get("task_to_skills", {}).get(task_id)
            if task_entry is None:
                logger.info(
                    "[Skills] Task '%s' not found in external mapping for domain '%s'",
                    task_id,
                    domain,
                )
                return None
            return list(task_entry.get("skills", []))

        task_entry = mapping.get(task_id)
        if task_entry is None:
            logger.info(
                "[Skills] Task '%s' not found in external mapping for domain '%s'",
                task_id,
                domain,
            )
            return None

        # Open-source mapping format:
        # {
        #   "chrome": {
        #     "<task_id>": ["skill_a", "skill_b", ...]
        #   }
        # }
        if isinstance(task_entry, list):
            normalized_entries: List[dict] = []
            for idx, item in enumerate(task_entry):
                if isinstance(item, str) and item.strip():
                    normalized_entries.append(
                        {
                            "skill_name": item.strip(),
                            "priority": f"P{min(idx, 3)}",
                        }
                    )
                elif isinstance(item, dict) and str(item.get("skill_name", "")).strip():
                    normalized_entries.append(item)
            return normalized_entries or None

        if isinstance(task_entry, dict):
            if isinstance(task_entry.get("skills"), list):
                raw_skills = task_entry.get("skills", [])
                normalized_entries = []
                for idx, item in enumerate(raw_skills):
                    if isinstance(item, str) and item.strip():
                        normalized_entries.append(
                            {
                                "skill_name": item.strip(),
                                "priority": f"P{min(idx, 3)}",
                            }
                        )
                    elif isinstance(item, dict) and str(item.get("skill_name", "")).strip():
                        normalized_entries.append(item)
                return normalized_entries or None

        logger.warning(
            "[Skills] Unsupported mapping entry format for %s/%s: %s",
            domain,
            task_id,
            type(task_entry).__name__,
        )
        return None

    def _load_domain_mapping(self, domain: str) -> Optional[dict]:
        if domain in self._domain_mapping_cache:
            return self._domain_mapping_cache[domain]

        if not self._mapping_root:
            self._domain_mapping_cache[domain] = None
            return None

        mapping_file = self._mapping_file_for_domain(domain)
        global_mapping_file = self._global_mapping_file()

        # Prefer the legacy/generated per-domain file when present.
        if mapping_file is not None and mapping_file.exists():
            data = json.loads(mapping_file.read_text(encoding="utf-8"))
            self._domain_mapping_cache[domain] = data
            return data

        if global_mapping_file is not None and global_mapping_file.exists():
            global_mapping = self._load_global_mapping(global_mapping_file)
            domain_mapping = global_mapping.get(domain) if isinstance(global_mapping, dict) else None
            if domain_mapping is None:
                self._domain_mapping_cache[domain] = None
                return None
            if not isinstance(domain_mapping, dict):
                logger.warning(
                    "[Skills] Unsupported domain mapping format in %s for domain '%s': %s",
                    global_mapping_file,
                    domain,
                    type(domain_mapping).__name__,
                )
                self._domain_mapping_cache[domain] = None
                return None
            self._domain_mapping_cache[domain] = domain_mapping
            return domain_mapping

        self._domain_mapping_cache[domain] = None
        return None

    def _mapping_file_for_domain(self, domain: str) -> Optional[Path]:
        if not self._mapping_root:
            return None
        if self._mapping_root.is_file():
            return None
        return self._mapping_root / domain / "task_skill_mapping_generated.json"

    def _domain_mapping_file_exists(self, domain: str) -> bool:
        mapping_file = self._mapping_file_for_domain(domain)
        return bool(mapping_file is not None and mapping_file.exists())

    def _global_mapping_file(self) -> Optional[Path]:
        if not self._mapping_root:
            return None
        if self._mapping_root.is_file():
            return self._mapping_root

        candidate = self._mapping_root / "task_skill_mapping.json"
        if candidate.exists():
            return candidate
        return None

    def _load_global_mapping(self, mapping_file: Path) -> dict:
        if self._global_mapping_cache is not None:
            return self._global_mapping_cache

        data = json.loads(mapping_file.read_text(encoding="utf-8"))
        if not isinstance(data, dict):
            logger.warning(
                "[Skills] Global mapping file %s did not contain a JSON object. Got %s",
                mapping_file,
                type(data).__name__,
            )
            data = {}
        self._global_mapping_cache = data
        return data

    def _select_top_skills(self, skill_entries: Sequence[dict]) -> List[str]:
        ranked_entries = sorted(
            enumerate(skill_entries),
            key=lambda item: (
                self._priority_rank(item[1].get("priority")),
                item[0],
            ),
        )
        if self._top_k is not None:
            ranked_entries = ranked_entries[: self._top_k]
        return [
            entry.get("skill_name", "").strip()
            for _, entry in ranked_entries
            if entry.get("skill_name", "").strip()
        ]

    def _resolve_skill_directory_name(
        self, skill_name: str, domain: Optional[str]
    ) -> Optional[str]:
        if not skill_name:
            return None

        self._ensure_skill_index()

        if skill_name in self._all_skill_dirs:
            return skill_name

        candidates = list(self._name_to_dirs.get(skill_name, []))
        if not candidates:
            candidates = list(
                self._normalized_name_to_dirs.get(self._normalize(skill_name), [])
            )

        if not candidates:
            return None

        if len(candidates) == 1:
            return candidates[0]

        if domain:
            domain_prefix = domain.upper().replace("_", "")
            prefixed = [
                candidate
                for candidate in candidates
                if candidate.startswith(f"{domain_prefix}_")
            ]
            if len(prefixed) == 1:
                return prefixed[0]
            if prefixed:
                logger.warning(
                    "Multiple prefixed skills matched '%s' for domain '%s': %s. Using %s",
                    skill_name,
                    domain,
                    prefixed,
                    prefixed[0],
                )
                return prefixed[0]

        logger.warning(
            "Multiple skill directories matched '%s': %s. Using %s",
            skill_name,
            candidates,
            candidates[0],
        )
        return candidates[0]

    def _ensure_skill_index(self) -> None:
        if self._index_built:
            return

        skill_loader = SkillLoader(skills_library_dir=self._skills_library_dir)
        for meta in skill_loader.discover_all_skills():
            directory_name = Path(meta.directory).name
            self._all_skill_dirs.add(directory_name)
            self._name_to_dirs.setdefault(meta.name, []).append(directory_name)
            self._normalized_name_to_dirs.setdefault(
                self._normalize(meta.name), []
            ).append(directory_name)
            self._normalized_name_to_dirs.setdefault(
                self._normalize(directory_name), []
            ).append(directory_name)

        self._index_built = True

    @classmethod
    def _priority_rank(cls, priority: Optional[str]) -> int:
        return cls._PRIORITY_ORDER.get((priority or "").upper(), 99)

    @staticmethod
    def _normalize(value: str) -> str:
        return "".join(ch for ch in value.lower() if ch.isalnum())

    @staticmethod
    def _resolve_path(path_str: str) -> Path:
        path = Path(path_str).expanduser()
        return path if path.is_absolute() else Path.cwd() / path


def resolve_task_skill_names(
    *,
    domain: Optional[str],
    task_id: Optional[str],
    fallback_skill_names: Optional[Sequence[str]] = None,
    skills_library_dir: str = "skills_library",
    mapping_root: Optional[str] = None,
    top_k: Optional[int] = 6,
) -> List[str]:
    cache_key = (mapping_root, skills_library_dir, top_k if top_k and top_k > 0 else None)
    resolver = _RESOLVER_CACHE.get(cache_key)
    if resolver is None:
        resolver = TaskSkillResolver(
            skills_library_dir=skills_library_dir,
            mapping_root=mapping_root,
            top_k=top_k,
        )
        _RESOLVER_CACHE[cache_key] = resolver

    return resolver.resolve_task_skills(
        domain=domain,
        task_id=task_id,
        fallback_skill_names=fallback_skill_names,
    )
