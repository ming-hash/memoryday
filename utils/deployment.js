// utils/deployment.js

/**
 * 部署模式管理工具
 */

// 部署模式配置
const DEPLOYMENT_CONFIGS = {
  'local-dev': {
    name: 'local-dev',
    title: '本地开发环境',
    description: '使用本地Docker容器运行后端服务',
    apiUrl: 'http://localhost:8000/api',
    useCloudBase: false,
    enabled: true,
    priority: 1
  },
  'local': {
    name: 'local',
    title: '本地生产环境',
    description: '本地完整生产环境部署',
    apiUrl: 'http://localhost:8000/api',
    useCloudBase: false,
    enabled: true,
    priority: 2
  },
  'cloudbase': {
    name: 'cloudbase',
    title: '腾讯云CloudBase',
    description: '云端部署，无需管理服务器',
    apiUrl: 'https://whateatday-0gor3cwl4f527bba.tcloudbaseapp.com/api',
    useCloudBase: true,
    cloudBaseEnv: 'whateatday-0gor3cwl4f527bba',
    enabled: true,
    priority: 3
  }
}

/**
 * 获取部署配置
 */
function getDeploymentConfig(mode) {
  return DEPLOYMENT_CONFIGS[mode] || DEPLOYMENT_CONFIGS['local-dev']
}

/**
 * 获取所有可用的部署模式
 */
function getAvailableDeployments() {
  return Object.values(DEPLOYMENT_CONFIGS)
    .filter(config => config.enabled)
    .sort((a, b) => a.priority - b.priority)
}

/**
 * 检测最佳部署模式
 */
function detectBestDeployment() {
  // 尝试从本地存储获取用户偏好
  const savedConfig = wx.getStorageSync('deploymentConfig')
  if (savedConfig && savedConfig.mode) {
    return savedConfig.mode
  }
  
  // 默认使用本地开发环境
  return 'local-dev'
}

/**
 * 测试部署连接
 */
function testDeploymentConnection(mode) {
  return new Promise((resolve, reject) => {
    const config = getDeploymentConfig(mode)
    
    if (config.useCloudBase) {
      // 测试CloudBase连接
      wx.cloud.callFunction({
        name: 'memoryday-api',
        data: { action: 'healthCheck' },
        success: (res) => {
          resolve({
            mode: mode,
            status: 'success',
            responseTime: Date.now(),
            data: res.result
          })
        },
        fail: (err) => {
          reject({
            mode: mode,
            status: 'error',
            error: err
          })
        }
      })
    } else {
      // 测试本地API连接
      wx.request({
        url: config.apiUrl + '/health/',
        method: 'GET',
        timeout: 10000,
        success: (res) => {
          resolve({
            mode: mode,
            status: 'success',
            responseTime: Date.now(),
            data: res.data
          })
        },
        fail: (err) => {
          reject({
            mode: mode,
            status: 'error',
            error: err
          })
        }
      })
    }
  })
}

/**
 * 切换部署模式
 */
function switchDeploymentMode(mode, app) {
  const config = getDeploymentConfig(mode)
  
  if (!config || !config.enabled) {
    throw new Error(`部署模式 ${mode} 不可用`)
  }
  
  // 更新全局配置
  if (app && app.globalData) {
    app.globalData.deploymentMode = mode
    app.globalData.baseUrl = config.apiUrl
    app.globalData.useCloudBase = config.useCloudBase
    
    if (config.cloudBaseEnv) {
      app.globalData.cloudBaseEnv = config.cloudBaseEnv
    }
  }
  
  // 保存到本地存储
  wx.setStorageSync('deploymentConfig', {
    mode: mode,
    baseUrl: config.apiUrl,
    useCloudBase: config.useCloudBase,
    cloudBaseEnv: config.cloudBaseEnv,
    switchTime: Date.now()
  })
  
  return config
}

/**
 * 获取当前部署状态
 */
function getCurrentDeploymentStatus(app) {
  const currentMode = app?.globalData?.deploymentMode || detectBestDeployment()
  const config = getDeploymentConfig(currentMode)
  
  return {
    mode: currentMode,
    config: config,
    baseUrl: app?.globalData?.baseUrl || config.apiUrl,
    useCloudBase: app?.globalData?.useCloudBase || config.useCloudBase,
    isLocal: currentMode.startsWith('local'),
    isCloud: currentMode === 'cloudbase'
  }
}

/**
 * 自动检测并切换最佳部署模式
 */
async function autoDetectBestDeployment(app) {
  const availableModes = getAvailableDeployments()
  
  // 按优先级测试连接
  for (const modeConfig of availableModes) {
    try {
      const result = await testDeploymentConnection(modeConfig.name)
      if (result.status === 'success') {
        // 切换到可用的模式
        switchDeploymentMode(modeConfig.name, app)
        return {
          success: true,
          mode: modeConfig.name,
          config: modeConfig,
          responseTime: result.responseTime
        }
      }
    } catch (error) {
      console.warn(`部署模式 ${modeConfig.name} 连接失败:`, error)
      continue
    }
  }
  
  // 所有模式都失败，使用默认模式
  const defaultMode = 'local-dev'
  switchDeploymentMode(defaultMode, app)
  
  return {
    success: false,
    mode: defaultMode,
    config: getDeploymentConfig(defaultMode),
    error: '所有部署模式连接失败，已切换到默认模式'
  }
}

/**
 * 初始化部署配置
 */
function initDeployment(app) {
  // 从本地存储加载配置
  const savedConfig = wx.getStorageSync('deploymentConfig')
  
  if (savedConfig && savedConfig.mode) {
    // 使用保存的配置
    switchDeploymentMode(savedConfig.mode, app)
  } else {
    // 使用默认配置
    const defaultMode = detectBestDeployment()
    switchDeploymentMode(defaultMode, app)
  }
  
  return getCurrentDeploymentStatus(app)
}

module.exports = {
  DEPLOYMENT_CONFIGS,
  getDeploymentConfig,
  getAvailableDeployments,
  detectBestDeployment,
  testDeploymentConnection,
  switchDeploymentMode,
  getCurrentDeploymentStatus,
  autoDetectBestDeployment,
  initDeployment
}