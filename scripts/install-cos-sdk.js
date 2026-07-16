// scripts/install-cos-sdk.js
// 腾讯云COS SDK安装脚本

const fs = require('fs')
const path = require('path')
const { execSync } = require('child_process')

console.log('🚀 开始安装腾讯云COS SDK...')

try {
  // 检查是否已安装npm
  execSync('npm --version', { stdio: 'inherit' })
  
  // 安装COS SDK
  console.log('📦 安装 cos-wx-sdk-v5...')
  execSync('npm install cos-wx-sdk-v5', { stdio: 'inherit' })
  
  console.log('✅ COS SDK安装完成!')
  
  // 更新package.json中的依赖
  const packagePath = path.join(__dirname, '../package.json')
  const packageJson = JSON.parse(fs.readFileSync(packagePath, 'utf8'))
  
  // 确保dependencies存在
  if (!packageJson.dependencies) {
    packageJson.dependencies = {}
  }
  
  // 添加COS SDK依赖
  packageJson.dependencies['cos-wx-sdk-v5'] = '^1.3.0'
  
  // 写入更新后的package.json
  fs.writeFileSync(packagePath, JSON.stringify(packageJson, null, 2))
  
  console.log('📝 package.json已更新')
  
  // 创建安装完成标记
  const installMarker = path.join(__dirname, '../.cos-sdk-installed')
  fs.writeFileSync(installMarker, `COS SDK安装完成: ${new Date().toISOString()}`)
  
  console.log('🎉 腾讯云COS SDK安装流程完成!')
  console.log('')
  console.log('下一步操作:')
  console.log('1. 配置 .env 文件中的腾讯云密钥')
  console.log('2. 在微信小程序后台配置合法域名')
  console.log('3. 运行 npm run setup 进行完整配置')
  
} catch (error) {
  console.error('❌ 安装失败:', error.message)
  console.log('')
  console.log('请检查:')
  console.log('1. Node.js是否已安装')
  console.log('2. npm是否可用')
  console.log('3. 网络连接是否正常')
  process.exit(1)
}