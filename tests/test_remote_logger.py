import os
import sys
import time

# 添加项目根目录到路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# 设置远程服务器 IP 和端口
# 你也可以通过环境变量设置：$env:YIBO_LOG_IP="47.109.184.107"
os.environ['YIBO_LOG_IP'] = '47.109.184.107'
os.environ['YIBO_LOG_PORT'] = '9000'

from src.core.logger import get_logger

def test_remote_connection():
    print(f"正在测试远程连接: {os.environ['YIBO_LOG_IP']}:{os.environ['YIBO_LOG_PORT']}")
    logger = get_logger()
    
    try:
        # 1. 发送一些普通日志
        print("发送常规测试日志...")
        logger.info("Remote Test: Starting heavy load test...")
        
        # 2. 发送大量日志以冲破服务端 4KB 缓冲区
        print("发送大量日志 (100条) 以触发服务端磁盘写入...")
        for i in range(100):
            # 构造一个稍微大点的内容 (约 100 字节)
            msg = f"Bulk Log Message #{i:03d}: " + "A" * 80
            logger.info(msg)
            # 稍微停顿一下，避免本地队列瞬间塞满，也让网络传输稳一点
            if i % 20 == 0:
                time.sleep(0.1)
        
        # 3. 发送一个带有二进制大块数据的日志
        print("发送一个大块 Dump 数据 (2KB)...")
        large_data = b'X' * 2048
        logger.dump("Large Payload Test", large_data)
        
        # 等待发送完成
        print("等待 ACK 和传输完成 (约 5 秒)...")
        time.sleep(5)
        
        print("测试完成。现在体量应该已经超过 4KB，请检查服务端磁盘文件。")
    except Exception as e:
        print(f"测试过程中出现错误: {e}")
    finally:
        logger.stop()

if __name__ == "__main__":
    test_remote_connection()
