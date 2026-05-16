# LongTailLib-Eval 联邦长尾学习评估平台

LongTailLib-Eval 是一个专注于**联邦长尾学习（Federated Long-Tail Learning）**的评估与实验平台。

近期项目经历了一次重大的架构重构，从原有的基于 Tkinter 的桌面客户端 GUI（`gui.py`）升级为了现代化的 **B/S (浏览器/服务器)** 架构。新架构采用了前后端分离的设计，大幅提升了交互体验、任务调度能力及数据可视化的效果。

## ✨ 核心特性

- **现代化的 UI 界面**：前端采用 Vue 3 + Element Plus 构建，提供响应式、体验优异的现代化操作界面。
- **高性能 API 与任务调度**：后端基于 FastAPI 开发，通过子进程稳定管理长期运行的实验任务，提供标准的 RESTful API。
- **实时日志与监控**：通过引入 WebSocket 协议，实现系统日志和进程运行时信息向前端的低延迟实时推送。
- **可视化数据分析**：内置了包括实验结果对比分析、长尾数据分布特征（长尾度）的多种图表展示。
- **便捷的文件系统集成**：后端 API 打通系统层，前端可直观查看和使用本地 `dataset/` 模型数据集库以及 `results/` 评估产生的结果输出。

## 📁 目录结构摘要

```text
LongTailLib-main/
├── backend/                  # FastAPI 后端服务端代码
│   ├── main.py               # 后端主程序与 API 路由入口
│   └── requirements.txt      # 后端专属 Python 依赖
├── frontend/                 # 基于 Vue 3 的现代前端应用代码
│   ├── src/                  # 前端源码、页面视图及组件库
│   └── package.json          # Node 依赖清单与构建脚本
├── dataset/                  # 核心本地模型数据集存放目录
├── results/                  # 历史训练数据以及运行评估结果目录
├── system/                   # 联邦长尾学习底层训练评估控制逻辑
├── env_cuda_latest.yaml      # 核心运行时的 Conda 环境配置表
└── gui.py                    # Legacy：旧版 Tkinter 界面入口（已弃用/作历史参考）
```

## 🚀 部署与运行指南

环境要求：
- 系统：Windows / Linux / macOS
- 核心环境：Anaconda / Miniconda，Python 3.11+
- 前端环境：Node.js (建议 v16 及以上) 与 npm

请按顺序启动和配置环境：

### 1. 配置 Conda 核心运行环境

核心联邦学习系统依赖基于 GPU 的 PyTorch 等相关深度学习生态环境：

```bash
# 在项目根目录下，通过 yaml 创建 Conda 虚拟环境
conda env create -f env_cuda_latest.yaml

# 激活新创建的虚拟环境
conda activate LongTailLib
```

### 2. 启动 Backend (FastAPI 服务)

在激活的 `LongTailLib` Conda 环境中完成最后后端运行所需的依赖补充并启动监听：

```bash
# 切换至后端目录
cd backend

# 安装后端依赖库
pip install -r requirements.txt

# 启动 FastAPI 服务端服务 (热重载模式, 默认暴露 8000 端口)
python -m uvicorn main:app --reload --host 0.0.0.0 --port 8000
```
> 服务验证：启动后您可以在浏览器中访问 `http://localhost:8000/docs` 查看 Swagger UI 提供的接口交互文档。

### 3. 启动 Frontend (Vue 3 页面服务端)

在**全新的终端窗口**中完成前端项目的依赖初始化和调试启动：

```bash
# 切换至前端目录
cd frontend

# 安装所有前端构建运行时所需的 Node 依赖
npm install

# 启动 Vite 的本地热更新开发服务器 (默认往往分配 5173 端口)
npm run dev
```

成功运行后终端会给出一个本地地址（如：`http://localhost:5173`）。在您的现代浏览器中打开它，即可纵览并操作联邦学习评估平台的所有功能。
