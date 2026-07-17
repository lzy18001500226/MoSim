#!/usr/bin/env python3
"""Train and freeze bounded neural-residual and RL gain-scheduler artifacts."""

from __future__ import annotations

import argparse
import hashlib
import json
import math
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import gymnasium as gym
import numpy as np
from gymnasium import spaces
from sklearn.neural_network import MLPRegressor
from stable_baselines3 import PPO
from stable_baselines3.common.utils import set_random_seed


ROOT = Path(__file__).resolve().parents[2]
TRAIN_SEED = 20260717
EVALUATION_SEED = 20260718
OBSERVATION_SIZE = 12
ACTION_SIZE = 3
NEURAL_HIDDEN_SIZE = 12
RL_HIDDEN_SIZE = 16
OBSERVATION_SCALE = np.array([2.5] * 3 + [3.0] * 3 + [3.0] * 3 + [3.0] * 3)
NEURAL_RESIDUAL_LIMIT = 0.6
RL_SCHEDULE_LIMIT = 0.25


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def canonical_json(data: Any) -> bytes:
    return (json.dumps(data, sort_keys=True, separators=(",", ":")) + "\n").encode("utf-8")


def disturbance_from_observation(observation: np.ndarray, latent: np.ndarray) -> np.ndarray:
    position_error = observation[..., 0:3]
    velocity_error = observation[..., 3:6]
    reference_acceleration = observation[..., 6:9]
    velocity = observation[..., 9:12]
    coupled_velocity = np.stack((velocity[..., 1], -velocity[..., 0], velocity[..., 2]), axis=-1)
    return (
        latent
        + 0.18 * np.tanh(0.8 * velocity)
        - 0.09 * position_error
        - 0.04 * velocity_error
        + 0.05 * coupled_velocity
        + 0.03 * reference_acceleration
    )


def generate_neural_dataset(seed: int, sample_count: int) -> tuple[np.ndarray, np.ndarray, dict[str, Any]]:
    rng = np.random.default_rng(seed)
    position_error = rng.uniform(-2.0, 2.0, size=(sample_count, 3))
    velocity_error = rng.uniform(-2.5, 2.5, size=(sample_count, 3))
    reference_acceleration = rng.uniform(-2.0, 2.0, size=(sample_count, 3))
    velocity = rng.uniform(-2.5, 2.5, size=(sample_count, 3))
    latent = rng.uniform(-0.22, 0.22, size=(sample_count, 3))
    observation = np.concatenate(
        (position_error, velocity_error, reference_acceleration, velocity), axis=1
    )
    disturbance = disturbance_from_observation(observation, latent)
    target = np.clip(-disturbance, -NEURAL_RESIDUAL_LIMIT, NEURAL_RESIDUAL_LIMIT)
    manifest = {
        "schema": "mosim.learning_dataset.v1",
        "kind": "domain_randomized_quadrotor_outer_loop_residual",
        "seed": seed,
        "sample_count": sample_count,
        "observation_fields": [
            "position_error_x", "position_error_y", "position_error_z",
            "velocity_error_x", "velocity_error_y", "velocity_error_z",
            "reference_acceleration_x", "reference_acceleration_y", "reference_acceleration_z",
            "velocity_x", "velocity_y", "velocity_z",
        ],
        "target_fields": ["residual_acceleration_x", "residual_acceleration_y", "residual_acceleration_z"],
        "residual_limit_mps2": NEURAL_RESIDUAL_LIMIT,
        "runtime_log_validation_sources": [
            "Results/sunray_ros1/p1_pid_cascade_runtime_r4_hover0291_20260716",
            "Results/sunray_ros1/p1_pid_neural_runtime_r1_hover0291_20260716",
            "Results/sunray_ros1/p1_pid_feedforward_runtime_r6_ff05_hover0291_20260716",
        ],
        "claim_boundary": "Synthetic domain-randomized outer-loop identification data; listed runtime logs ground feature ranges but are not relabeled as training truth.",
    }
    return observation, target, manifest


class GainScheduleEnv(gym.Env[np.ndarray, np.ndarray]):
    metadata = {"render_modes": []}

    def __init__(self, seed: int = TRAIN_SEED, episode_steps: int = 240) -> None:
        super().__init__()
        self.observation_space = spaces.Box(-1.0, 1.0, shape=(OBSERVATION_SIZE,), dtype=np.float32)
        self.action_space = spaces.Box(
            0.0, RL_SCHEDULE_LIMIT, shape=(ACTION_SIZE,), dtype=np.float32
        )
        self.episode_steps = episode_steps
        self.dt = 0.025
        self._initial_seed = seed
        self._rng = np.random.default_rng(seed)
        self.position = np.zeros(3)
        self.velocity = np.zeros(3)
        self.target = np.zeros(3)
        self.latent = np.zeros(3)
        self.mass_scale = 1.0
        self.step_index = 0

    def _raw_observation(self) -> np.ndarray:
        position_error = self.target - self.position
        velocity_error = -self.velocity
        reference_acceleration = np.zeros(3)
        return np.concatenate((position_error, velocity_error, reference_acceleration, self.velocity))

    def _observation(self) -> np.ndarray:
        return np.clip(self._raw_observation() / OBSERVATION_SCALE, -1.0, 1.0).astype(np.float32)

    def reset(self, *, seed: int | None = None, options: dict[str, Any] | None = None):
        super().reset(seed=seed)
        if seed is not None:
            self._rng = np.random.default_rng(seed)
        self.position = self._rng.uniform(-1.8, 1.8, size=3)
        self.velocity = self._rng.uniform(-0.8, 0.8, size=3)
        self.target = self._rng.uniform(-0.6, 0.6, size=3)
        self.latent = self._rng.uniform(-0.22, 0.22, size=3)
        self.mass_scale = float(self._rng.uniform(0.82, 1.18))
        self.step_index = 0
        return self._observation(), {}

    def step(self, action: np.ndarray):
        schedule = np.clip(np.asarray(action, dtype=float), 0.0, RL_SCHEDULE_LIMIT)
        raw = self._raw_observation()
        position_error = raw[0:3]
        velocity_error = raw[3:6]
        # The fixed fallback is intentionally conservative. The bounded policy
        # may recover performance, but can never remove or reverse either gain.
        base_acceleration = (1.0 + 2.0 * schedule) * 0.90 * position_error + (
            1.0 + schedule
        ) * 0.55 * velocity_error
        disturbance = disturbance_from_observation(raw, self.latent)
        acceleration = base_acceleration / self.mass_scale + disturbance
        self.velocity += acceleration * self.dt
        self.position += self.velocity * self.dt
        self.step_index += 1
        tracking_cost = float(1.5 * np.dot(position_error, position_error) + 0.25 * np.dot(self.velocity, self.velocity))
        action_cost = float(0.01 * np.dot(schedule, schedule))
        safety_cost = 5.0 if np.any(np.abs(self.position) > 3.5) or np.any(np.abs(self.velocity) > 4.0) else 0.0
        reward = -(tracking_cost + action_cost + safety_cost)
        terminated = safety_cost > 0.0
        truncated = self.step_index >= self.episode_steps
        return self._observation(), reward, terminated, truncated, {
            "tracking_cost": tracking_cost,
            "schedule": schedule.tolist(),
        }


def train_neural_residual() -> tuple[MLPRegressor, dict[str, Any], dict[str, Any]]:
    x_train, y_train, manifest = generate_neural_dataset(TRAIN_SEED, 16000)
    x_eval, y_eval, _ = generate_neural_dataset(EVALUATION_SEED, 4000)
    model = MLPRegressor(
        hidden_layer_sizes=(NEURAL_HIDDEN_SIZE,),
        activation="tanh",
        solver="adam",
        alpha=1.0e-5,
        batch_size=256,
        learning_rate_init=2.0e-3,
        max_iter=450,
        random_state=TRAIN_SEED,
        early_stopping=True,
        validation_fraction=0.15,
        n_iter_no_change=30,
    )
    model.fit(x_train / OBSERVATION_SCALE, y_train)
    prediction = np.clip(model.predict(x_eval / OBSERVATION_SCALE), -NEURAL_RESIDUAL_LIMIT, NEURAL_RESIDUAL_LIMIT)
    baseline_rmse = float(np.sqrt(np.mean(np.square(y_eval))))
    model_rmse = float(np.sqrt(np.mean(np.square(prediction - y_eval))))
    metrics = {
        "evaluation_samples": len(x_eval),
        "baseline_zero_residual_rmse_mps2": baseline_rmse,
        "model_rmse_mps2": model_rmse,
        "rmse_improvement_fraction": 1.0 - model_rmse / baseline_rmse,
        "iterations": int(model.n_iter_),
        "loss": float(model.loss_),
    }
    return model, manifest, metrics


def train_rl_scheduler(total_timesteps: int) -> tuple[PPO, dict[str, Any]]:
    set_random_seed(TRAIN_SEED)
    env = GainScheduleEnv(TRAIN_SEED)
    model = PPO(
        "MlpPolicy",
        env,
        learning_rate=1.0e-4,
        n_steps=512,
        batch_size=128,
        n_epochs=10,
        gamma=0.985,
        gae_lambda=0.95,
        clip_range=0.2,
        ent_coef=0.0,
        policy_kwargs={"net_arch": {"pi": [RL_HIDDEN_SIZE, RL_HIDDEN_SIZE], "vf": [RL_HIDDEN_SIZE, RL_HIDDEN_SIZE]}},
        seed=TRAIN_SEED,
        verbose=0,
        device="cpu",
    )
    model.learn(total_timesteps=total_timesteps, progress_bar=False)
    metrics = evaluate_rl_policy(model, EVALUATION_SEED, episodes=40)
    return model, metrics


def evaluate_rl_policy(model: PPO, seed: int, episodes: int) -> dict[str, Any]:
    learned_costs: list[float] = []
    baseline_costs: list[float] = []
    for episode in range(episodes):
        env = GainScheduleEnv(seed + episode)
        observation, _ = env.reset(seed=seed + episode)
        learned_cost = 0.0
        done = False
        while not done:
            action, _ = model.predict(observation, deterministic=True)
            observation, reward, terminated, truncated, _ = env.step(action)
            learned_cost -= float(reward)
            done = terminated or truncated
        env = GainScheduleEnv(seed + episode)
        observation, _ = env.reset(seed=seed + episode)
        baseline_cost = 0.0
        done = False
        while not done:
            observation, reward, terminated, truncated, _ = env.step(np.zeros(3, dtype=np.float32))
            baseline_cost -= float(reward)
            done = terminated or truncated
        learned_costs.append(learned_cost)
        baseline_costs.append(baseline_cost)
    baseline_mean = float(np.mean(baseline_costs))
    learned_mean = float(np.mean(learned_costs))
    return {
        "episodes": episodes,
        "baseline_mean_cost": baseline_mean,
        "learned_mean_cost": learned_mean,
        "cost_improvement_fraction": 1.0 - learned_mean / baseline_mean,
    }


def array_data(value: np.ndarray) -> list[Any]:
    return np.asarray(value, dtype=float).tolist()


def extract_rl_weights(model: PPO) -> dict[str, Any]:
    policy_layers = [layer for layer in model.policy.mlp_extractor.policy_net if hasattr(layer, "weight")]
    if len(policy_layers) != 2:
        raise RuntimeError(f"expected two PPO policy layers, found {len(policy_layers)}")
    action_layer = model.policy.action_net
    return {
        "w1": array_data(policy_layers[0].weight.detach().cpu().numpy().T),
        "b1": array_data(policy_layers[0].bias.detach().cpu().numpy()),
        "w2": array_data(policy_layers[1].weight.detach().cpu().numpy().T),
        "b2": array_data(policy_layers[1].bias.detach().cpu().numpy()),
        "w3": array_data(action_layer.weight.detach().cpu().numpy().T),
        "b3": array_data(action_layer.bias.detach().cpu().numpy()),
    }


def format_c_array(name: str, value: np.ndarray) -> str:
    flat = np.asarray(value, dtype=float).reshape(-1)
    body = ",\n    ".join(f"{item:.17g}" for item in flat)
    return f"static const double {name}[{flat.size}] = {{\n    {body}\n}};"


def build_weights_header(neural: MLPRegressor, rl_weights: dict[str, Any], artifact_sha256: str) -> str:
    blocks = [
        "#ifndef MOSIM_LEARNING_CONTROL_WEIGHTS_H",
        "#define MOSIM_LEARNING_CONTROL_WEIGHTS_H",
        "",
        f'#define MOSIM_LEARNING_ARTIFACT_SHA256 "{artifact_sha256}"',
        format_c_array("MOSIM_LEARNING_OBSERVATION_SCALE", OBSERVATION_SCALE),
        format_c_array("MOSIM_NEURAL_W1", neural.coefs_[0]),
        format_c_array("MOSIM_NEURAL_B1", neural.intercepts_[0]),
        format_c_array("MOSIM_NEURAL_W2", neural.coefs_[1]),
        format_c_array("MOSIM_NEURAL_B2", neural.intercepts_[1]),
        format_c_array("MOSIM_RL_W1", np.asarray(rl_weights["w1"])),
        format_c_array("MOSIM_RL_B1", np.asarray(rl_weights["b1"])),
        format_c_array("MOSIM_RL_W2", np.asarray(rl_weights["w2"])),
        format_c_array("MOSIM_RL_B2", np.asarray(rl_weights["b2"])),
        format_c_array("MOSIM_RL_W3", np.asarray(rl_weights["w3"])),
        format_c_array("MOSIM_RL_B3", np.asarray(rl_weights["b3"])),
        "",
        "#endif",
        "",
    ]
    return "\n\n".join(blocks)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--artifact", default="Config/control_platform/learning_control_artifact.json")
    parser.add_argument("--weights-header", default="Scripts/control_platform/learning_control_weights.h")
    parser.add_argument("--result-dir", default="Results/control_platform/p9_learning_training_20260717")
    parser.add_argument("--rl-timesteps", type=int, default=50000)
    args = parser.parse_args()

    artifact_path = (ROOT / args.artifact).resolve()
    weights_path = (ROOT / args.weights_header).resolve()
    result_dir = (ROOT / args.result_dir).resolve()
    result_dir.mkdir(parents=True, exist_ok=True)

    neural, dataset_manifest, neural_metrics = train_neural_residual()
    rl_model, rl_metrics = train_rl_scheduler(args.rl_timesteps)
    rl_weights = extract_rl_weights(rl_model)
    dataset_hash = sha256_bytes(canonical_json(dataset_manifest))
    payload = {
        "schema": "mosim.learning_control_artifact.v1",
        "status": "trained",
        "dataset": {
            "manifest": dataset_manifest,
            "manifest_sha256": dataset_hash,
            "train_seed": TRAIN_SEED,
            "evaluation_seed": EVALUATION_SEED,
        },
        "observation": {
            "size": OBSERVATION_SIZE,
            "scale": OBSERVATION_SCALE.tolist(),
        },
        "neural_residual": {
            "trained": True,
            "training_algorithm": "sklearn_mlp_regressor",
            "architecture": [OBSERVATION_SIZE, NEURAL_HIDDEN_SIZE, ACTION_SIZE],
            "activation": "tanh",
            "output_limit_mps2": NEURAL_RESIDUAL_LIMIT,
            "weights": {
                "w1": array_data(neural.coefs_[0]), "b1": array_data(neural.intercepts_[0]),
                "w2": array_data(neural.coefs_[1]), "b2": array_data(neural.intercepts_[1]),
            },
            "metrics": neural_metrics,
        },
        "rl_gain_scheduler": {
            "trained": True,
            "training_algorithm": "stable_baselines3_ppo",
            "architecture": [OBSERVATION_SIZE, RL_HIDDEN_SIZE, RL_HIDDEN_SIZE, ACTION_SIZE],
            "activation": "tanh",
            "action_bounds": [0.0, RL_SCHEDULE_LIMIT],
            "total_timesteps": args.rl_timesteps,
            "weights": rl_weights,
            "metrics": rl_metrics,
        },
        "fallback": {
            "controller": "cascade_pid",
            "conditions": ["disabled", "nonfinite_input", "artifact_mismatch", "output_out_of_bounds"],
        },
        "claim_boundary": "Frozen deterministic inference artifacts for bounded outer-loop augmentation; Gazebo/PX4 acceptance is a separate gate.",
    }
    payload["artifact_sha256"] = sha256_bytes(canonical_json(payload))
    artifact_path.parent.mkdir(parents=True, exist_ok=True)
    artifact_path.write_bytes(json.dumps(payload, indent=2).encode("utf-8") + b"\n")
    weights_path.write_text(
        build_weights_header(neural, rl_weights, payload["artifact_sha256"]),
        encoding="utf-8", newline="\n",
    )
    (result_dir / "TRAINING_SUMMARY.json").write_text(
        json.dumps({k: v for k, v in payload.items() if k not in {"neural_residual", "rl_gain_scheduler"}} | {
            "neural_residual_metrics": neural_metrics,
            "rl_gain_scheduler_metrics": rl_metrics,
        }, indent=2) + "\n",
        encoding="utf-8", newline="\n",
    )
    rl_model.save(result_dir / "rl_gain_scheduler_ppo")
    print(json.dumps({
        "artifact": str(artifact_path),
        "weights_header": str(weights_path),
        "artifact_sha256": payload["artifact_sha256"],
        "neural_metrics": neural_metrics,
        "rl_metrics": rl_metrics,
    }, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
