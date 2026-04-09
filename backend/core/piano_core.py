# # backend/core/piano_core.py

# import numpy as np
# import math
# import struct


# class PianoServer:
#     """真正的 Piano PIR 服务器"""

#     def __init__(self, data_list: list):
#         self.data_matrix = [np.frombuffer(d, dtype=np.uint8) for d in data_list]
#         self.db_size = len(data_list)
#         self.block_size = len(self.data_matrix[0])

#         self.chunk_size = math.ceil(math.sqrt(self.db_size))
#         self.num_chunks = math.ceil(self.db_size / self.chunk_size)

#         print(f"[PianoServer] 初始化: {self.db_size} 条")
#         print(f"[PianoServer] chunk_size={self.chunk_size}, num_chunks={self.num_chunks}")

#     def process_query(self, query_bytes: bytes) -> bytes:
#         """
#         输入：每个 chunk 一个 offset（除了 target chunk）
#         输出：每个 chunk 一个 q_j（block）
#         """

#         offsets = []
#         num_offsets = len(query_bytes) // 4

#         for i in range(num_offsets):
#             offset = struct.unpack('<I', query_bytes[i*4:(i+1)*4])[0]
#             offsets.append(offset)

#         if len(offsets) != self.num_chunks - 1:
#             print("❌ offset 数量错误")
#             return b''

#         print(f"[PianoServer] 收到 offsets: {len(offsets)}")

#         result_blocks = []

#         offset_idx = 0

#         for chunk in range(self.num_chunks):
#             xor_result = np.zeros(self.block_size, dtype=np.uint8)

#             for other_chunk in range(self.num_chunks):
#                 if other_chunk == chunk:
#                     continue

#                 offset = offsets[offset_idx]
#                 idx = other_chunk * self.chunk_size + offset

#                 if idx >= self.db_size:
#                     idx = self.db_size - 1

#                 xor_result ^= self.data_matrix[idx]

#                 offset_idx += 1

#                 if offset_idx >= len(offsets):
#                     offset_idx = 0  # 防止越界（循环用）

#             result_blocks.append(xor_result)

#         # 拼接所有 q_j
#         return b''.join([b.tobytes() for b in result_blocks])




# import numpy as np
# import math
# import struct
# import threading

# class PianoServer:
#     """
#     完整的 Piano PIR 服务器
#     支持动态增量数据，且强制所有查询（含新病历）均通过 PIR 异或逻辑实现。
#     """

#     def __init__(self, data_list: list):
#         # 1. 基础数据加载
#         self.data_matrix = [np.frombuffer(d, dtype=np.uint8) for d in data_list]
#         self.db_size = len(data_list)
#         # 获取块大小（通常为 8192）
#         self.block_size = len(self.data_matrix[0]) if self.data_matrix else 8192

#         # 【核心修复】锁定分块几何结构
#         # 即使数据增加，chunk_size 也必须固定为 sqrt(10000) = 100
#         # 这样 idx = k * chunk_size + offset 的计算方式才不会错位
#         self.chunk_size = math.ceil(math.sqrt(self.db_size)) # 100
#         self.num_chunks = math.ceil(self.db_size / self.chunk_size) # 100
        
#         # 增量数据存储
#         self.new_records = []
#         self.new_records_count = 0
#         self.lock = threading.Lock()
        
#         print(f"[PianoServer] 初始化完成:")
#         print(f" - 基准数据: {self.db_size} 条")
#         print(f" - 块大小 (BlockSize): {self.block_size}")
#         print(f" - 协议宽度 (ChunkSize): {self.chunk_size}")
#         print(f" - 协议块数 (NumChunks): {self.num_chunks}")

#     def add_record(self, record_bytes: bytes):
#         """线程安全地动态添加新记录到增量池"""
#         with self.lock:
#             if len(record_bytes) < self.block_size:
#                 record_bytes = record_bytes + b'\x00' * (self.block_size - len(record_bytes))
#             else:
#                 record_bytes = record_bytes[:self.block_size]
            
#             self.new_records.append(np.frombuffer(record_bytes, dtype=np.uint8))
#             self.new_records_count += 1
#             print(f"[PianoServer] 增量数据已同步。总记录数: {self.db_size + self.new_records_count}")

#     def _get_data_by_index(self, idx: int) -> np.ndarray:
#         """
#         根据逻辑索引获取数据块
#         此函数透明地处理基础数据和追加的增量数据
#         """
#         if idx < self.db_size:
#             return self.data_matrix[idx]
#         else:
#             new_idx = idx - self.db_size
#             if new_idx < self.new_records_count:
#                 return self.new_records[new_idx]
#             else:
#                 # 如果查询索引越界，返回全0块（异或单位元），不影响最终结果
#                 return np.zeros(self.block_size, dtype=np.uint8)

#     def process_query(self, query_bytes: bytes) -> bytes:
#         """
#         执行 PIR 查询。
#         无论查询的是 index 5 还是 index 10000，都必须走这个异或流程。
#         """
#         # 1. 解析前端发来的偏移量 (Offsets)
#         # 每个偏移量 4 字节，对应除了目标块以外的其他所有块
#         num_offsets = len(query_bytes) // 4
#         offsets = struct.unpack(f'<{num_offsets}I', query_bytes)

#         # 锁死返回 100 个块，确保与前端 piano.js 期待的长度一致
#         expected_num_chunks = self.num_chunks 
#         result_blocks = []

#         # 获取当前总数据量，防止越界
#         total_current_size = self.db_size + self.new_records_count

#         # 2. 核心 PIR 异或逻辑
#         # 对应每一个响应块 q_j
#         for j in range(expected_num_chunks):
#             # 初始化一个空白的异或结果
#             xor_result = np.zeros(self.block_size, dtype=np.uint8)
            
#             # offset_ptr 用于遍历前端传来的偏移量数组
#             offset_ptr = 0
            
#             # 遍历所有的分块 k
#             for k in range(expected_num_chunks):
#                 # 按照 PIR 协议，跳过当前响应块对应的分块
#                 if k == j:
#                     continue
                
#                 # 获取该块的偏移量。如果前端没传够（理论上不会），补0
#                 off = offsets[offset_ptr] if offset_ptr < len(offsets) else 0
                
#                 # 【关键修复】计算物理索引
#                 # 必须使用固定的 self.chunk_size (100)，这样无论数据增加多少，
#                 # 逻辑分块的起始位置永远是 0, 100, 200... 
#                 idx = k * self.chunk_size + off
                
#                 # 只有当索引在当前实际数据范围内时才参与异或
#                 if idx < total_current_size:
#                     xor_result ^= self._get_data_by_index(idx)
                
#                 offset_ptr += 1

#             # 收集该块的异或结果
#             result_blocks.append(xor_result.tobytes())

#         # 拼接并返回二进制流 (大小应为 100 * 8192 = 819200)

#         # ========== 添加调试日志 ==========
#         # 只打印前3个块，避免刷屏
#         if j < 5:
#             # 打印前50字节
#             preview = xor_result.tobytes()[:50]
#             print(f"[PianoServer] q_{j} 前50字节: {preview}")
#         # ================================

#         return b''.join(result_blocks)

#     def get_current_total_count(self):
#         """返回实时总记录数"""
#         with self.lock:
#             return self.db_size + self.new_records_count

# backend/core/piano_core.py
import numpy as np
import math
import struct
import threading

class PianoServer:
    def __init__(self, data_list: list, chunk_size: int = 100):
        """
        data_list: 二进制数据列表
        chunk_size: 固定块大小，与预处理表一致（默认100）
        """
        self.data_matrix = [np.frombuffer(d, dtype=np.uint8) for d in data_list]
        self.db_size = len(data_list)
        self.block_size = len(self.data_matrix[0]) if self.data_matrix else 8192
        
        # 固定分块参数，与预处理表保持一致
        self.chunk_size = chunk_size
        self.num_chunks = math.ceil(self.db_size / self.chunk_size)
        
        # 增量数据
        self.new_records = []
        self.new_records_count = 0
        self.lock = threading.Lock()
        
        print(f"[PianoServer] 初始化完成")
        print(f"  基础数据: {self.db_size} 条")
        print(f"  块大小: {self.chunk_size}, 块数: {self.num_chunks}")
        print(f"  数据块大小: {self.block_size} 字节")

    def add_record(self, record_bytes: bytes):
        """动态添加新记录"""
        with self.lock:
            if len(record_bytes) < self.block_size:
                record_bytes = record_bytes + b'\x00' * (self.block_size - len(record_bytes))
            elif len(record_bytes) > self.block_size:
                record_bytes = record_bytes[:self.block_size]
            
            self.new_records.append(np.frombuffer(record_bytes, dtype=np.uint8))
            self.new_records_count += 1
            print(f"[PianoServer] 添加新记录，当前增量: {self.new_records_count}")

    def _get_data_by_index(self, idx: int) -> np.ndarray:
        """根据索引获取数据"""
        if idx < self.db_size:
            return self.data_matrix[idx]
        else:
            new_idx = idx - self.db_size
            if new_idx < self.new_records_count:
                return self.new_records[new_idx]
            return np.zeros(self.block_size, dtype=np.uint8)

    def process_query(self, query_bytes: bytes) -> bytes:
        """
        执行 PIR 查询
        输入：偏移向量（每个块一个偏移，共 num_chunks-1 个）
        输出：所有块的异或结果（共 num_chunks 个块）
        """
        # 使用当前总数据量计算块参数
        total_size = self.db_size + self.new_records_count
        num_chunks = math.ceil(total_size / self.chunk_size)
        
        # 解析偏移
        expected_offsets = num_chunks - 1
        actual_offsets = len(query_bytes) // 4
        
        if actual_offsets != expected_offsets:
            print(f"[PianoServer] 偏移数量不匹配: 期望 {expected_offsets}, 实际 {actual_offsets}")
            # 如果数量不匹配，尝试补齐或截断
            if actual_offsets < expected_offsets:
                # 补齐为0
                query_bytes = query_bytes + b'\x00' * (expected_offsets - actual_offsets) * 4
            else:
                query_bytes = query_bytes[:expected_offsets * 4]
        
        offsets = []
        for i in range(expected_offsets):
            offset = struct.unpack('<I', query_bytes[i*4:(i+1)*4])[0]
            offsets.append(offset % self.chunk_size)
        
        # 计算每个块的异或结果
        result_blocks = []
        
        for target_chunk in range(num_chunks):
            xor_result = np.zeros(self.block_size, dtype=np.uint8)
            offset_idx = 0
            
            for other_chunk in range(num_chunks):
                if other_chunk == target_chunk:
                    continue
                
                off = offsets[offset_idx] if offset_idx < len(offsets) else 0
                idx = other_chunk * self.chunk_size + off
                
                if idx < total_size:
                    xor_result ^= self._get_data_by_index(idx)
                
                offset_idx += 1
            
            result_blocks.append(xor_result.tobytes())
        
        return b''.join(result_blocks)

    def get_current_total_count(self):
        """获取当前总记录数"""
        with self.lock:
            return self.db_size + self.new_records_count