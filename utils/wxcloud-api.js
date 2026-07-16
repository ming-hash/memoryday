// utils/wxcloud-api.js
// 微信云托管专用API封装

function getAppInstance() {
  return getApp()
}

/**
 * 微信云托管API客户端
 * 使用 wx.cloud.callContainer 调用云托管服务
 */
class WxCloudApiClient {
  constructor(envId = '') {
    this.envId = envId
    this.service = 'memoryday-backend'
  }

  /**
   * 发起云托管请求
   * @param {string} path 请求路径
   * @param {Object} options 请求选项
   * @returns {Promise} 请求结果
   */
  async request(path, options = {}) {
    const {
      method = 'GET',
      data = {},
      headers = {},
      timeout = 10000
    } = options

    // 构建完整的请求配置
    const requestConfig = {
      config: {
        env: this.envId,
        service: this.service
      },
      path: path,
      method: method,
      header: {
        'Content-Type': 'application/json',
        'Authorization': wx.getStorageSync('token') ? `Bearer ${wx.getStorageSync('token')}` : '',
        ...headers
      },
      data: data,
      timeout: timeout
    }

    return new Promise((resolve, reject) => {
      wx.cloud.callContainer({
        ...requestConfig,
        success: (res) => {
          if (res.statusCode >= 200 && res.statusCode < 300) {
            resolve(res.data)
          } else {
            reject(this.handleError(res))
          }
        },
        fail: (error) => {
          reject(this.handleError(error))
        }
      })
    })
  }

  /**
   * 处理错误
   * @param {Object} error 错误对象
   * @returns {Object} 格式化后的错误
   */
  handleError(error) {
    console.error('云托管API请求错误:', error)
    
    if (error.statusCode === 401) {
      // token过期，跳转到登录页
      wx.removeStorageSync('token')
      wx.reLaunch({
        url: '/pages/login/login'
      })
    }
    
    return {
      code: error.statusCode || -1,
      message: error.errMsg || '云托管服务请求失败',
      data: error.data
    }
  }

  /**
   * GET请求
   * @param {string} path 请求路径
   * @param {Object} params 查询参数
   * @returns {Promise} 请求结果
   */
  get(path, params = {}) {
    return this.request(path, {
      method: 'GET',
      data: params
    })
  }

  /**
   * POST请求
   * @param {string} path 请求路径
   * @param {Object} data 请求数据
   * @returns {Promise} 请求结果
   */
  post(path, data = {}) {
    return this.request(path, {
      method: 'POST',
      data: data
    })
  }

  /**
   * PUT请求
   * @param {string} path 请求路径
   * @param {Object} data 请求数据
   * @returns {Promise} 请求结果
   */
  put(path, data = {}) {
    return this.request(path, {
      method: 'PUT',
      data: data
    })
  }

  /**
   * DELETE请求
   * @param {string} path 请求路径
   * @param {Object} data 请求数据
   * @returns {Promise} 请求结果
   */
  delete(path, data = {}) {
    return this.request(path, {
      method: 'DELETE',
      data: data
    })
  }

  /**
   * 文件上传（使用云托管服务）
   * @param {string} path 上传路径
   * @param {string} filePath 文件路径
   * @param {Object} formData 表单数据
   * @returns {Promise} 上传结果
   */
  async upload(path, filePath, formData = {}) {
    return new Promise((resolve, reject) => {
      wx.cloud.uploadFile({
        cloudPath: `memoryday/${Date.now()}_${Math.random().toString(36).substr(2)}`,
        filePath: filePath,
        config: {
          env: this.envId
        },
        success: (res) => {
          // 上传成功后，调用后端API记录文件信息
          this.post(path, {
            fileId: res.fileID,
            cloudPath: res.cloudPath,
            ...formData
          }).then(resolve).catch(reject)
        },
        fail: (error) => {
          reject(this.handleError(error))
        }
      })
    })
  }
}

/**
 * 检测是否支持微信云托管
 * @returns {boolean} 是否支持
 */
function isWxCloudSupported() {
  const app = getAppInstance()
  return wx.cloud && wx.cloud.callContainer && app && app.globalData.env.WX_CLOUD === 'true'
}

/**
 * 创建适配器，根据环境自动选择API调用方式
 */
class ApiAdapter {
  constructor() {
    const app = getAppInstance()
    this.envId = (app && app.globalData.env.WX_CLOUD_ENV) || ''
    this.useWxCloud = isWxCloudSupported()
    
    if (this.useWxCloud) {
      this.client = new WxCloudApiClient(this.envId)
    } else {
      // 使用传统API客户端
      const { apiClient } = require('./api')
      this.client = apiClient
    }
  }

  // 代理所有方法到实际客户端
  request(path, options) {
    return this.client.request(path, options)
  }

  get(path, params) {
    return this.client.get(path, params)
  }

  post(path, data) {
    return this.client.post(path, data)
  }

  put(path, data) {
    return this.client.put(path, data)
  }

  delete(path, data) {
    return this.client.delete(path, data)
  }

  upload(path, filePath, formData) {
    return this.client.upload(path, filePath, formData)
  }
}

// 创建全局API适配器实例
const apiAdapter = new ApiAdapter()

// 导出适配的API模块
module.exports = {
  WxCloudApiClient,
  ApiAdapter,
  apiAdapter,
  isWxCloudSupported
}