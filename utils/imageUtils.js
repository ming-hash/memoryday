/**
 * 图片处理工具类 - 支持腾讯云COS图片优化
 */

/**
 * 获取优化后的图片URL
 * @param {string} imageUrl 原始图片URL
 * @param {Object} options 优化选项
 * @returns {string} 优化后的图片URL
 */
function getOptimizedImageUrl(imageUrl, options = {}) {
  if (!imageUrl) {
    return ''
  }

  // 默认优化选项
  const defaultOptions = {
    width: 300,
    height: 200,
    quality: 80,
    format: 'webp',
    mode: 'crop' // 裁剪模式
  }

  const config = { ...defaultOptions, ...options }

  // 检查是否是COS图片
  if (imageUrl.includes('cos.myqcloud.com')) {
    // COS图片URL处理
    return optimizeCosImageUrl(imageUrl, config)
  } else if (imageUrl.startsWith('http')) {
    // 其他网络图片
    return imageUrl
  } else {
    // 本地图片
    return imageUrl
  }
}

/**
 * 优化COS图片URL（支持图片处理功能）
 * @param {string} cosUrl COS图片URL
 * @param {Object} options 优化选项
 * @returns {string} 优化后的COS图片URL
 */
function optimizeCosImageUrl(cosUrl, options) {
  try {
    // 解析原始COS URL
    const url = new URL(cosUrl)
    
    // 提取文件路径和参数
    const pathname = url.pathname
    const searchParams = new URLSearchParams(url.search)
    
    // 构建图片处理参数
    const imageProcessParams = []
    
    // 添加裁剪参数
    if (options.mode === 'crop' && options.width && options.height) {
      imageProcessParams.push(`imageMogr2/crop/${options.width}x${options.height}`)
    } else if (options.width && options.height) {
      imageProcessParams.push(`imageMogr2/thumbnail/${options.width}x${options.height}`)
    }
    
    // 添加质量参数
    if (options.quality) {
      imageProcessParams.push(`imageMogr2/quality/${options.quality}`)
    }
    
    // 添加格式转换
    if (options.format && options.format !== 'jpg') {
      imageProcessParams.push(`imageMogr2/format/${options.format}`)
    }
    
    // 如果有图片处理参数，添加到URL
    if (imageProcessParams.length > 0) {
      const imageProcessQuery = `?${imageProcessParams.join('|')}`
      return `${url.origin}${pathname}${imageProcessQuery}`
    }
    
    // 如果没有处理参数，返回原始URL
    return cosUrl
  } catch (error) {
    console.error('优化COS图片URL失败:', error)
    return cosUrl
  }
}

/**
 * 获取缩略图URL
 * @param {string} imageUrl 原始图片URL
 * @param {number} width 宽度
 * @param {number} height 高度
 * @returns {string} 缩略图URL
 */
function getThumbnailUrl(imageUrl, width = 150, height = 100) {
  return getOptimizedImageUrl(imageUrl, {
    width,
    height,
    quality: 70,
    mode: 'crop'
  })
}

/**
 * 获取预览图URL
 * @param {string} imageUrl 原始图片URL
 * @param {number} width 宽度
 * @param {number} height 高度
 * @returns {string} 预览图URL
 */
function getPreviewUrl(imageUrl, width = 600, height = 400) {
  return getOptimizedImageUrl(imageUrl, {
    width,
    height,
    quality: 85,
    mode: 'crop'
  })
}

/**
 * 获取原始图URL（不进行优化）
 * @param {string} imageUrl 原始图片URL
 * @returns {string} 原始图URL
 */
function getOriginalUrl(imageUrl) {
  return imageUrl
}

/**
 * 检查图片是否支持优化
 * @param {string} imageUrl 图片URL
 * @returns {boolean} 是否支持优化
 */
function canOptimizeImage(imageUrl) {
  return imageUrl && imageUrl.includes('cos.myqcloud.com')
}

/**
 * 预加载图片
 * @param {string} imageUrl 图片URL
 * @returns {Promise} 预加载Promise
 */
function preloadImage(imageUrl) {
  return new Promise((resolve, reject) => {
    if (!imageUrl) {
      reject(new Error('图片URL为空'))
      return
    }
    
    wx.getImageInfo({
      src: imageUrl,
      success: (res) => {
        resolve(res)
      },
      fail: (error) => {
        reject(error)
      }
    })
  })
}

/**
 * 批量预加载图片
 * @param {Array} imageUrls 图片URL数组
 * @returns {Promise} 预加载Promise
 */
function preloadImages(imageUrls) {
  if (!Array.isArray(imageUrls) || imageUrls.length === 0) {
    return Promise.resolve([])
  }
  
  const promises = imageUrls.map(url => preloadImage(url).catch(error => {
    console.warn('预加载图片失败:', url, error)
    return null
  }))
  
  return Promise.all(promises)
}

/**
 * 获取图片文件大小（用于显示）
 * @param {number} size 文件大小（字节）
 * @returns {string} 格式化后的文件大小
 */
function formatFileSize(size) {
  if (!size || size === 0) {
    return '0 B'
  }
  
  const units = ['B', 'KB', 'MB', 'GB']
  const index = Math.floor(Math.log(size) / Math.log(1024))
  const formattedSize = (size / Math.pow(1024, index)).toFixed(2)
  
  return `${formattedSize} ${units[index]}`
}

/**
 * 验证图片URL是否有效
 * @param {string} imageUrl 图片URL
 * @returns {Promise<boolean>} 是否有效
 */
function validateImageUrl(imageUrl) {
  return new Promise((resolve) => {
    if (!imageUrl) {
      resolve(false)
      return
    }
    
    // 检查URL格式
    try {
      new URL(imageUrl)
    } catch (error) {
      resolve(false)
      return
    }
    
    // 尝试获取图片信息
    wx.getImageInfo({
      src: imageUrl,
      success: () => {
        resolve(true)
      },
      fail: () => {
        resolve(false)
      }
    })
  })
}

module.exports = {
  getOptimizedImageUrl,
  getThumbnailUrl,
  getPreviewUrl,
  getOriginalUrl,
  canOptimizeImage,
  preloadImage,
  preloadImages,
  formatFileSize,
  validateImageUrl
}