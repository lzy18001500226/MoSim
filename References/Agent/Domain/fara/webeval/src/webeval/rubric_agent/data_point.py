"""DataPoint - the output of a single data generation run."""

from typing import (
    Annotated,
    Any,
    Dict,
    Iterable,
    List,
    Literal,
    Optional,
    Sequence,
    Tuple,
    Type,
    TypeVar,
    Union,
)
from datetime import datetime
from enum import Enum
import json
import os
import uuid

from pydantic import BaseModel, Field, model_validator


class Component(BaseModel):
    """Base class providing serialization/deserialization via pydantic."""

    def to_dict(self) -> Dict[str, Any]:
        return self.model_dump(mode="python")

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Component":
        return cls.model_validate(data)

    def save(self, path: os.PathLike) -> None:
        with open(path, "w") as f:
            json.dump(self.to_dict(), f, indent=2)

    @classmethod
    def load(cls, path: os.PathLike) -> "Component":
        with open(path, "r") as f:
            return cls.from_dict(json.load(f))


class SolverStatus(str, Enum):
    RUNNING = "running"
    COMPLETE = "complete"
    ABORTED = "aborted"
    WAITING_FOR_USER = "waiting_for_user"


class LLMUsage(Component):
    """Token usage from an LLM call."""

    prompt_tokens: int = 0
    completion_tokens: int = 0
    reasoning_tokens: int = 0


class LLMMessage(Component):
    """A single LLM call: request/response pair."""

    raw_response: str = ""
    reasoning: str = ""
    finish_reason: str = ""
    usage: LLMUsage = Field(default_factory=LLMUsage)


class LLMConversation(Component):
    """A sequence of LLM calls."""

    messages: List[LLMMessage] = Field(default_factory=list)

    @property
    def usage(self) -> LLMUsage:
        return LLMUsage(
            prompt_tokens=sum(m.usage.prompt_tokens for m in self.messages),
            completion_tokens=sum(m.usage.completion_tokens for m in self.messages),
            reasoning_tokens=sum(m.usage.reasoning_tokens for m in self.messages),
        )


class Outcome(Component):
    """Result of solving a task."""

    answer: str = ""


class Observation(Component):
    """Base class for things the agent observes."""

    type: Literal["observation"] = "observation"
    id: Optional[str] = None
    observation_type: str
    metadata: Dict[str, Any] = Field(default_factory=dict)
    timestamp: Optional[str] = None
    action_id: Optional[str] = None

    @model_validator(mode="before")
    @classmethod
    def _set_defaults(cls, data: Any) -> Any:
        if isinstance(data, dict):
            if data.get("id") is None:
                data["id"] = uuid.uuid4().hex
            if data.get("timestamp") is None:
                data["timestamp"] = datetime.now().isoformat()
        return data


class ComputerObservation(Observation):
    """Observation from the environment: screenshot and/or page state."""

    observation_type: Literal["environment"] = "environment"
    screenshot_path: str = ""
    url: str = ""
    page_info: str = ""


class ToolOutput(Observation):
    """Output from a tool/environment action."""

    observation_type: Literal["tool_output"] = "tool_output"
    output: str = ""
    error: str = ""


class UserMessageType(str, Enum):
    """Type of user message."""

    TASK = "task"
    FOLLOWUP_TASK = "followup_task"
    CRITICAL_POINT_RESPONSE = "critical_point_response"


class UserMessage(Observation):
    """A user message observation."""

    observation_type: Literal["user_message"] = "user_message"
    content: str = ""
    message_type: UserMessageType = UserMessageType.TASK


class AgentState(Component):
    """Snapshot of agent's internal state at decision time."""

    agent: str = ""
    tools_available: List[str] = Field(default_factory=list)
    plan: List[Dict[str, Any]] = Field(default_factory=list)
    facts: List[str] = Field(default_factory=list)


class Action(Component):
    """The agent's decision and action."""

    type: Literal["action"] = "action"
    id: Optional[str] = None
    timestamp: Optional[str] = None

    action_name: str = ""
    agent_state: AgentState = Field(default_factory=AgentState)
    llm_conversation: LLMConversation = Field(default_factory=LLMConversation)

    content: Dict[str, Any] = Field(default_factory=dict)
    action_nl_description: str = ""

    grounding: Optional[LLMConversation] = None

    @model_validator(mode="before")
    @classmethod
    def _set_defaults(cls, data: Any) -> Any:
        if isinstance(data, dict):
            if data.get("id") is None:
                data["id"] = uuid.uuid4().hex
            if data.get("timestamp") is None:
                data["timestamp"] = datetime.now().isoformat()
        return data


ObservationEvent = Annotated[
    Union[ComputerObservation, ToolOutput, UserMessage],
    Field(discriminator="observation_type"),
]

Event = Annotated[
    Union[ObservationEvent, Action],
    Field(discriminator="type"),
]

_O = TypeVar("_O", bound=Observation)
_T = TypeVar("_T")


def required(value: Optional[_T]) -> _T:
    """Unwrap an optional value, raising if None."""
    if value is None:
        raise ValueError("Required value is None")
    return value


def get_actions(events: Iterable[Event]) -> List[Action]:
    """Return actions from an event stream."""
    return [event for event in events if isinstance(event, Action)]


def get_observations(events: Iterable[Event], observation_type: Type[_O]) -> List[_O]:
    """Return observations of a specific type from an event stream."""
    return [event for event in events if isinstance(event, observation_type)]


def latest(observations: Sequence[_O]) -> Optional[_O]:
    """Return the last observation, or None if empty."""
    for obs in reversed(observations):
        return obs
    return None


def earliest(observations: Sequence[_O]) -> Optional[_O]:
    """Return the first observation, or None if empty."""
    for obs in observations:
        return obs
    return None


class ObservationsPre(BaseModel):
    """Observations before an action."""

    main: List[Observation] = Field(default_factory=list)
    previous_post: List[Observation] = Field(default_factory=list)
    late: Dict[str, List[Observation]] = Field(default_factory=dict)


class ObservationsPost(BaseModel):
    """Observations after an action."""

    main: List[Observation] = Field(default_factory=list)
    late: Dict[str, List[Observation]] = Field(default_factory=dict)
    next_pre: ObservationsPre = Field(default_factory=ObservationsPre)


class Step(BaseModel):
    """A single step: observations grouped around an action. Computed, never serialized."""

    observations_pre: ObservationsPre = Field(default_factory=ObservationsPre)
    action: Optional[Action] = None
    observations_post: ObservationsPost = Field(default_factory=ObservationsPost)


class StepSummary(BaseModel):
    """Per-step structured data extracted from SolverLog.steps."""

    index: int
    action_name: str = ""
    action_args: Dict[str, Any] = Field(default_factory=dict)
    action_nl_description: str = ""
    action_content: Dict[str, Any] = Field(default_factory=dict)
    url: str = ""
    state_description: str = ""
    previous_error: str = ""
    screenshot_path: str = ""
    user_messages_before: List[Tuple[UserMessageType, str]] = Field(
        default_factory=list
    )


class SolverConfig(Component):
    """Configuration for the solver."""

    hints: Optional[str] = None


class VerifierConfig(Component):
    """Configuration for task verification."""

    hints: Optional[str] = None
    config: List[Dict[str, Any]] = Field(default_factory=list)


class Task(Component):
    """Defines a task for the agent to solve."""

    task_id: str
    instruction: str
    images: List[str] = Field(default_factory=list)
    environment_config: Dict[str, Any] = Field(default_factory=dict)
    solver: SolverConfig = Field(default_factory=SolverConfig)
    verifier: VerifierConfig = Field(default_factory=VerifierConfig)
    metadata: Dict[str, Any] = Field(default_factory=dict)


class SolverLog(Component):
    """Solver output containing the sequence of observation-action steps."""

    events: List[Event] = Field(default_factory=list)
    status: SolverStatus = SolverStatus.RUNNING
    outcome: Optional[Outcome] = None

    def steps(self, with_tail_observations: bool = True) -> List[Step]:
        """Group events into steps based on action_id linkage.

        Args:
            with_tail_observations: If True (default), include a trailing step
                for observations that follow the last action. If False, only
                return steps that have an action.
        """

        def _append_late(
            d: Dict[str, List[Observation]], key: str, obs: Observation
        ) -> None:
            if key not in d:
                d[key] = []
            d[key].append(obs)

        # Pass 1: build steps with actions; collect all observations with action_id
        result: List[Step] = []
        current_pre: List[Observation] = []  # action_id=None only
        post_obs: List[
            tuple
        ] = []  # (obs, step_index_after) for observations with action_id
        for event in self.events:
            if isinstance(event, Action):
                result.append(
                    Step(
                        observations_pre=ObservationsPre(main=current_pre), action=event
                    )
                )
                current_pre = []
            elif event.action_id is None:
                current_pre.append(event)
            else:
                post_obs.append((event, len(result)))

        # Trailing observations with no action_id
        if with_tail_observations and current_pre:
            result.append(Step(observations_pre=ObservationsPre(main=current_pre)))

        # Pass 2: populate observations_post and observations_pre.late
        action_id_to_step_idx: Dict[str, int] = {}
        for i, step in enumerate(result):
            if step.action is not None and step.action.id is not None:
                action_id_to_step_idx[step.action.id] = i

        for obs, next_step_idx in post_obs:
            if obs.action_id not in action_id_to_step_idx:
                raise RuntimeError(
                    f"Observations reference action_id '{obs.action_id}' but no such action exists"
                )
            owner_idx = action_id_to_step_idx[obs.action_id]
            is_late = next_step_idx > owner_idx + 1
            result[owner_idx].observations_post.main.append(obs)
            if is_late:
                _append_late(
                    result[owner_idx].observations_post.late, obs.action_id, obs
                )
                if next_step_idx < len(result):
                    _append_late(
                        result[next_step_idx].observations_pre.late, obs.action_id, obs
                    )

        # Pass 3: link previous_post and next_pre
        for i in range(1, len(result)):
            result[i].observations_pre.previous_post = result[
                i - 1
            ].observations_post.main
        for i in range(len(result) - 1):
            result[i].observations_post.next_pre = result[i + 1].observations_pre

        return result

    def add_observation(self, observation: "ObservationEvent") -> None:
        self.events.append(observation)

    def add_action(self, action: Action) -> None:
        if self.events and isinstance(self.events[-1], Action):
            raise RuntimeError("Cannot add action: no observations since last action")
        self.events.append(action)

    def get_last_user_message(self) -> Optional[str]:
        """Return the content of the most recent UserMessage, or None if absent."""
        msg = latest(get_observations(self.events, UserMessage))
        return msg.content if msg else None

    def get_full_instruction(self) -> str:
        """Get the full instruction including follow-up tasks from user messages."""
        instructions = [
            msg.content
            for msg in get_observations(self.events, UserMessage)
            if msg.message_type in (UserMessageType.TASK, UserMessageType.FOLLOWUP_TASK)
        ]
        if len(instructions) == 1:
            return instructions[0]
        return "\n".join(f"{i + 1}. {inst}" for i, inst in enumerate(instructions))

    def _get_screenshot_and_user_msgs(
        self,
        step: Step,
    ) -> Tuple[str, List[Tuple[UserMessageType, str]]]:
        """Shared helper for screenshot lookup and user-message collection."""
        user_msgs: List[Tuple[UserMessageType, str]] = [
            (msg.message_type, msg.content)
            for msg in get_observations(step.observations_pre.main, UserMessage)
        ]

        post_obs = step.observations_post.main + step.observations_post.next_pre.main
        screenshot_obs = earliest(
            [
                obs
                for obs in get_observations(post_obs, ComputerObservation)
                if obs.screenshot_path
            ]
        )
        screenshot = screenshot_obs.screenshot_path if screenshot_obs else ""

        return screenshot, user_msgs

    def get_step_summaries(self) -> List[StepSummary]:
        """Extract structured per-step data for the current agent format.

        Current agents (GPT54Agent, ComputerAgent) log content as
        ``{"action": name, "arguments": {...}}``. The action name is read
        from ``Action.action_name``, and ``screen_description`` /
        ``reasoning`` are filtered out of ``action_args``.

        The URL is read from ``ComputerObservation.url`` on the most recent
        pre-action observation.
        """
        result: List[StepSummary] = []
        action_idx = 0
        for step in self.steps(with_tail_observations=False):
            action_idx += 1
            c = step.action.content
            args = c.get("arguments", {})
            filtered_args = {
                k: v
                for k, v in args.items()
                if k not in ("screen_description", "reasoning")
            }

            screenshot, user_msgs = self._get_screenshot_and_user_msgs(step)

            pre_obs = step.observations_pre.previous_post + step.observations_pre.main
            url_obs = latest(
                [
                    obs
                    for obs in get_observations(pre_obs, ComputerObservation)
                    if obs.url
                ]
            )
            url = url_obs.url if url_obs else ""

            result.append(
                StepSummary(
                    index=action_idx,
                    action_name=step.action.action_name,
                    action_args=filtered_args,
                    action_nl_description=step.action.action_nl_description,
                    action_content=c,
                    url=url,
                    state_description=args.get("screen_description", ""),
                    previous_error=c.get("other_state", {}).get("previous_error", ""),
                    screenshot_path=screenshot,
                    user_messages_before=user_msgs,
                )
            )
        return result


class VerificationResult(Component):
    """Result from a verifier."""

    result_type: Literal["base"] = "base"
    score: Optional[float] = None
    reasoning: Optional[str] = None
    verifier_name: str
    metadata: Dict[str, Any] = Field(default_factory=dict)

    @property
    def is_correct(self) -> Optional[bool]:
        if self.score is None:
            return None
        return self.score >= 0.5


class ImageScore(BaseModel):
    """Score for a single screenshot against task key points."""

    path: str = ""
    llm_message: LLMMessage = Field(default_factory=LLMMessage)
    score: int = 0


class WebJudgeResult(VerificationResult):
    """Structured result from WebJudge verification."""

    result_type: Literal["web_judge"] = "web_judge"
    key_points: str = ""
    image_scores: list[ImageScore] = Field(default_factory=list)


class MajorityVoteMetadata(BaseModel):
    """Metadata from majority voting in rubric scoring."""

    n_instances: int = 0
    median_instance_idx: int = 0
    all_scores: List[float] = Field(default_factory=list)
    median_score: float = 0.0
    outcome_votes: List[Optional[bool]] = Field(default_factory=list)
    majority_output_success: Optional[bool] = None


class MMRubricResult(VerificationResult):
    """Result from the multimodal rubric verification pipeline."""

    result_type: Literal["mm_rubric"] = "mm_rubric"
    total_max_points: float = 0
    total_earned_points: float = 0
    rubric_is_success: bool = False
    intermediate_mm_rubric_steps: Dict[str, Any] = Field(default_factory=dict)
    majority_vote_metadata: MajorityVoteMetadata = Field(
        default_factory=MajorityVoteMetadata
    )
    all_rubric_dicts: List[Dict[str, Any]] = Field(default_factory=list)
    all_scores_list: List[float] = Field(default_factory=list)


class MMRubricOutcomeResult(VerificationResult):
    """Binary outcome verification from the rubric pipeline."""

    result_type: Literal["mm_rubric_outcome"] = "mm_rubric_outcome"
    output_success: Optional[bool] = None
    primary_intent: str = ""



class TaskAgentResult(VerificationResult):
    """Result from the unified task verification classification (Step 10).

    Classifies a task along two axes before execution:
      - Task Ambiguity   (Category 7) — populated by :func:`classify_task`
      - Invalid Task     (Category 8) — populated by :func:`classify_task`
        classification step; fields default to empty/``None``
    """

    result_type: Literal["task_verification"] = "task_verification"
    # Axis 1: Ambiguity
    reasoning_is_ambiguous: str = ""
    is_ambiguous: Optional[bool] = None
    ambiguity_codes: List[str] = Field(default_factory=list)
    # Axis 2: Invalid task
    reasoning_is_invalid: str = ""
    is_invalid: Optional[bool] = None
    invalid_task_codes: List[str] = Field(default_factory=list)


VerificationResultEvent = Annotated[
    Union[
        MMRubricResult,
        MMRubricOutcomeResult,
        WebJudgeResult,
        TaskAgentResult,
        VerificationResult,
    ],
    Field(discriminator="result_type"),
]


class DataPointMetadata(Component):
    """Metadata about a data generation run."""

    stats: Dict[str, Any] = Field(default_factory=dict)
    run_id: Optional[str] = None
    created_at: Optional[str] = None

    @model_validator(mode="before")
    @classmethod
    def _set_created_at(cls, data: Any) -> Any:
        if isinstance(data, dict) and data.get("created_at") is None:
            data["created_at"] = datetime.now().isoformat()
        return data


class DataPoint(Component):
    """A single data generation run output."""

    task: Task
    solver_log: SolverLog = Field(default_factory=SolverLog)
    verification: Dict[str, VerificationResultEvent] = Field(default_factory=dict)
    metadata: DataPointMetadata = Field(default_factory=DataPointMetadata)
