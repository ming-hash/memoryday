// utils/api.js
const getCosService = require('../services/cosService')

function getAppInstance() {
  return getApp()
}

/**
 * API请求封装
 */
class ApiClient {
  constructor(baseURL = '') {
    this.baseURL = baseURL
  }

  /**
   * 发起请求
   * @param {string} url 请求地址
   * @param {Object} options 请求选项
   * @returns {Promise} 请求结果
   */
  async request(url, options = {}) {
    const {
      method = 'GET',
      data = {},
      headers = {},
      timeout = 10000
    } = options

    const fullUrl = `${this.baseURL}${url}`
    const token = wx.getStorageSync('token')

    const requestOptions = {
      url: fullUrl,
      method: method,
      header: {
        'Content-Type': 'application/json',
        'Authorization': token ? `Bearer ${token}` : '',
        ...headers
      },
      data: method === 'GET' ? data : JSON.stringify(data),
      timeout: timeout
    }

    return new Promise((resolve, reject) => {
      wx.request({
        ...requestOptions,
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
    console.error('API请求错误:', error)
    
    if (error.statusCode === 401) {
      // token过期，跳转到登录页
      wx.removeStorageSync('token')
      wx.reLaunch({
        url: '/pages/login/login'
      })
    }
    
    return {
      code: error.statusCode || -1,
      message: error.errMsg || '网络请求失败',
      data: error.data
    }
  }

  /**
   * GET请求
   * @param {string} url 请求地址
   * @param {Object} params 查询参数
   * @returns {Promise} 请求结果
   */
  get(url, params = {}) {
    return this.request(url, {
      method: 'GET',
      data: params
    })
  }

  /**
   * POST请求
   * @param {string} url 请求地址
   * @param {Object} data 请求数据
   * @returns {Promise} 请求结果
   */
  post(url, data = {}) {
    return this.request(url, {
      method: 'POST',
      data: data
    })
  }

  /**
   * PUT请求
   * @param {string} url 请求地址
   * @param {Object} data 请求数据
   * @returns {Promise} 请求结果
   */
  put(url, data = {}) {
    return this.request(url, {
      method: 'PUT',
      data: data
    })
  }

  /**
   * DELETE请求
   * @param {string} url 请求地址
   * @param {Object} data 请求数据
   * @returns {Promise} 请求结果
   */
  delete(url, data = {}) {
    return this.request(url, {
      method: 'DELETE',
      data: data
    })
  }

  /**
   * 上传文件（支持腾讯云COS和传统服务器上传）
   * @param {string} url 上传地址
   * @param {string} filePath 文件路径
   * @param {Object} formData 表单数据
   * @param {string} folder 上传文件夹（COS专用）
   * @returns {Promise} 上传结果
   */
  async upload(url, filePath, formData = {}, folder = null) {
    try {
      // 检查是否使用COS上传
      const cosService = getCosService()
      
      if (cosService && cosService.config && cosService.config.useCos) {
        // 使用COS上传
        console.log('使用腾讯云COS上传文件')
        
        // 验证文件大小
        const sizeValidation = await cosService.validateFileSize(filePath)
        if (!sizeValidation.valid) {
          throw new Error(sizeValidation.error)
        }
        
        // 验证文件类型
        if (!cosService.validateFileType(filePath)) {
          throw new Error('不支持的文件格式')
        }
        
        // 上传到COS
        const result = await cosService.uploadImage(filePath, null, folder)
        
        // 如果需要记录到后端，调用后端API
        if (url) {
          try {
            await this.request(url, {
              method: 'POST',
              data: {
                fileKey: result.key,
                fileUrl: result.url,
                fileName: result.fileName,
                fileSize: result.size,
                folder: folder
              }
            })
          } catch (error) {
            console.warn('文件记录到后端失败，不影响上传:', error)
          }
        }
        
        return result
      } else {
        // 使用传统服务器上传
        return new Promise((resolve, reject) => {
          wx.uploadFile({
            url: `${this.baseURL}${url}`,
            filePath: filePath,
            name: 'file',
            formData: formData,
            header: {
              'Authorization': `Bearer ${wx.getStorageSync('token')}`
            },
            success: (res) => {
              try {
                const data = JSON.parse(res.data)
                resolve(data)
              } catch (error) {
                reject(this.handleError(error))
              }
            },
            fail: (error) => {
              reject(this.handleError(error))
            }
          })
        })
      }
    } catch (error) {
      throw this.handleError(error)
    }
  }
}

// 创建API客户端实例（延迟初始化）
let _apiClient = null
function getApiClient() {
  if (!_apiClient) {
    const app = getAppInstance()
    _apiClient = new ApiClient((app && app.globalData && app.globalData.baseUrl) || 'http://localhost:8000/api')
  }
  return _apiClient
}

// 向后兼容的代理
const apiClient = new Proxy({}, {
  get(_, prop) { return getApiClient()[prop] }
})

// 菜品相关API
const dishApi = {
  // 获取菜品列表
  getDishes: (params = {}) => apiClient.get('/dishes', params),
  
  // 获取菜品详情
  getDish: (id) => apiClient.get(`/dishes/${id}`),
  
  // 创建菜品
  createDish: (data) => apiClient.post('/dishes', data),
  
  // 更新菜品
  updateDish: (id, data) => apiClient.put(`/dishes/${id}`, data),
  
  // 删除菜品
  deleteDish: (id) => apiClient.delete(`/dishes/${id}`),
  
  // 批量操作
  batchOperation: (data) => apiClient.post('/dishes/batch', data),
  
  // 上传菜品图片
  uploadImage: (filePath) => apiClient.upload('/dishes/upload', filePath),
  
  // 随机选择菜品
  randomDish: (filters = {}) => apiClient.post('/dishes/random', filters)
}

// 用户相关API
const userApi = {
  // 微信登录
  wechatLogin: (code) => apiClient.post('/auth/wechat', { code }),
  
  // 获取用户信息
  getUserInfo: () => apiClient.get('/user/info'),
  
  // 更新用户信息
  updateUserInfo: (data) => apiClient.put('/user/info', data)
}

// 统计相关API
const statsApi = {
  // 获取周统计
  getWeeklyStats: () => apiClient.get('/stats/weekly'),
  
  // 获取月统计
  getMonthlyStats: () => apiClient.get('/stats/monthly'),
  
  // 获取分布统计
  getDistributionStats: () => apiClient.get('/stats/distribution'),
  
  // 获取用餐记录
  getMealRecords: (params = {}) => apiClient.get('/stats/records', params)
}

// 标签相关API
const tagApi = {
  // 获取所有标签
  getTags: () => apiClient.get('/tags'),
  
  // 创建标签
  createTag: (data) => apiClient.post('/tags', data),
  
  // 搜索标签
  searchTags: (keyword) => apiClient.get('/tags/search', { keyword })
}

module.exports = {
  apiClient,
  dishApi,
  userApi,
  statsApi,
  tagApi
}