#!/usr/bin/env python3
"""
InvestCloud Customer Churn Prediction Project - Oracle Database Data Extractor
使用Oracle Instant Client连接UAT环境数据库，提取客户流失预测所需的核心数据表
"""

import oracledb
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import logging
import os
import sys

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(f'data_extraction_{datetime.now().strftime("%Y%m%d_%H%M%S")}.log'),
        logging.StreamHandler(sys.stdout)
    ]
)

class OracleDataExtractor:
    """Oracle数据库数据提取器"""
    
    def __init__(self, oracle_client_path=None):
        """
        初始化数据提取器
        
        Args:
            oracle_client_path (str): Oracle Instant Client路径，默认使用Windows路径
        """
        # Oracle客户端配置
        if oracle_client_path is None:
            oracle_client_path = r"C:\oracle\instantclient_21_18"
        
        self.oracle_client_path = oracle_client_path
        
        # 数据库连接配置
        self.username = "BGRO_citangk"
        self.password = "Cici0511"
        self.dsn = "UAT7ora:1521/ORAUAT7PRIV"
        
        # 租户ID列表（根据实际业务需求）
        self.tenant_ids = [58857, 58877, 58878, 78879]
        
        # 数据存储
        self.connection = None
        self.data_cache = {}
        
    def initialize_oracle_client(self):
        """初始化Oracle客户端"""
        try:
            logging.info(f"初始化Oracle客户端，路径: {self.oracle_client_path}")
            oracledb.init_oracle_client(lib_dir=self.oracle_client_path)
            logging.info("Oracle客户端初始化成功")
            return True
        except Exception as e:
            logging.error(f"Oracle客户端初始化失败: {e}")
            return False
    
    def connect_database(self):
        """连接数据库"""
        try:
            logging.info("连接Oracle数据库...")
            self.connection = oracledb.connect(
                user=self.username, 
                password=self.password, 
                dsn=self.dsn
            )
            logging.info("数据库连接成功")
            return True
        except Exception as e:
            logging.error(f"数据库连接失败: {e}")
            return False
    
    def disconnect_database(self):
        """断开数据库连接"""
        if self.connection:
            self.connection.close()
            logging.info("数据库连接已关闭")
    
    def extract_pnl_data(self, save_to_csv=True):
        """
        提取PROFITANDLOSSLITE表数据
        
        Args:
            save_to_csv (bool): 是否保存为CSV文件
            
        Returns:
            pd.DataFrame: PNL数据
        """
        logging.info("开始提取PROFITANDLOSSLITE表数据...")
        
        query = """
        SELECT
           pnl.ACCOUNTID,
           pnl.BE_ASOF,
           pnl.ASSETCLASSLEVEL1,
           pnl.BOOKMARKETVALUEPERIODEND,
           pnl.AVERAGEBOOKUNITCOST,
           pnl.QUANTITY,
           pnl.BOOKUGL,
           pnl.BOOKPRICEPERIODEND,
           pnl.ORIGINALCOST,
           pnl.TENANTID,
           sn.BE_CURRIND,
           sn.DATACLASS
        FROM SNAPSHOT sn
        JOIN PROFITANDLOSSLITE pnl ON pnl.BE_SNAPSHOTID = sn.ID
        WHERE pnl.TENANTID IN ({})
           AND sn.BE_CURRIND = 'Y'
           AND sn.DATACLASS = 'PROFITANDLOSSLITE'
        """.format(','.join(map(str, self.tenant_ids)))
        
        try:
            logging.info("执行PNL数据查询，这可能需要2-5分钟...")
            df = pd.read_sql(query, self.connection)
            
            logging.info(f"PNL数据提取成功: {len(df):,} 行")
            logging.info(f"唯一账户数: {df['ACCOUNTID'].nunique():,}")
            logging.info(f"数据时间范围: {df['BE_ASOF'].min()} 到 {df['BE_ASOF'].max()}")
            
            if save_to_csv:
                filename = '../data/raw/pnl_raw.csv'
                os.makedirs(os.path.dirname(filename), exist_ok=True)
                df.to_csv(filename, index=False)
                logging.info(f"PNL数据已保存到: {filename}")
            
            self.data_cache['pnl'] = df
            return df
            
        except Exception as e:
            logging.error(f"PNL数据提取失败: {e}")
            return None
    
    def extract_account_data(self, save_to_csv=True):
        """
        提取BEAMACCOUNT表数据
        
        Args:
            save_to_csv (bool): 是否保存为CSV文件
            
        Returns:
            pd.DataFrame: 账户数据
        """
        logging.info("开始提取BEAMACCOUNT表数据...")
        
        query = """
        SELECT
           acc.ACCOUNTID,
           acc.ACCOUNTNUMBER,
           acc.CLIENTID,
           acc.ACCOUNTTYPEID,
           acc.ADVISORID,
           acc.OPENDATE,
           acc.CLOSEDATE,
           acc.STATUS,
           acc.CREATEDDATE,
           acc.MODIFIEDDATE,
           acc.TENANTID
        FROM SNAPSHOT sn
        JOIN BEAMACCOUNT acc ON acc.BE_SNAPSHOTID = sn.ID
        WHERE acc.TENANTID IN ({})
           AND sn.BE_CURRIND = 'Y'
           AND sn.DATACLASS = 'BEAMACCOUNT'
        """.format(','.join(map(str, self.tenant_ids)))
        
        try:
            logging.info("执行账户数据查询...")
            df = pd.read_sql(query, self.connection)
            
            logging.info(f"账户数据提取成功: {len(df):,} 行")
            logging.info(f"唯一账户数: {df['ACCOUNTID'].nunique():,}")
            logging.info(f"唯一客户数: {df['CLIENTID'].nunique():,}")
            
            if save_to_csv:
                filename = '../data/raw/account_raw.csv'
                os.makedirs(os.path.dirname(filename), exist_ok=True)
                df.to_csv(filename, index=False)
                logging.info(f"账户数据已保存到: {filename}")
            
            self.data_cache['account'] = df
            return df
            
        except Exception as e:
            logging.error(f"账户数据提取失败: {e}")
            return None
    
    def extract_transaction_data(self, save_to_csv=True, days_back=365):
        """
        提取IDRTRANSACTION表数据
        
        Args:
            save_to_csv (bool): 是否保存为CSV文件
            days_back (int): 提取多少天前的交易数据
            
        Returns:
            pd.DataFrame: 交易数据
        """
        logging.info(f"开始提取IDRTRANSACTION表数据（最近{days_back}天）...")
        
        # 计算日期范围
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days_back)
        
        query = """
        SELECT
           txn.ACCOUNTID,
           txn.TRANSACTIONDATE,
           txn.TRANSACTIONTYPEID,
           txn.TRANSACTIONAMOUNT,
           txn.QUANTITY,
           txn.PRICE,
           txn.TRADEID,
           txn.INSTRUMENTID,
           txn.CREATEDDATE,
           txn.TENANTID
        FROM SNAPSHOT sn
        JOIN IDRTRANSACTION txn ON txn.BE_SNAPSHOTID = sn.ID
        WHERE txn.TENANTID IN ({})
           AND sn.BE_CURRIND = 'Y'
           AND sn.DATACLASS = 'IDRTRANSACTION'
           AND txn.TRANSACTIONDATE >= DATE '{}'
           AND txn.TRANSACTIONDATE <= DATE '{}'
        """.format(
            ','.join(map(str, self.tenant_ids)),
            start_date.strftime('%Y-%m-%d'),
            end_date.strftime('%Y-%m-%d')
        )
        
        try:
            logging.info("执行交易数据查询...")
            df = pd.read_sql(query, self.connection)
            
            logging.info(f"交易数据提取成功: {len(df):,} 行")
            logging.info(f"唯一账户数: {df['ACCOUNTID'].nunique():,}")
            logging.info(f"交易金额范围: {df['TRANSACTIONAMOUNT'].min():,.2f} 到 {df['TRANSACTIONAMOUNT'].max():,.2f}")
            
            if save_to_csv:
                filename = '../data/raw/transaction_raw.csv'
                os.makedirs(os.path.dirname(filename), exist_ok=True)
                df.to_csv(filename, index=False)
                logging.info(f"交易数据已保存到: {filename}")
            
            self.data_cache['transaction'] = df
            return df
            
        except Exception as e:
            logging.error(f"交易数据提取失败: {e}")
            return None
    
    def extract_user_data(self, save_to_csv=True):
        """
        提取USERS表数据
        
        Args:
            save_to_csv (bool): 是否保存为CSV文件
            
        Returns:
            pd.DataFrame: 用户数据
        """
        logging.info("开始提取USERS表数据...")
        
        query = """
        SELECT
           usr.USERID,
           usr.CLIENTID,
           usr.USERNAME,
           usr.EMAIL,
           usr.PHONE,
           usr.STATUS,
           usr.CREATEDDATE,
           usr.MODIFIEDDATE,
           usr.LASTLOGINDATE,
           usr.TENANTID
        FROM SNAPSHOT sn
        JOIN USERS usr ON usr.BE_SNAPSHOTID = sn.ID
        WHERE usr.TENANTID IN ({})
           AND sn.BE_CURRIND = 'Y'
           AND sn.DATACLASS = 'USERS'
        """.format(','.join(map(str, self.tenant_ids)))
        
        try:
            logging.info("执行用户数据查询...")
            df = pd.read_sql(query, self.connection)
            
            logging.info(f"用户数据提取成功: {len(df):,} 行")
            logging.info(f"唯一用户数: {df['USERID'].nunique():,}")
            logging.info(f"唯一客户数: {df['CLIENTID'].nunique():,}")
            
            if save_to_csv:
                filename = '../data/raw/user_raw.csv'
                os.makedirs(os.path.dirname(filename), exist_ok=True)
                df.to_csv(filename, index=False)
                logging.info(f"用户数据已保存到: {filename}")
            
            self.data_cache['user'] = df
            return df
            
        except Exception as e:
            logging.error(f"用户数据提取失败: {e}")
            return None
    
    def extract_all_data(self):
        """提取所有核心数据表"""
        logging.info("开始提取所有核心数据表...")
        
        results = {}
        
        # 提取用户数据
        results['user'] = self.extract_user_data()
        
        # 提取账户数据
        results['account'] = self.extract_account_data()
        
        # 提取交易数据
        results['transaction'] = self.extract_transaction_data()
        
        # 提取PNL数据
        results['pnl'] = self.extract_pnl_data()
        
        # 生成数据质量报告
        self.generate_data_quality_report(results)
        
        return results
    
    def generate_data_quality_report(self, data_dict):
        """生成数据质量报告"""
        logging.info("生成数据质量报告...")
        
        report = []
        report.append("=" * 60)
        report.append("数据提取质量报告")
        report.append("=" * 60)
        report.append(f"提取时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report.append(f"租户ID: {', '.join(map(str, self.tenant_ids))}")
        report.append("")
        
        for table_name, df in data_dict.items():
            if df is not None:
                report.append(f"{table_name.upper()}表:")
                report.append(f"  - 行数: {len(df):,}")
                report.append(f"  - 列数: {len(df.columns)}")
                
                if 'ACCOUNTID' in df.columns:
                    report.append(f"  - 唯一账户数: {df['ACCOUNTID'].nunique():,}")
                
                if 'CLIENTID' in df.columns:
                    report.append(f"  - 唯一客户数: {df['CLIENTID'].nunique():,}")
                
                # 检查空值
                null_counts = df.isnull().sum()
                high_null_cols = null_counts[null_counts > len(df) * 0.1].index.tolist()
                if high_null_cols:
                    report.append(f"  - 高空值列 (>10%): {', '.join(high_null_cols)}")
                
                report.append("")
            else:
                report.append(f"{table_name.upper()}表: 提取失败")
                report.append("")
        
        report_text = "\n".join(report)
        
        # 保存报告
        report_filename = f'../data/reports/data_quality_report_{datetime.now().strftime("%Y%m%d_%H%M%S")}.txt'
        os.makedirs(os.path.dirname(report_filename), exist_ok=True)
        
        with open(report_filename, 'w', encoding='utf-8') as f:
            f.write(report_text)
        
        logging.info(f"数据质量报告已保存到: {report_filename}")
        print(report_text)

def main():
    """主函数"""
    print("InvestCloud客户流失预测项目 - Oracle数据提取器")
    print("=" * 60)
    
    # 创建数据提取器
    extractor = OracleDataExtractor()
    
    try:
        # 初始化Oracle客户端
        if not extractor.initialize_oracle_client():
            print("Oracle客户端初始化失败，请检查路径和配置")
            return
        
        # 连接数据库
        if not extractor.connect_database():
            print("数据库连接失败，请检查连接信息")
            return
        
        # 提取所有数据
        results = extractor.extract_all_data()
        
        # 统计结果
        success_count = sum(1 for df in results.values() if df is not None)
        total_count = len(results)
        
        print(f"\n数据提取完成: {success_count}/{total_count} 个表成功提取")
        
        if success_count > 0:
            print("\n所有数据已保存到 ../data/raw/ 目录")
            print("请运行特征工程脚本进行下一步处理")
        
    except Exception as e:
        logging.error(f"数据提取过程发生错误: {e}")
        print(f"错误: {e}")
    
    finally:
        # 关闭数据库连接
        extractor.disconnect_database()

if __name__ == "__main__":
    main() 