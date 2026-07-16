// utils/validator.js

/**
 * 验证工具类
 */
class Validator {
  /**
   * 验证手机号格式
   * @param {string} phone 手机号
   * @returns {boolean} 是否有效
   */
  static isPhone(phone) {
    const phoneRegex = /^1[3-9]\d{9}$/
    return phoneRegex.test(phone)
  }

  /**
   * 验证邮箱格式
   * @param {string} email 邮箱
   * @returns {boolean} 是否有效
   */
  static isEmail(email) {
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/
    return emailRegex.test(email)
  }

  /**
   * 验证密码强度
   * @param {string} password 密码
   * @returns {Object} 验证结果
   */
  static validatePassword(password) {
    const result = {
      isValid: false,
      strength: 0,
      messages: []
    }

    if (!password) {
      result.messages.push('密码不能为空')
      return result
    }

    // 长度检查
    if (password.length < 6) {
      result.messages.push('密码长度至少6位')
    } else if (password.length >= 8) {
      result.strength += 1
    }

    // 包含数字
    if (/\d/.test(password)) {
      result.strength += 1
    } else {
      result.messages.push('至少包含一个数字')
    }

    // 包含字母
    if (/[a-zA-Z]/.test(password)) {
      result.strength += 1
    } else {
      result.messages.push('至少包含一个字母')
    }

    // 包含特殊字符
    if (/[!@#$%^&*()_+\-=\[\]{};':"\\|,.<>\/?]/.test(password)) {
      result.strength += 1
    }

    result.isValid = result.messages.length === 0 && result.strength >= 2
    return result
  }

  /**
   * 验证用户名
   * @param {string} username 用户名
   * @returns {Object} 验证结果
   */
  static validateUsername(username) {
    const result = {
      isValid: false,
      messages: []
    }

    if (!username) {
      result.messages.push('用户名不能为空')
      return result
    }

    // 长度检查
    if (username.length < 2) {
      result.messages.push('用户名长度至少2位')
    } else if (username.length > 20) {
      result.messages.push('用户名长度不能超过20位')
    }

    // 字符检查
    if (!/^[a-zA-Z0-9_\u4e00-\u9fa5]+$/.test(username)) {
      result.messages.push('用户名只能包含中文、英文、数字和下划线')
    }

    result.isValid = result.messages.length === 0
    return result
  }

  /**
   * 验证验证码格式
   * @param {string} code 验证码
   * @returns {boolean} 是否有效
   */
  static isVerificationCode(code) {
    return /^\d{4,6}$/.test(code)
  }

  /**
   * 验证URL格式
   * @param {string} url URL地址
   * @returns {boolean} 是否有效
   */
  static isURL(url) {
    try {
      new URL(url)
      return true
    } catch {
      return false
    }
  }

  /**
   * 验证图片文件
   * @param {Object} file 文件对象
   * @returns {Object} 验证结果
   */
  static validateImageFile(file) {
    const result = {
      isValid: false,
      messages: []
    }

    if (!file) {
      result.messages.push('请选择图片')
      return result
    }

    // 文件类型检查
    const allowedTypes = ['image/jpeg', 'image/png', 'image/gif', 'image/webp']
    if (!allowedTypes.includes(file.type)) {
      result.messages.push('只支持JPEG、PNG、GIF、WEBP格式的图片')
    }

    // 文件大小检查 (5MB)
    const maxSize = 5 * 1024 * 1024
    if (file.size > maxSize) {
      result.messages.push('图片大小不能超过5MB')
    }

    result.isValid = result.messages.length === 0
    return result
  }

  /**
   * 验证数字范围
   * @param {number} num 数字
   * @param {number} min 最小值
   * @param {number} max 最大值
   * @returns {boolean} 是否在范围内
   */
  static isNumberInRange(num, min, max) {
    return typeof num === 'number' && num >= min && num <= max
  }

  /**
   * 验证必填字段
   * @param {*} value 字段值
   * @param {string} fieldName 字段名
   * @returns {string|null} 错误信息
   */
  static required(value, fieldName) {
    if (value === null || value === undefined || value === '') {
      return `${fieldName}不能为空`
    }
    if (Array.isArray(value) && value.length === 0) {
      return `${fieldName}不能为空`
    }
    return null
  }

  /**
   * 验证最小长度
   * @param {string|Array} value 值
   * @param {number} min 最小长度
   * @param {string} fieldName 字段名
   * @returns {string|null} 错误信息
   */
  static minLength(value, min, fieldName) {
    if (value && value.length < min) {
      return `${fieldName}长度不能少于${min}个字符`
    }
    return null
  }

  /**
   * 验证最大长度
   * @param {string|Array} value 值
   * @param {number} max 最大长度
   * @param {string} fieldName 字段名
   * @returns {string|null} 错误信息
   */
  static maxLength(value, max, fieldName) {
    if (value && value.length > max) {
      return `${fieldName}长度不能超过${max}个字符`
    }
    return null
  }

  /**
   * 批量验证字段
   * @param {Object} fields 字段对象
   * @param {Object} rules 验证规则
   * @returns {Object} 验证结果
   */
  static validateFields(fields, rules) {
    const errors = {}
    let isValid = true

    for (const [fieldName, rules] of Object.entries(rules)) {
      const value = fields[fieldName]
      
      for (const rule of rules) {
        const error = rule.validator(value, ...rule.args)
        if (error) {
          errors[fieldName] = error
          isValid = false
          break
        }
      }
    }

    return { isValid, errors }
  }

  /**
   * 创建验证规则
   * @param {Function} validator 验证函数
   * @param {...any} args 参数
   * @returns {Object} 验证规则
   */
  static rule(validator, ...args) {
    return { validator, args }
  }
}

// 常用验证规则
Validator.rules = {
  required: (fieldName) => Validator.rule((value) => Validator.required(value, fieldName)),
  minLength: (min, fieldName) => Validator.rule((value) => Validator.minLength(value, min, fieldName)),
  maxLength: (max, fieldName) => Validator.rule((value) => Validator.maxLength(value, max, fieldName)),
  phone: () => Validator.rule((value) => Validator.isPhone(value) ? null : '请输入正确的手机号'),
  email: () => Validator.rule((value) => Validator.isEmail(value) ? null : '请输入正确的邮箱地址'),
  verificationCode: () => Validator.rule((value) => Validator.isVerificationCode(value) ? null : '验证码格式不正确')
}

module.exports = Validator