from __future__ import annotations

import csv
from pathlib import Path

import matplotlib.pyplot as plt


ROOT = Path(r"d:\小文件\深度空间作业\期末\task 1")
B_METRICS = ROOT / r"results\b_vase_magic3d_v2\trial\csv_logs\version_0\metrics.csv"
C_METRICS = ROOT / r"results\c_mouse_zero123\trial\csv_logs\version_5\metrics.csv"
OUT_DIR = ROOT / "report_assets"


def load_numeric_columns(csv_path: Path) -> dict[str, list[float]]:
    with csv_path.open("r", encoding="utf-8", newline="") as f:
        reader = csv.DictReader(f)
        columns = {name: [] for name in reader.fieldnames or []}
        for row in reader:
            for key, value in row.items():
                if value is None or value == "":
                    continue
                try:
                    columns[key].append(float(value))
                except ValueError:
                    continue
    return columns


def load_series(csv_path: Path, keys: list[str]) -> tuple[list[float], dict[str, list[float]]]:
    steps: list[float] = []
    series = {key: [] for key in keys}

    with csv_path.open("r", encoding="utf-8", newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            step_value = row.get("step", "")
            if not step_value:
                continue
            try:
                step = float(step_value)
            except ValueError:
                continue

            any_value = False
            parsed_values: dict[str, float] = {}
            for key in keys:
                raw = row.get(key, "")
                if not raw:
                    continue
                try:
                    parsed_values[key] = float(raw)
                    any_value = True
                except ValueError:
                    continue

            if not any_value:
                continue

            steps.append(step)
            for key in keys:
                series[key].append(parsed_values.get(key, float("nan")))

    return steps, series


def plot_b_curves() -> Path:
    keys = [
        "train/loss_sds",
        "train/loss_orient",
        "train/loss_sparsity",
        "train/loss_opaque",
    ]
    steps, series = load_series(B_METRICS, keys)

    fig, axes = plt.subplots(2, 1, figsize=(10, 8), constrained_layout=True)

    axes[0].plot(steps, series["train/loss_sds"], color="#1f77b4", linewidth=1.5)
    axes[0].set_title("B: Magic3D vase training curve")
    axes[0].set_xlabel("Step")
    axes[0].set_ylabel("SDS loss")
    axes[0].grid(alpha=0.3)

    axes[1].plot(steps, series["train/loss_orient"], label="orient", linewidth=1.2)
    axes[1].plot(steps, series["train/loss_sparsity"], label="sparsity", linewidth=1.2)
    axes[1].plot(steps, series["train/loss_opaque"], label="opaque", linewidth=1.2)
    axes[1].set_xlabel("Step")
    axes[1].set_ylabel("Auxiliary losses")
    axes[1].grid(alpha=0.3)
    axes[1].legend()

    out_path = OUT_DIR / "b_magic3d_training_curves.png"
    fig.savefig(out_path, dpi=180, bbox_inches="tight")
    plt.close(fig)
    return out_path


def plot_c_curves() -> Path:
    keys = [
        "train/loss",
        "train/loss_ref",
        "train/loss_zero123",
        "train/loss_zero123_sds",
    ]
    steps, series = load_series(C_METRICS, keys)

    fig, axes = plt.subplots(2, 1, figsize=(10, 8), constrained_layout=True)

    axes[0].plot(steps, series["train/loss"], label="total", linewidth=1.4)
    axes[0].plot(steps, series["train/loss_ref"], label="ref", linewidth=1.2)
    axes[0].plot(steps, series["train/loss_zero123"], label="zero123", linewidth=1.2)
    axes[0].set_title("C: Zero123 mouse training curve")
    axes[0].set_xlabel("Step")
    axes[0].set_ylabel("Loss")
    axes[0].grid(alpha=0.3)
    axes[0].legend()

    axes[1].plot(steps, series["train/loss_zero123_sds"], color="#d62728", linewidth=1.4)
    axes[1].set_xlabel("Step")
    axes[1].set_ylabel("Zero123 SDS loss")
    axes[1].grid(alpha=0.3)

    out_path = OUT_DIR / "c_zero123_training_curves.png"
    fig.savefig(out_path, dpi=180, bbox_inches="tight")
    plt.close(fig)
    return out_path


def plot_combined_summary() -> Path:
    b_steps, b_series = load_series(B_METRICS, ["train/loss_sds"])
    c_steps, c_series = load_series(C_METRICS, ["train/loss", "train/loss_zero123_sds"])

    fig, axes = plt.subplots(1, 2, figsize=(12, 4.8), constrained_layout=True)

    axes[0].plot(b_steps, b_series["train/loss_sds"], color="#1f77b4", linewidth=1.4)
    axes[0].set_title("B: Magic3D SDS loss")
    axes[0].set_xlabel("Step")
    axes[0].set_ylabel("Loss")
    axes[0].grid(alpha=0.3)

    axes[1].plot(c_steps, c_series["train/loss"], label="total", linewidth=1.2)
    axes[1].plot(c_steps, c_series["train/loss_zero123_sds"], label="zero123_sds", linewidth=1.2)
    axes[1].set_title("C: Zero123 training loss")
    axes[1].set_xlabel("Step")
    axes[1].set_ylabel("Loss")
    axes[1].grid(alpha=0.3)
    axes[1].legend()

    out_path = OUT_DIR / "training_curves_summary.png"
    fig.savefig(out_path, dpi=180, bbox_inches="tight")
    plt.close(fig)
    return out_path


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    outputs = [
        plot_b_curves(),
        plot_c_curves(),
        plot_combined_summary(),
    ]
    for path in outputs:
        print(path)


if __name__ == "__main__":
    main()
