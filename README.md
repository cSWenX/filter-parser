# Filter-Parser 图片滤镜参数反向分析软件

## 🔍 项目概述

这是一个图片滤镜参数反向分析软件，用户上传带滤镜效果的图片，系统自动分析并提取滤镜参数（亮度、对比度、饱和度等），支持参数保存、历史管理和基于历史参数生成新的滤镜图片。

## 🎯 核心功能

1. **图片滤镜参数分析** - 自动识别8类核心参数的调整值
2. **参数保存与管理** - 本地存储历史参数，支持命名和删除
3. **滤镜图片生成** - 基于历史参数对新图片应用滤镜效果
4. **数据导出** - 支持参数复制和TXT文件导出

## 🏗️ 技术架构

### 前端
- **React 18** + TypeScript
- **Vite** 构建工具
- **Tailwind CSS** 样式框架
- **Zustand** 状态管理
- **react-dropzone** 文件上传

### 后端
- **Flask** Web框架
- **OpenCV** 图像分析
- **Pillow** 图像处理
- **NumPy** 数值计算

## 📁 项目结构

```
Filter-Parser/
├── frontend/          # React前端应用
├── backend/           # Flask后端API
├── uploads/           # 临时上传目录
├── output/            # 生成图片输出
└── docs/              # 项目文档
```

详细结构参见 `项目结构设计.md`

## 🚀 快速开始

### 环境要求
- Node.js 16+
- Python 3.8+
- npm/yarn

### 安装依赖

**前端依赖**
```bash
cd frontend
npm install
```

**后端依赖**
```bash
cd backend
pip install -r requirements.txt
```

### 启动开发服务器

**启动后端**
```bash
cd backend
python app.py
# 运行在 http://localhost:5000
```

**启动前端**
```bash
cd frontend
npm run dev
# 运行在 http://localhost:3000
```

## 📋 开发记录

### 已完成任务
- [x] 项目架构设计
- [x] 技术栈选型
- [x] 目录结构规划
- [x] 核心算法设计

### 待开发功能
- [ ] 前端React应用搭建
- [ ] 后端Flask API开发
- [ ] 图像分析算法实现
- [ ] 滤镜生成算法实现
- [ ] 本地存储和加密
- [ ] 文件管理和清理机制
- [ ] 测试用例编写

## 🔧 核心模块说明

### 图像分析模块 (`backend/services/image_analyzer.py`)
负责分析上传图片的8类核心参数：
- 亮度 (Brightness)
- 对比度 (Contrast)
- 饱和度 (Saturation)
- 锐化 (Sharpness)
- 色温 (Color Temperature)
- 色调 (Hue)
- 阴影 (Shadow)
- 高光 (Highlight)

### 滤镜生成模块 (`backend/services/filter_generator.py`)
基于历史参数对新上传图片应用滤镜效果，支持：
- 像素级参数调整
- 批量参数应用
- 原始分辨率保持

### 本地存储模块 (`frontend/services/storage.ts`)
管理历史参数的本地存储：
- 加密存储用户参数
- 最多保存50条记录
- 支持参数的增删改查

## 📊 性能指标

- 单张图片分析时间: ≤3秒
- 滤镜图片生成时间: ≤2秒
- 并发处理能力: 50用户
- 参数分析精度误差: ≤±8%
- 历史参数存储上限: 50条

## 🔒 安全特性

- 图片24小时自动清理
- 本地参数数据加密
- 严格的文件格式验证
- CORS跨域访问控制

## 📝 API接口

### 主要端点
- `POST /api/upload` - 图片上传
- `POST /api/analyze` - 参数分析
- `POST /api/generate` - 滤镜生成
- `GET /api/health` - 健康检查

详细API文档参见 `docs/API.md`

## 🐛 调试信息

### 常见问题
1. **图片上传失败** - 检查文件格式和大小限制
2. **分析时间过长** - 可能是图片尺寸过大，建议压缩
3. **参数保存失败** - 检查localStorage空间和浏览器权限

### 日志位置
- 前端日志: 浏览器Console
- 后端日志: 终端输出

## 🧪 测试

### 运行测试
```bash
# 前端测试
cd frontend && npm test

# 后端测试
cd backend && pytest
```

### 测试覆盖
- 单元测试: 核心算法和工具函数
- 集成测试: API接口和数据流
- E2E测试: 完整用户操作流程

## 📋 部署说明

详细部署指南参见 `docs/DEPLOYMENT.md`

## 🔄 版本管理

当前版本: v1.0.0-dev

### 版本更新时需要同步：
- 更新 `项目结构设计.md`
- 更新本README文件
- 更新相关配置文件

---

*本文档会随项目开发进度持续更新*