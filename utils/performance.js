// utils/performance.js

/**
 * 性能监控工具类
 */
class PerformanceMonitor {
  constructor() {
    this.metrics = new Map()
    this.timers = new Map()
    this.reports = []
  }

  /**
   * 开始计时
   * @param {string} name 计时器名称
   * @returns {string} 计时器ID
   */
  start(name) {
    const id = `${name}_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`
    this.timers.set(id, {
      name,
      startTime: Date.now(),
      endTime: null,
      duration: null
    })
    return id
  }

  /**
   * 结束计时
   * @param {string} id 计时器ID
   * @returns {Object} 计时结果
   */
  end(id) {
    if (!this.timers.has(id)) {
      return null
    }

    const timer = this.timers.get(id)
    timer.endTime = Date.now()
    timer.duration = timer.endTime - timer.startTime

    // 记录到指标中
    this.recordMetric(timer.name, timer.duration)

    // 移除计时器
    this.timers.delete(id)

    return timer
  }

  /**
   * 记录性能指标
   * @param {string} name 指标名称
   * @param {number} value 指标值
   * @param {Object} tags 标签
   */
  recordMetric(name, value, tags = {}) {
    if (!this.metrics.has(name)) {
      this.metrics.set(name, [])
    }

    const metric = {
      value,
      timestamp: Date.now(),
      tags
    }

    this.metrics.get(name).push(metric)

    // 保持最近100条记录
    if (this.metrics.get(name).length > 100) {
      this.metrics.get(name).shift()
    }
  }

  /**
   * 获取性能指标统计
   * @param {string} name 指标名称
   * @returns {Object} 统计信息
   */
  getMetricStats(name) {
    if (!this.metrics.has(name) || this.metrics.get(name).length === 0) {
      return null
    }

    const values = this.metrics.get(name).map(m => m.value)
    const sum = values.reduce((a, b) => a + b, 0)
    const avg = sum / values.length
    const min = Math.min(...values)
    const max = Math.max(...values)

    // 计算百分位数
    const sorted = [...values].sort((a, b) => a - b)
    const p95 = sorted[Math.floor(sorted.length * 0.95)]
    const p99 = sorted[Math.floor(sorted.length * 0.99)]

    return {
      count: values.length,
      sum,
      avg: Math.round(avg),
      min,
      max,
      p95,
      p99,
      latest: values[values.length - 1]
    }
  }

  /**
   * 报告性能数据
   * @param {string} type 报告类型
   * @param {Object} data 报告数据
   * @param {Object} metadata 元数据
   */
  report(type, data, metadata = {}) {
    const report = {
      type,
      data,
      metadata,
      timestamp: Date.now(),
      environment: this.getEnvironmentInfo()
    }

    this.reports.push(report)

    // 保持最近50条报告
    if (this.reports.length > 50) {
      this.reports.shift()
    }

    // 开发环境下打印到控制台
    const devFlag = typeof __wxConfig !== 'undefined' && __wxConfig.envVersion === 'develop'
    if (devFlag) {
      console.log(`[Performance] ${type}:`, data)
    }
  }

  /**
   * 获取环境信息
   * @returns {Object} 环境信息
   */
  getEnvironmentInfo() {
    try {
      const systemInfo = wx.getSystemInfoSync()
      return {
        platform: systemInfo.platform,
        version: systemInfo.version,
        SDKVersion: systemInfo.SDKVersion,
        language: systemInfo.language,
        screenWidth: systemInfo.screenWidth,
        screenHeight: systemInfo.screenHeight,
        windowWidth: systemInfo.windowWidth,
        windowHeight: systemInfo.windowHeight,
        pixelRatio: systemInfo.pixelRatio
      }
    } catch (error) {
      return { error: error.message }
    }
  }

  /**
   * 监控页面加载性能
   */
  monitorPageLoad() {
    const timerId = this.start('page_load')

    // 页面显示时结束计时
    const onShow = () => {
      this.end(timerId)
      wx.offAppShow(onShow)
    }

    wx.onAppShow(onShow)
  }

  /**
   * 监控API请求性能
   * @param {string} url API地址
   * @param {string} method 请求方法
   * @returns {Function} 结束监控函数
   */
  monitorApiRequest(url, method) {
    const timerId = this.start('api_request')
    
    return (success, statusCode, data) => {
      const timer = this.end(timerId)
      if (timer) {
        this.report('api_request', {
          url,
          method,
          duration: timer.duration,
          success,
          statusCode,
          dataSize: data ? JSON.stringify(data).length : 0
        })
      }
    }
  }

  /**
   * 监控组件渲染性能
   * @param {string} componentName 组件名称
   */
  monitorComponentRender(componentName) {
    const timerId = this.start(`component_render_${componentName}`)
    
    return () => {
      const timer = this.end(timerId)
      if (timer) {
        this.report('component_render', {
          componentName,
          duration: timer.duration
        })
      }
    }
  }

  /**
   * 获取所有性能报告
   * @returns {Array} 性能报告列表
   */
  getReports() {
    return [...this.reports]
  }

  /**
   * 清空所有性能数据
   */
  clear() {
    this.metrics.clear()
    this.timers.clear()
    this.reports = []
  }
}

// 创建全局性能监控实例
const performanceMonitor = new PerformanceMonitor()

// 常用性能监控点
const PerformancePoints = {
  PAGE_LOAD: 'page_load',
  API_REQUEST: 'api_request',
  COMPONENT_RENDER: 'component_render',
  IMAGE_LOAD: 'image_load',
  DATA_SYNC: 'data_sync',
  USER_INTERACTION: 'user_interaction'
}

module.exports = {
  PerformanceMonitor,
  performanceMonitor,
  PerformancePoints
}