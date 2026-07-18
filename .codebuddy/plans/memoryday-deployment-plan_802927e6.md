---
name: memoryday-deployment-plan
overview: 为 MemoryDay 微信小程序项目制定完整的云服务器部署方案，同时支持 CloudBase 云服务部署和自建服务器部署，提供 IP+端口和域名两种访问方式供小程序切换。
todos:
  - id: install-docker
    content: 安装 Docker 和 Docker Compose 到 OpenCloudOS 9 服务器
    status: completed
  - id: config-firewall
    content: 配置防火墙，开放 80/443/8000 端口
    status: completed
    dependencies:
      - install-docker
  - id: deploy-cloudfunctions
    content: 使用 [cloudbase MCP] 部署 CloudFunctions（getOpenId 和 memoryday-api）
    status: completed
    dependencies:
      - install-docker
  - id: deploy-cloudrun
    content: 使用 [cloudbase MCP] 部署 CloudRun 容器服务
    status: completed
    dependencies:
      - install-docker
  - id: prepare-env
    content: 准备 backend/.env 配置文件
    status: completed
    dependencies:
      - install-docker
  - id: start-docker-compose
    content: 启动 Docker Compose 服务（Django + MySQL + Redis + Nginx）
    status: completed
    dependencies:
      - prepare-env
  - id: db-migration
    content: 执行数据库迁移和静态文件收集
    status: completed
    dependencies:
      - start-docker-compose
  - id: update-miniprogram-config
    content: 修改小程序 app.js，添加访问方式配置开关
    status: completed
    dependencies:
      - db-migration
  - id: test-backend
    content: 测试自建后端服务健康检查
    status: completed
    dependencies:
      - db-migration
  - id: test-miniprogram
    content: 测试小程序功能（切换访问模式）
    status: completed
    dependencies:
      - update-miniprogram-config
---

## 产品概述

MemoryDay 微信小程序后端部署项目，需要将小程序完整部署到云服务器，包括 CloudBase 云服务和自建服务器后端。

## 核心功能

- **CloudBase 云函数**: 部署 getOpenId 和 memoryday-api，处理微信登录和 API 请求
- **CloudBase 云托管**: 部署 memoryday-backend Node.js 容器服务
- **自建后端服务**: Django REST Framework API + MySQL + Redis + Nginx
- **小程序前端**: 支持 IP+端口和域名两种访问方式，通过配置文件开关切换
- **环境安装**: 在 OpenCloudOS 9 服务器上安装 Docker 和所有依赖服务

## 技术架构

- 服务器: OpenCloudOS 9, 2核2G
- 容器: Docker + Docker Compose
- 后端: Django 4.2.7 + Django REST Framework
- 数据库: MySQL 8.0
- 缓存: Redis 7
- 反向代理: Nginx
- 小程序: 微信原生小程序框架

## 技术栈

- **服务器环境**: OpenCloudOS 9, Docker, Docker Compose
- **CloudBase**: CloudFunctions (Node.js), CloudRun (容器)
- **自建后端**: Django 4.2.7, MySQL 8.0, Redis 7, Nginx
- **小程序前端**: 原生微信小程序, JavaScript

## 实施方案

### CloudBase 部署

- 使用 CloudBase MCP 工具部署云函数
- 使用 manageCloudRun 部署容器服务

### 自建服务器部署

- Docker Compose 编排所有服务
- 环境变量配置敏感信息
- Nginx 反向代理 HTTP/HTTPS 请求

### 小程序配置

- 添加全局配置开关 accessMode
- 支持运行时切换 IP/域名访问方式

## 目录结构

```
memoryday/
├── cloudfunctions/
│   ├── getOpenId/       # 微信登录云函数
│   └── memoryday-api/   # API 云函数
├── cloudrun/
│   └── memoryday-backend/  # CloudRun 容器
├── backend/             # 自建 Django 后端
│   ├── docker/          # Docker 配置
│   ├── apps/           # Django 应用
│   └── manage.py
├── miniprogram/        # 微信小程序前端
│   ├── app.js          # 全局配置（需修改）
│   └── pages/          # 页面组件
└── docker-compose.yml  # Docker 编排配置
```

## Agent Extensions

### MCP 工具

- **cloudbase (MCP)**: 用于部署 CloudBase 云函数和云托管服务
- 用途: 部署 cloudfunctions/ 和 cloudrun/ 到 CloudBase
- 预期结果: CloudFunctions 和 CloudRun 服务上线并可访问

### Skill

- **cloud-functions**: CloudBase 云函数开发规范
- 用途: 指导云函数部署流程和配置
- 预期结果: 云函数正确部署并响应请求
- **cloudrun-development**: CloudBase 云托管开发规范
- 用途: 指导容器化后端部署
- 预期结果: 容器服务运行在 CloudBase
- **miniprogram-development**: 微信小程序开发规范
- 用途: 指导小程序配置和调试
- 预期结果: 小程序正确配置访问方式