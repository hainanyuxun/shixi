# InvestCloud金融客户流失预测特征重要性分析

## 基于四大核心表的特征体系重构

### 重要发现：用户级别预测策略
通过深入分析InvestCloud的数据结构，我们确定了**用户级别**的流失预测策略，这比传统的账户级别预测更具商业价值。

### 流失标签重新定义
**主要流失标签**: USERS.STATUS字段
```sql
CASE 
    WHEN STATUS = 'A' THEN 0  -- 活跃用户 (Active)
    WHEN STATUS = 'R' THEN 0  -- 重新激活用户 (Reactivated) 
    WHEN STATUS IN ('S', 'L') THEN 1  -- 流失用户 (Suspended/Locked)
END AS churn_label
```

**预测层级架构**:
```
用户级别主预测 (USERS.STATUS) - 商业价值最高
    ↓ 支撑数据
账户聚合特征 (beamaccount) - 用户投资复杂度
    ↓ 行为数据  
交易行为分析 (IDRTRANSACTION) - 活跃度和投资表现
    ↓ 价值数据
资产价值趋势 (PROFITANDLOSSLITE) - 财务健康状况
```

## 一级重要特征（核心预测因子）⭐⭐⭐⭐⭐

### 1. 用户交易行为衰退特征 (基于IDRTRANSACTION表)

```sql
-- 用户级别交易活跃度分析
WITH user_trading_metrics AS (
    SELECT 
        u.USERNAME,
        COUNT(t.EVENTDATE) as transaction_frequency_30d,
        SUM(ABS(t.BOOKAMOUNT)) as total_transaction_volume,
        AVG(ABS(t.BOOKAMOUNT)) as avg_transaction_amount,
        STDDEV(t.BOOKAMOUNT) as transaction_volatility,
        MAX(t.EVENTDATE) as last_transaction_date,
        SYSDATE - MAX(t.EVENTDATE) as days_since_last_transaction,
        SUM(CASE WHEN t.BOOKAMOUNT > 0 THEN t.BOOKAMOUNT ELSE 0 END) as total_inflow,
        SUM(CASE WHEN t.BOOKAMOUNT < 0 THEN ABS(t.BOOKAMOUNT) ELSE 0 END) as total_outflow
    FROM USERS u
    JOIN USER_TO_ACCOUNT ua ON u.USERNAME = ua.USERNAME
    JOIN beamaccount b ON ua.ACCOUNTID = b.ID
    LEFT JOIN IDRTRANSACTION t ON b.ACCOUNTSHORTNAME = t.ACCOUNTSHORTNAME
    WHERE t.EVENTDATE >= SYSDATE - 30
    GROUP BY u.USERNAME
)
```

**核心衍生特征**:
- **交易频率衰退率**: 近30天 vs 历史90天交易频率比较
- **交易停滞期**: 最后一次交易距今天数
- **资金净流向**: (流入-流出)/总交易额，负值表示资金流出
- **交易规模变化**: 平均交易金额的趋势变化
- **交易一致性**: 交易时间间隔的标准差

**预测重要性**: ⭐⭐⭐⭐⭐ (最重要)  
**业务解释**: 交易活动衰退是用户流失的最强预警信号，特别是交易频率突然下降和持续资金流出

---

### 2. 用户投资表现恶化特征 (基于PROFITANDLOSSLITE + IDRTRANSACTION表)

```sql
-- 用户级别投资表现分析
WITH user_investment_performance AS (
    SELECT 
        u.USERNAME,
        SUM(p.BOOKMARKETVALUEPERIODEND) as total_market_value,
        SUM(p.BOOKUGL) as total_unrealized_pnl,
        AVG(p.BOOKUGL / NULLIF(p.BOOKMARKETVALUEPERIODEND, 0)) as avg_unrealized_pnl_ratio,
        SUM(t.BOOKTOTALGAIN) as total_realized_gain,
        SUM(t.BOOKTOTALLOSS) as total_realized_loss,
        COUNT(DISTINCT p.ASSETCLASSLEVEL1) as asset_class_diversity,
        STDDEV(p.BOOKMARKETVALUEPERIODEND) as portfolio_volatility
    FROM USERS u
    JOIN USER_TO_ACCOUNT ua ON u.USERNAME = ua.USERNAME
    JOIN beamaccount b ON ua.ACCOUNTID = b.ID
    LEFT JOIN PROFITANDLOSSLITE p ON b.ACCOUNTSHORTNAME = p.ACCOUNTSHORTNAME
    LEFT JOIN IDRTRANSACTION t ON b.ACCOUNTSHORTNAME = t.ACCOUNTSHORTNAME
    WHERE p.BE_ASOF >= SYSDATE - 90
    GROUP BY u.USERNAME
)
```

**核心衍生特征**:
- **投资收益率**: (当前市值 - 原始成本) / 原始成本
- **未实现损益比率**: 未实现损益 / 总市值
- **收益损失比**: 总收益 / ABS(总损失)
- **连续亏损天数**: 连续未实现损益为负的天数
- **风险调整收益**: 收益率 / 投资组合波动性

**预测重要性**: ⭐⭐⭐⭐⭐ (最重要)  
**业务解释**: 持续投资亏损直接影响客户满意度，是高净值客户流失的核心原因

---

### 3. 用户账户管理复杂度下降特征 (基于beamaccount表聚合)

```sql
-- 用户账户管理复杂度分析
WITH user_account_complexity AS (
    SELECT 
        u.USERNAME,
        COUNT(b.ID) as total_accounts,
        COUNT(DISTINCT b.CLASSIFICATION1) as account_type_diversity,
        SUM(CASE WHEN b.ACCOUNTCLOSEDATE IS NULL THEN 1 ELSE 0 END) as active_accounts,
        AVG(SYSDATE - b.ACCOUNTOPENDATE) as avg_account_age,
        SUM(COALESCE(b.CAPITALCOMMITMENTAMOUNT, 0)) as total_capital_commitment,
        COUNT(DISTINCT b.DOMICILESTATE) as geographic_diversity,
        COUNT(DISTINCT b.ACCOUNTMANAGER) as advisor_diversity
    FROM USERS u
    JOIN USER_TO_ACCOUNT ua ON u.USERNAME = ua.USERNAME
    JOIN beamaccount b ON ua.ACCOUNTID = b.ID
    GROUP BY u.USERNAME
)
```

**核心衍生特征**:
- **账户关闭比例**: 已关闭账户数 / 总账户数
- **账户类型集中度**: 1 - (不同账户类型数 / 总账户数)
- **资本承诺强度**: 总资本承诺 / 总账户数
- **关系深度评分**: 平均账户年龄 + 账户类型多样性
- **服务关系稳定性**: 投资顾问的稳定性评估

**预测重要性**: ⭐⭐⭐⭐⭐ (最重要)  
**业务解释**: 用户简化账户结构和减少资本承诺通常预示准备转移资产

---

### 4. 用户参与度下降特征 (基于USERS + BeamAccountOverride表)

```sql
-- 用户参与度综合评估
WITH user_engagement AS (
    SELECT 
        u.USERNAME,
        -- 联系信息完整度 (0-5分)
        (CASE WHEN u.EMAILADDRESS IS NOT NULL THEN 1 ELSE 0 END +
         CASE WHEN u.EMAILADDRESS2 IS NOT NULL THEN 1 ELSE 0 END +
         CASE WHEN u.PRIMARYPHONENUMBER IS NOT NULL THEN 1 ELSE 0 END +
         CASE WHEN u.PHONE2 IS NOT NULL THEN 1 ELSE 0 END +
         CASE WHEN u.PHONE3 IS NOT NULL THEN 1 ELSE 0 END) as contact_completeness,
        
        -- 安全设置深度 (0-3分)
        (CASE WHEN u.SECRETQUESTION IS NOT NULL THEN 1 ELSE 0 END +
         CASE WHEN u.SECRETQUESTION2 IS NOT NULL THEN 1 ELSE 0 END +
         CASE WHEN u.SECRETQUESTION3 IS NOT NULL THEN 1 ELSE 0 END) as security_setup_depth,
        
        -- 配置修改活跃度
        COUNT(o.FieldName) as config_modifications,
        SYSDATE - MAX(o.LastModified) as days_since_last_config
    FROM USERS u
    LEFT JOIN USER_TO_ACCOUNT ua ON u.USERNAME = ua.USERNAME
    LEFT JOIN BeamAccountOverride o ON ua.ACCOUNTID = o.AccountId
    GROUP BY u.USERNAME, u.EMAILADDRESS, u.EMAILADDRESS2, 
             u.PRIMARYPHONENUMBER, u.PHONE2, u.PHONE3,
             u.SECRETQUESTION, u.SECRETQUESTION2, u.SECRETQUESTION3
)
```

**核心衍生特征**:
- **信息完整度评分**: (联系方式数量 + 安全设置数量) / 8 * 100
- **配置参与频率**: 最近90天配置修改次数
- **信息维护及时性**: 距离最后信息更新的天数
- **用户参与度综合评分**: 加权综合各参与度指标

**预测重要性**: ⭐⭐⭐⭐ (重要)  
**业务解释**: 用户参与度下降反映对平台依赖程度降低，是流失的重要前兆

## 二级重要特征（重要支撑因子）⭐⭐⭐

### 1. 用户资产配置行为特征

```sql
-- 用户资产配置分析
WITH user_asset_allocation AS (
    SELECT 
        u.USERNAME,
        COUNT(DISTINCT p.ASSETCLASSLEVEL1) as l1_asset_diversity,
        COUNT(DISTINCT p.ASSETCLASSLEVEL2) as l2_asset_diversity,
        COUNT(DISTINCT p.PRIMARYSECURITYSYMBOL) as security_diversity,
        -- 计算各资产类别占比
        SUM(CASE WHEN p.ASSETCLASSLEVEL1 = 'Equity' 
            THEN p.BOOKMARKETVALUEPERIODEND ELSE 0 END) / 
        SUM(p.BOOKMARKETVALUEPERIODEND) as equity_ratio,
        -- 投资组合集中度 (HHI指数)
        SUM(POWER(p.BOOKMARKETVALUEPERIODEND / SUM(p.BOOKMARKETVALUEPERIODEND) OVER(), 2)) as concentration_index
    FROM USERS u
    JOIN USER_TO_ACCOUNT ua ON u.USERNAME = ua.USERNAME
    JOIN beamaccount b ON ua.ACCOUNTID = b.ID
    JOIN PROFITANDLOSSLITE p ON b.ACCOUNTSHORTNAME = p.ACCOUNTSHORTNAME
    WHERE p.BE_ASOF = (SELECT MAX(BE_ASOF) FROM PROFITANDLOSSLITE)
    GROUP BY u.USERNAME
)
```

### 2. 用户生命周期和价值特征

```sql
-- 用户生命周期价值分析
WITH user_lifecycle_value AS (
    SELECT 
        u.USERNAME,
        -- 基础人口统计学
        FLOOR(MONTHS_BETWEEN(SYSDATE, u.DATEOFBIRTH) / 12) as age,
        u.STATEPROVINCE,
        CASE 
            WHEN ua.TENANTID = (SELECT ID FROM TENANT WHERE NAME = 'NeubergerBerman_Employee') 
            THEN 'Internal' 
            ELSE 'External' 
        END as user_type,
        
        -- 关系深度
        MIN(b.ACCOUNTOPENDATE) as first_account_date,
        SYSDATE - MIN(b.ACCOUNTOPENDATE) as total_relationship_days,
        
        -- 客户价值
        SUM(p.BOOKMARKETVALUEPERIODEND) as total_asset_value,
        SUM(ABS(t.BOOKAMOUNT)) as total_transaction_volume
    FROM USERS u
    LEFT JOIN USER_TO_ACCOUNT ua ON u.USERNAME = ua.USERNAME
    LEFT JOIN beamaccount b ON ua.ACCOUNTID = b.ID
    LEFT JOIN PROFITANDLOSSLITE p ON b.ACCOUNTSHORTNAME = p.ACCOUNTSHORTNAME
    LEFT JOIN IDRTRANSACTION t ON b.ACCOUNTSHORTNAME = t.ACCOUNTSHORTNAME
    GROUP BY u.USERNAME, u.DATEOFBIRTH, u.STATEPROVINCE, ua.TENANTID
)
```

### 3. 用户风险承受度变化特征

基于投资组合的风险特征变化，包括资产配置的风险偏好变化、波动性容忍度等。

## 三级重要特征（补充因子）⭐⭐

### 1. 外部市场环境因素
- 市场波动性对用户行为的影响
- 同期竞争对手活动
- 宏观经济环境变化

### 2. 地理和人口统计学特征
- 基于州的财富分层
- 年龄段的流失模式差异
- 用户类型(内部/外部)的行为差异

## 特征工程最佳实践

### 时间窗口设计
```python
# InvestCloud特定的时间窗口
time_windows = {
    'immediate': 7,      # 7天 - 捕捉即时行为变化
    'short_term': 30,    # 30天 - 近期趋势分析
    'quarterly': 90,     # 90天 - 季度投资周期
    'annual': 365,       # 1年 - 年度投资基准
    'lifecycle': 1095,   # 3年 - 完整投资周期
}
```

### 关键特征组合
```python
# 高价值特征组合策略
feature_combinations = {
    'behavioral_decline_score': [
        'transaction_frequency_decline',
        'days_since_last_transaction', 
        'config_modification_decline'
    ],
    'financial_performance_score': [
        'unrealized_pnl_ratio',
        'realized_gain_loss_ratio',
        'portfolio_volatility'
    ],
    'relationship_depth_score': [
        'total_accounts',
        'account_type_diversity',
        'avg_account_age',
        'total_capital_commitment'
    ],
    'engagement_health_score': [
        'contact_completeness',
        'security_setup_depth',
        'config_participation_rate'
    ]
}
```

### 特征重要性排序
```python
feature_importance_tiers = {
    'tier_1_critical': {
        'features': [
            'transaction_frequency_decline',
            'unrealized_pnl_deterioration', 
            'account_closure_rate',
            'days_since_last_transaction'
        ],
        'weight': 0.6,
        'description': '直接流失预警信号'
    },
    'tier_2_important': {
        'features': [
            'portfolio_value_trend',
            'asset_allocation_changes',
            'user_engagement_score',
            'capital_commitment_changes'
        ],
        'weight': 0.3,
        'description': '重要支撑指标'
    },
    'tier_3_supporting': {
        'features': [
            'demographic_features',
            'geographic_risk_factors',
            'market_environment_factors'
        ],
        'weight': 0.1,
        'description': '补充上下文信息'
    }
}
```

## 数据质量和特征验证

### 关键验证检查
1. **用户-账户关联**: 确认USERS表与beamaccount表的关联方式
2. **时间序列一致性**: 跨表日期字段的对齐
3. **财务逻辑验证**: 市值、损益等计算的合理性
4. **缺失值模式**: 关键字段的缺失值分布

### 特征稳定性监控
- 特征分布的时间稳定性
- 与目标变量相关性的稳定性
- 业务逻辑一致性检查

## 建模策略建议

### 两层预测架构
1. **用户级别主模型**: 基于USERS.STATUS的流失预测
2. **账户级别辅助模型**: 支持细粒度风险分析

### 推荐模型类型
- **主力模型**: XGBoost, LightGBM (处理复杂特征交互)
- **基线模型**: Logistic Regression, Random Forest
- **时间序列**: LSTM/GRU (针对资产价值趋势)

### 评估指标设计
- **技术指标**: AUC-ROC, Precision@10%, Recall@高价值客户
- **业务指标**: 客户价值保护率, 挽回成功率, 预警提前期

---

**更新日志**:
- 2024-12-19: 完全重构，基于InvestCloud四表架构
- 2024-12-19: 重新定义用户级别预测策略  
- 2024-12-19: 建立特征重要性分层体系 