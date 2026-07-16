// config/cos.js - 腾讯云COS配置

/**
 * 腾讯云COS配置
 * 根据环境变量自动选择开发/生产环境配置
 */

// 存储桶后缀配置 - 集中管理存储桶名称中的变量部分
const STORAGE_SUFFIX = '1259810697' // 存储桶后缀，统一配置
const BUCKET_NAME = `memoryday-${STORAGE_SUFFIX}` // 完整的存储桶名称

// 开发环境配置
const devConfig = {
  // COS配置
  cos: {
    region: 'ap-beijing', // 存储桶地域
    bucket: BUCKET_NAME, // 使用统一的存储桶名称
    storageSuffix: STORAGE_SUFFIX, // 存储桶后缀变量
    // 上传相关配置
    upload: {
      maxSize: 5 * 1024 * 1024, // 5MB
      allowedTypes: ['image/jpeg', 'image/png', 'image/gif', 'image/webp'],
      // 图片处理配置
      imageProcess: {
        thumbnail: '?imageView2/1/w/200/h/200', // 缩略图
        preview: '?imageView2/0/q/80' // 预览图质量压缩
      }
    },
    // URL生成配置
    url: {
      useSignedUrl: true, // 私有读写存储桶需要使用签名URL
      defaultExpires: 3600, // 默认签名有效期（秒）
      bucketDomain: `${BUCKET_NAME}.cos.ap-beijing.myqcloud.com` // 存储桶域名
    }
  },
  // STS临时密钥配置（开发环境使用固定密钥）
  sts: {
    durationSeconds: 1800, // 临时密钥有效期（秒）
    policy: {
      version: '2.0',
      statement: [
        {
          effect: 'allow',
          action: [
            'name/cos:PutObject',
            'name/cos:PostObject',
            'name/cos:GetObject',
            'name/cos:DeleteObject'
          ],
          resource: [
            `qcs::cos:ap-beijing:uid/${STORAGE_SUFFIX}:${BUCKET_NAME}/*`
          ]
        }
      ]
    }
  }
}

// 生产环境配置
const prodConfig = {
  cos: {
    region: 'ap-beijing',
    bucket: BUCKET_NAME,
    storageSuffix: STORAGE_SUFFIX,
    upload: {
      maxSize: 5 * 1024 * 1024,
      allowedTypes: ['image/jpeg', 'image/png', 'image/gif', 'image/webp'],
      imageProcess: {
        thumbnail: '?imageView2/1/w/200/h/200',
        preview: '?imageView2/0/q/80'
      }
    },
    url: {
      useSignedUrl: true,
      defaultExpires: 3600,
      bucketDomain: `${BUCKET_NAME}.cos.ap-beijing.myqcloud.com`
    }
  },
  sts: {
    durationSeconds: 1800,
    policy: {
      version: '2.0',
      statement: [
        {
          effect: 'allow',
          action: [
            'name/cos:PutObject',
            'name/cos:PostObject',
            'name/cos:GetObject',
            'name/cos:DeleteObject'
          ],
          resource: [
            `qcs::cos:ap-beijing:uid/${STORAGE_SUFFIX}:${BUCKET_NAME}/*`
          ]
        }
      ]
    }
  }
}

// 根据环境选择配置（现在开发和生产使用同一存储桶，配置相同）
const { isDevelopment } = require('./env')
const baseConfig = devConfig  // 统一使用开发环境配置，因为存储桶相同

// 获取完整的COS配置（现在不需要appId参数）
const getCosConfig = () => {
  return baseConfig
}

module.exports = {
  devConfig,
  prodConfig,
  getCosConfig
}