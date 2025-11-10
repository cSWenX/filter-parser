#!/bin/bash

# 云部署构建脚本
echo "🚀 开始构建云部署版本..."

# 清理旧的构建文件
echo "🧹 清理旧的构建文件..."
rm -rf dist
rm -rf node_modules/.vite

# 安装依赖
echo "📦 安装依赖..."
npm install

# 构建项目
echo "🔨 构建项目..."
npm run build

# 检查构建结果
if [ -d "dist" ]; then
    echo "✅ 构建成功！"
    echo "📊 构建文件大小："
    du -sh dist/*
    echo "📁 构建文件列表："
    find dist -name "*.js" -o -name "*.css" -o -name "*.html" | head -10
else
    echo "❌ 构建失败！"
    exit 1
fi

# 验证关键文件存在
echo "🔍 验证关键文件..."
if [ ! -f "dist/index.html" ]; then
    echo "❌ 缺少 index.html"
    exit 1
fi

if [ ! -f "dist/assets/index-*.js" ] && [ ! -f "dist/assets/index.js" ]; then
    echo "❌ 缺少主要JavaScript文件"
    exit 1
fi

if [ ! -f "dist/assets/index-*.css" ] && [ ! -f "dist/assets/index.css" ]; then
    echo "❌ 缺少主要CSS文件"
    exit 1
fi

echo "🎉 云部署构建完成，可以部署到Zeabur了！"