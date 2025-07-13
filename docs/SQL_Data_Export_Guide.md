# SQL数据导出到CSV文件完整指南

## 项目概述

根据InvestCloud客户流失预测项目的需求，我们需要从Oracle数据库导出四大核心表的数据到CSV文件：

1. **beamaccount** - 账户基础信息表
2. **IDRTRANSACTION** - 交易记录表  
3. **PROFITANDLOSSLITE** - 损益和市值表
4. **USERS** - 用户信息表（如果可用）

## 方案一：SQL*Plus命令行导出（推荐）

### 1. 设置导出环境

```sql
-- 连接到Oracle数据库
sqlplus username/password@database_connection_string

-- 设置输出格式
SET ECHO OFF
SET FEEDBACK OFF
SET HEADING ON
SET PAGESIZE 0
SET TERMOUT OFF
SET TRIMSPOOL ON
SET COLSEP ','
SET LINESIZE 32767
SET NUMWIDTH 20
```

### 2. 账户数据导出

```sql
-- 导出账户基础信息
SPOOL Account_sampledata.csv

SELECT
    'ID','ACCOUNTCLOSEDATE','ACCOUNTOPENDATE','BOOKCCY','CLASSIFICATION1',
    'DOMICILECOUNTRY','DOMICILESTATE','ACCOUNTSTATUS','churn_flag','account_age_days'
FROM DUAL
UNION ALL
SELECT
    TO_CHAR(ID),
    TO_CHAR(ACCOUNTCLOSEDATE, 'YYYY-MM-DD'),
    TO_CHAR(ACCOUNTOPENDATE, 'YYYY-MM-DD'),
    BOOKCCY,
    CLASSIFICATION1,
    DOMICILECOUNTRY,
    DOMICILESTATE,
    ACCOUNTSTATUS,
    TO_CHAR(CASE WHEN ACCOUNTCLOSEDATE IS NULL THEN 0 ELSE 1 END),
    TO_CHAR(FLOOR(
        CASE 
            WHEN ACCOUNTCLOSEDATE IS NULL 
            THEN SYSDATE - ACCOUNTOPENDATE 
            ELSE ACCOUNTCLOSEDATE - ACCOUNTOPENDATE 
        END
    ))
FROM (
    SELECT
        a.ID,
        a.ACCOUNTCLOSEDATE,
        a.ACCOUNTOPENDATE,
        a.BOOKCCY,
        a.CLASSIFICATION1,
        a.DOMICILECOUNTRY,
        a.DOMICILESTATE,
        a.ACCOUNTSTATUS,
        ROW_NUMBER() OVER (
            PARTITION BY CASE WHEN a.ACCOUNTCLOSEDATE IS NULL THEN 0 ELSE 1 END
            ORDER BY ORA_HASH(a.ID)
        ) AS rn
    FROM beamaccount a
    WHERE a.TENANTID IN (58857, 58877, 58878, 78879)
)
WHERE rn <= 15
ORDER BY churn_flag, ID;

SPOOL OFF
```

### 3. 交易数据导出

```sql
-- 导出交易记录
SPOOL Transaction_sampledata.csv

SELECT
    'ACCOUNTID','BOOKAMOUNT','ASSETCLASSLEVEL1','EVENTDATE',
    'TRADEDATE','QUANTITY','BOOKTOTALLOSS','BOOKTOTALGAIN'
FROM DUAL
UNION ALL
SELECT
    TO_CHAR(t.ACCOUNTID),
    TO_CHAR(t.BOOKAMOUNT),
    t.ASSETCLASSLEVEL1,
    TO_CHAR(t.EVENTDATE, 'YYYY-MM-DD'),
    TO_CHAR(t.TRADEDATE, 'YYYY-MM-DD'),
    TO_CHAR(t.QUANTITY),
    TO_CHAR(t.BOOKTOTALLOSS),
    TO_CHAR(t.BOOKTOTALGAIN)
FROM (
    WITH sampled_accounts AS (
        SELECT
            a.ID AS ACCOUNT_ID,
            a.ACCOUNTCLOSEDATE,
            CASE WHEN a.ACCOUNTCLOSEDATE IS NULL THEN 0 ELSE 1 END AS churn_flag
        FROM (
            SELECT
                a.*,
                ROW_NUMBER() OVER (
                    PARTITION BY CASE WHEN a.ACCOUNTCLOSEDATE IS NULL THEN 0 ELSE 1 END
                    ORDER BY ORA_HASH(a.ID)
                ) AS rn
            FROM beamaccount a
            WHERE a.TENANTID IN (58857, 58877, 58878, 78879)
        ) a
        WHERE a.rn <= 15
    )
    SELECT
        t.ACCOUNTID,
        t.BOOKAMOUNT,
        t.ASSETCLASSLEVEL1,
        t.EVENTDATE,
        t.TRADEDATE,
        t.QUANTITY,
        t.BOOKTOTALLOSS,
        t.BOOKTOTALGAIN
    FROM sampled_accounts sa
    JOIN IDRTRANSACTION t ON sa.ACCOUNT_ID = t.ACCOUNTID
    WHERE (
        sa.churn_flag = 1
        AND t.EVENTDATE >= ADD_MONTHS(sa.ACCOUNTCLOSEDATE, -12)
        AND t.EVENTDATE <= sa.ACCOUNTCLOSEDATE
    )
    OR (
        sa.churn_flag = 0
        AND t.EVENTDATE >= ADD_MONTHS(TRUNC(SYSDATE), -12)
    )
    ORDER BY t.ACCOUNTID, t.EVENTDATE
) t;

SPOOL OFF
```

### 4. PNL数据导出

```sql
-- 导出损益数据
SPOOL PNL_sampledata.csv

SELECT
    'ACCOUNTID','BE_ASOF','ASSETCLASSLEVEL1','DAY_BOOK_MARKET_VALUE',
    'AVG_BOOK_UNIT_COST','TOTAL_DAILY_QUANTITY','DAILY_BOOKUGL',
    'AVG_BOOK_PRICE_PERIODEND','DAILY_ORIGINAL_COST_SUM'
FROM DUAL
UNION ALL
SELECT
    TO_CHAR(pnl.ACCOUNTID),
    TO_CHAR(pnl.BE_ASOF, 'YYYY-MM-DD'),
    pnl.ASSETCLASSLEVEL1,
    TO_CHAR(pnl.DAY_BOOK_MARKET_VALUE),
    TO_CHAR(pnl.AVG_BOOK_UNIT_COST),
    TO_CHAR(pnl.TOTAL_DAILY_QUANTITY),
    TO_CHAR(pnl.DAILY_BOOKUGL),
    TO_CHAR(pnl.AVG_BOOK_PRICE_PERIODEND),
    TO_CHAR(pnl.DAILY_ORIGINAL_COST_SUM)
FROM (
    WITH sampled_accounts AS (
        SELECT
            a.ID AS ACCOUNT_ID,
            a.ACCOUNTCLOSEDATE,
            a.ACCOUNTOPENDATE,
            CASE WHEN a.ACCOUNTCLOSEDATE IS NULL THEN 0 ELSE 1 END AS churn_flag
        FROM (
            SELECT
                a.*,
                ROW_NUMBER() OVER (
                    PARTITION BY CASE WHEN a.ACCOUNTCLOSEDATE IS NULL THEN 0 ELSE 1 END
                    ORDER BY ORA_HASH(a.ID)
                ) AS rn
            FROM beamaccount a
            WHERE a.TENANTID IN (58857, 58877, 58878, 78879)
        ) a
        WHERE a.rn <= 15
    )
    SELECT
        pnl.ACCOUNTID,
        pnl.BE_ASOF,
        pnl.ASSETCLASSLEVEL1,
        SUM(pnl.BOOKMARKETVALUEPERIODEND) AS DAY_BOOK_MARKET_VALUE,
        AVG(pnl.AVERAGEBOOKUNITCOST) AS AVG_BOOK_UNIT_COST,
        SUM(pnl.QUANTITY) AS TOTAL_DAILY_QUANTITY,
        SUM(pnl.BOOKUGL) AS DAILY_BOOKUGL,
        AVG(pnl.BOOKPRICEPERIODEND) AS AVG_BOOK_PRICE_PERIODEND,
        SUM(pnl.ORIGINALCOST) AS DAILY_ORIGINAL_COST_SUM
    FROM sampled_accounts sa
    JOIN SNAPSHOT sn 
        ON sn.ACCOUNTID = sa.ACCOUNT_ID
        AND sn.BE_CURRIND = 'Y'
        AND sn.DATACLASS = 'PROFITANDLOSSLITE'
    JOIN SNAPSHOTREASON sr 
        ON sr.ID = sn.BE_SNAPSHOTREASON
        AND sr.CODE = 'EOD'
    JOIN PROFITANDLOSSLITE pnl 
        ON pnl.BE_SNAPSHOTID = sn.ID
    WHERE (
        sa.churn_flag = 1
        AND pnl.BE_ASOF >= ADD_MONTHS(sa.ACCOUNTCLOSEDATE, -12)
        AND pnl.BE_ASOF <= sa.ACCOUNTCLOSEDATE
    )
    OR (
        sa.churn_flag = 0
        AND pnl.BE_ASOF >= ADD_MONTHS(TRUNC(SYSDATE), -12)
    )
    GROUP BY
        pnl.ACCOUNTID,
        pnl.BE_ASOF,
        pnl.ASSETCLASSLEVEL1
    ORDER BY
        pnl.ACCOUNTID,
        pnl.BE_ASOF,
        pnl.ASSETCLASSLEVEL1
) pnl;

SPOOL OFF
```

## 方案二：Python脚本自动导出

### 创建Python导出脚本

```python
#!/usr/bin/env python3
"""
Oracle数据库导出到CSV的Python脚本
"""

import cx_Oracle
import pandas as pd
import os
from datetime import datetime
import logging

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class OracleDataExporter:
    def __init__(self, connection_string):
        """
        初始化Oracle数据导出器
        Args:
            connection_string: Oracle连接字符串，格式：username/password@host:port/service_name
        """
        self.connection_string = connection_string
        self.connection = None
        
    def connect(self):
        """连接到Oracle数据库"""
        try:
            self.connection = cx_Oracle.connect(self.connection_string)
            logging.info("Oracle数据库连接成功")
            return True
        except Exception as e:
            logging.error(f"Oracle数据库连接失败: {e}")
            return False
    
    def export_accounts_data(self, filename='Account_sampledata.csv'):
        """导出账户数据"""
        sql = '''
        SELECT
            ID,
            ACCOUNTCLOSEDATE,
            ACCOUNTOPENDATE,
            BOOKCCY,
            CLASSIFICATION1,
            DOMICILECOUNTRY,
            DOMICILESTATE,
            ACCOUNTSTATUS,
            CASE WHEN ACCOUNTCLOSEDATE IS NULL THEN 0 ELSE 1 END AS churn_flag,
            FLOOR(
                CASE 
                    WHEN ACCOUNTCLOSEDATE IS NULL 
                    THEN SYSDATE - ACCOUNTOPENDATE 
                    ELSE ACCOUNTCLOSEDATE - ACCOUNTOPENDATE 
                END
            ) AS account_age_days
        FROM (
            SELECT
                a.*,
                ROW_NUMBER() OVER (
                    PARTITION BY CASE WHEN a.ACCOUNTCLOSEDATE IS NULL THEN 0 ELSE 1 END
                    ORDER BY ORA_HASH(a.ID)
                ) AS rn
            FROM beamaccount a
            WHERE a.TENANTID IN (58857, 58877, 58878, 78879)
        ) a
        WHERE rn <= 15
        ORDER BY churn_flag, ID
        '''
        
        try:
            df = pd.read_sql(sql, self.connection)
            df.to_csv(filename, index=False)
            logging.info(f"账户数据导出成功: {filename}, 共{len(df)}条记录")
            return True
        except Exception as e:
            logging.error(f"账户数据导出失败: {e}")
            return False
    
    def export_transaction_data(self, filename='Transaction_sampledata.csv'):
        """导出交易数据"""
        # 这里使用与上面SQL相同的查询逻辑
        # ... [完整SQL查询代码]
        pass
    
    def export_pnl_data(self, filename='PNL_sampledata.csv'):
        """导出PNL数据"""
        # 这里使用与上面SQL相同的查询逻辑
        # ... [完整SQL查询代码]
        pass
    
    def export_all_data(self):
        """导出所有数据"""
        if not self.connect():
            return False
        
        success = True
        success &= self.export_accounts_data()
        success &= self.export_transaction_data()
        success &= self.export_pnl_data()
        
        if self.connection:
            self.connection.close()
            logging.info("数据库连接已关闭")
        
        return success

# 使用示例
if __name__ == "__main__":
    # 配置数据库连接字符串
    connection_string = "username/password@host:port/service_name"
    
    exporter = OracleDataExporter(connection_string)
    
    if exporter.export_all_data():
        print("✅ 所有数据导出成功！")
    else:
        print("❌ 数据导出过程中出现错误")
```

## 方案三：Oracle SQL Developer导出

### 1. 在SQL Developer中执行查询

1. 打开Oracle SQL Developer
2. 连接到数据库
3. 执行上述SQL查询
4. 在结果窗口右键点击 → Export → CSV

### 2. 导出设置

- **格式**: CSV
- **编码**: UTF-8
- **分隔符**: 逗号(,)
- **包含列标题**: 是
- **日期格式**: YYYY-MM-DD

## 数据质量检查

### 导出后验证脚本

```python
import pandas as pd

def validate_exported_data():
    """验证导出的数据质量"""
    
    # 加载数据
    accounts_df = pd.read_csv('Account_sampledata.csv')
    transactions_df = pd.read_csv('Transaction_sampledata.csv')
    pnl_df = pd.read_csv('PNL_sampledata.csv')
    
    print("=== 数据导出质量检查 ===")
    
    # 基本统计
    print(f"账户数据: {len(accounts_df)} 条记录, {len(accounts_df.columns)} 列")
    print(f"交易数据: {len(transactions_df)} 条记录, {len(transactions_df.columns)} 列")
    print(f"PNL数据: {len(pnl_df)} 条记录, {len(pnl_df.columns)} 列")
    
    # 流失标签分布
    churn_dist = accounts_df['churn_flag'].value_counts()
    print(f"\n流失标签分布:")
    print(f"  活跃客户 (0): {churn_dist.get(0, 0)} 个")
    print(f"  流失客户 (1): {churn_dist.get(1, 0)} 个")
    
    # 关联关系检查
    account_ids = set(accounts_df['ID'])
    transaction_account_ids = set(transactions_df['ACCOUNTID']) 
    pnl_account_ids = set(pnl_df['ACCOUNTID'])
    
    print(f"\n关联关系检查:")
    print(f"  交易数据覆盖账户: {len(transaction_account_ids & account_ids)}/{len(account_ids)}")
    print(f"  PNL数据覆盖账户: {len(pnl_account_ids & account_ids)}/{len(account_ids)}")
    
    # 缺失值检查
    print(f"\n缺失值检查:")
    for name, df in [("账户", accounts_df), ("交易", transactions_df), ("PNL", pnl_df)]:
        missing = df.isnull().sum().sum()
        print(f"  {name}数据缺失值: {missing}")

if __name__ == "__main__":
    validate_exported_data()
```

## 注意事项

### 1. 数据安全
- 确保敏感数据的安全传输和存储
- 使用加密连接
- 及时删除临时文件

### 2. 性能优化
- 对于大数据量，考虑分批导出
- 添加适当的索引
- 使用并行查询（如果数据库支持）

### 3. 错误处理
- 设置查询超时
- 添加重试机制
- 记录详细的错误日志

### 4. 数据验证
- 检查导出的记录数
- 验证关键字段的完整性
- 确认日期格式的正确性

这个指南提供了完整的SQL数据导出方案，你可以根据实际的数据库环境和权限选择最适合的方法。 