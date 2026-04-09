# # backend/core/piano_preprocess.py
# import numpy as np
# import json
# import os
# import math
# import secrets
# from Crypto.Cipher import AES
# import struct

# class PianoPreprocess:
#     """PIANO 离线预处理"""
    
#     def __init__(self, db_path, npy_path, meta_path):
#         self.db_path = db_path
#         self.npy_path = npy_path
#         self.meta_path = meta_path
#         self.db_matrix = None
#         self.db_size = 0
#         self.block_size = 0
#         self.chunk_size = 0
#         self.num_chunks = 0
        
#     # def load_db(self):
#     #     """加载数据库"""
#     #     self.db_matrix = np.load(self.npy_path)
#     #     self.db_size = len(self.db_matrix)
#     #     self.block_size = self.db_matrix.shape[1]
#     #     self.chunk_size = math.ceil(math.sqrt(self.db_size))
#     #     self.num_chunks = math.ceil(self.db_size / self.chunk_size)
#     #     print(f"[预处理] 数据库: {self.db_size} 条记录, 块大小 {self.block_size}")
#     #     print(f"[预处理] 分块: {self.num_chunks} 个块, 每块 {self.chunk_size} 条")
    
#     # 在 load_db 中，使用当前实际记录数
#     def load_db(self):
#         self.db_matrix = np.load(self.npy_path)
#         self.db_size = len(self.db_matrix)  # 当前实际条数
#         self.block_size = self.db_matrix.shape[1]
#         self.chunk_size = math.ceil(math.sqrt(self.db_size))
#         self.num_chunks = math.ceil(self.db_size / self.chunk_size)
#         print(f"[预处理] 当前数据库: {self.db_size} 条记录, chunk_size={self.chunk_size}, num_chunks={self.num_chunks}")

#     def generate_random_set(self, key):
#         """从 PRF key 生成随机集合 S (必须与前端 piano.js 的 getSetFromKey 保持 100% 一致)"""
#         indices =[]
#         for chunk in range(self.num_chunks):
#             hash_val = 0
#             for byte in key:
#                 # 对应 JS 的: hash = (hash * 131 + (keyBytes[i] ^ chunk)) >>> 0
#                 hash_val = (hash_val * 131 + (byte ^ chunk)) & 0xFFFFFFFF
            
#             offset = hash_val % self.chunk_size
#             idx = chunk * self.chunk_size + offset
            
#             if idx >= self.db_size:
#                 idx = self.db_size - 1
                
#             indices.append(idx)
#         return indices
    
#     def compute_parity(self, indices):
#         """计算集合的奇偶校验和"""
#         result = np.zeros(self.block_size, dtype=np.uint8)
#         for idx in indices:
#             result = np.bitwise_xor(result, self.db_matrix[idx])
#         return result.tobytes()
    
#     def compute_parity_without_chunk(self, indices, exclude_chunk):
#         """计算排除某个块后的奇偶校验和"""
#         result = np.zeros(self.block_size, dtype=np.uint8)
#         for i, idx in enumerate(indices):
#             if i == exclude_chunk:
#                 continue
#             result = np.bitwise_xor(result, self.db_matrix[idx])
#         return result.tobytes()
    
#     def build_tables(self):
#         """
#         构建主表、备份表和替换条目
#         论文参数: M₁ = √n·lnκ·α(κ), M₂ = 3·lnκ·α(κ)
#         这里取 α(κ) = 2, lnκ ≈ 3.7, 所以 M₁ = √n * 7.4 ≈ 740, M₂ = 22
#         """
#         import math
        
#         # 安全参数
#         kappa = 40  # 统计安全参数
#         alpha = 2   # 超常数函数
        
#         M1 = int(math.sqrt(self.db_size) * math.log(kappa) * alpha)
#         M2 = int(3 * math.log(kappa) * alpha)
        
#         print(f"[预处理] 参数: M1={M1}, M2={M2}")
        
#         # 主表
#         primary_table = []
        
#         # 备份表: 每个块一个列表
#         backup_table = {j: [] for j in range(self.num_chunks)}
        
#         # 替换条目: 每个块一个列表
#         replacement_entries = {j: [] for j in range(self.num_chunks)}
        
#         print("[预处理] 生成主表...")
#         for i in range(M1):
#             key = secrets.token_bytes(16)
#             indices = self.generate_random_set(key)
#             parity = self.compute_parity(indices)
#             primary_table.append({
#                 'key': key.hex(),
#                 'parity': parity,
#                 'indices': indices
#             })
#             if (i + 1) % 100 == 0:
#                 print(f"  已生成 {i+1}/{M1} 条")
        
#         print("[预处理] 生成备份表和替换条目...")
#         for chunk in range(self.num_chunks):
#             # 替换条目: 随机索引及其值
#             for _ in range(M2):
#                 offset = secrets.randbelow(self.chunk_size)
#                 idx = chunk * self.chunk_size + offset
#                 if idx >= self.db_size:
#                     idx = self.db_size - 1
#                 replacement_entries[chunk].append({
#                     'index': idx,
#                     'value': self.db_matrix[idx].tobytes()
#                 })
            
#             # 备份表: 随机集合及其排除当前块的奇偶校验
#             for _ in range(M2):
#                 key = secrets.token_bytes(16)
#                 indices = self.generate_random_set(key)
#                 parity = self.compute_parity_without_chunk(indices, chunk)
#                 backup_table[chunk].append({
#                     'key': key.hex(),
#                     'parity': parity,
#                     'indices': indices
#                 })
            
#             if (chunk + 1) % 20 == 0:
#                 print(f"  已处理 {chunk+1}/{self.num_chunks} 个块")
        
#         return {
#             'primary_table': primary_table,
#             'backup_table': backup_table,
#             'replacement_entries': replacement_entries,
#             'params': {
#                 'db_size': self.db_size,
#                 'block_size': self.block_size,
#                 'chunk_size': self.chunk_size,
#                 'num_chunks': self.num_chunks,
#                 'M1': M1,
#                 'M2': M2
#             }
#         }
    
#     def save_tables(self, output_path):
#         """保存预处理结果到文件"""
#         tables = self.build_tables()
        
#         # 转换 bytes 为 base64 以便 JSON 存储
#         for item in tables['primary_table']:
#             item['parity'] = item['parity'].hex()
        
#         for chunk in tables['backup_table']:
#             for item in tables['backup_table'][chunk]:
#                 item['parity'] = item['parity'].hex()
        
#         for chunk in tables['replacement_entries']:
#             for item in tables['replacement_entries'][chunk]:
#                 item['value'] = item['value'].hex()
        
#         with open(output_path, 'w', encoding='utf-8') as f:
#             json.dump(tables, f, ensure_ascii=False, indent=2)
        
#         print(f"[预处理] 保存到 {output_path}")
#         return tables


# if __name__ == "__main__":
#     BASE_DIR = os.path.dirname(os.path.dirname(__file__))
#     NPY_PATH = os.path.join(BASE_DIR, 'storage', 'db.npy')
#     OUTPUT_PATH = os.path.join(BASE_DIR, 'storage', 'piano_tables.json')
    
#     preprocess = PianoPreprocess(NPY_PATH, NPY_PATH, None)
#     preprocess.load_db()
#     preprocess.save_tables(OUTPUT_PATH)

# backend/core/piano_preprocess.py
import numpy as np
import json
import os
import math
import secrets
from Crypto.Cipher import AES
import struct

class PianoPreprocess:
    """完整 PIANO 协议离线预处理"""
    
    def __init__(self, db_path, npy_path, meta_path):
        self.db_path = db_path
        self.npy_path = npy_path
        self.meta_path = meta_path
        self.db_matrix = None
        self.db_size = 0
        self.block_size = 0
        self.chunk_size = 0
        self.num_chunks = 0
        
    def load_db(self):
        """加载数据库"""
        self.db_matrix = np.load(self.npy_path)
        self.db_size = len(self.db_matrix)
        self.block_size = self.db_matrix.shape[1]
        self.chunk_size = 100  # 固定分块，与前端保持一致
        self.num_chunks = math.ceil(self.db_size / self.chunk_size)
        print(f"[预处理] 数据库: {self.db_size} 条记录")
        print(f"[预处理] chunk_size={self.chunk_size}, num_chunks={self.num_chunks}")
        print(f"[预处理] block_size={self.block_size} 字节")
    
    def generate_random_set(self, key):
        """从 PRF key 生成随机集合 S（与前端 getSetFromKey 一致）"""
        indices = []
        for chunk in range(self.num_chunks):
            hash_val = 0
            for byte in key:
                hash_val = (hash_val * 131 + (byte ^ chunk)) & 0xFFFFFFFF
            offset = hash_val % self.chunk_size
            idx = chunk * self.chunk_size + offset
            if idx >= self.db_size:
                idx = self.db_size - 1
            indices.append(idx)
        return indices
    
    def compute_parity(self, indices):
        """计算集合的奇偶校验和"""
        result = np.zeros(self.block_size, dtype=np.uint8)
        for idx in indices:
            result = np.bitwise_xor(result, self.db_matrix[idx])
        return result.tobytes()
    
    def compute_parity_without_chunk(self, indices, exclude_chunk):
        """计算排除某个块后的奇偶校验和"""
        result = np.zeros(self.block_size, dtype=np.uint8)
        for i, idx in enumerate(indices):
            if i == exclude_chunk:
                continue
            result = np.bitwise_xor(result, self.db_matrix[idx])
        return result.tobytes()
    
    def build_tables(self):
        """
        构建主表、备份表和替换条目
        论文参数: M₁ = √n·lnκ·α(κ), M₂ = 3·lnκ·α(κ)
        """
        import math
        
        kappa = 40
        alpha = 4  # 增大到4，确保主表覆盖概率足够高
        
        # 主表大小：√n * lnκ * α
        M1 = int(math.sqrt(self.db_size) * math.log(kappa) * alpha)
        # 备份表大小
        M2 = int(3 * math.log(kappa) * alpha)
        
        print(f"[预处理] 参数: M1={M1}, M2={M2}")
        print(f"[预处理] 预期命中概率: {M1 / self.num_chunks:.2f}")
        
        primary_table = []
        backup_table = {j: [] for j in range(self.num_chunks)}
        replacement_entries = {j: [] for j in range(self.num_chunks)}
        
        print("[预处理] 生成主表...")
        for i in range(M1):
            key = secrets.token_bytes(16)
            indices = self.generate_random_set(key)
            parity = self.compute_parity(indices)
            primary_table.append({
                'key': key.hex(),
                'parity': parity.hex(),
                'indices': indices
            })
            if (i + 1) % 500 == 0:
                print(f"  已生成 {i+1}/{M1} 条")
        
        print("[预处理] 生成备份表和替换条目...")
        for chunk in range(self.num_chunks):
            # 替换条目
            for _ in range(M2):
                offset = secrets.randbelow(self.chunk_size)
                idx = chunk * self.chunk_size + offset
                if idx >= self.db_size:
                    idx = self.db_size - 1
                replacement_entries[chunk].append({
                    'index': idx,
                    'value': self.db_matrix[idx].tobytes().hex()
                })
            
            # 备份表
            for _ in range(M2):
                key = secrets.token_bytes(16)
                indices = self.generate_random_set(key)
                parity = self.compute_parity_without_chunk(indices, chunk)
                backup_table[chunk].append({
                    'key': key.hex(),
                    'parity': parity.hex(),
                    'indices': indices
                })
            
            if (chunk + 1) % 20 == 0:
                print(f"  已处理 {chunk+1}/{self.num_chunks} 个块")
        
        return {
            'primary_table': primary_table,
            'backup_table': backup_table,
            'replacement_entries': replacement_entries,
            'params': {
                'db_size': self.db_size,
                'block_size': self.block_size,
                'chunk_size': self.chunk_size,
                'num_chunks': self.num_chunks,
                'M1': M1,
                'M2': M2
            }
        }
    
    def save_tables(self, output_path):
        """保存预处理结果"""
        tables = self.build_tables()
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(tables, f, ensure_ascii=False, indent=2)
        
        print(f"[预处理] 保存到 {output_path}")
        print(f"[预处理] 主表大小: {len(tables['primary_table'])}")
        print(f"[预处理] 备份表条目: {sum(len(v) for v in tables['backup_table'].values())}")
        print(f"[预处理] 替换条目: {sum(len(v) for v in tables['replacement_entries'].values())}")
        return tables


if __name__ == "__main__":
    BASE_DIR = os.path.dirname(os.path.dirname(__file__))
    NPY_PATH = os.path.join(BASE_DIR, 'storage', 'db.npy')
    OUTPUT_PATH = os.path.join(BASE_DIR, 'storage', 'piano_tables.json')
    
    if not os.path.exists(NPY_PATH):
        print(f"错误: {NPY_PATH} 不存在，请先运行 data_engine.preprocessor")
        exit(1)
    
    preprocess = PianoPreprocess(NPY_PATH, NPY_PATH, None)
    preprocess.load_db()
    preprocess.save_tables(OUTPUT_PATH)
    BASE_DIR = os.path.dirname(os.path.dirname(__file__))
    NPY_PATH = os.path.join(BASE_DIR, 'storage', 'db.npy')
    OUTPUT_PATH = os.path.join(BASE_DIR, 'storage', 'piano_tables.json')
    
    preprocess = PianoPreprocess(NPY_PATH, NPY_PATH, None)
    preprocess.load_db()
    preprocess.save_tables(OUTPUT_PATH)