# PROFITANDLOSSLITE 表字段参考（客户流失预测项目）

## 表概述
**表名**: PROFITANDLOSSLITE  
**数据频率**: 每日EOD快照  
**关联字段**: ACCOUNTSHORTNAME → beamaccount.ACCOUNTSHORTNAME  
**时间字段**: BE_ASOF（数据日期）  

## 一级重要字段（核心时间序列特征）

### 💰 市场价值和损益核心指标
| 字段名 | 数据类型 | 示例值 | 业务含义 | 建模用途 |
|--------|----------|--------|----------|----------|
| **BOOKMARKETVALUEPERIODEND** | NUMBER(20,5) | 698.95 | 期末账面市值（账户货币） | **最重要** - 资产价值趋势分析 |
| **BOOKUGL** | NUMBER(20,5) | 8364.57 | 账面未实现损益 | **关键指标** - 投资表现和风险信号 |
| **QUANTITY** | NUMBER(20,5) | 698.95 | 持仓数量 | 仓位变化趋势 |
| **AVERAGEBOOKUNITCOST** | NUMBER(20,5) | -10.97 | 平均账面单位成本 | 成本基础变化 |
| **BOOKPRICEPERIODEND** | NUMBER(20,5) | 1 | 期末账面价格 | 价格波动性计算 |

### 📅 时间和账户标识
| 字段名 | 数据类型 | 示例值 | 业务含义 | 建模用途 |
|--------|----------|--------|----------|----------|
| **BE_ASOF** | DATE | 43535 | 数据日期 | **时间序列基础** - 必须字段 |
| **ACCOUNTSHORTNAME** | VARCHAR2(50) | 59302865 | 账户短名称 | **关联键** - 与beamaccount关联 |

### 🏷️ 资产分类和策略
| 字段名 | 数据类型 | 示例值 | 业务含义 | 建模用途 |
|--------|----------|--------|----------|----------|
| **ASSETCLASSLEVEL1** | VARCHAR2(50) | Alternatives | 主要资产类别 | **投资组合多样性分析** |
| **ASSETCLASSLEVEL2** | VARCHAR2(50) | Hedge Funds | 二级资产类别 | 细分投资偏好 |
| **ASSETCLASSLEVEL3** | VARCHAR2(50) | Lower Vol Hedge Funds | 三级资产类别 | 最细粒度风险偏好 |
| **STRATEGYNAME** | VARCHAR2(100) | Options - Hedge Options Premium Fund | 策略名称 | 策略复杂度评估 |

## 二级重要字段（支撑特征）

### 💸 成本和收益分析
| 字段名 | 数据类型 | 示例值 | 业务含义 | 建模用途 |
|--------|----------|--------|----------|----------|
| **BOOKAMORTIZEDCOSTPERIODEND** | NUMBER(20,5) | -7665.62 | 期末摊销成本 | 成本基础追踪 |
| **ORIGINALCOST** | NUMBER(20,5) | 0 | 原始成本 | 总收益率计算 |
| **ANNUALINCOME** | NUMBER(20,5) | 0 | 年度收益 | 收入稳定性 |
| **BOOKACCRUEDINTPERIODEND** | NUMBER(20,5) | 0 | 期末应计利息 | 固定收益分析 |

### 🌍 货币和汇率
| 字段名 | 数据类型 | 示例值 | 业务含义 | 建模用途 |
|--------|----------|--------|----------|----------|
| **BOOKCCY** | VARCHAR2(5) | USD | 账户基础货币 | 货币风险评估 |
| **LOCALCCY** | VARCHAR2(5) | USD | 本地货币 | 汇率风险 |
| **FXRATE** | NUMBER(20,5) | 1 | 汇率 | 外汇风险分析 |

### 🎯 证券识别和特征
| 字段名 | 数据类型 | 示例值 | 业务含义 | 建模用途 |
|--------|----------|--------|----------|----------|
| **PRIMARYSECURITYSYMBOL** | VARCHAR2(50) | XX9P08428 | 主要证券代码 | 证券集中度分析 |
| **SECURITYDESCRIPTION** | VARCHAR2(255) | LB DIVERSIFIED ARBITRAGE FUND(SPV) LLC | 证券描述 | 投资类型分析 |
| **POSITIONTYPE** | VARCHAR2(40) | HEDGE FUND | 仓位类型 | 投资风格分类 |
| **CUSIP** | VARCHAR2(30) | XX9P08428 | CUSIP代码 | 证券唯一标识 |

### 📊 风险和评级指标
| 字段名 | 数据类型 | 示例值 | 业务含义 | 建模用途 |
|--------|----------|--------|----------|----------|
| **MOODYSRATING** | VARCHAR2(40) | - | 穆迪评级 | 信用风险评估 |
| **SPRATING** | VARCHAR2(40) | - | 标普评级 | 信用质量分析 |
| **COUPON** | NUMBER(38,12) | - | 票面利率 | 固定收益特征 |
| **INVESTMENTMATURITYDATE** | DATE | - | 投资到期日 | 期限结构分析 |

## 三级重要字段（补充信息）

### 🏢 管理和服务
| 字段名 | 数据类型 | 示例值 | 业务含义 | 建模用途 |
|--------|----------|--------|----------|----------|
| **PLANNER** | VARCHAR2(100) | BRIAN HAHN | 规划师姓名 | 顾问关系质量 |
| **PORTFOLIOMANAGER** | VARCHAR2(100) | UNMANAGED ACCOUNT | 投资组合经理 | 管理服务质量 |
| **MANAGED** | VARCHAR2(1) | N | 是否全权委托管理 | 服务模式分类 |

### 🏭 行业和地理分布
| 字段名 | 数据类型 | 示例值 | 业务含义 | 建模用途 |
|--------|----------|--------|----------|----------|
| **SECURITYSECTORLEVEL1** | VARCHAR2(50) | ALTERNATIVE INVESTMENTS | 一级行业分类 | 行业集中度分析 |
| **SECURITYSECTORLEVEL2** | VARCHAR2(50) | NB HEDGE FUNDS | 二级行业分类 | 细分行业风险 |
| **COUNTRYOFISSUANCE** | VARCHAR2(50) | US | 发行国 | 地理风险分布 |
| **COUNTRYOFRISK** | VARCHAR2(50) | US | 风险国家 | 地缘风险评估 |

### 📈 替代投资专用字段
| 字段名 | 数据类型 | 示例值 | 业务含义 | 建模用途 |
|--------|----------|--------|----------|----------|
| **BOOKALTSCOMMITTEDCAPITAL** | NUMBER(20,5) | - | 承诺资本 | 私募投资分析 |
| **BOOKALTSUNFUNDEDCOMMITMENT** | NUMBER(20,5) | - | 未出资承诺 | 流动性风险 |
| **ALTSMOIC** | VARCHAR2(5) | - | 投资倍数 | 私募投资表现 |
| **ALTSDVPI** | NUMBER(20,5) | 0.75 | 分配/实缴比率 | 回流资金比率 |

## 关键特征工程机会

### 📊 时间序列衍生特征

#### 1. 资产价值趋势特征
```sql
-- 30天价值变化率
(CURRENT_MARKET_VALUE - LAG_30D_MARKET_VALUE) / LAG_30D_MARKET_VALUE AS mv_change_30d

-- 价值波动性（30天标准差）
STDDEV(BOOKMARKETVALUEPERIODEND) OVER (
    PARTITION BY ACCOUNTSHORTNAME 
    ORDER BY BE_ASOF 
    ROWS 29 PRECEDING
) AS mv_volatility_30d

-- 最大回撤深度
(MAX_MV_30D - CURRENT_MV) / MAX_MV_30D AS max_drawdown_30d
```

#### 2. 未实现损益模式
```sql
-- 未实现损益率
BOOKUGL / NULLIF(BOOKMARKETVALUEPERIODEND, 0) AS unrealized_pnl_ratio

-- 损益趋势（7天移动平均）
AVG(BOOKUGL) OVER (
    PARTITION BY ACCOUNTSHORTNAME 
    ORDER BY BE_ASOF 
    ROWS 6 PRECEDING
) AS avg_ugl_7d

-- 损益稳定性
STDDEV(BOOKUGL) OVER (
    PARTITION BY ACCOUNTSHORTNAME 
    ORDER BY BE_ASOF 
    ROWS 29 PRECEDING
) AS ugl_stability_30d
```

#### 3. 持仓行为特征
```sql
-- 持仓集中度变化
COUNT(DISTINCT PRIMARYSECURITYSYMBOL) AS position_diversity

-- 资产类别分布变化
COUNT(DISTINCT ASSETCLASSLEVEL1) AS asset_class_diversity

-- 持仓周转率（数量变化）
ABS(QUANTITY - LAG(QUANTITY)) / LAG(QUANTITY) AS position_turnover
```

### 🎯 投资组合风险指标

#### 4. 风险管理特征
```sql
-- 投资组合β值（相对于基准的波动性）
CORR(daily_return, market_benchmark_return) AS portfolio_beta

-- 夏普比率代理指标
(AVG_DAILY_RETURN - RISK_FREE_RATE) / STDDEV_DAILY_RETURN AS sharpe_proxy

-- 下行风险（负收益的标准差）
STDDEV(CASE WHEN daily_return < 0 THEN daily_return END) AS downside_risk
```

#### 5. 流动性风险特征
```sql
-- 另类投资占比
SUM(CASE WHEN ASSETCLASSLEVEL1 = 'Alternatives' 
         THEN BOOKMARKETVALUEPERIODEND ELSE 0 END) / 
SUM(BOOKMARKETVALUEPERIODEND) AS alternatives_ratio

-- 未出资承诺比例
SUM(BOOKALTSUNFUNDEDCOMMITMENT) / SUM(BOOKMARKETVALUEPERIODEND) AS unfunded_ratio
```

## 数据质量考虑

### ⚠️ 潜在数据问题
1. **缺失值模式**:
   - 替代投资字段（BOOKALT*）仅对特定资产类型有值
   - 固定收益字段（COUPON, MATURITY）仅对债券类资产有效
   - 评级字段可能大量为空

2. **数据一致性检查**:
   ```sql
   -- 市值与价格数量一致性
   ABS(BOOKMARKETVALUEPERIODEND - (BOOKPRICEPERIODEND * QUANTITY)) < 0.01
   
   -- 未实现损益计算验证
   BOOKUGL ≈ BOOKMARKETVALUEPERIODEND - BOOKAMORTIZEDCOSTPERIODEND
   ```

3. **异常值检测**:
   - 市值突然大幅变化（>50%单日变化）
   - 负价格或负数量
   - 极端的未实现损益比率

### 📋 建模准备检查清单

#### 数据验证
- [ ] **时间序列完整性**: 检查BE_ASOF字段的连续性
- [ ] **账户关联验证**: 确保所有ACCOUNTSHORTNAME都能与beamaccount表关联
- [ ] **数值字段合理性**: 检查市值、价格等字段的数值范围
- [ ] **分类字段一致性**: 验证资产类别、策略名称等的标准化

#### 特征工程准备
- [ ] **时间窗口设计**: 确定7/30/90天的分析窗口
- [ ] **缺失值策略**: 针对不同字段类型制定填充策略
- [ ] **异常值处理**: 设定合理的上下限阈值
- [ ] **标准化策略**: 考虑不同账户规模的归一化方法

## 与其他表的关联策略

### 🔗 主要关联关系
```sql
-- 与账户基础信息关联
PROFITANDLOSSLITE p
JOIN beamaccount a ON p.ACCOUNTSHORTNAME = a.ACCOUNTSHORTNAME

-- 与交易记录关联（通过账户+日期）
PROFITANDLOSSLITE p  
JOIN IDRTRANSACTION t ON p.ACCOUNTSHORTNAME = t.ACCOUNTID
    AND p.BE_ASOF = t.EVENTDATE
```

### 📊 聚合分析策略
```sql
-- 账户级别日度聚合
SELECT 
    ACCOUNTSHORTNAME,
    BE_ASOF,
    SUM(BOOKMARKETVALUEPERIODEND) as total_portfolio_value,
    SUM(BOOKUGL) as total_unrealized_pnl,
    COUNT(DISTINCT PRIMARYSECURITYSYMBOL) as num_positions,
    COUNT(DISTINCT ASSETCLASSLEVEL1) as asset_class_diversity
FROM PROFITANDLOSSLITE 
GROUP BY ACCOUNTSHORTNAME, BE_ASOF;
```

---

**使用建议**: 
- 优先使用市值和未实现损益的时间序列特征
- 重点关注资产配置多样性的变化趋势  
- 将替代投资比例作为流动性风险的重要指标
- 结合交易频率数据分析客户参与度变化 