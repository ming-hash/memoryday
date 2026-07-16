/**
 * 腾讯云COS集成测试脚本
 * 用于验证COS服务的配置和功能
 */

const getCosService = require('../services/cosService')
const imageUtils = require('../utils/imageUtils')

// 测试配置
const testConfig = {
  testImagePath: '/images/demo/dish1.jpg',
  testBucketName: 'dish-images',
  maxFileSize: 5 * 1024 * 1024 // 5MB
}

class CosTester {
  constructor() {
    this.cosService = getCosService()
    this.testResults = []
  }

  /**
   * 运行所有测试
   */
  async runAllTests() {
    console.log('🚀 开始腾讯云COS集成测试...\n')
    
    try {
      await this.testCosServiceInitialization()
      await this.testImageUtils()
      await this.testFileValidation()
      await this.testUrlProcessing()
      
      this.printTestResults()
      
    } catch (error) {
      console.error('❌ 测试失败:', error.message)
      this.printTestResults()
    }
  }

  /**
   * 测试COS服务初始化
   */
  async testCosServiceInitialization() {
    console.log('📋 测试COS服务初始化...')
    
    try {
      // 检查配置
      if (!this.cosService.config) {
        throw new Error('COS服务配置未初始化')
      }
      
      const config = this.cosService.config
      const requiredFields = ['secretId', 'secretKey', 'bucket', 'region']
      
      for (const field of requiredFields) {
        if (!config[field]) {
          throw new Error(`缺少必要的配置字段: ${field}`)
        }
      }
      
      this.recordTestResult('COS服务初始化', true, '配置验证通过')
      
    } catch (error) {
      this.recordTestResult('COS服务初始化', false, error.message)
      throw error
    }
  }

  /**
   * 测试图片处理工具
   */
  async testImageUtils() {
    console.log('🖼️ 测试图片处理工具...')
    
    try {
      const testUrls = [
        'https://example.com/image.jpg',
        '/images/local.jpg',
        'http://tmp/wx123456.jpg'
      ]
      
      // 测试URL验证
      for (const url of testUrls) {
        if (!imageUtils.isValidImageUrl(url)) {
          throw new Error(`URL验证失败: ${url}`)
        }
      }
      
      // 测试COS URL识别
      const cosUrl = 'https://memoryday-dev-1250000000.cos.ap-beijing.myqcloud.com/dish_images/test.jpg'
      if (!imageUtils.isCosUrl(cosUrl)) {
        throw new Error('COS URL识别失败')
      }
      
      // 测试URL优化
      const optimizedUrl = imageUtils.getOptimizedUrl(cosUrl, 'thumbnail')
      if (!optimizedUrl.includes('imageView2')) {
        throw new Error('URL优化功能异常')
      }
      
      this.recordTestResult('图片处理工具', true, 'URL处理功能正常')
      
    } catch (error) {
      this.recordTestResult('图片处理工具', false, error.message)
      throw error
    }
  }

  /**
   * 测试文件验证
   */
  async testFileValidation() {
    console.log('📁 测试文件验证功能...')
    
    try {
      // 测试文件格式验证
      const supportedFormats = ['test.jpg', 'image.png', 'photo.webp']
      const unsupportedFormats = ['document.pdf', 'text.txt']
      
      for (const file of supportedFormats) {
        if (!imageUtils.isSupportedImageFormat(file)) {
          throw new Error(`支持格式验证失败: ${file}`)
        }
      }
      
      for (const file of unsupportedFormats) {
        if (imageUtils.isSupportedImageFormat(file)) {
          throw new Error(`不支持格式验证失败: ${file}`)
        }
      }
      
      // 测试文件大小验证（模拟）
      const sizeValidation = await imageUtils.validateFileSize('/images/demo/dish1.jpg')
      if (!sizeValidation.valid) {
        throw new Error('文件大小验证功能异常')
      }
      
      this.recordTestResult('文件验证功能', true, '格式和大小验证正常')
      
    } catch (error) {
      this.recordTestResult('文件验证功能', false, error.message)
      throw error
    }
  }

  /**
   * 测试URL处理
   */
  async testUrlProcessing() {
    console.log('🔗 测试URL处理功能...')
    
    try {
      const testUrls = [
        '/images/demo/dish1.jpg',
        'https://example.com/photo.jpg',
        'https://memoryday-dev-1250000000.cos.ap-beijing.myqcloud.com/dish_images/test.jpg'
      ]
      
      // 测试批量URL处理
      const processedUrls = imageUtils.getOptimizedUrls(testUrls, 'preview')
      
      if (processedUrls.length !== testUrls.length) {
        throw new Error('批量URL处理数量不匹配')
      }
      
      // 测试不同类型URL的处理
      for (let i = 0; i < testUrls.length; i++) {
        const original = testUrls[i]
        const processed = processedUrls[i]
        
        if (imageUtils.isCosUrl(original)) {
          // COS URL应该被优化
          if (!processed.includes('imageView2')) {
            throw new Error('COS URL优化失败')
          }
        } else {
          // 非COS URL应该保持不变
          if (processed !== original) {
            throw new Error('非COS URL处理异常')
          }
        }
      }
      
      this.recordTestResult('URL处理功能', true, '批量处理和优化正常')
      
    } catch (error) {
      this.recordTestResult('URL处理功能', false, error.message)
      throw error
    }
  }

  /**
   * 记录测试结果
   */
  recordTestResult(testName, passed, message) {
    this.testResults.push({
      name: testName,
      passed: passed,
      message: message,
      timestamp: new Date().toISOString()
    })
    
    const status = passed ? '✅' : '❌'
    console.log(`${status} ${testName}: ${message}`)
  }

  /**
   * 打印测试结果汇总
   */
  printTestResults() {
    console.log('\n📊 测试结果汇总:')
    console.log('='.repeat(50))
    
    const passedTests = this.testResults.filter(r => r.passed).length
    const totalTests = this.testResults.length
    const successRate = (passedTests / totalTests * 100).toFixed(1)
    
    console.log(`总测试数: ${totalTests}`)
    console.log(`通过数: ${passedTests}`)
    console.log(`成功率: ${successRate}%`)
    
    if (passedTests === totalTests) {
      console.log('\n🎉 所有测试通过！腾讯云COS集成配置正确。')
    } else {
      console.log('\n⚠️ 部分测试失败，请检查配置和代码。')
      
      // 显示失败的测试
      const failedTests = this.testResults.filter(r => !r.passed)
      console.log('\n失败的测试:')
      failedTests.forEach(test => {
        console.log(`❌ ${test.name}: ${test.message}`)
      })
    }
    
    console.log('='.repeat(50))
  }

  /**
   * 生成配置检查报告
   */
  generateConfigReport() {
    const config = this.cosService.config
    
    console.log('\n🔧 配置检查报告:')
    console.log('='.repeat(50))
    
    if (config) {
      console.log('✅ COS配置已加载')
      console.log(`📁 存储桶: ${config.bucket}`)
      console.log(`🌍 地域: ${config.region}`)
      console.log(`🔑 SecretId: ${config.secretId ? '已配置' : '未配置'}`)
      console.log(`🔑 SecretKey: ${config.secretKey ? '已配置' : '未配置'}`)
      console.log(`🔗 域名: ${config.domain}`)
    } else {
      console.log('❌ COS配置未加载')
    }
    
    console.log('='.repeat(50))
  }
}

// 运行测试
async function main() {
  const tester = new CosTester()
  
  try {
    // 生成配置报告
    tester.generateConfigReport()
    
    // 运行功能测试
    await tester.runAllTests()
    
  } catch (error) {
    console.error('测试执行异常:', error)
  }
}

// 如果是直接运行此文件，则执行测试
if (typeof module !== 'undefined' && require.main === module) {
  main()
}

module.exports = CosTester