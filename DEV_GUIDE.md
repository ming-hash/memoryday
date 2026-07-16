# 今日吃啥 - 开发指南

## 🚀 快速开始

### 环境要求
- 微信开发者工具最新版本
- Node.js 14+ (可选，用于构建工具)
- Git 版本控制

### 开发步骤

1. **克隆项目**
   ```bash
   git clone <项目地址>
   cd memoryday
   ```

2. **打开微信开发者工具**
   - 选择项目目录
   - 使用测试号或正式AppID
   - 点击"编译"开始开发

3. **开发模式**
   ```bash
   # 开发环境
   npm run dev
   
   # 生产环境构建
   npm run build
   ```

## 📁 项目结构

```
memoryday/
├── app.js                 # 小程序入口
├── app.json              # 全局配置
├── app.wxss             # 全局样式
├── project.config.json  # 项目配置
├── sitemap.json         # 搜索配置
│
├── components/          # 自定义组件
│   ├── loading/         # 加载组件
│   ├── empty-state/     # 空状态组件
│   └── dish-card/       # 菜品卡片组件
│
├── pages/               # 页面文件
│   ├── index/           # 首页
│   ├── dish-detail/     # 菜品详情
│   ├── dish-edit/       # 菜品编辑
│   ├── statistics/      # 统计页面
│   ├── user/           # 用户页面
│   ├── login/          # 登录页面
│   └── settings/       # 设置页面
│
├── utils/               # 工具函数
│   ├── util.js         # 通用工具
│   ├── api.js          # API封装
│   ├── validator.js    # 验证工具
│   ├── event.js        # 事件总线
│   └── performance.js   # 性能监控
│
├── config/              # 配置文件
│   ├── config.js        # 应用配置
│   └── env.js          # 环境配置
│
├── services/            # 服务层
│   └── storage.js       # 存储服务
│
├── images/              # 图片资源
│   ├── dishes/          # 菜品图片
│   ├── icons/           # 图标资源
│   └── backgrounds/    # 背景图片
│
└── docs/                # 文档
    ├── API.md          # API文档
    └── DESIGN.md       # 设计规范
```

## 🛠️ 开发规范

### 代码风格
- 使用ES6+语法特性
- 组件命名采用帕斯卡命名法 (PascalCase)
- 变量命名采用驼峰命名法 (camelCase)
- 文件命名采用短横线命名法 (kebab-case)

### 组件开发
```javascript
// components/example/example.js
Component({
  properties: {
    // 属性定义
    title: {
      type: String,
      value: '默认标题'
    }
  },
  
  data: {
    // 内部状态
    count: 0
  },
  
  methods: {
    // 事件处理
    onTap() {
      this.triggerEvent('customEvent', { value: this.data.count })
    }
  }
})
```

### API调用规范
```javascript
// 使用封装的API服务
const { dishApi } = require('../../utils/api')

Page({
  async getDishes() {
    try {
      const dishes = await dishApi.getDishes()
      this.setData({ dishes })
    } catch (error) {
      app.showErrorToast('获取菜品失败')
    }
  }
})
```

### 状态管理
- 页面状态使用 `data` 管理
- 全局状态使用 `app.globalData`
- 持久化数据使用 `StorageService`

## 🔧 常用命令

### 开发命令
```bash
# 启动开发服务器
npm run dev

# 构建生产版本
npm run build

# 代码检查
npm run lint

# 代码格式化
npm run format
```

### Git工作流
```bash
# 创建功能分支
git checkout -b feature/新功能

# 提交更改
git add .
git commit -m "feat: 添加新功能"

# 推送到远程
git push origin feature/新功能

# 创建Pull Request
```

## 📱 页面路由

### 主要页面
| 页面 | 路径 | 功能 |
|------|------|------|
| 首页 | `/pages/index/index` | 菜品展示和随机选择 |
| 详情页 | `/pages/dish-detail/dish-detail` | 菜品详细信息 |
| 编辑页 | `/pages/dish-edit/dish-edit` | 新增/编辑菜品 |
| 统计页 | `/pages/statistics/statistics` | 数据统计和分析 |
| 用户页 | `/pages/user/user` | 个人中心和设置 |
| 登录页 | `/pages/login/login` | 用户认证 |
| 设置页 | `/pages/settings/settings` | 应用设置 |

### 页面跳转
```javascript
// 跳转到详情页
wx.navigateTo({
  url: `/pages/dish-detail/dish-detail?id=${dishId}`
})

// 返回上一页
wx.navigateBack()

// 跳转到tab页
wx.switchTab({
  url: '/pages/index/index'
})
```

## 🎨 样式规范

### 尺寸单位
- 使用 `rpx` 作为主要尺寸单位
- 设计稿宽度为 750rpx
- 1rpx = 屏幕宽度 / 750

### 颜色规范
```css
/* 主色调 */
--primary-color: #07C160;
--primary-hover: #05a854;

/* 辅助色 */
--success-color: #07C160;
--warning-color: #FF976A;
--danger-color: #FF4D4F;

/* 中性色 */
--text-color: #333;
--text-secondary: #666;
--text-disabled: #999;
--border-color: #e0e0e0;
--background-color: #f5f5f5;
```

### 间距规范
```css
/* 间距变量 */
--spacing-xs: 8rpx;
--spacing-sm: 16rpx;
--spacing-md: 24rpx;
--spacing-lg: 32rpx;
--spacing-xl: 48rpx;
```

## 🔐 权限配置

### 小程序权限
```json
{
  "permission": {
    "scope.userLocation": {
      "desc": "你的位置信息将用于小程序位置接口的效果展示"
    },
    "scope.camera": {
      "desc": "需要访问你的相机用于拍照上传菜品图片"
    },
    "scope.writePhotosAlbum": {
      "desc": "需要访问你的相册用于选择菜品图片"
    }
  }
}
```

## 📊 性能优化

### 图片优化
- 使用合适的图片格式 (WebP > JPEG > PNG)
- 图片大小不超过 500KB
- 使用懒加载和预加载

### 代码优化
- 按需引入组件和工具
- 使用分包加载
- 避免频繁的setData操作

### 网络优化
- API请求合并
- 数据缓存策略
- 离线功能支持

## 🐛 调试技巧

### 开发者工具
- 使用Console面板查看日志
- 使用Network面板监控请求
- 使用Storage面板查看缓存

### 真机调试
- 使用预览功能测试真机效果
- 使用远程调试解决真机问题

## 📦 发布流程

1. **测试验证**
   - 功能测试
   - 性能测试
   - 兼容性测试

2. **代码审核**
   - 代码质量检查
   - 安全漏洞扫描
   - 用户体验评估

3. **提交审核**
   - 填写版本信息
   - 上传代码包
   - 等待审核通过

4. **发布上线**
   - 选择发布版本
   - 设置发布范围
   - 监控线上效果

## 🤝 贡献指南

### 提交Issue
1. 描述问题或建议
2. 提供复现步骤
3. 添加相关截图

### 提交PR
1. Fork项目仓库
2. 创建功能分支
3. 编写测试用例
4. 更新相关文档

### 代码审查
- 至少需要1个审查者批准
- 通过所有自动化测试
- 符合代码规范要求

## 📞 技术支持

### 常见问题
1. **图片上传失败**
   - 检查网络连接
   - 确认图片格式和大小

2. **登录失败**
   - 检查微信授权状态
   - 确认API服务正常

3. **页面白屏**
   - 检查JavaScript错误
   - 确认依赖加载完成

### 获取帮助
- 查看文档和示例
- 提交Issue寻求帮助
- 联系开发团队支持

---

**Happy Coding! 🎉**