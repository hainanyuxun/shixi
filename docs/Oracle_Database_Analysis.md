# InvestCloud Oracle 数据库结构分析

## 数据概览

基于你提供的SQL查询和CSV样本数据，我们有三个核心数据表：

### 1. ACCOUNT 表（客户账户基础信息）

**表名**: `beamaccount`  
**数据量**: 约1.5万个不同客户账户（推测）  
**关键字段分析**:

```sql
-- 核心字段结构
ID                  -- 客户账户唯一标识符
ACCOUNTCLOSEDATE    -- 账户关闭日期（NULL=活跃客户）
ACCOUNTOPENDATE     -- 账户开设日期  
BOOKCCY            -- 基础货币（主要是USD）
CLASSIFICATION1     -- 账户类型分类
DOMICILECOUNTRY     -- 所在国家
DOMICILESTATE       -- 所在州
ACCOUNTSTATUS       -- 账户状态（OPEN/CLOSED）
TENANTID           -- 租户ID（多租户架构）
```

**流失标签定义**: `churn_flag = CASE WHEN ACCOUNTCLOSEDATE IS NULL THEN 0 ELSE 1 END`

#### 📊 数据洞察：

**客户类型分布**:
- Individual（个人账户）
- IRA（个人退休账户）  
- Trust（信托账户）
- Joint（联名账户）
- Entity（实体账户）
- WRAP Fee Accounts（包装费用账户）
- RETIREMENT PLAN（退休计划）
- Non-Profit（非营利组织）

**地理分布**: 主要集中在美国各州（NY, CA, FL, TX, NJ等）

**账户年龄**: 从几个月到20+年不等，体现了客户生命周期的多样性

### 2. PNL 表（损益和市场价值数据）

**表名**: `PROFITANDLOSSLITE`  
**数据量**: 每账户每日记录，约36万条记录  
**时间范围**: 近12个月的每日快照

```sql
-- 核心财务指标
ACCOUNTID                    -- 关联账户ID
BE_ASOF                     -- 数据日期（每日EOD）
ASSETCLASSLEVEL1            -- 资产类别（主要是Equity）
BOOKMARKETVALUEPERIODEND    -- 期末账面市值
AVERAGEBOOKUNITCOST         -- 平均账面单位成本
QUANTITY                    -- 持仓数量
BOOKUGL                     -- 账面未实现损益
BOOKPRICEPERIODEND          -- 期末账面价格
ORIGINALCOST                -- 原始成本
```

#### 📈 关键特征工程机会：

**时间序列特征**:
- 账面价值变化趋势（30/60/90天）
- 未实现损益波动性
- 持仓数量变化模式
- 平均成本基础变化

**财务健康指标**:
- 投资收益率 = (当前市值 - 原始成本) / 原始成本
- 资产波动性 = STDDEV(日收益率)
- 最大回撤深度

### 3. TRANSACTION 表（交易行为数据）

**表名**: `IDRTRANSACTION`  
**数据量**: 每笔交易记录，约8000条记录  
**时间范围**: 近12个月的所有交易

```sql
-- 交易行为字段
ACCOUNTID           -- 关联账户ID
BOOKAMOUNT         -- 交易金额
ASSETCLASSLEVEL1   -- 资产类别
EVENTDATE          -- 事件发生日期
TRADEDATE          -- 交易日期
QUANTITY           -- 交易数量
BOOKTOTALLOSS      -- 账面总损失
BOOKTOTALGAIN      -- 账面总收益
```

#### 🔄 交易模式洞察：

**交易特征**:
- 买入/卖出模式（正负金额）
- 交易频率和规律性
- 平均交易规模
- 盈亏实现模式

**高价值衍生特征**:
- 交易频率下降率
- 平均交易间隔增加
- 净流出资金趋势
- 交易规模变化

## 数据质量评估

### ✅ 高质量方面：
1. **数据完整性**: 核心字段缺失率很低
2. **时间一致性**: 所有表都有清晰的时间维度
3. **关联完整性**: 通过ACCOUNTID可以很好地关联
4. **业务逻辑**: 流失定义明确（账户关闭日期）

### ⚠️ 需要注意的问题：
1. **数据倾斜**: 从样本看，流失客户和活跃客户各15个，但实际分布可能不平衡
2. **缺失值**: 一些交易记录的BOOKTOTALLOSS/GAIN为空
3. **异常值**: 交易金额变化很大，需要异常值检测
4. **时效性**: 确保使用最新的账户状态

## 特征优先级重新评估

### 🔥 一级重要特征（基于实际数据）

#### 1. 交易行为衰退模式
```sql
-- 关键指标SQL示例
SELECT 
    ACCOUNTID,
    COUNT(*) as transaction_count_30d,
    SUM(ABS(BOOKAMOUNT)) as total_transaction_volume,
    AVG(ABS(BOOKAMOUNT)) as avg_transaction_size,
    MAX(EVENTDATE) as last_transaction_date,
    STDDEV(BOOKAMOUNT) as transaction_volatility
FROM IDRTRANSACTION 
WHERE EVENTDATE >= ADD_MONTHS(SYSDATE, -1)
GROUP BY ACCOUNTID;
```

#### 2. 资产价值趋势变化
```sql
-- 市值变化趋势
SELECT 
    ACCOUNTID,
    AVG(BOOKMARKETVALUEPERIODEND) as avg_market_value,
    STDDEV(BOOKMARKETVALUEPERIODEND) as value_volatility,
    (MAX(BOOKMARKETVALUEPERIODEND) - MIN(BOOKMARKETVALUEPERIODEND)) / 
     NULLIF(MIN(BOOKMARKETVALUEPERIODEND), 0) as value_range_ratio
FROM PROFITANDLOSSLITE 
WHERE BE_ASOF >= ADD_MONTHS(SYSDATE, -3)
GROUP BY ACCOUNTID;
```

#### 3. 账户生命周期特征
```sql
-- 账户年龄和类型
SELECT 
    ID,
    FLOOR(SYSDATE - ACCOUNTOPENDATE) as account_age_days,
    CLASSIFICATION1 as account_type,
    DOMICILESTATE as location
FROM beamaccount;
```

### ⭐ 二级重要特征

#### 4. 盈亏实现模式
- 实现损益 vs 未实现损益比率
- 盈利交易 vs 亏损交易频率
- 风险承受度变化

#### 5. 投资组合集中度
- 单一资产类别占比
- 持仓集中度指标
- 投资多样化程度

## 特征工程策略

### 时间窗口设计
```python
# 推荐的分析窗口
analysis_windows = {
    'recent_activity': 30,      # 30天 - 近期行为变化
    'quarterly_trend': 90,      # 90天 - 季度趋势
    'annual_baseline': 365,     # 1年 - 年度基准
    'pre_churn_period': 180,    # 180天 - 流失前模式
}
```

### 关键衍生特征
```python
# 核心特征计算
features_engineering = {
    # 交易行为特征
    'transaction_frequency_decline': '近30天 vs 90天交易频率比',
    'avg_transaction_size_change': '交易规模变化趋势',
    'days_since_last_transaction': '最后交易距今天数',
    'net_flow_trend': '资金净流入/流出趋势',
    
    # 投资表现特征  
    'portfolio_return_30d': '30天投资组合收益率',
    'unrealized_pnl_ratio': '未实现损益/总市值比率',
    'value_at_risk': '基于历史波动的风险价值',
    'max_drawdown': '最大回撤深度',
    
    # 客户生命周期特征
    'account_age_months': '账户开设月数',
    'account_type_encoded': '账户类型编码',
    'geographic_risk': '地理位置风险评分',
}
```

## 数据提取建议

### Phase 1: 核心数据获取（第1周）
```sql
-- 1. 完整的账户基础信息
SELECT * FROM beamaccount 
WHERE TENANTID IN (58857, 58877, 58878, 78879);

-- 2. 近12个月的PNL数据
SELECT * FROM PROFITANDLOSSLITE pnl
JOIN SNAPSHOT sn ON pnl.BE_SNAPSHOTID = sn.ID
WHERE sn.BE_CURRIND = 'Y' 
  AND pnl.BE_ASOF >= ADD_MONTHS(SYSDATE, -12);

-- 3. 近12个月的交易数据
SELECT * FROM IDRTRANSACTION 
WHERE EVENTDATE >= ADD_MONTHS(SYSDATE, -12);
```

### Phase 2: 特征工程（第2周）
- 计算时间序列特征
- 构建交易行为模式
- 计算投资表现指标

### Phase 3: 模型准备（第3周）
- 特征选择和验证
- 数据预处理和标准化
- 训练/测试集划分

## 预期建模挑战

### 1. 数据不平衡
- 预计流失客户比例较低（<20%）
- 需要使用SMOTE或下采样技术

### 2. 时间序列特性
- 需要防止时间泄露
- 考虑季节性和市场周期影响

### 3. 特征相关性
- 市值、交易金额等特征可能高度相关
- 需要特征选择和降维

## 建议的评估策略

### 业务导向指标
- **Precision@10%**: 预测最高风险10%客户的准确率
- **早期预警效果**: 提前30/60/90天的预测能力
- **假阳性成本**: 错误预警的业务成本
- **挽留ROI**: 基于预测进行干预的投资回报率

### 技术指标
- **AUC-ROC**: 总体分类能力
- **AUC-PR**: 不平衡数据集表现
- **时间稳定性**: 模型在不同时间段的稳定性

---

**总结**: 你的数据质量很高，包含了预测客户流失所需的核心信息。重点应该放在交易行为衰退模式和投资组合价值变化趋势上，这些是最强的流失预警信号。 