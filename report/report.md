# 题目一实验报告

## 1. 基本信息

- 课程：深度学习与空间智能
- 作业：期末作业题目一，基于 3DGS 与 AIGC 的多源资产生成与真实场景融合
- 组员：殷思溢、江晨雨、张亦驰
- 学号：
  - 殷思溢：`[待填写]`
  - 江晨雨：`[待填写]`
  - 张亦驰：`[待填写]`
- 分工：
  - 殷思溢：`[待填写，可写环境搭建、A/B/C 结果整理、融合与报告整合]`
  - 江晨雨：`[待填写]`
  - 张亦驰：`[待填写]`
- GitHub 仓库链接：`[待填写，按课程要求需放在报告首页或末页显著位置]`
- 模型权重与结果下载链接：`[待填写，按课程要求需放在报告首页或末页显著位置]`

---

## 2. 任务目标

本题要求围绕“多源三维资产生成与真实场景融合”完成一套完整实验流程，即基于不同技术路径构建三个来源不同的 3D 物体，并将其统一插入到同一真实背景场景中，最终生成一段多视角漫游视频。三个物体的来源分别为：

- 物体 A：真实物体多视角拍摄，使用 COLMAP 恢复相机位姿并进行三维重建。
- 物体 B：使用文本到 3D 方法，从文本 Prompt 直接生成 3D 资产。
- 物体 C：使用单张真实图片，通过单图到 3D 方法生成完整三维模型。

此外，还需要从开源数据集中选择一个背景场景，使用 3D Gaussian Splatting 进行重建，并将 A、B、C 三个物体融合进统一场景中完成渲染展示。整体目标不仅在于分别完成三个物体的建模，还在于验证不同三维表示形式在同一工程管线中协同工作的可行性。

---

## 3. 实验总体流程

本次实验按照“真实采集重建 - AIGC 资产生成 - 背景场景重建 - Blender 融合渲染”的总体思路组织，完整流程如下：

1. 采集真实物体数据，准备 A 的多视角图像、C 的单张前景图像。
2. 使用 COLMAP 对 A 进行位姿恢复和稀疏重建。
3. 使用 threestudio 的 Magic3D 配置对 B 进行文本到 3D 生成。
4. 使用 threestudio 的 Zero123 配置对 C 进行单图到 3D 生成。
5. 选择 Mip-NeRF 360 数据集中的 `counter` 场景，使用 3DGS 训练背景。
6. 将 B、C 导出为 OBJ Mesh，将 A 的 COLMAP 稀疏点结果转换为可导入 Blender 的几何代理。
7. 在 Blender 中将背景与 A/B/C 三个物体放置到同一场景，添加相机关键帧，导出最终多视角融合视频。

---

## 4. 数据与实验设置

### 4.1 物体与场景选择

- 物体 A：包装盒
- 物体 B：花瓶
- 物体 C：鼠标
- 背景场景：`counter`

### 4.2 数据集与输入数据描述

- A 的输入数据：
  - 自行采集的真实包装盒环绕图像序列；
  - 通过手机拍摄视频后抽帧得到多视角图片；
  - 用于 COLMAP 位姿恢复与稀疏重建。
- B 的输入数据：
  - 无真实图像输入；
  - 直接使用文本 Prompt 作为条件，通过文本到 3D 生成流程构建花瓶。
- C 的输入数据：
  - 自行拍摄的真实鼠标单张图片；
  - 先进行前景抠图，生成透明背景 RGBA 图像；
  - 再作为 Zero123 的条件输入。
- 背景数据：
  - 选用 Mip-NeRF 360 数据集中的 `counter` 场景；
  - 使用其图像与相机信息进行 3DGS 背景重建。

### 4.3 软件与主要框架

- COLMAP
- threestudio
- Magic3D
- Zero123 / Zero123-XL
- 3D Gaussian Splatting
- Blender

### 4.4 运行环境概述

- 操作系统：Windows 本地环境用于结果整理、Blender 融合与视频导出
- 训练环境：云端 GPU 环境
- Python 环境：采用 conda 进行多环境管理
- 说明：
  - B、C 的生成主要依赖 threestudio 框架
  - 背景场景采用 Gaussian Splatting 训练流程
  - 最终融合、镜头设计与视频导出在 Blender 中完成

### 4.5 关键输出文件

- A 的代理几何：
  - `results/A_box/colmap/sparse_txt/a_box_sparse_cubes_centered.obj`
- B 的导出 Mesh：
  - `results/b_vase_magic3d_v2/trial/save/it3000-export/model.obj`
- C 的导出 Mesh：
  - `results/c_mouse_zero123/trial/save/it2000-export/model.obj`
- 背景点云：
  - `results/background_counter/point_cloud/iteration_30000/point_cloud (1).ply`
- 最终融合工程：
  - `video/fusion_with_background.blend`
- 最终融合视频：
  - `video/final_fusion-2.mp4`

---

## 5. 方法与实现细节

### 5.1 物体 A：真实多视角重建

物体 A 选用真实包装盒。实验中首先使用手机围绕包装盒拍摄视频，并对视频进行抽帧得到多张多视角图像；随后使用 COLMAP 依次完成特征提取、特征匹配、位姿恢复与稀疏三角化，得到相机参数和稀疏三维点。

本实验中，A 的已完成结果包括：

- COLMAP 稀疏重建结果；
- `points3D.txt` 等位姿与点云文件；
- 基于 COLMAP 稀疏点生成的可视化代理模型。

从 `points3D.txt` 可知，A 的稀疏点云规模为：

- 稀疏点数量：235
- 平均 track length：2

为了将 A 插入 Blender 融合场景，我们额外编写了一个转换脚本，将 COLMAP 稀疏点转换为：

- ASCII PLY 点云；
- 由小立方体组成的 OBJ；
- 居中版本的 OBJ。

对应文件路径如下：

- `results/A_box/colmap/sparse_txt/a_box_sparse_points.ply`
- `results/A_box/colmap/sparse_txt/a_box_sparse_cubes.obj`
- `results/A_box/colmap/sparse_txt/a_box_sparse_cubes_centered.obj`

在 Blender 中，我们对这些小立方体进行筛选与清理，只保留主要连通块，并将其作为 A 的几何代理加入最终场景。需要说明的是，最终融合展示采用的是基于 COLMAP 稀疏重建结果的可视化表示，而不是完整的物体级高质量 3DGS 或表面网格，因此 A 的视觉质量明显弱于 B 与 C，但其空间位置与真实几何来源仍具有明确意义。

### 5.2 物体 B：文本到 3D 生成

物体 B 采用 Magic3D 路线完成。我们使用 threestudio 的 `magic3d-system`，通过文本 Prompt 生成一个花瓶类三维资产。最终选用的 Prompt 如下：

`a single elegant ceramic vase, smooth white glazed ceramic, minimalistic shape, clean silhouette, studio product photography, centered object, clean background, highly detailed 3D asset`

从实验配置文件可知，B 的主要训练设置包括：

- 方法：Magic3D
- 最大训练步数：3000
- 优化器：Adam
- 学习率：0.01
- 背景模块学习率：0.001
- Guidance：Stable Diffusion v1.5

最终导出的结果文件为：

- `results/b_vase_magic3d_v2/trial/save/it3000-export/model.obj`

该结果在形状完整性方面较好，适合作为最终融合视频中的虚拟物体。

### 5.3 物体 C：单图到 3D 生成

物体 C 选用真实鼠标。首先对单张鼠标图片进行前景抠图，获得透明背景的 RGBA 图像，再使用 Zero123 路线进行单图到 3D 重建。

从配置文件可知，C 的主要设置包括：

- 方法：Zero123
- 输入图像：去背景后的鼠标图片
- 最大训练步数：2000
- 优化器：Adam
- 学习率：0.01
- Guidance：Zero123-XL

最终导出的结果文件为：

- `results/c_mouse_zero123/trial/save/it2000-export/model.obj`

相较于文本到 3D 的 B，C 的几何形状与原始物体更一致，但由于仅依赖单张图像，其背面与遮挡区域的恢复能力仍然有限。

### 5.4 背景场景重建

背景选择 Mip-NeRF 360 数据集中的 `counter` 场景，并采用 Gaussian Splatting 路线进行训练。配置参数中可确认：

- source path：`data/background/counter`
- model path：`outputs/background_counter`
- `eval=True`

训练完成后，得到了背景点云结果，例如：

- `results/background_counter/point_cloud/iteration_30000/point_cloud (1).ply`

该结果用于后续 Blender 融合。

### 5.5 场景融合与统一表达

本题的一个难点在于不同资产的表示形式并不一致：

- 背景：3DGS 结果，本质上是高斯点表示；
- B、C：threestudio 导出的 OBJ Mesh；
- A：COLMAP 稀疏点，经额外脚本转换为由小立方体组成的可视化 OBJ。

为了统一表达并完成最终渲染，我们采用了 Blender 融合方案：

1. 将 B、C 的 OBJ 直接导入 Blender。
2. 将 A 的 `a_box_sparse_cubes_centered.obj` 导入 Blender，并通过清理离群点与适当缩放，保留其主要结构。
3. 将背景的 PLY 点云导入 Blender，作为统一环境背景。
4. 在 Blender 中对三个物体进行摆位、缩放与构图设计。
5. 设置相机多关键帧，生成漫游式融合视频。

这种方案的优点在于工程实现相对直接，能够在有限时间内将不同来源、不同表示形式的三维资产统一到同一场景中；其不足在于背景点云在 Blender 中更接近视口可视化效果，渲染管线不如纯 Mesh 工作流稳定，因此最终视频导出采用了更务实的视口 / Playblast 方案。

---

## 6. 结果展示

### 6.1 A / B / C 单体结果

- A：完成了真实物体的 COLMAP 位姿恢复与稀疏三维重建，并进一步生成了 Blender 可导入的立方体代理模型。
- B：完成了基于文本 Prompt 的花瓶三维生成，并成功导出 OBJ Mesh。
- C：完成了基于单张鼠标图像的 Zero123 三维生成，并成功导出 OBJ Mesh。

### 6.2 背景结果

- 使用 `counter` 场景完成背景训练，并成功导出背景点云结果，可用于后续融合展示。

### 6.3 融合结果

最终在 Blender 中将背景与 A、B、C 三个物体统一放置到同一场景中，并通过多关键帧相机路径生成了带有镜头运动的融合视频。当前最终视频文件为：

- `final_fusion-2.mp4`

若最终提交时采用其他文件名，应同步修改报告中的对应描述。

### 6.4 训练曲线与可视化图表

按照课程要求，报告需提供训练过程中的 Loss 曲线等可视化结果。由于本次实验训练阶段未接入 WandB / SwanLab 在线记录平台，因此本文中的训练曲线图均依据 threestudio / PyTorch Lightning 在本地导出的 `metrics.csv` 日志文件重新绘制，用于展示训练过程中的损失变化趋势。换言之，本文图表的数据来源是真实训练日志，本报告中的曲线并非手工伪造，也不是后验估计，而是对本地原始训练记录的可视化重绘。若最终提交时需要严格对齐课程对 WandB / SwanLab 平台截图的要求，可在后续补录到相应平台后再替换为平台导出图。

#### 6.4.1 训练曲线总览

![训练曲线总览](report_assets/fig_loss_overview_final.png)

图中左侧为 B 的 Magic3D 训练过程中 `SDS loss` 的变化趋势，右侧为 C 的 Zero123 训练过程中 `total loss` 与 `zero123_sds loss` 的变化趋势。

#### 6.4.2 B：Magic3D 曲线

![B: Magic3D 训练曲线](report_assets/fig_b_loss_final.png)

现象分析：

- `train/loss_sds` 在训练前期波动较大，说明文本到 3D 路线对初始化较敏感；
- 辅助损失如 `orient / sparsity / opaque` 整体维持在较低量级，主要作用是约束几何与体密度；
- 由于文本到 3D 的优化本质上带有较强不稳定性，因此曲线呈现明显震荡是符合预期的。

#### 6.4.3 C：Zero123 曲线

![C: Zero123 训练曲线](report_assets/fig_c_loss_final.png)

现象分析：

- `train/loss` 与 `train/loss_ref` 在训练初期下降较快，说明单图先验迅速对几何形状起到约束；
- `train/loss_zero123_sds` 虽然仍存在波动，但整体处于可控范围；
- 相比 B，C 在参考图像约束下训练过程更稳定，最终更容易保持与真实鼠标轮廓的一致性。

#### 6.4.4 C：代理验证指标曲线

![C: 代理验证指标曲线](report_assets/fig_c_proxy_validation_final.png)

由于当前实验流程未额外保存标准验证集的数值日志，因此本文进一步基于 `results/c_mouse_zero123/trial/save/itXXX-val.mp4` 中保存的阶段性验证视频，提取每个阶段的首帧渲染结果，并与条件输入参考图进行相似性比较，构建代理验证指标曲线。这里给出的指标包括：

- `PSNR`：反映代理验证视图与参考图在像素空间上的误差水平；
- `SSIM`：反映结构相似程度；
- `Mask IoU`：根据前景掩码估计目标轮廓的一致性。

需要说明的是，这些曲线并不是课程意义上的“标准验证集指标”，而是基于真实中间验证输出构造的代理评价结果，主要用于反映 `C` 在训练过程中对输入条件图的保持程度与形状稳定性变化趋势。对应的原始数值表可见：

- `report_assets/c_proxy_validation_metrics.csv`

### 6.5 超参数与指标详表

#### 6.5.1 A / B / C / 背景实验设置表

| 模块 | 方法 / 系统 | 输入 | 网络 / 表达 | 优化器 | 学习率 | 训练步数 / 迭代数 | 主要损失 / 约束 | 关键输出 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| A | COLMAP 稀疏重建 + Blender 代理融合 | 包装盒多视角图像 | 稀疏点云 + 小立方体 OBJ 代理 | 不适用 | 不适用 | 不适用 | 特征匹配与三角化，不属于神经网络训练 | `a_box_sparse_cubes_centered.obj` |
| B | threestudio `magic3d-system` | 文本 Prompt | implicit-volume + HashGrid | Adam | geometry `0.01`，background `0.001` | `3000` steps | `loss_sds`、`loss_orient`、`loss_sparsity`、`loss_opaque` | `it3000-export/model.obj` |
| C | threestudio `zero123-system` | 鼠标 RGBA 单图 | implicit-volume + HashGrid | Adam | `0.01` | `2000` steps | `loss_ref`、`loss_zero123`、`loss_zero123_sds`、`loss_rgb`、`loss_mask`、`loss_orient` 等 | `it2000-export/model.obj` |
| 背景 | Gaussian Splatting | Mip-NeRF 360 `counter` | 3DGS / SH degree `3` | `[待补，如需可查训练脚本默认值]` | `[待补]` | 至少到 `30000` iteration | 高斯点优化 | `point_cloud (1).ply` |

#### 6.5.2 C 路线分阶段分辨率 / batch 设置

Zero123 配置中采用渐进式分辨率与 batch 设置，关键配置如下：

| 阶段 | 图像分辨率 | 随机相机 batch size | milestone |
| --- | --- | --- | --- |
| 阶段 1 | `128 x 128` | `12` | step `< 200` |
| 阶段 2 | `256 x 256` | `4` | `200 <= step < 300` |
| 阶段 3 | `512 x 512` | `2` | step `>= 300` |

#### 6.5.3 结果指标与完成情况表

| 模块 | 关键结果指标 | 当前结果 |
| --- | --- | --- |
| A | COLMAP 稀疏点数量 | `235` |
| A | 代理融合形式 | 稀疏点转小立方体 OBJ 后在 Blender 融合 |
| B | 最大训练步数 | `3000` |
| B | 导出状态 | 已成功导出 OBJ |
| C | 最大训练步数 | `2000` |
| C | 导出状态 | 已成功导出 OBJ |
| 背景 | 点云输出迭代 | `30000` |
| 最终融合 | 三物体是否全部进入场景 | 是 |
| 最终融合 | 视频是否成功导出 | 是 |
| 最终融合 | 视频文件 | `final_fusion-2.mp4` |

#### 6.5.4 模型权重与核心结果文件说明

按照课程要求，需要在报告中给出项目的模型权重或核心结果文件说明。结合本题不同模块的实现方式，本实验中的“最优模型权重 / 最终结果文件”可整理如下：

| 模块 | 类型 | 推荐作为提交材料的文件 | 说明 |
| --- | --- | --- | --- |
| A | 重建结果文件 | `results/A_box/colmap/sparse/1/points3D.bin` | A 不属于神经网络训练任务，因此不存在 `ckpt` 类权重文件；其核心结果为 COLMAP 稀疏重建输出。 |
| A | 重建结果文件 | `results/A_box/colmap/sparse/1/images.bin` | 对应相机位姿与图像索引信息。 |
| A | 重建结果文件 | `results/A_box/colmap/sparse/1/cameras.bin` | 对应相机内参信息。 |
| A | 融合代理几何 | `results/A_box/colmap/sparse_txt/a_box_sparse_cubes_centered.obj` | 最终用于 Blender 融合的代理几何文件。 |
| B | 最终模型权重 | `results/b_vase_magic3d_v2/trial/ckpts/epoch=0-step=3000.ckpt` | 花瓶文本到 3D 训练完成后保留的最终 checkpoint，可作为最优/最终权重提交。 |
| B | 备用权重 | `results/b_vase_magic3d_v2/trial/ckpts/last.ckpt` | 与最终 checkpoint 对应的 latest 权重备份。 |
| B | 导出模型 | `results/b_vase_magic3d_v2/trial/save/it3000-export/model.obj` | 最终导出的 Mesh 结果。 |
| C | 最终模型权重 | `results/c_mouse_zero123/trial/ckpts/epoch=0-step=2000.ckpt` | 鼠标单图到 3D 训练完成后保留的最终 checkpoint，可作为最优/最终权重提交。 |
| C | 备用权重 | `results/c_mouse_zero123/trial/ckpts/last.ckpt` | 与最终 checkpoint 对应的 latest 权重备份。 |
| C | 导出模型 | `results/c_mouse_zero123/trial/save/it2000-export/model.obj` | 最终导出的 Mesh 结果。 |
| 背景 | 最终场景结果 | `results/background_counter/point_cloud/iteration_30000/point_cloud (1).ply` | 背景 3DGS 的最终点云结果。 |

若最终提交时需要上传网盘，可优先上传以下几项作为“模型权重 / 核心结果”：

- `B`：`epoch=0-step=3000.ckpt`
- `C`：`epoch=0-step=2000.ckpt`
- 背景：`iteration_30000/point_cloud (1).ply`
- `A`：COLMAP 稀疏重建结果与 Blender 代理几何文件

如果课程要求“首页或末页给出模型权重下载链接”，则可在网盘上传上述文件后，将共享链接填写到报告首页与附录的对应位置。

#### 6.5.5 代码仓库说明、环境说明与运行命令

为满足课程对于 `GitHub Repository / README / 环境配置 / 数据准备 / 运行命令` 的要求，本文对应的仓库材料已整理为以下文件：

- 仓库说明文件：`README.md`
- 生成任务环境说明：`environments/gen3d_environment.yml`
- 背景重建环境说明：`environments/gsbg2_environment.yml`

其中 `README.md` 已包含以下内容：

- 项目概述与目录结构；
- A / B / C / 背景的输入数据说明；
- 关键输出文件路径；
- 代表性的训练命令；
- Blender 融合与最终视频位置；
- 报告辅助脚本说明。

在环境说明方面，本项目采用多环境方案而不是单一环境：

- `gen3d`：用于 threestudio / Magic3D / Zero123 路线；
- `gsbg2`：用于 Gaussian Splatting 背景重建；
- Windows + Blender：用于本地融合和视频导出。

在数据准备方面，README 中已分别说明：

- A：将真实包装盒视频抽帧后放入 `results/A_box/images/`；
- B：直接采用文本 Prompt，无需额外图像；
- C：准备去背景后的鼠标 RGBA 图像；
- 背景：准备 Mip-NeRF 360 的 `counter` 场景数据。

在运行命令方面，README 中已记录并整理：

- A 的 COLMAP 代表性命令；
- B 的 Magic3D 训练命令；
- C 的 Zero123 训练命令；
- 背景 Gaussian Splatting 的代表性训练命令；
- 最终 Blender 融合所使用的输入文件位置。

---

## 7. 三种方法对比分析

### 7.1 几何准确度

- A 的几何来源最贴近真实采集数据，因此在真实物体一致性上最强。
- 但由于当前最终展示采用的是 COLMAP 稀疏点的代理表示，A 的可视化效果较粗糙。
- C 基于真实单图输入，整体轮廓与原始鼠标较一致。
- B 为纯文本生成，形状完整但与现实中某个具体物体不存在一一对应关系。

### 7.2 纹理细节

- B 和 C 的导出 Mesh 在视觉上明显优于 A 的稀疏点代理。
- B 的整体纹理和轮廓较统一，视觉效果较“完整”。
- C 保留了真实鼠标的一些整体形状特征，但单图方法在不可见面的细节恢复上仍存在局限。
- A 在最终视频中主要体现为空间位置与结构示意，纹理表达最弱。

### 7.3 计算成本与工程复杂度

- A 的核心成本在于数据采集与 COLMAP 处理。
- B 和 C 的主要成本在于 GPU 训练时间、模型依赖和环境配置。
- 背景 3DGS 的环境编译和 CUDA 扩展安装过程最复杂，调试成本较高。
- 融合阶段由于资产表达形式不一致，需要额外进行 Blender 层面的工程处理。

### 7.4 综合结论

- 若强调与真实物体的一致性，真实采集路线更可靠，但需要更完整、更稳定的重建链路支持。
- 若强调视觉完整性与生成效率，文本到 3D 路线更适合快速获得外观完整的三维资产。
- 若已拥有单张真实图像并希望快速恢复特定物体的整体形状，则单图到 3D 路线具有较高实用价值。

---

## 8. 关键问题与调试过程

本实验在实现过程中涉及多套环境、不同三维表示形式以及 CUDA 扩展编译，因此调试工作占据了较大比重。核心问题主要包括以下三类：

### 8.1 Zero123 环境与权重问题

- 权重下载中断；
- 环境切换时 Python 路径混乱；
- `ldm` 相关模块缺失；
- YAML 配置需替换为兼容版本；
- 显存不足导致任务被系统 `Killed`。

最终通过更换更大显存实例、使用兼容配置并重新整理依赖环境解决。

### 8.2 背景 Gaussian Splatting 编译问题

- CUDA / nvcc 路径不匹配；
- `glm/glm.hpp` 缺失；
- `simple-knn` 与 PyTorch 动态库链接问题；
- 多个扩展包需分别编译与修复依赖。

最终通过安装 `cuda-toolkit`、补齐 GLM 头文件、修复动态库路径等方式完成背景训练。

### 8.3 Blender 融合问题

- 原始融合工程未保存，需要重新导入素材；
- A 只有稀疏点代理，需要清理离群方块并重新缩放；
- 背景 PLY 在 Blender 中主要以点云方式显示，普通渲染不稳定；
- 最终通过视口导出 / Playblast 方案完成融合视频生成，并成功保留背景点云与三物体效果。

---

## 9. 不足与改进方向

尽管本次实验已经完成题目要求的主要流程，但从结果质量和工程完备性来看，仍存在以下不足：

1. A 在最终视频中采用的是稀疏点代理几何，而不是完整高质量物体重建结果。
2. 背景点云在 Blender 中更偏向视口显示方案，渲染稳定性不如标准 Mesh 流程。
3. 最终融合镜头设计较为基础，若有更多时间可以进一步优化光照、材质与镜头路径。
4. 若后续继续完善，可重点考虑：
   - 对 A 补做更完整的物体级 3DGS 或表面重建；
   - 将背景点云进一步转换为更适合渲染的场景表示；
   - 增加更自然的镜头轨迹、更高分辨率输出以及更稳定的渲染方案。

---

## 10. 结论

本实验完成了从真实物体采集、AIGC 三维资产生成、背景场景重建，到 Blender 场景融合与视频导出的完整流程。通过将多源三维资产统一到同一场景中，我们验证了不同 3D 生成路线在同一工程管线下协同融合的可行性。

从实验结果来看：

- 文本到 3D 路线适合快速生成视觉完整的虚拟资产；
- 单图到 3D 路线适合从真实图像恢复特定物体的整体结构；
- 真实多视角路线在几何真实性方面最具潜力，但需要更完整、更稳定的重建流程支撑；
- Blender 作为统一融合平台，能够在资产表达不一致的条件下完成最终展示，是一条具有现实可操作性的工程折中方案。

---

## 11. 外部链接与提交说明

按照课程要求，报告首页或末页需附上项目 GitHub 仓库链接以及模型权重下载地址。由于当前这两项信息尚未最终确定，本文先保留如下占位，待最终提交前统一补齐：

- GitHub 仓库链接：`[待填写]`
- 模型权重网盘链接：`[待填写]`

此外，训练曲线图的来源说明如下：

- 本报告中的 Loss 曲线依据本地 `metrics.csv` 日志文件重绘；
- 原始日志来自 threestudio / PyTorch Lightning 训练过程自动导出的本地记录；
- 当前版本未提供 WandB / SwanLab 平台导出截图。

最终提交前，请同时将首页和末页中的占位同步更新，确保助教能够直接访问相关仓库和下载链接。

---

## 12. 提交前待补信息

以下内容在正式提交前仍需补齐：

- `[ ]` 三位组员学号
- `[ ]` 三位组员具体分工
- `[ ]` GitHub 仓库链接
- `[ ]` 模型权重网盘链接
- `[ ]` 如果有训练曲线图，插入 Loss 曲线截图
- `[ ]` 如果最终视频文件名不是 `final_fusion-2.mp4`，同步修改文中描述
- `[ ]` 将本草稿整理成 PDF 版正式报告
