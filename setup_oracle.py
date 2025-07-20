#!/usr/bin/env python3
"""
InvestCloud Customer Churn Prediction Project - Oracle Environment Setup
帮助用户配置Oracle Instant Client和数据库连接环境
"""

import os
import sys
import platform
import urllib.request
import zipfile
from pathlib import Path

def print_banner():
    """打印横幅"""
    print("=" * 70)
    print("InvestCloud 客户流失预测项目 - Oracle环境配置")
    print("=" * 70)
    print()

def check_python_version():
    """检查Python版本"""
    print("🔍 检查Python版本...")
    if sys.version_info < (3, 8):
        print("❌ 需要Python 3.8或更高版本")
        print(f"   当前版本: {sys.version}")
        return False
    else:
        print(f"✅ Python版本: {sys.version}")
        return True

def install_dependencies():
    """安装Python依赖包"""
    print("\n📦 安装Python依赖包...")
    
    try:
        import subprocess
        
        # 安装oracledb
        print("安装 oracledb...")
        result = subprocess.run([sys.executable, "-m", "pip", "install", "oracledb>=1.4.0"], 
                              capture_output=True, text=True)
        if result.returncode == 0:
            print("✅ oracledb 安装成功")
        else:
            print(f"❌ oracledb 安装失败: {result.stderr}")
            return False
        
        # 安装其他依赖
        print("安装其他依赖包...")
        result = subprocess.run([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"], 
                              capture_output=True, text=True)
        if result.returncode == 0:
            print("✅ 所有依赖包安装成功")
        else:
            print(f"⚠️ 部分依赖包安装可能有问题: {result.stderr}")
        
        return True
        
    except Exception as e:
        print(f"❌ 依赖包安装失败: {e}")
        return False

def check_oracle_client():
    """检查Oracle Instant Client"""
    print("\n🔍 检查Oracle Instant Client...")
    
    # 检查常见路径
    possible_paths = [
        r"C:\oracle\instantclient_21_18",
        r"C:\oracle\instantclient_19_21", 
        r"C:\Program Files\Oracle\instantclient_21_18",
        "/opt/oracle/instantclient_21_18",
        "/usr/lib/oracle/21/client64/lib",
        "/usr/local/oracle/instantclient_21_18"
    ]
    
    found_paths = []
    for path in possible_paths:
        if os.path.exists(path):
            found_paths.append(path)
    
    if found_paths:
        print("✅ 找到Oracle Instant Client:")
        for path in found_paths:
            print(f"   - {path}")
        return found_paths[0]  # 返回第一个找到的路径
    else:
        print("❌ 未找到Oracle Instant Client")
        return None

def provide_oracle_instructions():
    """提供Oracle Instant Client安装说明"""
    print("\n📋 Oracle Instant Client 安装说明:")
    print()
    
    system = platform.system()
    
    if system == "Windows":
        print("🪟 Windows系统:")
        print("1. 访问Oracle官网: https://www.oracle.com/database/technologies/instant-client/downloads.html")
        print("2. 下载 'Basic Package' (约80MB)")
        print("3. 解压到 C:\\oracle\\instantclient_21_18")
        print("4. 添加到系统PATH环境变量")
        
    elif system == "Darwin":  # macOS
        print("🍎 macOS系统:")
        print("1. 使用Homebrew安装:")
        print("   brew install instantclient-basic")
        print("2. 或手动下载并解压到 /usr/local/oracle/instantclient_21_18")
        
    elif system == "Linux":
        print("🐧 Linux系统:")
        print("1. Ubuntu/Debian:")
        print("   sudo apt-get install libaio1")
        print("   # 然后下载并解压Oracle Instant Client")
        print("2. CentOS/RHEL:")
        print("   sudo yum install libaio")
        print("   # 然后下载并解压Oracle Instant Client")
    
    print()
    print("💡 提示: 下载后记得设置LD_LIBRARY_PATH (Linux/macOS) 或 PATH (Windows)")

def test_oracle_connection():
    """测试Oracle连接"""
    print("\n🔄 测试Oracle数据库连接...")
    
    try:
        # 导入并测试Oracle模块
        import oracledb
        print("✅ oracledb模块导入成功")
        
        # 尝试初始化Oracle客户端
        oracle_path = check_oracle_client()
        if oracle_path:
            try:
                oracledb.init_oracle_client(lib_dir=oracle_path)
                print("✅ Oracle客户端初始化成功")
                
                # 这里不进行实际数据库连接测试，避免暴露凭据
                print("💡 Oracle环境配置完成，可以使用数据库功能")
                return True
                
            except Exception as e:
                print(f"❌ Oracle客户端初始化失败: {e}")
                return False
        else:
            print("❌ 请先安装Oracle Instant Client")
            return False
            
    except ImportError:
        print("❌ oracledb模块未安装或安装失败")
        return False

def create_config_template():
    """创建配置文件模板"""
    print("\n📝 创建配置文件模板...")
    
    config_content = """# Oracle数据库连接配置
# 请根据实际环境修改以下配置

[database]
username = BGRO_citangk
password = Cici0511
dsn = UAT7ora:1521/ORAUAT7PRIV

[oracle_client]
# Oracle Instant Client路径 (Windows)
lib_dir_windows = C:\\oracle\\instantclient_21_18

# Oracle Instant Client路径 (Linux/macOS)  
lib_dir_unix = /usr/local/oracle/instantclient_21_18

[tenants]
# 租户ID列表，逗号分隔
tenant_ids = 58857,58877,58878,78879

[extraction]
# 交易数据提取天数
transaction_days_back = 365

# 数据保存路径
data_output_dir = ../data/raw/
"""
    
    try:
        with open('config.ini', 'w', encoding='utf-8') as f:
            f.write(config_content)
        print("✅ 配置文件模板已创建: config.ini")
        print("💡 请根据实际环境修改配置文件")
        return True
    except Exception as e:
        print(f"❌ 配置文件创建失败: {e}")
        return False

def main():
    """主函数"""
    print_banner()
    
    # 检查Python版本
    if not check_python_version():
        return
    
    # 安装Python依赖
    install_dependencies()
    
    # 检查Oracle客户端
    oracle_path = check_oracle_client()
    
    if not oracle_path:
        provide_oracle_instructions()
        print("\n⚠️ 请先安装Oracle Instant Client，然后重新运行此脚本")
    else:
        # 测试Oracle连接
        if test_oracle_connection():
            print("\n🎉 Oracle环境配置成功！")
            
            # 创建配置文件
            create_config_template()
            
            print("\n📋 后续步骤:")
            print("1. 修改 config.ini 中的数据库连接信息")
            print("2. 运行: cd src && python run_feature_engineering.py")
            print("3. 选择Oracle数据库作为数据源")
        else:
            print("\n❌ Oracle环境配置失败")
            provide_oracle_instructions()

if __name__ == "__main__":
    main() 