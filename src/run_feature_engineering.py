#!/usr/bin/env python3
"""
InvestCloud Customer Churn Prediction Project - Feature Engineering Runner
便捷的运行脚本，支持选择Oracle数据库或样本数据作为数据源
"""

import sys
import os
from datetime import datetime

def print_banner():
    """打印项目横幅"""
    print("=" * 80)
    print("InvestCloud 客户流失预测项目 - 特征工程")
    print("=" * 80)
    print(f"运行时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()

def print_menu():
    """打印选择菜单"""
    print("📊 数据源选择:")
    print("1. Oracle数据库 (实时数据，需要数据库连接)")
    print("2. 样本CSV文件 (离线数据，无需数据库)")
    print("3. 退出")
    print()

def validate_oracle_environment():
    """验证Oracle环境配置"""
    print("🔍 验证Oracle环境配置...")
    
    # 检查Oracle Instant Client路径
    oracle_client_path = r"C:\oracle\instantclient_21_18"
    if not os.path.exists(oracle_client_path):
        print(f"❌ Oracle Instant Client路径不存在: {oracle_client_path}")
        print("请确保已正确安装Oracle Instant Client")
        return False
    
    # 检查oracledb包
    try:
        import oracledb
        print("✅ oracledb包已安装")
    except ImportError:
        print("❌ oracledb包未安装")
        print("请运行: pip install oracledb")
        return False
    
    print("✅ Oracle环境配置验证通过")
    return True

def run_with_oracle():
    """使用Oracle数据库运行特征工程"""
    print("🔄 启动Oracle数据库模式...")
    
    # 验证Oracle环境
    if not validate_oracle_environment():
        print("\n⚠️ Oracle环境验证失败，建议使用样本数据模式")
        return False
    
    try:
        from tier1_feature_engineering import main
        main(use_oracle=True)
        return True
    except Exception as e:
        print(f"❌ Oracle模式运行失败: {e}")
        print("建议检查数据库连接配置或使用样本数据模式")
        return False

def run_with_samples():
    """使用样本数据运行特征工程"""
    print("🔄 启动样本数据模式...")
    
    # 检查样本数据文件
    sample_files = [
        '../Account_sampledata.csv',
        '../Transaction_sampledata.csv', 
        '../PNL_sampledata.csv'
    ]
    
    missing_files = []
    for file_path in sample_files:
        if not os.path.exists(file_path):
            missing_files.append(file_path)
    
    if missing_files:
        print("❌ 以下样本数据文件不存在:")
        for file_path in missing_files:
            print(f"   - {file_path}")
        return False
    
    print("✅ 样本数据文件验证通过")
    
    try:
        from tier1_feature_engineering import main
        main(use_oracle=False)
        return True
    except Exception as e:
        print(f"❌ 样本数据模式运行失败: {e}")
        return False

def main():
    """主函数"""
    print_banner()
    
    while True:
        print_menu()
        
        try:
            choice = input("请选择数据源 (1-3): ").strip()
            
            if choice == '1':
                print("\n" + "="*50)
                print("启动Oracle数据库模式")
                print("="*50)
                success = run_with_oracle()
                
            elif choice == '2':
                print("\n" + "="*50)
                print("启动样本数据模式")
                print("="*50)
                success = run_with_samples()
                
            elif choice == '3':
                print("👋 退出程序")
                sys.exit(0)
                
            else:
                print("❌ 无效选择，请输入1-3")
                continue
            
            if success:
                print("\n" + "="*50)
                print("✅ 特征工程完成！")
                print("🎯 接下来可以运行基线模型开发")
                print("="*50)
                break
            else:
                print("\n⚠️ 执行失败，请重新选择")
                continue
                
        except KeyboardInterrupt:
            print("\n\n👋 用户中断，退出程序")
            sys.exit(0)
        except Exception as e:
            print(f"\n❌ 发生错误: {e}")
            continue

if __name__ == "__main__":
    main() 