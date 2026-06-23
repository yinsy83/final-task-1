from __future__ import annotations

import math
import re
from dataclasses import dataclass
from pathlib import Path

import imageio.v3 as iio
import matplotlib.pyplot as plt
import numpy as np
from PIL import Image


ROOT = Path(r"d:\小文件\深度空间作业\期末\task 1")
C_SAVE_DIR = ROOT / r"results\c_mouse_zero123\trial\save"
REFERENCE_IMAGE = C_SAVE_DIR / "all_training_images.png"
OUT_DIR = ROOT / "report_assets"
OUT_FIG = OUT_DIR / "c_proxy_validation_curves.png"
OUT_CSV = OUT_DIR / "c_proxy_validation_metrics.csv"


@dataclass
class MetricRow:
    step: int
    psnr: float
    ssim: float
    mask_iou: float


def load_reference_image(path: Path) -> np.ndarray:
    image = Image.open(path).convert("RGB")
    return np.asarray(image, dtype=np.float32)


def extract_best_tile(video_path: Path, reference: np.ndarray) -> np.ndarray:
    frame = iio.imread(video_path, index=0).astype(np.float32)
    height, width, _ = frame.shape
    tile_count = max(width // height, 1)
    tile_width = width // tile_count

    best_tile: np.ndarray | None = None
    best_score = -float("inf")
    ref_mask = estimate_foreground_mask(reference)

    for index in range(tile_count):
        tile = frame[:, index * tile_width : (index + 1) * tile_width, :]
        tile_image = Image.fromarray(tile.astype(np.uint8)).resize(
            (reference.shape[1], reference.shape[0]),
            Image.Resampling.BILINEAR,
        )
        tile_array = np.asarray(tile_image, dtype=np.float32)
        tile_mask = estimate_foreground_mask(tile_array)
        score = mask_iou(ref_mask, tile_mask)
        if score > best_score:
            best_score = score
            best_tile = tile_array

    if best_tile is None:
        raise RuntimeError(f"Failed to extract tile from {video_path}")
    return best_tile


def estimate_background_color(image: np.ndarray) -> np.ndarray:
    h, w, _ = image.shape
    patches = np.concatenate(
        [
            image[:8, :8].reshape(-1, 3),
            image[:8, w - 8 :].reshape(-1, 3),
            image[h - 8 :, :8].reshape(-1, 3),
            image[h - 8 :, w - 8 :].reshape(-1, 3),
        ],
        axis=0,
    )
    return np.median(patches, axis=0)


def estimate_foreground_mask(image: np.ndarray, threshold: float = 25.0) -> np.ndarray:
    bg = estimate_background_color(image)
    distance = np.linalg.norm(image - bg[None, None, :], axis=2)
    return distance > threshold


def mask_iou(mask_a: np.ndarray, mask_b: np.ndarray) -> float:
    intersection = np.logical_and(mask_a, mask_b).sum()
    union = np.logical_or(mask_a, mask_b).sum()
    if union == 0:
        return 0.0
    return float(intersection / union)


def psnr(image_a: np.ndarray, image_b: np.ndarray) -> float:
    mse = float(np.mean((image_a - image_b) ** 2))
    if mse <= 1e-8:
        return 99.0
    return float(20.0 * math.log10(255.0 / math.sqrt(mse)))


def ssim_global(image_a: np.ndarray, image_b: np.ndarray) -> float:
    gray_a = (
        0.299 * image_a[..., 0] + 0.587 * image_a[..., 1] + 0.114 * image_a[..., 2]
    )
    gray_b = (
        0.299 * image_b[..., 0] + 0.587 * image_b[..., 1] + 0.114 * image_b[..., 2]
    )

    mu_a = float(gray_a.mean())
    mu_b = float(gray_b.mean())
    var_a = float(gray_a.var())
    var_b = float(gray_b.var())
    cov = float(((gray_a - mu_a) * (gray_b - mu_b)).mean())

    c1 = (0.01 * 255.0) ** 2
    c2 = (0.03 * 255.0) ** 2
    numerator = (2 * mu_a * mu_b + c1) * (2 * cov + c2)
    denominator = (mu_a**2 + mu_b**2 + c1) * (var_a + var_b + c2)
    if abs(denominator) < 1e-8:
        return 0.0
    return float(numerator / denominator)


def collect_rows() -> list[MetricRow]:
    reference = load_reference_image(REFERENCE_IMAGE)
    ref_mask = estimate_foreground_mask(reference)

    rows: list[MetricRow] = []
    for video_path in sorted(C_SAVE_DIR.glob("it*-val.mp4")):
        match = re.search(r"it(\d+)-val\.mp4$", video_path.name)
        if not match:
            continue
        step = int(match.group(1))
        candidate = extract_best_tile(video_path, reference)
        rows.append(
            MetricRow(
                step=step,
                psnr=psnr(reference, candidate),
                ssim=ssim_global(reference, candidate),
                mask_iou=mask_iou(ref_mask, estimate_foreground_mask(candidate)),
            )
        )
    rows.sort(key=lambda row: row.step)
    return rows


def save_csv(rows: list[MetricRow]) -> None:
    lines = ["step,psnr,ssim,mask_iou"]
    for row in rows:
        lines.append(
            f"{row.step},{row.psnr:.4f},{row.ssim:.4f},{row.mask_iou:.4f}"
        )
    OUT_CSV.write_text("\n".join(lines) + "\n", encoding="utf-8")


def save_figure(rows: list[MetricRow]) -> None:
    steps = [row.step for row in rows]
    psnr_values = [row.psnr for row in rows]
    ssim_values = [row.ssim for row in rows]
    iou_values = [row.mask_iou for row in rows]

    fig, axes = plt.subplots(3, 1, figsize=(10, 10), constrained_layout=True)

    axes[0].plot(steps, psnr_values, marker="o", linewidth=1.5, color="#1f77b4")
    axes[0].set_title("C: proxy validation PSNR curve")
    axes[0].set_xlabel("Step")
    axes[0].set_ylabel("PSNR (dB)")
    axes[0].grid(alpha=0.3)

    axes[1].plot(steps, ssim_values, marker="o", linewidth=1.5, color="#2ca02c")
    axes[1].set_title("C: proxy validation SSIM curve")
    axes[1].set_xlabel("Step")
    axes[1].set_ylabel("SSIM")
    axes[1].grid(alpha=0.3)

    axes[2].plot(steps, iou_values, marker="o", linewidth=1.5, color="#d62728")
    axes[2].set_title("C: proxy validation foreground IoU curve")
    axes[2].set_xlabel("Step")
    axes[2].set_ylabel("Mask IoU")
    axes[2].grid(alpha=0.3)

    fig.savefig(OUT_FIG, dpi=180, bbox_inches="tight")
    plt.close(fig)


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    rows = collect_rows()
    if not rows:
        raise RuntimeError("No validation videos were found for C.")
    save_csv(rows)
    save_figure(rows)
    print(OUT_CSV)
    print(OUT_FIG)


if __name__ == "__main__":
    main()
