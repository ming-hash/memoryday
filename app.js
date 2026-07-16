// app.js
const { eventBus, Events } = require('./utils/event')
const { performanceMonitor, PerformancePoints } = require('./utils/performance')
const StorageService = require('./services/storage')
const { getEnvVars, isDevelopment } = require('./config/env')
const deploymentUtil = require('./utils/deployment')

App({
  onLaunch() {
    // 性能监控 - 应用启动
    performanceMonitor.monitorPageLoad()
    
    // 初始化环境变量
    this.globalData.env = getEnvVars()
    
    // 初始化部署配置
    this.initDeploymentConfig()
    
    // 开发环境日志
    if (isDevelopment()) {
      console.log('小程序启动 - 开发环境')
      console.log('环境变量:', this.globalData.env)
      console.log('API地址:', this.globalData.baseUrl)
      console.log('CODEBUDDY_DEBUG app.js: 检查图片资源是否存在')
    }

    // 初始化用户信息
    this.initUserInfo()

    // 监听网络状态变化
    this.monitorNetwork()

    // 监听应用生命周期事件
    this.setupAppLifecycle()

    // 触发应用就绪事件
    eventBus.emit(Events.APP_READY)
  },
  globalData: {
    userInfo: null,
    env: {},
    baseUrl: 'http://localhost:8000/api', // 初始化时先设置为开发环境，后续在onLaunch中更新
    useCloudBase: false, // 是否使用腾讯云CloudBase
    cloudBaseEnv: '', // CloudBase环境ID
    deploymentMode: 'local-dev', // 部署模式：local-dev, local, cloudbase
    localApiUrl: 'http://localhost:8000/api', // 本地API地址
    dishes: [],
    filters: {
      mealTime: null,
      cookingTime: [],
      difficulty: [],
      cuisineType: [],
      ingredients: []
    },
    settings: {
      notifications: true,
      darkMode: false,
      autoBackup: false
    },
    network: {
      isConnected: true,
      type: 'wifi'
    }
  },

  // 初始化用户信息
  initUserInfo() {
    const userInfo = StorageService.getUserInfo()
    const token = StorageService.getToken()
    
    if (userInfo && token) {
      this.globalData.userInfo = userInfo
      eventBus.emit(Events.USER_LOGIN, userInfo)
    }
  },

  // 获取用户信息
  getUserInfo() {
    return new Promise((resolve, reject) => {
      if (this.globalData.userInfo) {
        resolve(this.globalData.userInfo)
        return
      }

      const storedUserInfo = StorageService.getUserInfo()
      if (storedUserInfo) {
        this.globalData.userInfo = storedUserInfo
        resolve(storedUserInfo)
        return
      }

      // 尝试获取微信用户信息
      wx.getUserInfo({
        success: (res) => {
          this.globalData.userInfo = res.userInfo
          resolve(res.userInfo)
        },
        fail: (err) => {
          reject(err)
        }
      })
    })
  },

  // 更新用户信息
  updateUserInfo(userInfo) {
    this.globalData.userInfo = { ...this.globalData.userInfo, ...userInfo }
    StorageService.setUserInfo(this.globalData.userInfo)
    eventBus.emit(Events.USER_UPDATE, this.globalData.userInfo)
  },

  // 用户登录
  userLogin(userInfo, token) {
    this.globalData.userInfo = userInfo
    StorageService.setUserInfo(userInfo)
    StorageService.setToken(token)
    eventBus.emit(Events.USER_LOGIN, userInfo)
  },

  // 用户登出
  userLogout() {
    this.globalData.userInfo = null
    StorageService.removeUserInfo()
    StorageService.removeToken()
    eventBus.emit(Events.USER_LOGOUT)
  },

  // 显示提示消息
  showToast(message, type = 'info', duration = 2000) {
    const config = {
      title: message,
      duration: duration,
      icon: type === 'success' ? 'success' : 'none'
    }

    if (type === 'loading') {
      config.icon = 'loading'
    }

    wx.showToast(config)
    eventBus.emit(Events.TOAST_SHOW, { message, type, duration })
  },

  // 显示错误提示
  showErrorToast(msg, duration = 2000) {
    this.showToast(msg, 'error', duration)
  },

  // 显示成功提示
  showSuccessToast(msg, duration = 2000) {
    this.showToast(msg, 'success', duration)
  },

  // 显示加载提示
  showLoadingToast(msg = '加载中...', duration = 0) {
    this.showToast(msg, 'loading', duration)
  },

  // 网络请求封装（带性能监控，支持多种部署模式）
  request(url, data = {}, method = 'GET') {
    const complete = performanceMonitor.monitorApiRequest(url, method)
    
    // 检查部署模式并选择正确的请求方式
    const deploymentMode = this.globalData.deploymentMode || 'local-dev'
    
    if (deploymentMode === 'cloudbase' && this.globalData.useCloudBase && url.startsWith('/api/')) {
      // CloudBase环境：使用云函数调用
      const action = url.replace('/api/', '')
      return this.callCloudFunction(action, data, complete)
    } else if (deploymentMode.startsWith('local')) {
      // 本地部署环境：使用HTTP请求
      return this.callLocalApi(url, data, method, complete)
    } else {
      // 默认使用本地API
      return this.callLocalApi(url, data, method, complete)
    }
  },

  // 调用本地API
  callLocalApi(url, data = {}, method = 'GET', complete) {
    return new Promise((resolve, reject) => {
      const token = wx.getStorageSync('token')
      const headers = {
        'Content-Type': 'application/json'
      }
      // 只在token有效时才添加Authorization头，避免发送 "Bearer null"
      if (token && token !== 'null' && token !== 'undefined') {
        headers['Authorization'] = 'Bearer ' + token
      }

      wx.request({
        url: this.globalData.baseUrl + url,
        data: data,
        method: method,
        header: headers,
        success: (res) => {
          complete(true, res.statusCode, res.data)
          
          if (res.statusCode === 200) {
            resolve(res.data)
          } else if (res.statusCode === 401) {
            // Token过期，触发登出
            this.userLogout()
            reject(new Error('AUTH_REQUIRED'))
          } else {
            reject(res)
          }
        },
        fail: (err) => {
          complete(false, 0, null)
          reject(err)
        }
      })
    })
  },

  // 调用CloudBase云函数
  callCloudFunction(action, data = {}, complete) {
    return new Promise((resolve, reject) => {
      wx.cloud.callFunction({
        name: 'memoryday-api',
        data: {
          action: action,
          data: data
        },
        success: (res) => {
          complete(true, 200, res.result)
          if (res.result && res.result.error) {
            reject(new Error(res.result.error))
          } else {
            resolve(res.result)
          }
        },
        fail: (err) => {
          complete(false, 0, null)
          reject(err)
        }
      })
    })
  },

  // 监控网络状态
  monitorNetwork() {
    // 获取当前网络状态
    wx.getNetworkType({
      success: (res) => {
        this.globalData.network = {
          isConnected: true,
          type: res.networkType
        }
        eventBus.emit(Events.NETWORK_CONNECTED, res.networkType)
      }
    })

    // 监听网络状态变化
    wx.onNetworkStatusChange((res) => {
      this.globalData.network = {
        isConnected: res.isConnected,
        type: res.networkType
      }

      if (res.isConnected) {
        eventBus.emit(Events.NETWORK_CONNECTED, res.networkType)
      } else {
        eventBus.emit(Events.NETWORK_DISCONNECTED)
      }
    })
  },

  // 设置应用生命周期监听
  setupAppLifecycle() {
    wx.onAppShow((res) => {
      eventBus.emit(Events.APP_SHOW, res)
    })

    wx.onAppHide((res) => {
      eventBus.emit(Events.APP_HIDE, res)
    })
  },

  // 检查网络连接
  checkNetwork() {
    return new Promise((resolve, reject) => {
      wx.getNetworkType({
        success: (res) => {
          const isConnected = res.networkType !== 'none'
          resolve(isConnected)
        },
        fail: reject
      })
    })
  },

  // 显示模态对话框
  showModal(options) {
    return new Promise((resolve) => {
      wx.showModal({
        ...options,
        success: (res) => {
          eventBus.emit(Events.MODAL_SHOW, options)
          resolve(res)
        }
      })
    })
  },

  // 显示确认对话框
  confirm(message, title = '提示') {
    return this.showModal({
      title,
      content: message,
      showCancel: true
    })
  },

  // 显示警告对话框
  alert(message, title = '提示') {
    return this.showModal({
      title,
      content: message,
      showCancel: false
    })
  },

  // 获取设备信息
  getDeviceInfo() {
    try {
      return wx.getSystemInfoSync()
    } catch (error) {
      console.error('获取设备信息失败:', error)
      return null
    }
  },

  // 获取性能报告
  getPerformanceReport() {
    return performanceMonitor.getReports()
  },

  // 清理性能数据
  clearPerformanceData() {
    performanceMonitor.clear()
  },

  // 初始化部署配置
  initDeploymentConfig() {
    try {
      // 初始化部署配置
      const deploymentStatus = deploymentUtil.initDeployment(this)
      
      // 开发环境日志
      if (isDevelopment()) {
        console.log('部署配置初始化完成:', deploymentStatus)
        console.log('当前部署模式:', deploymentStatus.mode)
        console.log('API地址:', deploymentStatus.baseUrl)
      }
      
      // 监听网络状态变化，自动切换部署模式
      this.setupDeploymentAutoSwitch()
      
    } catch (error) {
      console.error('部署配置初始化失败:', error)
      // 使用默认配置
      this.globalData.deploymentMode = 'local-dev'
      this.globalData.baseUrl = 'http://localhost:8000/api'
      this.globalData.useCloudBase = false
    }
  },

  // 设置部署自动切换
  setupDeploymentAutoSwitch() {
    // 监听网络状态变化
    wx.onNetworkStatusChange((res) => {
      if (res.isConnected) {
        // 网络恢复时，尝试自动检测最佳部署模式
        this.autoDetectDeployment()
      }
    })
  },

  // 自动检测部署模式
  async autoDetectDeployment() {
    try {
      const result = await deploymentUtil.autoDetectBestDeployment(this)
      
      if (isDevelopment()) {
        console.log('自动检测部署模式结果:', result)
      }
      
      if (!result.success) {
        // 所有模式都失败，显示提示
        this.showModal({
          title: '网络连接提示',
          content: '所有部署模式连接失败，已切换到本地开发模式。请检查网络连接或本地服务是否启动。',
          showCancel: false
        })
      }
      
    } catch (error) {
      console.error('自动检测部署模式失败:', error)
    }
  },

  // 切换部署模式
  switchDeploymentMode(mode) {
    try {
      const config = deploymentUtil.switchDeploymentMode(mode, this)
      
      // 显示切换成功提示
      wx.showToast({
        title: `已切换到${config.title}`,
        icon: 'success',
        duration: 2000
      })
      
      // 触发部署模式切换事件
      eventBus.emit('DEPLOYMENT_MODE_CHANGED', {
        mode: mode,
        config: config
      })
      
      return config
      
    } catch (error) {
      console.error('切换部署模式失败:', error)
      wx.showToast({
        title: '切换失败: ' + error.message,
        icon: 'none',
        duration: 3000
      })
      throw error
    }
  },

  // 获取当前部署状态
  getDeploymentStatus() {
    return deploymentUtil.getCurrentDeploymentStatus(this)
  },

  // 测试部署连接
  testDeploymentConnection(mode) {
    return deploymentUtil.testDeploymentConnection(mode)
  },

  // 获取可用的部署模式
  getAvailableDeployments() {
    return deploymentUtil.getAvailableDeployments()
  }
})