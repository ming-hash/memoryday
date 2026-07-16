// utils/event.js

/**
 * 事件总线类
 * 用于组件间通信
 */
class EventBus {
  constructor() {
    this.events = new Map()
  }

  /**
   * 监听事件
   * @param {string} eventName 事件名称
   * @param {Function} callback 回调函数
   * @param {Object} context 上下文
   * @returns {Function} 取消监听函数
   */
  on(eventName, callback, context = null) {
    if (!this.events.has(eventName)) {
      this.events.set(eventName, [])
    }

    const event = {
      callback,
      context,
      once: false
    }

    this.events.get(eventName).push(event)

    // 返回取消监听函数
    return () => {
      this.off(eventName, callback, context)
    }
  }

  /**
   * 监听一次性事件
   * @param {string} eventName 事件名称
   * @param {Function} callback 回调函数
   * @param {Object} context 上下文
   * @returns {Function} 取消监听函数
   */
  once(eventName, callback, context = null) {
    if (!this.events.has(eventName)) {
      this.events.set(eventName, [])
    }

    const event = {
      callback,
      context,
      once: true
    }

    this.events.get(eventName).push(event)

    // 返回取消监听函数
    return () => {
      this.off(eventName, callback, context)
    }
  }

  /**
   * 取消监听事件
   * @param {string} eventName 事件名称
   * @param {Function} callback 回调函数
   * @param {Object} context 上下文
   */
  off(eventName, callback, context = null) {
    if (!this.events.has(eventName)) {
      return
    }

    const events = this.events.get(eventName)
    const index = events.findIndex(event => 
      event.callback === callback && 
      event.context === context
    )

    if (index !== -1) {
      events.splice(index, 1)
    }

    if (events.length === 0) {
      this.events.delete(eventName)
    }
  }

  /**
   * 触发事件
   * @param {string} eventName 事件名称
   * @param {...any} args 参数
   * @returns {boolean} 是否有监听器处理
   */
  emit(eventName, ...args) {
    if (!this.events.has(eventName)) {
      return false
    }

    const events = this.events.get(eventName)
    let hasListener = false

    // 遍历所有监听器
    for (let i = 0; i < events.length; i++) {
      const event = events[i]
      
      try {
        // 调用回调函数
        if (event.context) {
          event.callback.apply(event.context, args)
        } else {
          event.callback(...args)
        }
        
        hasListener = true

        // 如果是一次性事件，移除监听器
        if (event.once) {
          events.splice(i, 1)
          i--
        }
      } catch (error) {
        console.error(`Event ${eventName} handler error:`, error)
      }
    }

    // 清理空的事件列表
    if (events.length === 0) {
      this.events.delete(eventName)
    }

    return hasListener
  }

  /**
   * 移除所有事件监听器
   * @param {string} eventName 事件名称（可选）
   */
  removeAllListeners(eventName = null) {
    if (eventName) {
      this.events.delete(eventName)
    } else {
      this.events.clear()
    }
  }

  /**
   * 获取事件监听器数量
   * @param {string} eventName 事件名称
   * @returns {number} 监听器数量
   */
  listenerCount(eventName) {
    if (!this.events.has(eventName)) {
      return 0
    }
    return this.events.get(eventName).length
  }

  /**
   * 检查是否有事件监听器
   * @param {string} eventName 事件名称
   * @returns {boolean} 是否有监听器
   */
  hasListeners(eventName) {
    return this.listenerCount(eventName) > 0
  }
}

// 创建全局事件总线实例
const eventBus = new EventBus()

// 常用事件名称
const Events = {
  // 用户相关事件
  USER_LOGIN: 'user:login',
  USER_LOGOUT: 'user:logout',
  USER_UPDATE: 'user:update',

  // 菜品相关事件
  DISH_CREATE: 'dish:create',
  DISH_UPDATE: 'dish:update',
  DISH_DELETE: 'dish:delete',
  DISH_SELECT: 'dish:select',

  // 网络相关事件
  NETWORK_CONNECTED: 'network:connected',
  NETWORK_DISCONNECTED: 'network:disconnected',

  // 应用生命周期事件
  APP_READY: 'app:ready',
  APP_SHOW: 'app:show',
  APP_HIDE: 'app:hide',

  // 页面导航事件
  PAGE_NAVIGATE: 'page:navigate',
  PAGE_BACK: 'page:back',

  // 数据同步事件
  DATA_SYNC_START: 'data:sync:start',
  DATA_SYNC_COMPLETE: 'data:sync:complete',
  DATA_SYNC_ERROR: 'data:sync:error',

  // UI事件
  MODAL_SHOW: 'modal:show',
  MODAL_HIDE: 'modal:hide',
  TOAST_SHOW: 'toast:show',
  TOAST_HIDE: 'toast:hide'
}

module.exports = {
  EventBus,
  eventBus,
  Events
}