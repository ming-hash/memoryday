#!/usr/bin/env node

/**
 * 项目初始化脚本
 * 用于设置开发环境和初始化配置
 */

const fs = require('fs')
const path = require('path')
const { execSync } = require('child_process')

console.log('🚀 开始初始化今日吃啥小程序项目...\n')

// 检查Node.js版本
const nodeVersion = process.version
console.log(`📦 Node.js版本: ${nodeVersion}`)

if (parseFloat(nodeVersion.slice(1)) < 14) {
  console.warn('⚠️  建议使用Node.js 14或更高版本')
}

// 创建必要的目录结构
const directories = [
  'images/dishes',
  'images/icons', 
  'images/backgrounds',
  'components/common',
  'components/layout',
  'services',
  'config',
  'utils',
  'docs'
]

console.log('\n📁 创建目录结构...')
directories.forEach(dir => {
  const dirPath = path.join(__dirname, '..', dir)
  if (!fs.existsSync(dirPath)) {
    fs.mkdirSync(dirPath, { recursive: true })
    console.log(`✅ 创建目录: ${dir}`)
  } else {
    console.log(`ℹ️  目录已存在: ${dir}`)
  }
})

// 检查微信开发者工具
console.log('\n🔧 检查开发环境...')
try {
  const result = execSync('which cli', { encoding: 'utf8' })
  console.log('✅ 微信开发者工具CLI已安装')
} catch (error) {
  console.log('ℹ️  微信开发者工具CLI未安装，请手动安装')
}

// 创建环境配置文件
console.log('\n⚙️  创建环境配置...')
const envConfig = `// 环境配置
const isDevelopment = process.env.NODE_ENV === 'development'

module.exports = {
  // API配置
  API_BASE_URL: isDevelopment 
    ? 'http://localhost:8000/api' 
    : 'https://api.yourdomain.com/api',
  
  // 上传配置
  UPLOAD_CONFIG: {
    maxSize: 5 * 1024 * 1024, // 5MB
    allowedTypes: ['image/jpeg', 'image/png', 'image/gif', 'image/webp']
  },
  
  // 应用配置
  APP_CONFIG: {
    name: '今日吃啥',
    version: '1.0.0',
    description: '帮你记录和管理菜谱的小程序'
  },
  
  // 开发工具配置
  DEV_TOOLS: {
    enableLog: isDevelopment,
    enablePerformance: isDevelopment
  }
}
`

fs.writeFileSync(path.join(__dirname, '..', 'config', 'environment.js'), envConfig)
console.log('✅ 创建环境配置文件')

// 创建Git忽略规则
console.log('\n🔒 配置Git忽略规则...')
const gitignore = `# 依赖目录
node_modules/
npm-debug.log*
yarn-debug.log*
yarn-error.log*

# 开发工具生成的文件
project.config.json
project.private.config.json
*.workspace

# 日志文件
*.log
logs/

# 运行时文件
*.pid
*.seed
*.pid.lock

# 构建输出
dist/
build/

# 环境变量
.env
.env.local
.env.development.local
.env.test.local
.env.production.local

# IDE
.vscode/
.idea/
*.swp
*.swo
*~

# 操作系统
.DS_Store
.DS_Store?
._*
.Spotlight-V100
.Trashes
ehthumbs.db
Thumbs.db

# 临时文件
*.tmp
*.temp
`

fs.writeFileSync(path.join(__dirname, '..', '.gitignore'), gitignore)
console.log('✅ 更新.gitignore文件')

// 创建package.json脚本
console.log('\n📦 配置Package.json脚本...')
const packageJsonPath = path.join(__dirname, '..', 'package.json')
let packageJson = {}

if (fs.existsSync(packageJsonPath)) {
  packageJson = JSON.parse(fs.readFileSync(packageJsonPath, 'utf8'))
}

packageJson.scripts = {
  "dev": "echo '请在微信开发者工具中编译'",
  "build": "echo '请在微信开发者工具中上传'", 
  "lint": "eslint . --ext .js",
  "format": "prettier --write \"**/*.{js,json,wxml,wxss}\"",
  "setup": "node scripts/setup.js",
  "clean": "rm -rf dist build",
  "test": "echo '暂无测试框架'"
}

fs.writeFileSync(packageJsonPath, JSON.stringify(packageJson, null, 2))
console.log('✅ 更新Package.json脚本')

console.log('\n🎉 项目初始化完成！')
console.log('\n📋 下一步操作：')
console.log('1. 打开微信开发者工具')
console.log('2. 选择项目目录')
console.log('3. 点击"编译"开始开发')
console.log('4. 运行 npm run dev 启动开发服务器\n')

console.log('💡 提示：')
console.log('- 修改 config/environment.js 配置API地址')
console.log('- 查看 DEV_GUIDE.md 获取详细开发指南')
console.log('- 运行 npm run lint 检查代码规范\n')

console.log('Happy Coding! 🚀')