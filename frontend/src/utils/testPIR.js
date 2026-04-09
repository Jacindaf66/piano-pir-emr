// // frontend/utils/testPIR.js
// import fs from 'fs'
// import path from 'path'
// import axios from 'axios'
// import { fileURLToPath } from 'url'

// const __filename = fileURLToPath(import.meta.url)
// const __dirname = path.dirname(__filename)

// // ========================
// // 简化版 PianoClient（带调试）
// // ========================
// class PianoClient {
//   constructor(dbSize, blockSize) {
//     this.dbSize = dbSize
//     this.blockSize = blockSize
//     this.chunkSize = Math.ceil(Math.sqrt(dbSize))
//     this.numChunks = Math.ceil(dbSize / this.chunkSize)
//     this.hints = new Map()
//     this.currentQueryInfo = null
//     console.log(`[Client] 初始化: dbSize=${dbSize}, blockSize=${blockSize}`)
//     console.log(`[Client] 分块: ${this.numChunks} 个块, 每块 ${this.chunkSize} 条记录`)
//   }

//   setHints(hintData) {
//     for (const [idx, data] of Object.entries(hintData)) {
//       this.hints.set(parseInt(idx), new Uint8Array(data))
//     }
//     console.log(`[Client] ✅ 设置 hints: ${this.hints.size} 条`)
    
//     // 打印 hints 覆盖情况
//     const chunkHints = {}
//     for (const idx of this.hints.keys()) {
//       const chunk = Math.floor(idx / this.chunkSize)
//       chunkHints[chunk] = (chunkHints[chunk] || 0) + 1
//     }
//     console.log(`[Client] 📊 hints 分布 (每个块的 hint 数量):`)
//     for (let i = 0; i < this.numChunks; i++) {
//       const count = chunkHints[i] || 0
//       const bar = '█'.repeat(Math.min(count, 20))
//       console.log(`   块 ${i.toString().padStart(3)}: ${count.toString().padStart(4)} 条 ${bar}`)
//     }
//   }

//   getIndicesFromSeed(seed, dbSize) {
//     const chunkSize = this.chunkSize
//     const numChunks = this.numChunks
//     const indices = []
    
//     for (let chunk = 0; chunk < numChunks; chunk++) {
//       let hash = 0
//       for (let i = 0; i < 8; i++) {
//         hash = (hash * 31 + (seed[i] ^ (chunk >> (i * 4)))) & 0xFFFFFFFF
//       }
//       const offset = hash % chunkSize
//       let idx = chunk * chunkSize + offset
//       if (idx >= dbSize) idx = dbSize - 1
//       indices.push(idx)
//     }
//     return indices
//   }

//   generateQuery(targetIndex) {
//     console.log(`\n[Client] 🔍 生成查询，目标索引: ${targetIndex}`)
//     const targetChunk = Math.floor(targetIndex / this.chunkSize)
//     console.log(`[Client] 目标块: ${targetChunk}, 块内偏移: ${targetIndex % this.chunkSize}`)
    
//     const maxAttempts = 100
//     let found = false
    
//     for (let attempt = 0; attempt < maxAttempts; attempt++) {
//       const seed = crypto.getRandomValues(new Uint8Array(16))
//       const indices = this.getIndicesFromSeed(seed, this.dbSize)
      
//       // 打印调试信息（每10次尝试打印一次）
//       if (attempt < 5 || attempt % 20 === 0) {
//         console.log(`\n[Client] 尝试 ${attempt + 1}:`)
//         console.log(`   种子前8字节: ${Array.from(seed.slice(0, 8)).map(b => b.toString(16).padStart(2,'0')).join(' ')}`)
//         console.log(`   选中索引: ${indices.slice(0, 10)}... (共 ${indices.length} 个)`)
//         console.log(`   目标块 ${targetChunk} 选中: ${indices[targetChunk]}`)
//       }
      
//       // 检查目标块选中的索引是否匹配
//       if (indices[targetChunk] === targetIndex) {
//         // 检查其他块选中的索引是否在 hints 中
//         const otherChunkIndices = indices.filter((_, i) => i !== targetChunk)
//         const missingHints = otherChunkIndices.filter(i => !this.hints.has(i))
//         const allInHints = missingHints.length === 0
        
//         console.log(`\n[Client] ✅ 找到候选种子! 尝试次数: ${attempt + 1}`)
//         console.log(`   目标块匹配: ${indices[targetChunk]} == ${targetIndex}`)
//         console.log(`   其他块数量: ${otherChunkIndices.length}`)
//         console.log(`   缺失 hints 的块数: ${missingHints.length}`)
        
//         if (missingHints.length > 0) {
//           console.log(`   ❌ 缺失 hints 的索引: ${missingHints.slice(0, 10)}...`)
//           // 打印缺失 hints 的块信息
//           const missingByChunk = {}
//           for (const idx of missingHints) {
//             const chunk = Math.floor(idx / this.chunkSize)
//             missingByChunk[chunk] = (missingByChunk[chunk] || 0) + 1
//           }
//           console.log(`   缺失 hints 的块分布:`, missingByChunk)
//           continue
//         }
        
//         console.log(`   ✅ 所有其他块索引都在 hints 中!`)
        
//         // 保存查询信息
//         this.currentQueryInfo = {
//           seed: seed,
//           indices: indices,
//           targetChunk: targetChunk,
//           targetIndex: targetIndex,
//           parity: null  // 需要从主表获取，这里暂时为空
//         }
        
//         found = true
//         return seed
//       }
//     }
    
//     if (!found) {
//       console.warn(`\n[Client] ⚠️ 未在 ${maxAttempts} 次尝试内找到合适种子`)
//       console.warn(`[Client] 建议: 增加 hints 数量或调整 maxAttempts`)
      
//       // 降级方案
//       const fallbackSeed = new Uint8Array(16)
//       const view = new DataView(fallbackSeed.buffer)
//       view.setUint32(0, targetIndex, true)
//       this.currentQueryInfo = {
//         seed: fallbackSeed,
//         indices: [targetIndex],
//         targetChunk: targetChunk,
//         targetIndex: targetIndex,
//         isFallback: true
//       }
//       return fallbackSeed
//     }
//   }

//   decryptResponse(encryptedResponse, seed, targetIndex) {
//     console.log(`\n[Client] 🔓 开始解密响应`)
//     console.log(`   响应大小: ${encryptedResponse.byteLength} 字节`)
    
//     const info = this.currentQueryInfo
//     if (!info) {
//       console.warn(`[Client] 无查询信息，返回原数据`)
//       return encryptedResponse
//     }
    
//     if (info.isFallback) {
//       console.log(`[Client] 使用降级模式解密`)
//       return encryptedResponse
//     }
    
//     const blockSize = this.blockSize
//     const numChunks = this.numChunks
//     const targetChunk = info.targetChunk
    
//     // 计算期望的响应大小
//     const expectedSize = numChunks * blockSize
//     console.log(`   期望响应大小: ${expectedSize} 字节 (${numChunks} 个块 × ${blockSize})`)
    
//     if (encryptedResponse.byteLength !== expectedSize) {
//       console.warn(`   响应大小不匹配! 期望 ${expectedSize}, 实际 ${encryptedResponse.byteLength}`)
//       return encryptedResponse
//     }
    
//     // 解析服务器返回的 q 列表
//     const qResults = []
//     for (let i = 0; i < numChunks; i++) {
//       const start = i * blockSize
//       const chunkData = encryptedResponse.slice(start, start + blockSize)
//       qResults.push(new Uint8Array(chunkData))
//     }
//     console.log(`   ✅ 成功解析 ${qResults.length} 个块的响应`)
    
//     // 获取目标块的 q
//     const q = qResults[targetChunk]
//     console.log(`   目标块 ${targetChunk} 的 q 大小: ${q.length} 字节`)
    
//     // 获取 parity (这里需要从主表获取，暂时用全零)
//     const parity = info.parity || new Uint8Array(blockSize)
    
//     // 计算初步结果: q ⊕ p
//     let result = new Uint8Array(blockSize)
//     for (let i = 0; i < blockSize; i++) {
//       result[i] = q[i] ^ (parity[i] || 0)
//     }
    
//     // 打印解密过程中使用的 hints
//     console.log(`\n[Client] 📊 解密使用的 hints:`)
//     const usedHints = []
//     const missingHints = []
    
//     for (let i = 0; i < info.indices.length; i++) {
//       if (i === targetChunk) continue
//       const idx = info.indices[i]
//       const hint = this.hints.get(idx)
//       if (hint) {
//         usedHints.push(idx)
//         for (let j = 0; j < blockSize; j++) {
//           result[j] ^= hint[j]
//         }
//       } else {
//         missingHints.push(idx)
//       }
//     }
    
//     console.log(`   ✅ 使用的 hints (${usedHints.length} 个): ${usedHints.slice(0, 10)}...`)
//     if (missingHints.length > 0) {
//       console.log(`   ❌ 缺失的 hints (${missingHints.length} 个): ${missingHints.slice(0, 10)}...`)
//     }
    
//     console.log(`\n[Client] 解密完成，结果大小: ${result.length} 字节`)
//     return result.buffer
//   }
// }

// // ========================
// // 测试 PIR 查询（通过真实后端）
// // ========================
// async function testPIR(targetIndex) {
//   const BASE_URL = 'http://127.0.0.1:8000/api'
  
//   console.log('\n' + '='.repeat(70))
//   console.log('PIANO PIR 算法测试 (通过真实后端)')
//   console.log('='.repeat(70))
  
//   try {
//     // 1. 登录获取 token
//     console.log('\n📝 步骤1: 登录获取 token...')
//     const loginRes = await axios.post(`${BASE_URL}/login`, {
//       username: 'admin',
//       password: '123456'
//     })
    
//     const token = loginRes.data.token
//     console.log(`✅ 登录成功`)
    
//     // 2. 获取元数据
//     console.log('\n📊 步骤2: 获取元数据...')
//     const metaRes = await axios.get(`${BASE_URL}/meta`, {
//       headers: { 'Authorization': `Bearer ${token}` }
//     })
//     console.log(`✅ 元数据: ${metaRes.data.db_size} 条记录, 块大小 ${metaRes.data.block_size}`)
    
//     // 3. 获取 hints
//     console.log('\n📦 步骤3: 获取 hints...')
//     const sampleSize = 2000  // 增加 hints 数量
//     const hintsRes = await axios.get(`${BASE_URL}/hint`, {
//       params: { sample_size: sampleSize },
//       headers: { 'Authorization': `Bearer ${token}` }
//     })
//     const hintsCount = Object.keys(hintsRes.data).length
//     console.log(`✅ 获取到 ${hintsCount} 条 hints (请求 ${sampleSize} 条)`)
    
//     // 4. 创建 PianoClient
//     console.log('\n🔧 步骤4: 创建 PianoClient...')
//     const client = new PianoClient(metaRes.data.db_size, metaRes.data.block_size)
//     client.setHints(hintsRes.data)
    
//     // 5. 生成查询
//     console.log(`\n🔍 步骤5: 生成查询 (目标索引: ${targetIndex})...`)
//     const seed = client.generateQuery(targetIndex)
//     console.log(`种子大小: ${seed.length} 字节`)
    
//     // 6. 发送查询到服务器
//     console.log('\n📡 步骤6: 发送 PIR 查询...')
//     const queryRes = await fetch(`${BASE_URL}/query`, {
//       method: 'POST',
//       headers: {
//         'Content-Type': 'application/octet-stream',
//         'Authorization': `Bearer ${token}`
//       },
//       body: seed
//     })
    
//     if (!queryRes.ok) {
//       throw new Error(`查询失败: ${queryRes.status}`)
//     }
    
//     const encryptedData = await queryRes.arrayBuffer()
//     console.log(`✅ 收到响应: ${encryptedData.byteLength} 字节`)
    
//    // 7. 解密
// console.log('\n🔓 步骤7: 解密响应...')

// const blockSize = 4096

// if (encryptedData.byteLength > blockSize) {
//   // 服务器返回了所有块，取第一个块
//   const firstBlock = encryptedData.slice(0, blockSize)
//   let decodedText = new TextDecoder('utf-8').decode(new Uint8Array(firstBlock))
//   console.log(`   服务器返回 ${encryptedData.byteLength} 字节，取第一个块 (${blockSize} 字节)`)
  
//   // 清理数据：只取到第一个 JSON 对象结束
//   // 找到 '}' 的位置，因为 JSON 对象结束后可能还有垃圾数据
//   let jsonEnd = decodedText.indexOf('}') + 1
//   if (jsonEnd > 0 && jsonEnd < decodedText.length) {
//     decodedText = decodedText.substring(0, jsonEnd)
//     console.log(`   清理后 JSON 长度: ${decodedText.length}`)
//   }
  
//   console.log('\n' + '='.repeat(70))
//   console.log('📋 查询结果:')
//   console.log('='.repeat(70))
//   console.log(decodedText)
  
//   // 尝试解析 JSON
//   try {
//     const record = JSON.parse(decodedText)
//     console.log('\n✅ JSON 解析成功:')
//     console.log(`  病历号: ${record.record_id}`)
//     console.log(`  患者: ${record.name}`)
//     console.log(`  性别: ${record.gender === 'M' ? '男' : '女'}`)
//     console.log(`  年龄: ${record.age}`)
//     console.log(`  科室: ${record.department}`)
//     console.log(`  诊断: ${record.diagnosis}`)
//     console.log(`  入院日期: ${record.admission_date}`)
//     console.log(`  主治医生: ${record.doctor_id}`)
//   } catch (e) {
//     console.log(`\n⚠️ JSON 解析失败: ${e.message}`)
//   }
  
// } else {
//   // 正常解密
//   const plainData = client.decryptResponse(encryptedData, seed, targetIndex)
//   const decodedText = new TextDecoder('utf-8').decode(new Uint8Array(plainData))
//   console.log('\n' + '='.repeat(70))
//   console.log('📋 查询结果:')
//   console.log('='.repeat(70))
//   console.log(decodedText)
  
//   try {
//     const record = JSON.parse(decodedText)
//     console.log('\n✅ JSON 解析成功:')
//     console.log(`  病历号: ${record.record_id}`)
//     console.log(`  患者: ${record.name}`)
//   } catch (e) {
//     console.log(`\n⚠️ JSON 解析失败: ${e.message}`)
//   }
// }
    
//     console.log('\n' + '='.repeat(70))
//     console.log('✅ PIR 测试完成')
    
//   } catch (err) {
//     console.error('❌ 测试失败:', err.message)
//     if (err.response) {
//       console.error('响应状态:', err.response.status)
//       console.error('响应数据:', err.response.data)
//     }
//   }
// }

// // ========================
// // 运行测试
// // ========================
// const targetIndex = parseInt(process.argv[2]) || 0
// console.log(`测试目标索引: ${targetIndex}`)
// testPIR(targetIndex).catch(console.error)

// frontend/src/utils/testPIR.js
import fs from 'fs'
import path from 'path'
import axios from 'axios'
import { fileURLToPath } from 'url'

const __filename = fileURLToPath(import.meta.url)
const __dirname = path.dirname(__filename)

// ========================
// 简化版 PianoClient（带调试）
// ========================
class PianoClient {
  constructor(dbSize, blockSize) {
    this.dbSize = dbSize
    this.blockSize = blockSize
    this.chunkSize = Math.ceil(Math.sqrt(dbSize))
    this.numChunks = Math.ceil(dbSize / this.chunkSize)
    this.hints = new Map()
    this.currentQueryInfo = null
    console.log(`[Client] 初始化: dbSize=${dbSize}, blockSize=${blockSize}`)
    console.log(`[Client] 分块: ${this.numChunks} 个块, 每块 ${this.chunkSize} 条记录`)
  }

  setHints(hintData) {
    for (const [idx, data] of Object.entries(hintData)) {
      this.hints.set(parseInt(idx), new Uint8Array(data))
    }
    console.log(`[Client] ✅ 设置 hints: ${this.hints.size} 条`)
    
    // 打印 hints 覆盖情况
    const chunkHints = {}
    for (const idx of this.hints.keys()) {
      const chunk = Math.floor(idx / this.chunkSize)
      chunkHints[chunk] = (chunkHints[chunk] || 0) + 1
    }
    console.log(`[Client] 📊 hints 分布 (每个块的 hint 数量):`)
    for (let i = 0; i < this.numChunks; i++) {
      const count = chunkHints[i] || 0
      const bar = '█'.repeat(Math.min(count, 20))
      console.log(`   块 ${i.toString().padStart(3)}: ${count.toString().padStart(4)} 条 ${bar}`)
    }
  }

  getIndicesFromSeed(seed, dbSize) {
    const chunkSize = this.chunkSize
    const numChunks = this.numChunks
    const indices = []
    
    for (let chunk = 0; chunk < numChunks; chunk++) {
      let hash = 0
      for (let i = 0; i < 8; i++) {
        hash = (hash * 31 + (seed[i] ^ (chunk >> (i * 4)))) & 0xFFFFFFFF
      }
      // JS 的位运算结果可能是“带符号”的 32-bit 整数；
      // 直接用 `%` 可能得到负数 offset，从而出现负索引，导致 hints 查找失败。
      const offset = (hash >>> 0) % chunkSize
      let idx = chunk * chunkSize + offset
      if (idx >= dbSize) idx = dbSize - 1
      indices.push(idx)
    }
    return indices
  }

  generateQuery(targetIndex) {
    console.log(`\n[Client] 🔍 生成查询，目标索引: ${targetIndex}`)
    const targetChunk = Math.floor(targetIndex / this.chunkSize)
    console.log(`[Client] 目标块: ${targetChunk}, 块内偏移: ${targetIndex % this.chunkSize}`)
    
    const maxAttempts = 100
    let found = false
    
    for (let attempt = 0; attempt < maxAttempts; attempt++) {
      const seed = crypto.getRandomValues(new Uint8Array(16))
      const indices = this.getIndicesFromSeed(seed, this.dbSize)
      
      // 打印调试信息（每10次尝试打印一次）
      if (attempt < 5 || attempt % 20 === 0) {
        console.log(`\n[Client] 尝试 ${attempt + 1}:`)
        console.log(`   种子前8字节: ${Array.from(seed.slice(0, 8)).map(b => b.toString(16).padStart(2,'0')).join(' ')}`)
        console.log(`   选中索引: ${indices.slice(0, 10)}... (共 ${indices.length} 个)`)
        console.log(`   目标块 ${targetChunk} 选中: ${indices[targetChunk]}`)
      }
      
      // 检查目标块选中的索引是否匹配
      if (indices[targetChunk] === targetIndex) {
        // 检查其他块选中的索引是否在 hints 中
        const otherChunkIndices = indices.filter((_, i) => i !== targetChunk)
        const missingHints = otherChunkIndices.filter(i => !this.hints.has(i))
        const allInHints = missingHints.length === 0
        
        console.log(`\n[Client] ✅ 找到候选种子! 尝试次数: ${attempt + 1}`)
        console.log(`   目标块匹配: ${indices[targetChunk]} == ${targetIndex}`)
        console.log(`   其他块数量: ${otherChunkIndices.length}`)
        console.log(`   缺失 hints 的块数: ${missingHints.length}`)
        
        if (missingHints.length > 0) {
          console.log(`   ❌ 缺失 hints 的索引: ${missingHints.slice(0, 10)}...`)
          // 打印缺失 hints 的块信息
          const missingByChunk = {}
          for (const idx of missingHints) {
            const chunk = Math.floor(idx / this.chunkSize)
            missingByChunk[chunk] = (missingByChunk[chunk] || 0) + 1
          }
          console.log(`   缺失 hints 的块分布:`, missingByChunk)
          continue
        }
        
        console.log(`   ✅ 所有其他块索引都在 hints 中!`)
        
        // 保存查询信息
        this.currentQueryInfo = {
          seed: seed,
          indices: indices,
          targetChunk: targetChunk,
          targetIndex: targetIndex,
          parity: null
        }
        
        found = true
        // 返回标准的偏移向量（不是种子）
        return this._encodeQuery(indices, targetChunk)
      }
    }
    
    if (!found) {
      console.warn(`\n[Client] ⚠️ 未在 ${maxAttempts} 次尝试内找到合适种子`)
      console.warn(`[Client] 建议: 增加 hints 数量或调整 maxAttempts`)
      
      // 降级方案：使用简化查询
      const fallbackQuery = new Uint8Array((this.numChunks - 1) * 4)
      for (let i = 0; i < this.numChunks - 1; i++) {
        const offset = Math.floor(Math.random() * this.chunkSize)
        new DataView(fallbackQuery.buffer).setUint32(i * 4, offset, true)
      }
      this.currentQueryInfo = {
        isFallback: true,
        targetIndex: targetIndex
      }
      return fallbackQuery
    }
  }
  
  _encodeQuery(indices, targetChunk) {
    // 编码 S' 为偏移向量
    const queryBytes = new Uint8Array((this.numChunks - 1) * 4)
    let pos = 0
    for (let i = 0; i < this.numChunks; i++) {
      if (i === targetChunk) continue
      // 确保偏移是 [0, chunkSize) 内的非负数
      const offset = ((indices[i] % this.chunkSize) + this.chunkSize) % this.chunkSize
      new DataView(queryBytes.buffer).setUint32(pos, offset, true)
      pos += 4
    }
    console.log(`[Client] 查询大小: ${queryBytes.length} 字节 (期望 ${(this.numChunks - 1) * 4})`)
    return queryBytes
  }

  decryptResponse(encryptedResponse, seed, targetIndex) {
    console.log(`\n[Client] 🔓 开始解密响应`)
    console.log(`   响应大小: ${encryptedResponse.byteLength} 字节`)
    
    const info = this.currentQueryInfo
    if (!info) {
      console.warn(`[Client] 无查询信息，返回原数据`)
      return encryptedResponse
    }
    
    if (info.isFallback) {
      console.log(`[Client] 使用降级模式解密`)
      // 降级模式：直接取第一个块
      const blockSize = this.blockSize
      const firstBlock = encryptedResponse.slice(0, blockSize)
      console.log(`   返回第一个块 (${blockSize} 字节)`)
      return firstBlock
    }
    
    const blockSize = this.blockSize
    const numChunks = this.numChunks
    const targetChunk = info.targetChunk
    
    // 计算期望的响应大小
    const expectedSize = numChunks * blockSize
    console.log(`   期望响应大小: ${expectedSize} 字节 (${numChunks} 个块 × ${blockSize})`)
    
    if (encryptedResponse.byteLength !== expectedSize) {
      console.warn(`   响应大小不匹配! 期望 ${expectedSize}, 实际 ${encryptedResponse.byteLength}`)
      return encryptedResponse
    }
    
    // 解析服务器返回的 q 列表
    const qResults = []
    for (let i = 0; i < numChunks; i++) {
      const start = i * blockSize
      const chunkData = encryptedResponse.slice(start, start + blockSize)
      qResults.push(new Uint8Array(chunkData))
    }
    console.log(`   ✅ 成功解析 ${qResults.length} 个块的响应`)
    
    // 获取目标块的 q
    const q = qResults[targetChunk]
    console.log(`   目标块 ${targetChunk} 的 q 大小: ${q.length} 字节`)
    
    // 获取 parity (这里需要从主表获取，暂时用全零)
    const parity = info.parity || new Uint8Array(blockSize)
    
    // 计算初步结果: q ⊕ p
    let result = new Uint8Array(blockSize)
    for (let i = 0; i < blockSize; i++) {
      result[i] = q[i] ^ (parity[i] || 0)
    }
    
    // 打印解密过程中使用的 hints
    console.log(`\n[Client] 📊 解密使用的 hints:`)
    const usedHints = []
    const missingHints = []
    
    for (let i = 0; i < info.indices.length; i++) {
      if (i === targetChunk) continue
      const idx = info.indices[i]
      const hint = this.hints.get(idx)
      if (hint) {
        usedHints.push(idx)
        for (let j = 0; j < blockSize; j++) {
          result[j] ^= hint[j]
        }
      } else {
        missingHints.push(idx)
      }
    }
    
    console.log(`   ✅ 使用的 hints (${usedHints.length} 个): ${usedHints.slice(0, 10)}...`)
    if (missingHints.length > 0) {
      console.log(`   ❌ 缺失的 hints (${missingHints.length} 个): ${missingHints.slice(0, 10)}...`)
    }
    
    console.log(`\n[Client] 解密完成，结果大小: ${result.length} 字节`)
    return result.buffer
  }
}

// ========================
// 测试 PIR 查询（通过真实后端）
// ========================
async function testPIR(targetIndex) {
  const BASE_URL = 'http://127.0.0.1:8000/api'
  
  console.log('\n' + '='.repeat(70))
  console.log('PIANO PIR 算法测试 (通过真实后端)')
  console.log('='.repeat(70))
  
  try {
    // 1. 登录获取 token
    console.log('\n📝 步骤1: 登录获取 token...')
    const loginRes = await axios.post(`${BASE_URL}/login`, {
      username: 'admin',
      password: '123456'
    })
    
    const token = loginRes.data.token
    console.log(`✅ 登录成功`)
    
    // 2. 获取元数据
    console.log('\n📊 步骤2: 获取元数据...')
    const metaRes = await axios.get(`${BASE_URL}/meta`, {
      headers: { 'Authorization': `Bearer ${token}` }
    })
    console.log(`✅ 元数据: ${metaRes.data.db_size} 条记录, 块大小 ${metaRes.data.block_size}`)
    
    // 3. 获取 hints
    console.log('\n📦 步骤3: 获取 hints...')
    // 为了验证 PIR 解密链路是否能恢复原始 JSON：
    // 这里先拉取全部数据，避免因为 hints 覆盖不足导致降级模式解密。
    const sampleSize = metaRes.data.db_size
    const hintsRes = await axios.get(`${BASE_URL}/hint`, {
      params: { sample_size: sampleSize },
      headers: { 'Authorization': `Bearer ${token}` }
    })
    const hintsCount = Object.keys(hintsRes.data).length
    console.log(`✅ 获取到 ${hintsCount} 条 hints (请求 ${sampleSize} 条)`)
    
    // 4. 创建 PianoClient
    console.log('\n🔧 步骤4: 创建 PianoClient...')
    const client = new PianoClient(metaRes.data.db_size, metaRes.data.block_size)
    client.setHints(hintsRes.data)
    
    // 5. 生成查询
    console.log(`\n🔍 步骤5: 生成查询 (目标索引: ${targetIndex})...`)
    const queryData = client.generateQuery(targetIndex)
    console.log(`查询大小: ${queryData.byteLength} 字节`)
    
    // 6. 发送查询到服务器
    console.log('\n📡 步骤6: 发送 PIR 查询...')
    const queryRes = await fetch(`${BASE_URL}/query`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/octet-stream',
        'Authorization': `Bearer ${token}`
      },
      body: queryData
    })
    
    if (!queryRes.ok) {
      throw new Error(`查询失败: ${queryRes.status}`)
    }
    
    const encryptedData = await queryRes.arrayBuffer()
    console.log(`✅ 收到响应: ${encryptedData.byteLength} 字节`)
    
    // 7. 解密
    console.log('\n🔓 步骤7: 解密响应...')
    const plainData = client.decryptResponse(encryptedData, queryData, targetIndex)
    const decodedText = new TextDecoder('utf-8').decode(new Uint8Array(plainData))
    
    console.log('\n' + '='.repeat(70))
    console.log('📋 查询结果:')
    console.log('='.repeat(70))
    console.log(decodedText)
    
    // 尝试解析 JSON
    try {
      const record = JSON.parse(decodedText)
      console.log('\n✅ JSON 解析成功:')
      console.log(`  病历号: ${record.record_id}`)
      console.log(`  患者: ${record.name}`)
      console.log(`  性别: ${record.gender === 'M' ? '男' : '女'}`)
      console.log(`  年龄: ${record.age}`)
      console.log(`  科室: ${record.department}`)
      console.log(`  诊断: ${record.diagnosis}`)
      console.log(`  入院日期: ${record.admission_date}`)
      console.log(`  主治医生: ${record.doctor_id}`)
    } catch (e) {
      console.log(`\n⚠️ JSON 解析失败: ${e.message}`)
    }
    
    console.log('\n' + '='.repeat(70))
    console.log('✅ PIR 测试完成')
    
  } catch (err) {
    console.error('❌ 测试失败:', err.message)
    if (err.response) {
      console.error('响应状态:', err.response.status)
      console.error('响应数据:', err.response.data)
    }
  }
}

// ========================
// 运行测试
// ========================
const targetIndex = parseInt(process.argv[2]) || 0
console.log(`测试目标索引: ${targetIndex}`)
testPIR(targetIndex).catch(console.error)