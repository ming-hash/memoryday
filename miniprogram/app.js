// app.js
App({
  onLaunch() {
    console.log('MemoryDay小程序启动')
    
    // 初始化云开发
    wx.cloud.init({
      env: 'whateatday-0gor3cwl4f527bba',
      traceUser: true
    })
    
    // 设置全局数据
    this.globalData = {
      userInfo: null,
      // 本地开发环境 API 地址
      baseUrl: 'http://127.0.0.1:8000/api',
      // 生产环境 API 地址（云端）
      prodUrl: 'https://whateatday-0gor3cwl4f527bba.tcloudbaseapp.com/api',
      // 开发模式标志 - 设为 true 使用本地后端
      devMode: true,
      env: 'whateatday-0gor3cwl4f527bba',
      useCloudBase: true,
      cloudBaseEnv: 'whateatday-0gor3cwl4f527bba'
    }
  },
  
  // 全局错误处理
  onError(msg) {
    console.error('小程序错误:', msg)
  },

  // 调用CloudBase云函数
  callCloudFunction(action, data = {}) {
    return new Promise((resolve, reject) => {
      wx.cloud.callFunction({
        name: 'memoryday-api',
        data: {
          action: action,
          data: data
        },
        success: (res) => {
          if (res.result && res.result.error) {
            reject(new Error(res.result.error))
          } else {
            resolve(res.result)
          }
        },
        fail: (err) => {
          reject(err)
        }
      })
    })
  },

  // API请求方法（支持本地和云端）
  async request(options) {
    const { url, method = 'GET', data = {} } = options
    const token = wx.getStorageSync('token')
    
    // 根据devMode选择API地址
    const baseUrl = this.globalData.devMode 
      ? this.globalData.baseUrl 
      : this.globalData.prodUrl
    
    const fullUrl = url.startsWith('http') ? url : `${baseUrl}${url}`
    
    return new Promise((resolve, reject) => {
      wx.request({
        url: fullUrl,
        method: method,
        header: {
          'Content-Type': 'application/json',
          'Authorization': token ? `Bearer ${token}` : ''
        },
        data: method === 'GET' ? data : JSON.stringify(data),
        timeout: 15000,
        success: (res) => {
          if (res.statusCode >= 200 && res.statusCode < 300) {
            resolve(res.data)
          } else if (res.statusCode === 401) {
            // Token过期，清除本地token
            wx.removeStorageSync('token')
            this.globalData.userInfo = null
            // 不强制跳转，由调用方决定如何处理
            reject(new Error('AUTH_REQUIRED'))
          } else {
            reject(new Error(res.data?.error?.message || res.data?.detail || `请求失败(${res.statusCode})`))
          }
        },
        fail: (err) => {
          console.error('请求失败:', err)
          reject(new Error('网络请求失败'))
        }
      })
    })
  },

  // 简化请求方法
  get(url, data = {}) {
    return this.request({ url, method: 'GET', data })
  },
  
  post(url, data = {}) {
    return this.request({ url, method: 'POST', data })
  },
  
  put(url, data = {}) {
    return this.request({ url, method: 'PUT', data })
  },
  
  delete(url, data = {}) {
    return this.request({ url, method: 'DELETE', data })
  },

  // Toast提示方法
  showErrorToast(msg) {
    wx.showToast({
      title: msg || '操作失败',
      icon: 'none',
      duration: 2000
    })
  },

  showSuccessToast(msg) {
    wx.showToast({
      title: msg || '操作成功',
      icon: 'success',
      duration: 1500
    })
  }
})