# InvestCloud客户流失预测项目 - 优化数据导出方案 (≤5000行)

## 🎯 导出策略概述

基于项目指南的用户级别预测架构，我们需要导出**五大核心表**，总数据量控制在**5000行以内**，确保包含足够的**流失**和**活跃**用户样本进行有效建模。

## 📊 数据量分配策略

### 核心原则
- **用户样本**: 100个用户 (50个流失用户 + 50个活跃用户)
- **时间窗口**: 最近12个月的数据
- **数据平衡**: 确保流失/活跃用户的平衡分布
- **业务代表性**: 覆盖不同价值层级和租户类型

### 数据量分配
```python
data_allocation = {
    'USERS': 100,                    # 100个用户基础信息
    'USER_TO_ACCOUNT': 200,          # 100个用户对应约200个账户
    'beamaccount': 200,              # 200个账户的详细信息
    'IDRTRANSACTION': 2000,          # 200个账户 × 平均10笔交易
    'PROFITANDLOSSLITE': 2400,       # 200个账户 × 平均12天数据
    'BeamAccountOverride': 100       # 配置变更记录
}
# 总计: 5000行
```

## 🔍 具体导出SQL方案

### 1. USERS表导出 (100行)

```sql
-- 导出100个代表性用户 (50流失 + 50活跃)
SPOOL Users_sample.csv

SELECT
    'USERNAME','STATUS','TENANTID','EMAILADDRESS','PHONE1',
    'DATEOFBIRTH','STATEPROVINCE','CREATEDATE','LASTMODIFIED'
FROM DUAL
UNION ALL
SELECT
    USERNAME,
    STATUS,
    TO_CHAR(TENANTID),
    EMAILADDRESS,
    PHONE1,
    TO_CHAR(DATEOFBIRTH, 'YYYY-MM-DD'),
    STATEPROVINCE,
    TO_CHAR(CREATEDATE, 'YYYY-MM-DD'),
    TO_CHAR(LASTMODIFIED, 'YYYY-MM-DD')
FROM (
    -- 50个流失用户 (S/L状态)
    SELECT *, ROW_NUMBER() OVER (ORDER BY ORA_HASH(USERNAME)) as rn
    FROM USERS 
    WHERE STATUS IN ('S', 'L')
      AND TENANTID IN (58857, 58877, 58878, 78879)
      AND ROWNUM <= 100
) WHERE rn <= 50
UNION ALL
SELECT
    USERNAME,
    STATUS,
    TO_CHAR(TENANTID),
    EMAILADDRESS,
    PHONE1,
    TO_CHAR(DATEOFBIRTH, 'YYYY-MM-DD'),
    STATEPROVINCE,
    TO_CHAR(CREATEDATE, 'YYYY-MM-DD'),
    TO_CHAR(LASTMODIFIED, 'YYYY-MM-DD')
FROM (
    -- 50个活跃用户 (A/R状态)
    SELECT *, ROW_NUMBER() OVER (ORDER BY ORA_HASH(USERNAME)) as rn
    FROM USERS 
    WHERE STATUS IN ('A', 'R')
      AND TENANTID IN (58857, 58877, 58878, 78879)
      AND ROWNUM <= 100
) WHERE rn <= 50;

SPOOL OFF
```

### 2. USER_TO_ACCOUNT映射表导出 (200行)

```sql
-- 导出用户-账户映射关系
SPOOL User_To_Account_sample.csv

WITH selected_users AS (
    -- 使用与USERS表相同的筛选逻辑
    SELECT USERNAME FROM (
        SELECT USERNAME, ROW_NUMBER() OVER (ORDER BY ORA_HASH(USERNAME)) as rn
        FROM USERS 
        WHERE STATUS IN ('S', 'L')
          AND TENANTID IN (58857, 58877, 58878, 78879)
          AND ROWNUM <= 100
    ) WHERE rn <= 50
    UNION ALL
    SELECT USERNAME FROM (
        SELECT USERNAME, ROW_NUMBER() OVER (ORDER BY ORA_HASH(USERNAME)) as rn
        FROM USERS 
        WHERE STATUS IN ('A', 'R')
          AND TENANTID IN (58857, 58877, 58878, 78879)
          AND ROWNUM <= 100
    ) WHERE rn <= 50
)
SELECT
    'USERNAME','ACCOUNTID','TENANTID','CREATEDATE'
FROM DUAL
UNION ALL
SELECT
    ua.USERNAME,
    TO_CHAR(ua.ACCOUNTID),
    TO_CHAR(ua.TENANTID),
    TO_CHAR(ua.CREATEDATE, 'YYYY-MM-DD')
FROM USER_TO_ACCOUNT ua
JOIN selected_users su ON ua.USERNAME = su.USERNAME;

SPOOL OFF
```

### 3. beamaccount表导出 (200行)

```sql
-- 导出账户基础信息
SPOOL Account_sample.csv

WITH selected_accounts AS (
    SELECT DISTINCT ua.ACCOUNTID 
    FROM USER_TO_ACCOUNT ua
    JOIN (
        -- 重复之前的用户筛选逻辑
        SELECT USERNAME FROM (
            SELECT USERNAME, ROW_NUMBER() OVER (ORDER BY ORA_HASH(USERNAME)) as rn
            FROM USERS 
            WHERE STATUS IN ('S', 'L')
              AND TENANTID IN (58857, 58877, 58878, 78879)
              AND ROWNUM <= 100
        ) WHERE rn <= 50
        UNION ALL
        SELECT USERNAME FROM (
            SELECT USERNAME, ROW_NUMBER() OVER (ORDER BY ORA_HASH(USERNAME)) as rn
            FROM USERS 
            WHERE STATUS IN ('A', 'R')
              AND TENANTID IN (58857, 58877, 58878, 78879)
              AND ROWNUM <= 100
        ) WHERE rn <= 50
    ) su ON ua.USERNAME = su.USERNAME
)
SELECT
    'ID','ACCOUNTSHORTNAME','ACCOUNTCLOSEDATE','ACCOUNTOPENDATE',
    'BOOKCCY','CLASSIFICATION1','DOMICILECOUNTRY','DOMICILESTATE',
    'ACCOUNTSTATUS','CAPITALCOMMITMENTAMOUNT','ACCOUNTMANAGER'
FROM DUAL
UNION ALL
SELECT
    TO_CHAR(b.ID),
    b.ACCOUNTSHORTNAME,
    TO_CHAR(b.ACCOUNTCLOSEDATE, 'YYYY-MM-DD'),
    TO_CHAR(b.ACCOUNTOPENDATE, 'YYYY-MM-DD'),
    b.BOOKCCY,
    b.CLASSIFICATION1,
    b.DOMICILECOUNTRY,
    b.DOMICILESTATE,
    b.ACCOUNTSTATUS,
    TO_CHAR(b.CAPITALCOMMITMENTAMOUNT),
    b.ACCOUNTMANAGER
FROM beamaccount b
JOIN selected_accounts sa ON b.ID = sa.ACCOUNTID;

SPOOL OFF
```

### 4. IDRTRANSACTION表导出 (2000行)

```sql
-- 导出交易记录 (最近12个月)
SPOOL Transaction_sample.csv

WITH selected_accounts AS (
    -- 使用相同的账户筛选逻辑
    SELECT DISTINCT b.ACCOUNTSHORTNAME 
    FROM beamaccount b
    JOIN USER_TO_ACCOUNT ua ON b.ID = ua.ACCOUNTID
    JOIN (
        SELECT USERNAME FROM (
            SELECT USERNAME, ROW_NUMBER() OVER (ORDER BY ORA_HASH(USERNAME)) as rn
            FROM USERS 
            WHERE STATUS IN ('S', 'L')
              AND TENANTID IN (58857, 58877, 58878, 78879)
              AND ROWNUM <= 100
        ) WHERE rn <= 50
        UNION ALL
        SELECT USERNAME FROM (
            SELECT USERNAME, ROW_NUMBER() OVER (ORDER BY ORA_HASH(USERNAME)) as rn
            FROM USERS 
            WHERE STATUS IN ('A', 'R')
              AND TENANTID IN (58857, 58877, 58878, 78879)
              AND ROWNUM <= 100
        ) WHERE rn <= 50
    ) su ON ua.USERNAME = su.USERNAME
)
SELECT
    'ACCOUNTSHORTNAME','BOOKAMOUNT','ASSETCLASSLEVEL1','EVENTDATE',
    'TRADEDATE','QUANTITY','BOOKTOTALLOSS','BOOKTOTALGAIN','EVENTTYPE'
FROM DUAL
UNION ALL
SELECT
    t.ACCOUNTSHORTNAME,
    TO_CHAR(t.BOOKAMOUNT),
    t.ASSETCLASSLEVEL1,
    TO_CHAR(t.EVENTDATE, 'YYYY-MM-DD'),
    TO_CHAR(t.TRADEDATE, 'YYYY-MM-DD'),
    TO_CHAR(t.QUANTITY),
    TO_CHAR(t.BOOKTOTALLOSS),
    TO_CHAR(t.BOOKTOTALGAIN),
    t.EVENTTYPE
FROM IDRTRANSACTION t
JOIN selected_accounts sa ON t.ACCOUNTSHORTNAME = sa.ACCOUNTSHORTNAME
WHERE t.EVENTDATE >= ADD_MONTHS(SYSDATE, -12)  -- 最近12个月
  AND ROWNUM <= 2000
ORDER BY t.EVENTDATE DESC;

SPOOL OFF
```

### 5. PROFITANDLOSSLITE表导出 (2400行)

```sql
-- 导出PNL数据 (最近12个月的月末数据)
SPOOL PNL_sample.csv

WITH selected_accounts AS (
    -- 使用相同的账户筛选逻辑
    SELECT DISTINCT b.ACCOUNTSHORTNAME 
    FROM beamaccount b
    JOIN USER_TO_ACCOUNT ua ON b.ID = ua.ACCOUNTID
    JOIN (
        SELECT USERNAME FROM (
            SELECT USERNAME, ROW_NUMBER() OVER (ORDER BY ORA_HASH(USERNAME)) as rn
            FROM USERS 
            WHERE STATUS IN ('S', 'L')
              AND TENANTID IN (58857, 58877, 58878, 78879)
              AND ROWNUM <= 100
        ) WHERE rn <= 50
        UNION ALL
        SELECT USERNAME FROM (
            SELECT USERNAME, ROW_NUMBER() OVER (ORDER BY ORA_HASH(USERNAME)) as rn
            FROM USERS 
            WHERE STATUS IN ('A', 'R')
              AND TENANTID IN (58857, 58877, 58878, 78879)
              AND ROWNUM <= 100
        ) WHERE rn <= 50
    ) su ON ua.USERNAME = su.USERNAME
),
monthly_pnl AS (
    SELECT 
        p.ACCOUNTSHORTNAME,
        p.BE_ASOF,
        p.ASSETCLASSLEVEL1,
        SUM(p.BOOKMARKETVALUEPERIODEND) AS TOTAL_MARKET_VALUE,
        AVG(p.AVERAGEBOOKUNITCOST) AS AVG_UNIT_COST,
        SUM(p.QUANTITY) AS TOTAL_QUANTITY,
        SUM(p.BOOKUGL) AS TOTAL_BOOKUGL,
        AVG(p.BOOKPRICEPERIODEND) AS AVG_PRICE,
        SUM(p.ORIGINALCOST) AS TOTAL_ORIGINAL_COST,
        ROW_NUMBER() OVER (
            PARTITION BY p.ACCOUNTSHORTNAME, 
                         TRUNC(p.BE_ASOF, 'MM')
            ORDER BY p.BE_ASOF DESC
        ) as rn
    FROM PROFITANDLOSSLITE p
    JOIN selected_accounts sa ON p.ACCOUNTSHORTNAME = sa.ACCOUNTSHORTNAME
    WHERE p.BE_ASOF >= ADD_MONTHS(SYSDATE, -12)
    GROUP BY p.ACCOUNTSHORTNAME, p.BE_ASOF, p.ASSETCLASSLEVEL1
)
SELECT
    'ACCOUNTSHORTNAME','BE_ASOF','ASSETCLASSLEVEL1','TOTAL_MARKET_VALUE',
    'AVG_UNIT_COST','TOTAL_QUANTITY','TOTAL_BOOKUGL',
    'AVG_PRICE','TOTAL_ORIGINAL_COST'
FROM DUAL
UNION ALL
SELECT
    ACCOUNTSHORTNAME,
    TO_CHAR(BE_ASOF, 'YYYY-MM-DD'),
    ASSETCLASSLEVEL1,
    TO_CHAR(TOTAL_MARKET_VALUE),
    TO_CHAR(AVG_UNIT_COST),
    TO_CHAR(TOTAL_QUANTITY),
    TO_CHAR(TOTAL_BOOKUGL),
    TO_CHAR(AVG_PRICE),
    TO_CHAR(TOTAL_ORIGINAL_COST)
FROM monthly_pnl 
WHERE rn = 1  -- 每月最后一天的数据
  AND ROWNUM <= 2400;

SPOOL OFF
```

### 6. BeamAccountOverride表导出 (100行)

```sql
-- 导出账户配置变更记录
SPOOL Account_Override_sample.csv

WITH selected_accounts AS (
    -- 使用相同的账户筛选逻辑
    SELECT DISTINCT ua.ACCOUNTID 
    FROM USER_TO_ACCOUNT ua
    JOIN (
        SELECT USERNAME FROM (
            SELECT USERNAME, ROW_NUMBER() OVER (ORDER BY ORA_HASH(USERNAME)) as rn
            FROM USERS 
            WHERE STATUS IN ('S', 'L')
              AND TENANTID IN (58857, 58877, 58878, 78879)
              AND ROWNUM <= 100
        ) WHERE rn <= 50
        UNION ALL
        SELECT USERNAME FROM (
            SELECT USERNAME, ROW_NUMBER() OVER (ORDER BY ORA_HASH(USERNAME)) as rn
            FROM USERS 
            WHERE STATUS IN ('A', 'R')
              AND TENANTID IN (58857, 58877, 58878, 78879)
              AND ROWNUM <= 100
        ) WHERE rn <= 50
    ) su ON ua.USERNAME = su.USERNAME
)
SELECT
    'AccountId','FieldName','FieldValue','LastModified','ModifiedBy'
FROM DUAL
UNION ALL
SELECT
    TO_CHAR(o.AccountId),
    o.FieldName,
    o.FieldValue,
    TO_CHAR(o.LastModified, 'YYYY-MM-DD'),
    o.ModifiedBy
FROM BeamAccountOverride o
JOIN selected_accounts sa ON o.AccountId = sa.ACCOUNTID
WHERE o.LastModified >= ADD_MONTHS(SYSDATE, -12)
  AND ROWNUM <= 100;

SPOOL OFF
```

## 🔧 Python自动化导出脚本

```python
#!/usr/bin/env python3
"""
InvestCloud客户流失预测项目 - 优化数据导出脚本
控制总数据量在5000行以内
"""

import cx_Oracle
import pandas as pd
import logging
from datetime import datetime

class OptimizedDataExporter:
    def __init__(self, connection_string):
        self.connection_string = connection_string
        self.connection = None
        self.export_summary = {}
        
    def connect(self):
        """连接Oracle数据库"""
        try:
            self.connection = cx_Oracle.connect(self.connection_string)
            logging.info("✅ Oracle数据库连接成功")
            return True
        except Exception as e:
            logging.error(f"❌ 数据库连接失败: {e}")
            return False
    
    def export_optimized_dataset(self):
        """导出优化的数据集"""
        if not self.connect():
            return False
            
        # 定义导出表和预期行数
        tables_config = {
            'users': {'filename': 'Users_sample.csv', 'expected_rows': 100},
            'user_to_account': {'filename': 'User_To_Account_sample.csv', 'expected_rows': 200},
            'accounts': {'filename': 'Account_sample.csv', 'expected_rows': 200},
            'transactions': {'filename': 'Transaction_sample.csv', 'expected_rows': 2000},
            'pnl': {'filename': 'PNL_sample.csv', 'expected_rows': 2400},
            'overrides': {'filename': 'Account_Override_sample.csv', 'expected_rows': 100}
        }
        
        total_exported = 0
        
        for table_name, config in tables_config.items():
            try:
                df = self._export_table(table_name)
                if df is not None:
                    df.to_csv(config['filename'], index=False)
                    exported_rows = len(df)
                    total_exported += exported_rows
                    
                    self.export_summary[table_name] = {
                        'exported_rows': exported_rows,
                        'expected_rows': config['expected_rows'],
                        'filename': config['filename']
                    }
                    
                    logging.info(f"✅ {table_name}: {exported_rows}行 → {config['filename']}")
                    
            except Exception as e:
                logging.error(f"❌ {table_name}导出失败: {e}")
        
        logging.info(f"🎯 总导出行数: {total_exported}/5000")
        return total_exported <= 5000
    
    def _export_table(self, table_name):
        """根据表名导出相应数据"""
        sql_queries = {
            'users': self._get_users_sql(),
            'user_to_account': self._get_user_to_account_sql(),
            'accounts': self._get_accounts_sql(),
            'transactions': self._get_transactions_sql(),
            'pnl': self._get_pnl_sql(),
            'overrides': self._get_overrides_sql()
        }
        
        sql = sql_queries.get(table_name)
        if sql:
            return pd.read_sql(sql, self.connection)
        return None
    
    def _get_users_sql(self):
        """获取用户数据SQL"""
        return """
        SELECT USERNAME, STATUS, TENANTID, EMAILADDRESS, PHONE1,
               DATEOFBIRTH, STATEPROVINCE, CREATEDATE, LASTMODIFIED
        FROM (
            SELECT *, ROW_NUMBER() OVER (ORDER BY ORA_HASH(USERNAME)) as rn
            FROM USERS 
            WHERE STATUS IN ('S', 'L')
              AND TENANTID IN (58857, 58877, 58878, 78879)
        ) WHERE rn <= 50
        UNION ALL
        SELECT USERNAME, STATUS, TENANTID, EMAILADDRESS, PHONE1,
               DATEOFBIRTH, STATEPROVINCE, CREATEDATE, LASTMODIFIED
        FROM (
            SELECT *, ROW_NUMBER() OVER (ORDER BY ORA_HASH(USERNAME)) as rn
            FROM USERS 
            WHERE STATUS IN ('A', 'R')
              AND TENANTID IN (58857, 58877, 58878, 78879)
        ) WHERE rn <= 50
        """
    
    # 其他SQL方法省略 (实际使用时需要完整实现)
    
    def generate_export_report(self):
        """生成导出报告"""
        print("\n" + "="*60)
        print("📊 InvestCloud数据导出报告")
        print("="*60)
        
        total_rows = 0
        for table, info in self.export_summary.items():
            exported = info['exported_rows']
            expected = info['expected_rows']
            filename = info['filename']
            status = "✅" if exported <= expected else "⚠️"
            
            print(f"{status} {table:15} | {exported:4d}/{expected:4d} 行 | {filename}")
            total_rows += exported
        
        print("-"*60)
        print(f"🎯 总计: {total_rows}/5000 行")
        print(f"📁 文件保存在当前目录")
        
        if total_rows <= 5000:
            print("✅ 数据量控制成功！")
        else:
            print("⚠️ 数据量超出预期，请检查SQL查询")

# 使用示例
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    
    # 配置数据库连接
    connection_string = "username/password@host:port/service_name"
    
    exporter = OptimizedDataExporter(connection_string)
    
    if exporter.export_optimized_dataset():
        exporter.generate_export_report()
        print("🎉 数据导出完成！可以开始特征工程和建模了。")
    else:
        print("❌ 数据导出失败，请检查日志")
```

## 📋 导出后数据验证清单

### 1. 数据量验证
```python
validation_checks = {
    'Users_sample.csv': {'max_rows': 100, 'key_cols': ['USERNAME', 'STATUS']},
    'User_To_Account_sample.csv': {'max_rows': 200, 'key_cols': ['USERNAME', 'ACCOUNTID']},
    'Account_sample.csv': {'max_rows': 200, 'key_cols': ['ID', 'ACCOUNTSHORTNAME']},
    'Transaction_sample.csv': {'max_rows': 2000, 'key_cols': ['ACCOUNTSHORTNAME', 'EVENTDATE']},
    'PNL_sample.csv': {'max_rows': 2400, 'key_cols': ['ACCOUNTSHORTNAME', 'BE_ASOF']},
    'Account_Override_sample.csv': {'max_rows': 100, 'key_cols': ['AccountId', 'FieldName']}
}
```

### 2. 关联完整性验证
- 确保所有USER_TO_ACCOUNT中的USERNAME在USERS表中存在
- 确保所有ACCOUNTID在beamaccount表中存在
- 验证交易和PNL数据与账户的关联关系

### 3. 业务逻辑验证
- 流失用户 (S/L) vs 活跃用户 (A/R) 的比例为1:1
- 时间范围控制在最近12个月
- 包含不同租户类型的数据

## 🎯 数据导出优势

### 1. 精确控制数据量
- **总量**: 严格控制在5000行以内
- **平衡**: 流失和活跃用户各50个，确保标签平衡
- **代表性**: 覆盖不同价值层级和租户类型

### 2. 支持完整特征工程
- **用户级别聚合**: 支持多账户用户的特征聚合
- **时间序列分析**: 12个月数据支持趋势分析
- **行为模式识别**: 交易和配置变更记录

### 3. 高效建模准备
- **标签明确**: 基于USERS.STATUS的直接流失标签
- **特征丰富**: 覆盖行为、财务、关系复杂度等维度
- **可扩展**: 验证效果后可按比例扩大到完整数据集

这个优化方案确保在有限的数据量下获得最大的建模价值，为你的客户流失预测项目奠定坚实基础！ 