// services/cosService.js - 腾讯云COS存储服务

const { getCosConfig } = require('../config/cos')
const app = getApp()

/**
 * 腾讯云COS存储服务
 * 提供图片上传、下载、删除等功能
 */
class CosService {
  constructor() {
    this.cos = null
    this.stsToken = null
    this.tokenExpireTime = 0
    this.appId = null
    this.config = null
    
    this.init()
  }

  /**
   * 初始化COS服务
   */
  init() {
    // 加载配置（现在不需要appId参数）
    this.config = getCosConfig()
    console.log('COS服务初始化完成，存储桶:', this.config.cos.bucket)
  }

  /**
   * 获取STS临时凭证
   */
  async getStsToken() {
    // 检查token是否有效（提前5分钟刷新）
    const now = Date.now()
    if (this.stsToken && now < this.tokenExpireTime - 5 * 60 * 1000) {
      return this.stsToken
    }

    try {
      // 调用后端API获取STS token（注意：URL末尾要有斜杠）
      const response = await app.request('/cos/sts-token/', {}, 'POST')
      
      if (response && response.data) {
        this.stsToken = response.data
        this.tokenExpireTime = now + response.data.expiredTime * 1000
        
        console.log('STS token获取成功，有效期至:', new Date(this.tokenExpireTime).toLocaleString())
        return this.stsToken
      } else {
        throw new Error('获取STS token失败')
      }
    } catch (error) {
      console.error('获取STS token失败:', error)
      
      // 开发环境降级方案不可用：小程序无法使用process.env
      // 如果STS获取失败，直接抛出错误，需要确保后端STS端点可用
      console.error('获取STS token失败，请确保后端/cos/sts-token/端点正常运行')
      throw error
    }
  }

  /**
   * 初始化COS SDK
   */
  async initCosSDK() {
    if (this.cos) {
      return this.cos
    }

    const stsToken = await this.getStsToken()
    
    // 动态导入COS SDK
    const COS = require('cos-wx-sdk-v5')
    
    this.cos = new COS({
      getAuthorization: (options, callback) => {
        callback({
          TmpSecretId: stsToken.tmpSecretId,
          TmpSecretKey: stsToken.tmpSecretKey,
          SecurityToken: stsToken.sessionToken,
          StartTime: Math.floor(Date.now() / 1000),
          ExpiredTime: stsToken.expiredTime,
          ScopeLimit: true
        })
      }
    })

    return this.cos
  }

  /**
   * 上传图片到COS
   * @param {string} filePath 本地文件路径
   * @param {string} fileName 文件名（可选，不传则自动生成）
   * @param {string} folder 文件夹路径（可选）
   * @returns {Promise} 上传结果
   */
  async uploadImage(filePath, fileName = null, folder = 'images') {
    try {
      await this.initCosSDK()
      
      // 生成文件名
      const timestamp = Date.now()
      const randomStr = Math.random().toString(36).substring(2, 8)
      const fileExt = this.getFileExtension(filePath)
      const finalFileName = fileName || `${timestamp}_${randomStr}${fileExt}`
      
      // 构建COS路径
      const cosKey = `${folder}/${finalFileName}`
      
      return new Promise((resolve, reject) => {
        this.cos.postObject({
          Bucket: this.config.cos.bucket,
          Region: this.config.cos.region,
          Key: cosKey,
          FilePath: filePath,
          onProgress: (progressData) => {
            console.log('上传进度:', progressData)
          }
        }, async (err, data) => {
          if (err) {
            console.error('COS上传失败:', err)
            reject(err)
          } else {
            console.log('COS上传成功:', data)
            
            // 构建访问URL（异步获取签名URL）
            const imageUrl = await this.getImageUrl(cosKey)
            
            resolve({
              success: true,
              url: imageUrl,
              key: cosKey,
              fileName: finalFileName,
              size: data.size,
              etag: data.ETag
            })
          }
        })
      })
      
    } catch (error) {
      console.error('上传图片失败:', error)
      throw error
    }
  }

  /**
   * 批量上传图片
   * @param {Array} filePaths 文件路径数组
   * @param {string} folder 文件夹路径
   * @returns {Promise} 上传结果数组
   */
  async uploadImages(filePaths, folder = 'images') {
    const uploadPromises = filePaths.map((filePath, index) => 
      this.uploadImage(filePath, null, folder)
    )
    
    return Promise.all(uploadPromises)
  }

  /**
   * 删除COS中的文件
   * @param {string} fileKey 文件在COS中的key
   * @returns {Promise} 删除结果
   */
  async deleteFile(fileKey) {
    try {
      await this.initCosSDK()
      
      return new Promise((resolve, reject) => {
        this.cos.deleteObject({
          Bucket: this.config.cos.bucket,
          Region: this.config.cos.region,
          Key: fileKey
        }, (err, data) => {
          if (err) {
            console.error('删除文件失败:', err)
            reject(err)
          } else {
            console.log('删除文件成功:', data)
            resolve({
              success: true,
              key: fileKey
            })
          }
        })
      })
      
    } catch (error) {
      console.error('删除文件失败:', error)
      throw error
    }
  }

  /**
   * 获取图片URL（支持图片处理）
   * 私有读写存储桶需要使用签名URL
   * @param {string} fileKey 文件key
   * @param {Object} options 处理选项
   * @returns {string} 图片URL
   */
  async getImageUrl(fileKey, options = {}) {
    try {
      // 私有读写存储桶需要获取签名URL
      const response = await app.request('/cos/signed-url/', {
        file_key: fileKey,
        expires: this.config.cos.url?.defaultExpires || 3600,
        style: options.thumbnail ? 'thumbnail' : options.preview ? 'preview' : 'original'
      }, 'POST')
      
      if (response && response.data && response.data.url) {
        return response.data.url
      }
      
      // 如果后端签名失败，返回无签名URL（会显示403错误）
      console.warn('获取签名URL失败，返回无签名URL')
      return this.getUnsignedUrl(fileKey, options)
      
    } catch (error) {
      console.error('获取签名URL失败:', error)
      // 降级方案：返回无签名URL
      return this.getUnsignedUrl(fileKey, options)
    }
  }
  
  /**
   * 获取无签名URL（仅供降级使用）
   * @param {string} fileKey 文件key
   * @param {Object} options 处理选项
   * @returns {string} 无签名URL
   */
  getUnsignedUrl(fileKey, options = {}) {
    const baseUrl = `https://${this.config.cos.url?.bucketDomain || 
      `${this.config.cos.bucket}.cos.${this.config.cos.region}.myqcloud.com`}/${fileKey}`
    
    if (options.thumbnail) {
      return baseUrl + this.config.cos.upload.imageProcess.thumbnail
    }
    
    if (options.preview) {
      return baseUrl + this.config.cos.upload.imageProcess.preview
    }
    
    return baseUrl
  }
  
  /**
   * 批量获取签名URL
   * @param {Array} fileKeys 文件key数组
   * @param {Object} options 选项
   * @returns {Promise} 签名URL数组
   */
  async getSignedUrls(fileKeys, options = {}) {
    try {
      const response = await app.request('/cos/batch-signed-urls/', {
        file_keys: fileKeys,
        expires: options.expires || this.config.cos.url?.defaultExpires || 3600,
        style: options.style || 'original'
      }, 'POST')
      
      if (response && response.data && response.data.urls) {
        return response.data.urls
      }
      
      console.warn('批量获取签名URL失败，返回无签名URL')
      return fileKeys.map(key => this.getUnsignedUrl(key, options))
      
    } catch (error) {
      console.error('批量获取签名URL失败:', error)
      return fileKeys.map(key => this.getUnsignedUrl(key, options))
    }
  }

  /**
   * 获取文件扩展名
   * @param {string} filePath 文件路径
   * @returns {string} 文件扩展名
   */
  getFileExtension(filePath) {
    const lastDotIndex = filePath.lastIndexOf('.')
    if (lastDotIndex === -1) {
      return '.jpg' // 默认扩展名
    }
    return filePath.substring(lastDotIndex)
  }

  /**
   * 验证文件类型
   * @param {string} filePath 文件路径
   * @returns {boolean} 是否支持的文件类型
   */
  validateFileType(filePath) {
    const ext = this.getFileExtension(filePath).toLowerCase()
    const allowedExts = ['.jpg', '.jpeg', '.png', '.gif', '.webp']
    return allowedExts.includes(ext)
  }

  /**
   * 获取文件信息
   * @param {string} filePath 文件路径
   * @returns {Promise} 文件信息
   */
  getFileInfo(filePath) {
    return new Promise((resolve, reject) => {
      wx.getFileInfo({
        filePath: filePath,
        success: (res) => {
          resolve(res)
        },
        fail: (err) => {
          reject(err)
        }
      })
    })
  }

  /**
   * 验证文件大小
   * @param {string} filePath 文件路径
   * @returns {Promise} 验证结果
   */
  async validateFileSize(filePath) {
    try {
      const fileInfo = await this.getFileInfo(filePath)
      const maxSize = this.config.cos.upload.maxSize
      
      if (fileInfo.size > maxSize) {
        throw new Error(`文件大小不能超过 ${maxSize / 1024 / 1024}MB`)
      }
      
      return {
        valid: true,
        size: fileInfo.size
      }
    } catch (error) {
      return {
        valid: false,
        error: error.message
      }
    }
  }
}

// 创建单例实例
let cosServiceInstance = null

const getCosService = () => {
  if (!cosServiceInstance) {
    cosServiceInstance = new CosService()
  }
  return cosServiceInstance
}

module.exports = getCosService