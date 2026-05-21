# Copyright 2023-2026 AgentEra(Agently.Tech)
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import copy

from typing import Callable, Literal, TYPE_CHECKING

if TYPE_CHECKING:
    from agently.types.data import SerializableValue
    from agently.types.trigger_flow import TriggerFlowRuntimeData

from agently.types.data import EMPTY
from agently.types.trigger_flow import TriggerFlowBlockData
from .BaseProcess import TriggerFlowBaseProcess
from .._async_utils import gather_cancel_on_error

TriggerFlowConditionHandler = Callable[["TriggerFlowRuntimeData"], bool]


class TriggerFlowMatchCaseProcess(TriggerFlowBaseProcess):
    def match(self, *, mode: Literal["hit_first", "hit_all"] = "hit_first"):
        match_block_data = TriggerFlowBlockData(
            outer_block=self._block_data,
        )
        match_id = self._blue_print.make_stable_identity_digest(
            {
                "kind": "match",
                "mode": mode,
                "listen_signals": self._definition_signals,
                "parent_group_id": self._definition_group_id,
                "parent_group_kind": self._definition_group_kind,
            },
        )
        result_signal = self._event_signal(f"Match-{ match_id }-Result", role="continuation")
        route_operator_id = f"match-route-{ match_id }"
        match_block_data.data.update(
            {
                "match_id": match_id,
                "cases": {},
                "branch_ends": [],
                "definition_branch_ends": [],
                "is_first_case": True,
                "has_else": False,
                "definition_outer_group_id": self._definition_group_id,
                "definition_outer_group_kind": self._definition_group_kind,
                "definition_route_operator_id": route_operator_id,
                "definition_result_signal": result_signal,
            }
        )

        async def match_case(data: "TriggerFlowRuntimeData"):
            data.layer_in()
            matched_count = 0
            tasks = []
            for case_id, condition in match_block_data.data["cases"].items():
                if callable(condition):
                    judgement = condition(data)
                else:
                    judgement = bool(data.value == condition)
                if judgement is True:
                    if mode == "hit_first":
                        await data.async_emit(
                            f"Match-{ match_id }-Case-{ case_id }",
                            data.value,
                            _layer_marks=data._layer_marks.copy(),
                        )
                        return
                    if mode == "hit_all":
                        data.layer_in()
                        matched_count += 1
                        data._system_runtime_data.set(
                            f"match_results.{ data.upper_layer_mark }.{ data.layer_mark }",
                            EMPTY,
                        )
                        tasks.append(
                            data.async_emit(
                                f"Match-{ match_id }-Case-{ case_id }",
                                data.value,
                                _layer_marks=data._layer_marks.copy(),
                            )
                        )
                        data.layer_out()
            await gather_cancel_on_error(*tasks)
            if matched_count == 0:
                if match_block_data.data["has_else"] is True:
                    await data.async_emit(
                        f"Match-{ match_id }-Else",
                        data.value,
                        _layer_marks=data._layer_marks.copy(),
                    )
                else:
                    await data.async_emit(
                        f"Match-{ match_id }-Result",
                        data.value,
                        _layer_marks=data._layer_marks.copy(),
                    )

        self._blue_print.add_handler(
            self.trigger_type,
            self.trigger_event,
            match_case,
            id=route_operator_id,
        )
        try:
            existing_operator = self._blue_print.definition.get_operator(route_operator_id)
        except KeyError:
            self._blue_print.definition.add_operator(
                id=route_operator_id,
                kind="match_route",
                name=f"match:{ match_id }",
                listen_signals=self._definition_signals,
                emit_signals=[result_signal],
                options={
                    "mode": mode,
                    "cases": [],
                },
                group_id=match_id,
                group_kind="match",
                parent_group_id=self._definition_group_id,
                parent_group_kind=self._definition_group_kind,
            )
        else:
            if (
                existing_operator.get("kind") != "match_route"
                or existing_operator.get("options", {}).get("mode") != mode
                or existing_operator.get("listen_signals") != self._definition_signals
            ):
                raise ValueError(
                    f"TriggerFlow match operator '{ route_operator_id }' already exists with a different definition."
                )

        return self._new(
            trigger_event=self.trigger_event,
            trigger_type=self.trigger_type,
            blueprint=self._blue_print,
            block_data=match_block_data,
            definition_signals=self._definition_signals,
            definition_group_id=match_id,
            definition_group_kind="match",
        )

    def case(self, condition: "TriggerFlowConditionHandler | SerializableValue"):
        if "match_id" not in self._block_data.data:
            raise NotImplementedError("Cannot use .case() before .match().")

        match_id = self._block_data.data["match_id"]
        condition_ref = None
        condition_value = None
        if callable(condition):
            condition_ref = self._blue_print._register_callable("condition", condition, strict=False, name=None)
        else:
            condition_value = condition
        case_id = self._blue_print.make_stable_identity_digest(
            {
                "kind": "match_case",
                "match_id": match_id,
                "condition_ref": condition_ref,
                "condition_value": condition_value,
            },
        )
        self._block_data.data["cases"][case_id] = condition

        is_first_case = self._block_data.data["is_first_case"]
        if is_first_case:
            self._block_data.data["is_first_case"] = False
        else:
            if not self.trigger_event.startswith(f"Match-{ match_id }"):
                self._block_data.data["branch_ends"].append(self.trigger_event)
                self._block_data.data["definition_branch_ends"].extend(copy.deepcopy(self._definition_signals))

        case_trigger = f"Match-{ match_id }-Case-{ case_id }"
        branch_trigger = f"Match-{ match_id }-Case-{ case_id }-Branch"

        route_operator = self._blue_print.definition.get_operator(self._block_data.data["definition_route_operator_id"])
        case_config = {
            "case_id": case_id,
            "route_signal": self._event_signal(case_trigger),
            "condition_ref": copy.deepcopy(condition_ref) if condition_ref is not None else None,
            "condition_value": condition_value,
            "is_else": False,
        }
        existing_case = next(
            (case for case in route_operator["options"]["cases"] if case.get("case_id") == case_id),
            None,
        )
        if existing_case is None:
            route_operator["options"]["cases"].append(case_config)
        elif existing_case != case_config:
            raise ValueError(
                f"TriggerFlow match case '{ case_id }' already exists with a different definition."
            )
        self._blue_print.definition.set_emit_signals(
            route_operator["id"],
            [
                *route_operator["emit_signals"],
                self._event_signal(case_trigger),
            ],
        )
        self._blue_print.definition.add_operator(
            id=f"match-case-{ case_id }",
            kind="match_case",
            name=f"case:{ case_id }",
            listen_signals=[self._event_signal(case_trigger)],
            emit_signals=[self._event_signal(branch_trigger, role="continuation")],
            condition_ref=condition_ref,
            options={"condition_value": condition_value} if condition_ref is None else {},
            group_id=match_id,
            group_kind="match",
            parent_group_id=self._block_data.data.get("definition_outer_group_id"),
            parent_group_kind=self._block_data.data.get("definition_outer_group_kind"),
        )

        return self._new(
            trigger_event=case_trigger,
            trigger_type="event",
            blueprint=self._blue_print,
            block_data=self._block_data,
            definition_signals=[self._event_signal(branch_trigger)],
            definition_group_id=match_id,
            definition_group_kind="match",
        )

    def case_else(self):
        if "match_id" not in self._block_data.data:
            raise NotImplementedError("Cannot use .case() before .match().")

        self._block_data.data["has_else"] = True
        match_id = self._block_data.data["match_id"]
        is_first_case = self._block_data.data["is_first_case"]
        if is_first_case:
            raise NotImplementedError("Cannot use .case_else() before any .case().")
        if not self.trigger_event.startswith(f"Match-{ match_id }"):
            self._block_data.data["branch_ends"].append(self.trigger_event)
            self._block_data.data["definition_branch_ends"].extend(copy.deepcopy(self._definition_signals))

        else_trigger = f"Match-{ match_id }-Else"
        branch_trigger = f"Match-{ match_id }-Else-Branch"
        route_operator = self._blue_print.definition.get_operator(self._block_data.data["definition_route_operator_id"])
        else_signal = self._event_signal(else_trigger)
        existing_else_signal = route_operator["options"].get("else_signal")
        if existing_else_signal is None:
            route_operator["options"]["else_signal"] = else_signal
        elif existing_else_signal != else_signal:
            raise ValueError(
                f"TriggerFlow match else for '{ match_id }' already exists with a different definition."
            )
        self._blue_print.definition.set_emit_signals(
            route_operator["id"],
            [
                *route_operator["emit_signals"],
                else_signal,
            ],
        )
        self._blue_print.definition.add_operator(
            id=f"match-else-{ match_id }",
            kind="match_case",
            name=f"else:{ match_id }",
            listen_signals=[self._event_signal(else_trigger)],
            emit_signals=[self._event_signal(branch_trigger, role="continuation")],
            options={"is_else": True},
            group_id=match_id,
            group_kind="match",
            parent_group_id=self._block_data.data.get("definition_outer_group_id"),
            parent_group_kind=self._block_data.data.get("definition_outer_group_kind"),
        )

        return self._new(
            trigger_event=else_trigger,
            trigger_type="event",
            blueprint=self._blue_print,
            block_data=self._block_data,
            definition_signals=[self._event_signal(branch_trigger)],
            definition_group_id=match_id,
            definition_group_kind="match",
        )

    def end_match(self):
        if "match_id" not in self._block_data.data:
            raise NotImplementedError("Cannot use .end_match() before .match().")
        match_id = self._block_data.data["match_id"]
        branch_ends = self._block_data.data["branch_ends"]
        definition_branch_ends = self._block_data.data["definition_branch_ends"]
        if not self.trigger_event.startswith(f"Match-{ match_id }"):
            branch_ends.append(self.trigger_event)
            definition_branch_ends.extend(copy.deepcopy(self._definition_signals))

        collect_operator_id = f"match-collect-{ match_id }"

        async def collect_branch_result(data: "TriggerFlowRuntimeData"):
            match_results = data._system_runtime_data.get(f"match_results.{ data.upper_layer_mark }")
            if match_results:
                if data.layer_mark in match_results:
                    match_results[data.layer_mark] = data.value
                for value in match_results.values():
                    if value is EMPTY:
                        data._system_runtime_data.set(f"match_results.{ data.upper_layer_mark }", match_results)
                        return
                data.layer_out()
                await data.async_emit(
                    f"Match-{ match_id }-Result",
                    list(match_results.values()),
                    _layer_marks=data._layer_marks.copy(),
                )
                del data._system_runtime_data[f"match_results.{ data.upper_layer_mark }"]
            else:
                data.layer_out()
                await data.async_emit(
                    f"Match-{ match_id }-Result",
                    data.value,
                    _layer_marks=data._layer_marks.copy(),
                )

        for trigger in branch_ends:
            self._blue_print.add_event_handler(trigger, collect_branch_result, id=collect_operator_id)

        self._blue_print.definition.add_operator(
            id=collect_operator_id,
            kind="match_collect",
            name=f"match_result:{ match_id }",
            listen_signals=definition_branch_ends,
            emit_signals=[self._block_data.data["definition_result_signal"]],
            group_id=match_id,
            group_kind="match",
            parent_group_id=self._block_data.data.get("definition_outer_group_id"),
            parent_group_kind=self._block_data.data.get("definition_outer_group_kind"),
        )

        outer_block = self._block_data.outer_block
        block_data = (
            outer_block
            if outer_block is not None
            else TriggerFlowBlockData(
                outer_block=None,
            )
        )

        return self._new(
            trigger_event=f"Match-{ match_id }-Result",
            trigger_type="event",
            blueprint=self._blue_print,
            block_data=block_data,
            definition_signals=[self._block_data.data["definition_result_signal"]],
            definition_group_id=self._block_data.data.get("definition_outer_group_id"),
            definition_group_kind=self._block_data.data.get("definition_outer_group_kind"),
        )

    # If Condition
    def if_condition(self, condition: "TriggerFlowConditionHandler | SerializableValue"):
        return self.match().case(condition)

    elif_condition = case
    else_condition = case_else
    end_condition = end_match
