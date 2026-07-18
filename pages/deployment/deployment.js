// pages/deployment/deployment.js
Page({
  data: {
    deploymentMode: 'local-dev', // 当前部署模式
    deploymentOptions: [
      {
        name: 'local-dev',
        title: '本地开发环境',
        description: '使用本地Docker容器运行后端服务',
        apiUrl: 'http://localhost:8000/api',
        enabled: true
      },
      {
        name: 'local',
        title: '本地生产环境',
        description: '本地完整生产环境部署',
        apiUrl: 'http://localhost:8000/api',
        enabled: true
      },
      {
        name: 'server',
        title: '远程服务器',
        description: '连接自建服务器（1.14.61.155）',
        apiUrl: 'http://1.14.61.155/api',
        enabled: true
      },
      {
        name: 'cloudbase',
        title: '腾讯云CloudBase',
        description: '云端部署，无需管理服务器',
        apiUrl: 'https://whateatday-0gor3cwl4f527bba.tcloudbaseapp.com/api',
        enabled: true
      }
    ],
    currentConfig: {}
  },

  onLoad() {
    // 获取当前部署配置
    const app = getApp()
    this.setData({
      deploymentMode: app.globalData.deploymentMode || 'local-dev',
      currentConfig: {
        baseUrl: app.globalData.baseUrl,
        useCloudBase: app.globalData.useCloudBase,
        deploymentMode: app.globalData.deploymentMode
      }
    })
  },

  // 选择部署模式
  selectDeployment(e) {
    const mode = e.currentTarget.dataset.mode
    const option = this.data.deploymentOptions.find(opt => opt.name === mode)
    
    if (!option || !option.enabled) {
      wx.showToast({
        title: '该部署模式不可用',
        icon: 'none'
      })
      return
    }

    // 更新全局配置
    const app = getApp()
    app.globalData.deploymentMode = mode
    app.globalData.baseUrl = option.apiUrl
    app.globalData.useCloudBase = mode === 'cloudbase'
    
    if (mode === 'cloudbase') {
      app.globalData.cloudBaseEnv = 'whateatday-0gor3cwl4f527bba'
    }

    // 保存到本地存储
    wx.setStorageSync('deploymentConfig', {
      mode: mode,
      baseUrl: option.apiUrl,
      useCloudBase: mode === 'cloudbase',
      switchTime: Date.now()
    })

    this.setData({
      deploymentMode: mode,
      currentConfig: {
        baseUrl: option.apiUrl,
        useCloudBase: mode === 'cloudbase',
        deploymentMode: mode
      }
    })

    wx.showToast({
      title: `已切换到${option.title}`,
      icon: 'success'
    })

    // 返回上一页
    setTimeout(() => {
      wx.navigateBack()
    }, 1000)
  },

  // 测试连接
  testConnection() {
    const app = getApp()
    const currentMode = this.data.deploymentMode
    
    wx.showLoading({
      title: '测试连接中...',
    })

    app.request('/health/', {}, 'GET')
      .then((res) => {
        wx.hideLoading()
        wx.showToast({
          title: `${this.getModeTitle(currentMode)}连接正常`,
          icon: 'success'
        })
      })
      .catch((err) => {
        wx.hideLoading()
        wx.showToast({
          title: `${this.getModeTitle(currentMode)}连接失败`,
          icon: 'none'
        })
        console.error('连接测试失败:', err)
      })
  },

  // 获取模式标题
  getModeTitle(mode) {
    const option = this.data.deploymentOptions.find(opt => opt.name === mode)
    return option ? option.title : '未知模式'
  },

  // 查看部署指南
  viewDeploymentGuide() {
    wx.navigateTo({
      url: '/pages/webview/webview?url=' + encodeURIComponent('https://github.com/your-repo/memoryday/blob/main/DEPLOYMENT_GUIDE.md')
    })
  },

  // 复制配置信息
  copyConfig() {
    const config = JSON.stringify(this.data.currentConfig, null, 2)
    wx.setClipboardData({
      data: config,
      success: () => {
        wx.showToast({
          title: '配置已复制',
          icon: 'success'
        })
      }
    })
  }
})