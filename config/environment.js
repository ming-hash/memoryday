// 环境配置
const { isDevelopment } = require('./env')

const devMode = isDevelopment()

module.exports = {
  // API配置
  API_BASE_URL: devMode 
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
    enableLog: devMode,
    enablePerformance: devMode
  }
}
