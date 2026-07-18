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

      // ============================================
      // 访问模式配置 (通过配置文件开关切换)
      // ============================================
      // 可选值:
      //   'local'   - 使用本地开发服务器 (http://127.0.0.1:8000)
      //   'ip'      - 使用自建服务器 IP+端口 访问
      //   'domain'  - 使用自建服务器域名访问
      //   'cloudbase' - 使用 CloudBase 云端服务
      accessMode: 'ip',

      // 自建服务器配置
      selfServer: {
        // IP+端口模式
        ip: {
          baseUrl: 'http://1.14.61.155/api',
        },
        // 域名模式
        domain: {
          baseUrl: 'https://你的域名.com/api',
        }
      },

      // CloudBase 云端配置
      cloudBase: {
        env: 'whateatday-0gor3cwl4f527bba',
        baseUrl: 'https://whateatday-0gor3cwl4f527bba.tcloudbaseapp.com/api',
        apiName: 'memoryday-api'
      },

      // 本地开发配置
      localDev: {
        baseUrl: 'http://127.0.0.1:8000/api'
      },

      // CloudBase 环境信息
      env: 'whateatday-0gor3cwl4f527bba',
      useCloudBase: true,
      cloudBaseEnv: 'whateatday-0gor3cwl4f527bba'
    }
  },

  // 获取当前 API 地址
  getApiBaseUrl() {
    const mode = this.globalData.accessMode
    const selfServer = this.globalData.selfServer

    switch (mode) {
      case 'local':
        return this.globalData.localDev.baseUrl
      case 'ip':
        return selfServer.ip.baseUrl
      case 'domain':
        return selfServer.domain.baseUrl
      case 'cloudbase':
        return this.globalData.cloudBase.baseUrl
      default:
        console.warn('未知的 accessMode:', mode, '默认使用 IP 模式')
        return selfServer.ip.baseUrl
    }
  },
  
  // 全局错误处理
  onError(msg) {
    console.error('小程序错误:', msg)
  },

  // 调用CloudBase云函数
  callCloudFunction(action, data = {}) {
    const apiName = this.globalData.cloudBase.apiName
    return new Promise((resolve, reject) => {
      wx.cloud.callFunction({
        name: apiName,
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

  // API请求方法（支持多种访问模式）
  async request(options) {
    const { url, method = 'GET', data = {} } = options
    const token = wx.getStorageSync('token')

    // 根据 accessMode 选择 API 地址
    const baseUrl = this.getApiBaseUrl()
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
            wx.removeStorageSync('token')
            this.globalData.userInfo = null
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