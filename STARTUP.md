# 项目启动指南

## 快速开始

### 后端启动
```bash
cd backend
pip3 install -r requirements.txt
python3 app.py
```

### 前端启动
```bash
cd frontend
npm install
npm run dev
```

## 验证服务

- 后端: http://localhost:5000/api/health
- 前端: http://localhost:3000

## 开发状态

✅ 项目架构完成
✅ 后端Flask API完成
✅ 前端React组件完成
🔄 依赖安装和服务启动

## 核心功能已实现

1. **图片上传**: 支持拖拽上传，格式验证
2. **参数分析**: 8类滤镜参数自动识别
3. **结果展示**: 参数卡片，置信度显示
4. **参数保存**: 本地存储，加密保护
5. **数据导出**: TXT文件导出，参数复制

## API接口

- `POST /api/upload` - 图片上传
- `POST /api/analyze/{image_id}` - 参数分析
- `POST /api/generate` - 滤镜生成
- `GET /api/health` - 健康检查

## 技术栈

**后端**: Flask + OpenCV + PIL + NumPy
**前端**: React + TypeScript + Tailwind + Zustand

项目结构完整，代码已就绪，请安装依赖后启动服务即可使用！