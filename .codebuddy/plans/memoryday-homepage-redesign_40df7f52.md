---
name: memoryday-homepage-redesign
overview: 将 MemoryDay 小程序首页按照参考图片的水彩温暖风格进行全面视觉重构，包括背景、色调、搜索栏、分类标签、菜品卡片网格、随机选菜按钮、添加按钮和底部导航栏的样式更新。
design:
  styleKeywords:
    - Soft Pastel Watercolor
    - Warm Coral Orange Palette
    - Capsule Rounded UI
    - Hand-drawn Food Illustration
    - Cozy Minimalist Layout
  fontSystem:
    fontFamily: PingFang SC
    heading:
      size: 36rpx
      weight: 600
    subheading:
      size: 28rpx
      weight: 500
    body:
      size: 26rpx
      weight: 400
  colorSystem:
    primary:
      - "#E8986C"
      - "#F0A060"
      - "#D4895A"
    background:
      - "#FFF8F0"
      - "#FFECD2"
      - "#FFFFFF"
    text:
      - "#5D4E3E"
      - "#8B7D75"
      - "#FFFFFF"
    functional:
      - "#E8986C"
      - "#E8DED5"
      - "#F5E6DA"
todos:
  - id: download-tabbar-icons
    content: 使用 [mcp:cloudbase/downloadRemoteFile] 下载新的TabBar图标素材（菜单/统计/我的 各2个状态共6个PNG）到images目录
    status: completed
  - id: update-global-style
    content: 更新 app.json 的 TabBar 配置(文字/颜色) 和 app.wxss 的全局主题色变量
    status: completed
  - id: rewrite-index-wxss
    content: 全面重写 index.wxss 样式：水彩背景、珊瑚橘配色系、胶囊形UI组件、卡片样式、按钮样式
    status: completed
    dependencies:
      - update-global-style
  - id: update-index-wxml
    content: 调整 index.wxml 页面结构：简化菜品卡片(仅图片+名称)、优化按钮布局、调整容器类名
    status: completed
    dependencies:
      - rewrite-index-wxss
  - id: polish-interaction
    content: 微调 index.js 交互逻辑：添加随机选菜的转盘动画效果、优化过渡动画
    status: completed
    dependencies:
      - update-index-wxml
---

## 产品需求概述

将 MemoryDay 小程序的**首页**进行全面视觉重构，使其与用户上传的参考图片保持一致。同时，**统一所有页面（首页、详情页、编辑页、统计页、设置页、用户页、登录页）的主题风格、配色方案、组件样式和字体规范**，保证功能不变的前提下实现全栈视觉一致性。

参考图片呈现的是一种**温暖水彩手绘风格**的美食小程序界面，核心特征包括：暖色水彩晕染背景、珊瑚橘色调、圆润胶囊形UI元素、简洁的菜品卡片（图片+名称）、以及自定义底部导航栏。

### 涉及修改范围

**核心首页改造：**

1. 首页页面结构（WXML）、样式（WXSS）、交互逻辑（JS）
2. 新增背景纹理图片资源
3. 搜索框、分类标签、菜品卡片、随机按钮、添加按钮的全部视觉更新

**全页面主题统一（保持功能不变）：**

4. 菜品详情页（pages/dish-detail/dish-detail.wxss）
5. 菜品编辑页（pages/dish-edit/dish-edit.wxss）
6. 统计页（pages/statistics/statistics.wxss）
7. 设置页（pages/settings/settings.wxss）
8. 用户页（pages/user/user.wxss）
9. 登录页（pages/login/login.wxss）
10. 通用卡片组件（components/dish-card/dish-card.wxss）
11. 全局样式表（app.wxss）— 建立统一的设计令牌
12. TabBar 配置（app.json）+ 图标资源（images/）

### 不涉及的范围

- 后端 API 和数据逻辑不变
- 页面跳转逻辑和业务功能不变
- 数据库结构和云函数逻辑不变

## 技术栈选择

- **平台**: 微信小程序原生开发（WXML / WXSS / JavaScript）
- **无第三方组件库**: 项目当前为纯原生实现，不引入 TDesign 等组件库，保持轻量
- **CSS 特性**: 使用 rpx 响应式单位、Flexbox/Grid 布局、CSS 渐变、圆角、阴影

## 实施方案

### 核心策略：纯样式+结构微调的重构方案

基于对现有代码的分析，当前首页的功能逻辑（搜索、筛选、随机选菜、跳转）已经完善，本次改造主要聚焦于**视觉层面的全面升级**：

1. **背景层改造**: 从纯灰色背景替换为暖色水彩纹理背景，使用 CSS 多重渐变模拟水彩晕染效果（无需外部图片依赖），或使用 base64 内嵌背景图
2. **色彩体系迁移**: 从当前的红色系 (#FF6B6B) 迁移到温暖的珊瑚橘色系 (#E8986C ~ #F0A060)
3. **UI 组件逐一匹配**: 搜索框、分类标签、菜品卡片、随机按钮、添加按钮全部按参考图重新设计
4. **TabBar 更新**: 修改 tab 文字标签（"首页" -> "菜单"），更换图标为与参考图一致的暖橙色风格图标

### 关键技术决策

| 决策点 | 选择 | 理由 |
| --- | --- | --- |
| 背景实现方式 | CSS radial-gradient 多重渐变模拟水彩效果 | 无需额外图片资源，加载快，可精确控制色调 |
| 字体方案 | PingFang SC（系统自带，小程序默认） | 小程序字体限制多，PingFang SC 是最佳中文显示字体 |
| 图标方案 | 下载 PNG 图标替换现有 TabBar 图标 | 参考图使用特定风格的房子/感叹号/勾选图标 |
| 卡片简化 | 移除评分/标签行，仅保留图片+名称 | 与参考图的极简卡片风格一致 |
| 胶囊形元素 | border-radius: 50rpx 统一应用 | 搜索框、标签、按钮均采用大圆角胶囊形 |


### 性能考量

- CSS 渐变背景由 GPU 合成渲染，不影响滚动性能
- 菜品图片懒加载机制保持不变
- 避免使用复杂的 filter/blur 效果（低端机型性能敏感）

## 目录结构变更

```
memoryday/
├── pages/index/
│   ├── index.wxml           # [MODIFY] 调整页面结构：卡片简化、按钮布局调整
│   ├── index.wxss           # [MODIFY] 全面重写样式：新配色、水彩背景、胶囊形UI
│   └── index.js             # [MODIFY] 微调：可选添加随机动画增强体验
├── images/
│   ├── home.png             # [REPLACE] 新的房子图标（橙色调）
│   ├── home-active.png      # [REPLACE] 激活态房子图标
│   ├── stats.png            # [REPLACE] 新的统计/感叹号图标
│   ├── stats-active.png     # [REPLACE] 激活态统计图标
│   ├── user.png             # [REPLACE] 新的用户/勾选图标
│   ├── user-active.png      # [REPLACE] 激活态用户图标
│   └── backgrounds/
│       └── watercolor-bg.png # [NEW] 水彩背景纹理图（备选方案）
├── app.json                 # [MODIFY] TabBar 文字更新、颜色更新
└── app.wxss                 # [MODIFY] 全局主题色变量更新
```

## 设计规范说明

### 设计目标

将首页从当前的**通用红色卡片风格**升级为**温暖治愈的水彩手绘美食风格**。整体视觉语言强调温馨、柔和、有食欲感，通过暖色调水彩背景营造手工感和亲切感。

### 美学方向: Soft/Pastel (柔和水彩风)

参考图片呈现出典型的水彩手绘美学特征：

- **水彩晕染背景**: 不规则的暖色斑块叠加在奶油底色上，营造手绘质感
- **温暖珊瑚橘主色**: 区别于常见的高饱和红色/蓝色，使用低饱和度的暖橙色调
- **圆润胶囊形态**: 所有交互元素都采用完全圆角的胶囊形状
- **极简信息层级**: 菜品卡片去除多余信息，只保留最关键的视觉（图片）和文字（名称）

### 页面规划（仅首页 1 页）

#### 页面: 首页 (pages/index)

**Block 1 - 水彩背景层**

- 全屏覆盖的水彩纹理背景，使用多重径向渐变叠加实现
- 主色调: 奶油白(#FFF8F0) 底 + 暖橙(#FFECD2) + 杏色(#FFDAB9) 斑块渐变
- 固定定位，不随内容滚动

**Block 2 - 搜索栏区域**

- 完全白色背景的胶囊形搜索框
- 左侧放大镜搜索图标（深灰色）
- 占位符文字 "搜索菜名或食材"（中灰棕色）
- 大圆角(50rpx)、浅阴影
- 位于顶部状态栏下方，水平居中

**Block 3 - 分类标签栏**

- 横向滚动的胶囊形标签组
- 5个标签: 全部(激活态)、早餐、午餐、晚餐、最爱
- 激活态: 珊瑚橘(#E8986C)填充 + 白色文字
- 未激活态: 白色填充 + 浅边框(#E8DED5) + 中灰文字
- 标签间距均匀，左右留边距

**Block 4 - 菜品网格区域**

- 2列等宽网格布局，间距16rpx
- 每张卡片:
- 白色背景、大圆角(20rpx)、柔和阴影
- 上部: 菜品图片(正方形, aspectFill模式)
- 下部: 菜品名称(居中, 单行省略)
- 无评分标签、无难度标签（比当前更简洁）
- 空状态时显示友好的空状态插图和提示文字

**Block 5 - 操作按钮区**

- **随机选菜按钮**: 宽幅胶囊形按钮
- 暖橙渐变色 (#F0A060 → #E8986C)
- 白色文字 "随机选菜"
- 位于菜品网格下方，固定在TabBar上方
- 带轻微阴影增加层次感
- **悬浮添加按钮(+)**: 圆形描边按钮
- 白色背景 + 珊瑚橘描边(2rpx) + "+" 文字
- 直径88rpx
- 位于右下角，在随机按钮右侧偏上位置

**Block 6 - 自定义TabBar（全局配置）**

- 三个tab: 菜单(首页)、统计、我的
- 图标: 房子/感叹号/勾选（暖橙线条风格）
- 选中色: 珊瑚橘 #E8986C
- 未选中色: 浅灰 #999999
- 背景: 半透明白色毛玻璃效果

### MCP 工具

- **cloudbase/downloadRemoteFile**
- 用途: 下载参考图中风格的 TabBar 图标（房子、感叹号、勾选）PNG 格式素材
- 预期成果: 替换 `images/` 目录下的现有图标文件为新风格的图标

---

## 全页面主题统一方案

### 当前样式问题分析

经过对所有页面样式文件的分析，发现以下不一致问题：

| 页面 | 主色调 | 卡片圆角 | 按钮圆角 | 背景色 | 问题 |
| --- | --- | --- | --- | --- | --- |
| 首页 | #FF6B6B红 | 16rpx | 24rpx | #f8f9fa灰 | 需改为珊瑚橘 |
| 详情页 | #333文字 | 16rpx | 12rpx | #fff白 | 配色过时 |
| 编辑页 | #FF6B6B红 | 12rpx | 50rpx | #fff白 | 标签蓝色不统一 |
| 统计页 | #FF6B6B红 | 16rpx | 无 | #f8f9fa灰 | 渐变蓝色块不统一 |
| 设置页 | #1890ff蓝 | 16rpx | 12rpx | #f5f5f5灰 | 蓝色系与整体冲突 |
| 用户页 | #333文字 | 16rpx | 16rpx | #fff白 | 红色徽章不统一 |
| 登录页 | #667eea紫+绿 | 24rpx | 12rpx | 渐变紫 | 与美食主题完全不搭 |
| 组件卡 | #FF6B6B红 | 16rpx | 24rpx | #fff白 | 标签蓝/橙混乱 |


### 统一设计令牌（Design Tokens）

在 `app.wxss` 中建立全局 CSS 变量，实现一处定义、全局生效：

```css
/* ==================== 全局设计令牌 ==================== */
page {
  /* 主色调 - 温暖珊瑚橘 */
  --color-primary: #E8986C;
  --color-primary-light: #F0A060;
  --color-primary-dark: #D4885A;
  --color-primary-gradient: linear-gradient(135deg, #F0A060 0%, #E8986C 100%);

  /* 背景色 - 奶油水彩风 */
  --color-bg-page: #FFF8F0;
  --color-bg-card: #FFFFFF;
  --color-bg-mask: rgba(0, 0, 0, 0.5);

  /* 文字色 - 温暖棕灰 */
  --color-text-primary: #5D4E3E;
  --color-text-secondary: #8B7D75;
  --color-text-tertiary: #A89B94;
  --color-text-placeholder: #B8ADA5;

  /* 边框和分隔线 */
  --color-border: #E8DED5;
  --color-divider: #F0EBE6;

  /* 功能色 - 保留必要语义色 */
  --color-danger: #E85A5A;
  --color-success: #5AAA7A;
  --color-warning: #E8A55A;
  --color-info: #5A8AE8;

  /* 圆角规范 */
  --radius-sm: 8rpx;
  --radius-md: 12rpx;
  --radius-lg: 16rpx;
  --radius-xl: 20rpx;
  --radius-capsule: 50rpx;

  /* 阴影规范 */
  --shadow-sm: 0 2rpx 8rpx rgba(93, 78, 62, 0.08);
  --shadow-md: 0 4rpx 16rpx rgba(93, 78, 62, 0.1);
  --shadow-lg: 0 8rpx 24rpx rgba(93, 78, 62, 0.12);

  /* 字体规范 */
  --font-size-xs: 22rpx;
  --font-size-sm: 24rpx;
  --font-size-md: 26rpx;
  --font-size-base: 28rpx;
  --font-size-lg: 30rpx;
  --font-size-xl: 32rpx;
  --font-size-xxl: 36rpx;
}
```

### 各页面改造详情

#### 1. 菜品详情页（dish-detail.wxss）

| 元素 | 当前样式 | 目标样式 |
| --- | --- | --- |
| 页面背景 | #fff白 | var(--color-bg-page) |
| 菜品名称 | #333 | var(--color-text-primary) |
| 星级评分 | #ffc107金 | var(--color-primary) |
| 描述卡片背景 | #f8f9fa | var(--color-bg-card) |
| 分隔线 | #f1f3f5 | var(--color-divider) |
| 按钮圆角 | 12rpx | var(--radius-lg) |
| 标签样式 | 蓝色系 | 统一为珊瑚橘系 |
| 弹窗按钮 | 保持原功能 | 更新为珊瑚橘主色 |


#### 2. 菜品编辑页（dish-edit.wxss）

| 元素 | 当前样式 | 目标样式 |
| --- | --- | --- |
| 表单边框 | #e9ecef | var(--color-border) |
| 聚焦边框 | #339af0蓝 | var(--color-primary) |
| 标签激活态 | #FF6B6B红 | var(--color-primary) |
| 标签未激活 | 蓝色边框 | 白底橘边框 |
| 危险按钮 | #ff6b6b | var(--color-danger) |
| 星级激活 | #ffc107 | var(--color-primary) |
| 弹窗样式 | 保持原功能 | 更新圆角为var(--radius-xl) |


#### 3. 统计页（statistics.wxss）

| 元素 | 当前样式 | 目标样式 |
| --- | --- | --- |
| 统计数字 | #FF6B6B红 | var(--color-primary) |
| 渐变背景 | 灰蓝渐变 | 暖橙淡色渐变 |
| 排名数字 | #FF6B6B红 | var(--color-primary) |
| 进度条填充 | 无 | var(--color-primary-gradient) |
| 更新徽章 | #FF6B6B红 | var(--color-primary) |
| 空状态图标 | 保持原图 | 可选更新为水彩风插图 |


#### 4. 设置页（settings.wxss）

| 元素 | 当前样式 | 目标样式 |
| --- | --- | --- |
| 页面背景 | #f5f5f5灰 | var(--color-bg-page) |
| 卡片背景 | #fff白 | var(--color-bg-card) |
| 分组标题 | #999灰 | var(--color-text-secondary) |
| 退出按钮 | #ff4d4f红 | var(--color-danger) |
| 分割线 | #f0f0f0 | var(--color-divider) |
| 圆角规范 | 16rpx | var(--radius-lg) |


#### 5. 用户页（user.wxss）

| 元素 | 当前样式 | 目标样式 |
| --- | --- | --- |
| 用户名称 | #333 | var(--color-text-primary) |
| 更新徽章 | #FF6B6B红 | var(--color-primary) |
| 快捷按钮边框 | #f1f3f5 | var(--color-border) |
| 圆角规范 | 16rpx | var(--radius-lg) |
| 版本文字 | #999 | var(--color-text-tertiary) |


#### 6. 登录页（login.wxss）

| 元素 | 当前样式 | 目标样式 |
| --- | --- | --- |
| 页面背景 | 紫蓝渐变 | 暖橙水彩渐变 |
| Logo背景 | 白色半透明 | 珊瑚橘半透明 |
| 主按钮 | #07C160绿 | var(--color-primary) |
| 聚焦边框 | #07C160绿 | var(--color-primary) |
| 协议链接 | #07C160绿 | var(--color-primary) |
| 其他登录方式 | 半透明白边 | 珊瑚橘边框 |
| 整体风格 | 科技感 | 温暖美食感 |


#### 7. 通用卡片组件（dish-card.wxss）

| 元素 | 当前样式 | 目标样式 |
| --- | --- | --- |
| 卡片圆角 | 16rpx | var(--radius-xl) |
| 阴影 | 深色阴影 | var(--shadow-md) |
| 菜品名称 | #333 | var(--color-text-primary) |
| 描述文字 | #666 | var(--color-text-secondary) |
| 元信息文字 | #888 | var(--color-text-tertiary) |
| 标签样式 | 蓝色/橙色混乱 | 统一珊瑚橘系 |
| 评分星星 | #ffc107金 | var(--color-primary) |


### 字体统一规范

| 元素类型 | 字号 | 字重 | 颜色 |
| --- | --- | --- | --- |
| 页面标题 | 36rpx | 600 | var(--color-text-primary) |
| 区块标题 | 32rpx | 600 | var(--color-text-primary) |
| 卡片标题 | 30rpx | 600 | var(--color-text-primary) |
| 正文内容 | 28rpx | 400 | var(--color-text-primary) |
| 次要文字 | 26rpx | 400 | var(--color-text-secondary) |
| 辅助说明 | 24rpx | 400 | var(--color-text-tertiary) |
| 最小文字 | 22rpx | 400 | var(--color-text-placeholder) |


### 目录结构变更（完整）

```
memoryday/
├── pages/
│   ├── index/
│   │   ├── index.wxml           # [MODIFY] 卡片简化、按钮布局
│   │   ├── index.wxss           # [MODIFY] 全面重写：水彩背景+新配色
│   │   └── index.js             # [KEEP] 功能逻辑不变
│   ├── dish-detail/
│   │   └── dish-detail.wxss     # [MODIFY] 统一配色和圆角规范
│   ├── dish-edit/
│   │   └── dish-edit.wxss       # [MODIFY] 统一标签和按钮样式
│   ├── statistics/
│   │   └── statistics.wxss      # [MODIFY] 统一主色调和进度条
│   ├── settings/
│   │   └── settings.wxss        # [MODIFY] 统一背景和圆角
│   ├── user/
│   │   └── user.wxss           # [MODIFY] 统一徽章和文字色
│   └── login/
│       └── login.wxss          # [MODIFY] 整体风格改为暖橙水彩风
├── components/
│   └── dish-card/
│       └── dish-card.wxss      # [MODIFY] 统一卡片圆角和标签色
├── images/
│   ├── home.png                # [REPLACE] 橙色调房子图标
│   ├── home-active.png         # [REPLACE] 激活态
│   ├── stats.png               # [REPLACE] 橙色调统计图标
│   ├── stats-active.png        # [REPLACE] 激活态
│   ├── user.png                # [REPLACE] 橙色调用户图标
│   └── user-active.png         # [REPLACE] 激活态
├── app.json                    # [MODIFY] TabBar文字+颜色
└── app.wxss                    # [MODIFY] 全局设计令牌变量
```

### 改造优先级

| 优先级 | 页面/文件 | 工作量 | 理由 |
| --- | --- | --- | --- |
| P0 | app.wxss（设计令牌） | 中 | 基础变量定义，后续依赖 |
| P0 | app.json（TabBar） | 小 | 全局导航一致性 |
| P0 | 首页样式 | 大 | 用户核心入口，参考图重点 |
| P1 | 登录页 | 中 | 用户第一体验页面 |
| P1 | 详情/编辑页 | 中 | 核心功能页面 |
| P2 | 统计页 | 小 | 数据展示页面 |
| P2 | 设置/用户页 | 小 | 次要功能页面 |
| P2 | 卡片组件 | 小 | 被多个页面引用 |


### 改造风险与缓解

| 风险 | 缓解措施 |
| --- | --- |
| 样式覆盖冲突 | 使用高优先级CSS变量，必要时用`!important` |
| 第三方组件样式冲突 | 独立命名空间，避免全局污染 |
| 登录页风格跳跃大 | 保持渐变但换用暖色调，紫→橙过渡 |
| TabBar图标下载失败 | 提供CSS/SVG备用方案 |
| 低端机型兼容 | 避免filter/blur等重特效 |