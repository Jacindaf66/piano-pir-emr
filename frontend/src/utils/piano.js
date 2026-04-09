// frontend/src/utils/piano.js

function hexToBytes(hex) {
  const bytes = new Uint8Array(hex.length / 2)
  for (let i = 0; i < hex.length; i += 2) {
    bytes[i / 2] = parseInt(hex.substr(i, 2), 16)
  }
  return bytes
}

// PRF：与后端算法保持一致
function getSetFromKey(keyBytes, dbSize, chunkSize, numChunks) {
  const indices = []
  for (let chunk = 0; chunk < numChunks; chunk++) {
    let hash = 0
    for (let i = 0; i < keyBytes.length; i++) {
      hash = (hash * 131 + (keyBytes[i] ^ chunk)) >>> 0
    }
    const offset = hash % chunkSize
    let idx = chunk * chunkSize + offset
    if (idx >= dbSize) idx = dbSize - 1
    indices.push(idx)
  }
  return indices
}

function testMembership(key, index, dbSize, chunkSize, numChunks) {
  const targetChunk = Math.floor(index / chunkSize)
  const indices = getSetFromKey(key, dbSize, chunkSize, numChunks)
  return indices[targetChunk] === index
}

export class PianoClient {
  constructor(dbSize, blockSize, pianoTables = null) {
    // 优先使用预处理表的参数
    if (pianoTables && pianoTables.params) {
      this.dbSize = pianoTables.params.db_size;
      this.chunkSize = pianoTables.params.chunk_size;
      this.numChunks = pianoTables.params.num_chunks;
      this.blockSize = pianoTables.params.block_size;
    } else {
      this.dbSize = dbSize;
      this.blockSize = blockSize;
      this.chunkSize = Math.ceil(Math.sqrt(dbSize));
      this.numChunks = Math.ceil(dbSize / this.chunkSize);
    }
    
    // 当前总数据量（用于边界检查）
    this.currentSize = this.dbSize;
    
    // 预处理表
    this.primaryTable = pianoTables?.primary_table || []
    this.backupTable = pianoTables?.backup_table || {}
    this.replacementEntries = pianoTables?.replacement_entries || {}
    
    // 消耗状态
    this.consumedPrimary = new Set()
    this.consumedReplacement = {}
    this.consumedBackup = {}
    
    for (let i = 0; i < this.numChunks; i++) {
      this.consumedReplacement[i] = 0
      this.consumedBackup[i] = 0
      if (!this.replacementEntries[i]) this.replacementEntries[i] = []
      if (!this.backupTable[i]) this.backupTable[i] = []
    }
    
    this.currentQuery = null
    
    console.log('[PianoClient] 初始化完成')
    console.log(`  dbSize: ${this.dbSize}, blockSize: ${this.blockSize}`)
    console.log(`  chunkSize: ${this.chunkSize}, numChunks: ${this.numChunks}`)
    console.log(`  主表大小: ${this.primaryTable.length}`)
  }

  updateCurrentSize(newSize) {
    if (newSize === this.currentSize) return
    this.currentSize = newSize
    console.log(`[PianoClient] 更新当前总数据量: ${this.currentSize}`)
  }

  generateQuery(targetIndex) {
    const targetChunk = Math.floor(targetIndex / this.chunkSize)
    console.log(`[PianoClient] 生成查询，目标索引: ${targetIndex} (块${targetChunk})`)
    
    // 1. 找主表条目
    let foundEntry = null
    let foundIdx = null
    
    for (let i = 0; i < this.primaryTable.length; i++) {
      if (this.consumedPrimary.has(i)) continue
      const entry = this.primaryTable[i]
      const key = hexToBytes(entry.key)
      if (testMembership(key, targetIndex, this.dbSize, this.chunkSize, this.numChunks)) {
        foundEntry = entry
        foundIdx = i
        break
      }
    }
    
    if (!foundEntry) {
      console.warn('[PianoClient] 未找到主表条目，使用降级方案')
      const fallbackQuery = new Uint8Array(4)
      const view = new DataView(fallbackQuery.buffer)
      view.setUint32(0, targetIndex, true)
      this.currentQuery = { isFallback: true, targetIndex }
      return fallbackQuery.buffer
    }
    
    // 2. 取替换条目
    let replacement = null
    if (this.consumedReplacement[targetChunk] < this.replacementEntries[targetChunk]?.length) {
      replacement = this.replacementEntries[targetChunk][this.consumedReplacement[targetChunk]]
      this.consumedReplacement[targetChunk]++
    }
    
    // 3. 生成集合 S
    const key = hexToBytes(foundEntry.key)
    const S = getSetFromKey(key, this.dbSize, this.chunkSize, this.numChunks)
    
    // 4. 生成编辑后的集合 S'
    const S_prime = [...S]
    if (replacement) {
      S_prime[targetChunk] = replacement.index
    }
    
    // 5. 保存查询信息
    this.currentQuery = {
      isFallback: false,
      targetChunk: targetChunk,
      targetIndex: targetIndex,
      parity: hexToBytes(foundEntry.parity),
      replacementValue: replacement ? hexToBytes(replacement.value) : null,
      S_prime: S_prime
    }
    
    this.consumedPrimary.add(foundIdx)
    
    // 6. 刷新主表
    if (this.consumedBackup[targetChunk] < this.backupTable[targetChunk]?.length) {
      const backup = this.backupTable[targetChunk][this.consumedBackup[targetChunk]]
      this.consumedBackup[targetChunk]++
      this.primaryTable.push({
        key: backup.key,
        parity: backup.parity
      })
    }
    
    // 7. 编码偏移向量
    const queryBytes = new Uint8Array((this.numChunks - 1) * 4)
    let pos = 0
    for (let i = 0; i < this.numChunks; i++) {
      if (i === targetChunk) continue
      const offset = S_prime[i] % this.chunkSize
      new DataView(queryBytes.buffer).setUint32(pos, offset, true)
      pos += 4
    }
    
    console.log(`[PianoClient] 查询大小: ${queryBytes.length} 字节`)
    return queryBytes.buffer
  }

  decryptResponse(encryptedResponse) {
    console.log(`[PianoClient] 解密响应，大小: ${encryptedResponse.byteLength} 字节`)
    
    if (this.currentQuery?.isFallback) {
      console.log('[PianoClient] 降级模式，直接返回')
      return encryptedResponse
    }
    
    if (!this.currentQuery) {
      return encryptedResponse
    }
    
    const query = this.currentQuery
    const blockSize = this.blockSize
    
    // 根据实际响应大小计算块数
    const actualNumChunks = encryptedResponse.byteLength / blockSize
    console.log(`实际块数: ${actualNumChunks}, 期望块数: ${this.numChunks}`)
    
    // 解析 q 列表
    const qResults = []
    for (let i = 0; i < actualNumChunks; i++) {
      const start = i * blockSize
      qResults.push(new Uint8Array(encryptedResponse.slice(start, start + blockSize)))
    }
    
    // 目标块的 q
    const targetChunk = query.targetChunk
    const q = targetChunk < qResults.length ? qResults[targetChunk] : qResults[0]
    
    // result = q ⊕ parity
    const parity = query.parity
    let result = new Uint8Array(blockSize)
    for (let i = 0; i < blockSize; i++) {
      result[i] = q[i] ^ parity[i]
    }
    
    console.log('[PianoClient] 解密完成')
    return result.buffer
  }
}