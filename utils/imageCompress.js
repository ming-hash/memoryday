// utils/imageCompress.js
// 菜品图片智能压缩工具（方案 A：小程序端 Canvas 缩放 + JPEG 质量压缩）
// 目标：上传前将长边限制在 MAX_SIDE 内、JPEG 质量 QUALITY，
//       肉眼无损但体积下降 60%~90%，从而降低云存储/流量费用。

const MAX_SIDE = 1280 // 长边最大像素，手机展示足够清晰
const QUALITY = 0.82 // JPEG 质量，人眼几乎无差异

/**
 * 获取图片原始信息
 * @param {string} filePath 临时文件路径
 * @returns {Promise<{width:number,height:number}>}
 */
function getImageInfo(filePath) {
  return new Promise((resolve, reject) => {
    wx.getImageInfo({
      src: filePath,
      success: (res) => resolve({ width: res.width, height: res.height, orientation: res.orientation }),
      fail: reject
    })
  })
}

/**
 * 通过 Canvas 2D 将图片等比缩放到目标尺寸并导出为 JPEG 临时文件
 * @param {string} filePath 源图片路径
 * @param {{width:number,height:number}} info 图片尺寸
 * @param {number} quality JPEG 质量 0~1
 * @returns {Promise<string>} 压缩后的临时文件路径
 */
function scaleViaCanvas(filePath, info, quality) {
  return new Promise((resolve, reject) => {
    const longSide = Math.max(info.width, info.height)
    const scale = longSide > MAX_SIDE ? MAX_SIDE / longSide : 1
    const targetWidth = Math.round(info.width * scale)
    const targetHeight = Math.round(info.height * scale)

    // 创建离屏 canvas（type=2d 用 Nodes 接口，兼容性最好）
    const query = wx.createSelectorQuery()
    // 无对应 wxml 节点时，用 wx.createOffscreenCanvas 更稳妥
    let canvas
    try {
      canvas = wx.createOffscreenCanvas({ type: '2d', width: targetWidth, height: targetHeight })
    } catch (e) {
      // 老基础库兜底：部分版本不支持 offscreen，返回原图
      console.warn('createOffscreenCanvas 不支持，使用原图:', e)
      resolve(filePath)
      return
    }

    const ctx = canvas.getContext('2d')
    const image = canvas.createImage()
    image.onload = () => {
      ctx.clearRect(0, 0, targetWidth, targetHeight)
      ctx.drawImage(image, 0, 0, targetWidth, targetHeight)
      wx.canvasToTempFilePath({
        canvas,
        x: 0,
        y: 0,
        width: targetWidth,
        height: targetHeight,
        destWidth: targetWidth,
        destHeight: targetHeight,
        fileType: 'jpg',
        quality,
        success: (res) => resolve(res.tempFilePath),
        fail: (err) => {
          console.warn('canvasToTempFilePath 失败，使用原图:', err)
          resolve(filePath)
        }
      })
    }
    image.onerror = (err) => {
      console.warn('图片解码失败，使用原图:', err)
      resolve(filePath)
    }
    image.src = filePath
  })
}

/**
 * 压缩单张图片（对外主接口）
 * 当图片长边已 ≤ MAX_SIDE 时直接返回原路径，跳过压缩。
 * @param {string} filePath
 * @returns {Promise<string>} 压缩后（或原）临时路径
 */
async function compressImage(filePath) {
  try {
    const info = await getImageInfo(filePath)
    const longSide = Math.max(info.width, info.height)
    if (longSide <= MAX_SIDE) {
      return filePath
    }
    return await scaleViaCanvas(filePath, info, QUALITY)
  } catch (error) {
    console.warn('压缩异常，回退原图:', error)
    return filePath
  }
}

/**
 * 批量压缩（保持顺序）
 * @param {string[]} filePaths
 * @returns {Promise<string[]>}
 */
async function compressImages(filePaths) {
  return Promise.all(filePaths.map((p) => compressImage(p)))
}

module.exports = {
  MAX_SIDE,
  QUALITY,
  compressImage,
  compressImages
}
