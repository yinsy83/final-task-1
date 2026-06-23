# Task 1: Multi-Source 3D Asset Generation and Scene Fusion

## 1. Project Overview

This directory contains the deliverables for course project `Task 1`, including:

- `A`: real-object multi-view reconstruction based on COLMAP
- `B`: text-to-3D vase generation based on threestudio / Magic3D
- `C`: single-image-to-3D mouse generation based on threestudio / Zero123
- background reconstruction based on 3D Gaussian Splatting
- final Blender-based fusion scene and roaming video

The final fused video currently used in the report is:

- `video/final_fusion-2.mp4`

The saved Blender project is:

- `video/fusion_with_background.blend`

## 2. Directory Structure

```text
task 1/
├─ README.md
├─ report_draft.md
├─ report_assets/
├─ environments/
│  ├─ gen3d_environment.yml
│  └─ gsbg2_environment.yml
├─ convert_colmap_points_to_ply.py
├─ generate_training_curves.py
├─ generate_c_proxy_validation_curve.py
└─ results/
   ├─ A_box/
   ├─ b_vase_magic3d_v2/
   ├─ c_mouse_zero123/
   └─ background_counter/
```

Important outputs:

- `results/A_box/colmap/sparse_txt/a_box_sparse_cubes_centered.obj`
- `results/b_vase_magic3d_v2/trial/save/it3000-export/model.obj`
- `results/c_mouse_zero123/trial/save/it2000-export/model.obj`
- `results/background_counter/point_cloud/iteration_30000/point_cloud (1).ply`

## 3. Environment Notes

This project was completed with multiple environments rather than one single unified environment.

- `gen3d`: used for `B` and `C` generation with threestudio
- `gsbg2`: used for Gaussian Splatting background reconstruction
- `Windows + Blender`: used for final fusion, scene layout and video export

Reference environment files are provided in:

- `environments/gen3d_environment.yml`
- `environments/gsbg2_environment.yml`

Important note:

- The actual training was executed in a cloud Linux GPU environment.
- The Blender fusion and result organization were completed locally on Windows.
- Therefore, the environment files in this repository should be regarded as documented reproduction references, not byte-for-byte exact system snapshots.

## 4. Data Preparation

### 4.1 Object A: Real Multi-View Box

Prepare multi-view images of the real box under:

```text
results/A_box/images/
```

These images are extracted from a hand-held video around the object.

### 4.2 Object B: Text-to-3D Vase

No external image is required. The object is generated from text prompt only.

Prompt used in this project:

```text
a single elegant ceramic vase, smooth white glazed ceramic, minimalistic shape, clean silhouette, studio product photography, centered object, clean background, highly detailed 3D asset
```

### 4.3 Object C: Single-Image Mouse

Prepare one foreground image of the mouse with removed background:

```text
outputs/C_mouse/preprocess/mouse_main_rgba.png
```

In this project, the single image is first preprocessed with background removal and then fed into Zero123.

### 4.4 Background Scene

Prepare the Mip-NeRF 360 `counter` scene under:

```text
data/background/counter/
```

According to the saved background config:

- `source_path=/inspire/hdd/project/fdu-aidake-cfff/public/yinsyyyy/深度空间期末任务一/data/background/counter`
- `eval=True`

## 5. Training Commands

### 5.1 A: COLMAP Reconstruction

Representative COLMAP commands:

```bash
colmap feature_extractor --database_path results/A_box/colmap/database.db --image_path results/A_box/images
colmap exhaustive_matcher --database_path results/A_box/colmap/database.db
mkdir -p results/A_box/colmap/sparse
colmap mapper --database_path results/A_box/colmap/database.db --image_path results/A_box/images --output_path results/A_box/colmap/sparse
```

After sparse reconstruction, the sparse point output can be converted into a Blender-friendly proxy geometry with:

```bash
python convert_colmap_points_to_ply.py
```

### 5.2 B: Magic3D Vase Training

The command recorded in `results/b_vase_magic3d_v2/trial/cmd.txt` is:

```bash
python launch.py --config configs/magic3d-coarse-sd-v15.yaml --gpu 0 --train system.prompt_processor.prompt="a single elegant ceramic vase, smooth white glazed ceramic, minimalistic shape, clean silhouette, studio product photography, centered object, clean background, highly detailed 3D asset" use_timestamp=false name=b_vase_magic3d_v2 tag=trial trainer.max_steps=3000
```

Main outputs:

- checkpoint: `results/b_vase_magic3d_v2/trial/ckpts/epoch=0-step=3000.ckpt`
- exported mesh: `results/b_vase_magic3d_v2/trial/save/it3000-export/model.obj`

### 5.3 C: Zero123 Mouse Training

The command recorded in `results/c_mouse_zero123/trial/cmd.txt` is:

```bash
python launch.py --config configs/zero123.yaml --gpu 0 --train data.image_path=/inspire/hdd/project/fdu-aidake-cfff/public/yinsyyyy/深度空间期末任务一/outputs/C_mouse/preprocess/mouse_main_rgba.png use_timestamp=false name=c_mouse_zero123 tag=trial trainer.max_steps=2000
```

Main outputs:

- checkpoint: `results/c_mouse_zero123/trial/ckpts/epoch=0-step=2000.ckpt`
- exported mesh: `results/c_mouse_zero123/trial/save/it2000-export/model.obj`

### 5.4 Background Gaussian Splatting

The exact saved config confirms:

- source path: `data/background/counter`
- output path: `outputs/background_counter`
- evaluation mode: `eval=True`

A representative Gaussian Splatting training command consistent with the saved config is:

```bash
python train.py -s data/background/counter -m outputs/background_counter --eval
```

Main output:

- `results/background_counter/point_cloud/iteration_30000/point_cloud (1).ply`

## 6. Test / Export / Fusion

### 6.1 Export Meshes

For the currently saved results, final meshes are already exported:

- `B`: `results/b_vase_magic3d_v2/trial/save/it3000-export/model.obj`
- `C`: `results/c_mouse_zero123/trial/save/it2000-export/model.obj`

### 6.2 Blender Fusion

Open the Blender project:

```text
video/fusion_with_background.blend
```

Objects used in fusion:

- `A`: `results/A_box/colmap/sparse_txt/a_box_sparse_cubes_centered.obj`
- `B`: `results/b_vase_magic3d_v2/trial/save/it3000-export/model.obj`
- `C`: `results/c_mouse_zero123/trial/save/it2000-export/model.obj`
- background: `results/background_counter/point_cloud/iteration_30000/point_cloud (1).ply`

Final exported video:

- `video/final_fusion-2.mp4`

## 7. Report-Related Scripts

The following helper scripts were added during report preparation:

- `generate_training_curves.py`
- `generate_c_proxy_validation_curve.py`
- `convert_colmap_points_to_ply.py`

These scripts are used for:

- generating training-loss figures from local `metrics.csv`
- generating proxy validation curves for `C`
- converting COLMAP sparse points into PLY / OBJ proxy assets

## 8. Notes

- `A` does not have a neural checkpoint. Its core outputs are COLMAP sparse reconstruction files and the generated Blender proxy geometry.
- `B` and `C` both have final `ckpt` files saved in their corresponding `trial/ckpts/` directories.
- The background result is stored as a point-based Gaussian Splatting output and later visualized/fused in Blender.
