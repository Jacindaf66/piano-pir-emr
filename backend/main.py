# 文件位置: backend/main.py
import sys
import os
import numpy as np

# 将当前目录加入路径，确保能导入 core 包
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from core.piano_core import PianoServer, PianoClient

def main():
    print("=== 阶段一：Piano 算法原型验证启动 ===")
    
    # 1. 准备数据 (Data Engineering 简易版)
    # 模拟 100 条数据，每条数据只是一个简单的数字 (转为 16字节 bytes)
    # 例如：第 5 条数据的内容就是 b'......5'
    DB_SIZE = 100
    BLOCK_SIZE = 16 # 16字节
    
    raw_data = []
    for i in range(DB_SIZE):
        # 创建一个内容为 i 的数据块
        # 'I' 表示 unsigned int, 4字节，我们补零到 16字节
        num_bytes = int(i).to_bytes(BLOCK_SIZE, byteorder='little') 
        raw_data.append(num_bytes)
    
    print(f"步骤1: 数据生成完毕，共 {DB_SIZE} 条，每条 {BLOCK_SIZE} 字节。")

    # 2. 初始化 Server
    server = PianoServer(raw_data)
    print("步骤2: Server 初始化完毕，数据已加载。")

    # 3. 初始化 Client
    client = PianoClient(DB_SIZE, BLOCK_SIZE)
    # 注入“作弊”缓存 (假装 Client 之前已经下载过很多数据，拥有所有 Hint)
    client.set_mock_hints(raw_data)
    print("步骤3: Client 初始化完毕，Hint 已预热。")

    # 4. 发起查询测试
    TARGET_INDEX = 5
    print(f"\n---> 开始模拟查询: 目标 Index = {TARGET_INDEX}")
    print(f"     目标真实值 (Int): {TARGET_INDEX}")
    print(f"     目标真实值 (Hex): {raw_data[TARGET_INDEX].hex()}")
    
    # 调用核心逻辑
    decrypted_bytes = client.generate_query_and_decrypt(TARGET_INDEX, server)
    
    # 5. 验证结果
    decrypted_int = int.from_bytes(decrypted_bytes, byteorder='little')
    print(f"\n---> 查询结束")
    print(f"     解密后结果 (Hex): {decrypted_bytes.hex()}")
    print(f"     解密后结果 (Int): {decrypted_int}")

    # 断言测试
    if decrypted_int == TARGET_INDEX:
        print("\n✅ 成功！算法原型逻辑验证通过！")
        print("   原理证明：Client 发送了一个随机 Seed，Server 根本不知道 Client 真正想要的是其中的哪一个。")
        print("   但 Client 利用本地的 Hint 成功消除了其他数据的干扰，还原了目标数据。")
    else:
        print("\n❌ 失败！解密数据不匹配。")

if __name__ == "__main__":
    main()