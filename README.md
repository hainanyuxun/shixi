# Customer Churn Prediction Project - Account Level Analysis

## Project Overview

This is an **account-level churn prediction project** for InvestCloud platform, focusing on predicting account closure risk through comprehensive analysis of account lifecycle, portfolio performance, and transaction behaviors. The project uses Oracle UAT database integration and provides production-ready machine learning models.

## Core Features

### 🎯 Prediction Target
- **Account-Level Churn Prediction**: Primary focus on account closure prediction
- **Account Lifecycle Analysis**: Based on ACCOUNTCLOSEDATE and account status
- **Risk Scoring Framework**: Comprehensive risk assessment for account retention

### 📊 Data Sources
- **BEAMACCOUNT**: Account master data, lifecycle, and demographics
- **PROFITANDLOSSLITE**: Portfolio performance and market values
- **IDRTRANSACTION**: Transaction behavior and activity patterns
- **Oracle UAT Database**: Real-time data integration

### 🔧 Technology Stack
- **Python 3.8+**: Primary development language
- **Oracle Database**: UAT environment data source
- **Scikit-learn**: Machine learning framework
- **Pandas/NumPy**: Data processing and analysis
- **Matplotlib/Seaborn**: Data visualization
- **oracledb**: Oracle database connectivity

## Project Structure

```
customer_churn_prediction/
├── README.md                                    # Project documentation
├── requirements.txt                             # Python dependencies
├── setup_oracle.py                            # Oracle environment setup
├── .gitignore                                  # Git ignore configuration
│
├── docs/                                       # Project documentation
│   ├── Customer_Churn_Prediction_Project_Guide.md
│   ├── beamaccount_table_fields_reference.md
│   ├── profitandlosslite_table_fields_reference.md
│   ├── IDRTRANSACTION_table_fields_reference.md
│   └── Oracle_Database_Analysis.md
│
├── src/                                        # Source code directory
│   ├── account_level_data_extractor.py        # Oracle data extraction
│   ├── account_level_feature_engineering.py   # Account feature engineering
│   ├── account_churn_model_development.py     # Model training & evaluation
│   ├── account_level_eda.py                   # Exploratory data analysis
│   ├── run_account_churn_pipeline.py          # Unified pipeline runner
│   └── [legacy files...]                      # Previous development files
│
├── models/                                     # Trained models
│   ├── best_account_churn_model_*.joblib
│   └── account_feature_scaler_*.joblib
│
├── data/                                       # Data directory (excluded from VCS)
│   ├── raw/                                   # Raw extracted data
│   ├── processed/                             # Processed feature data
│   └── reports/                               # Analysis reports
│
└── outputs/                                   # Analysis outputs
    ├── account_demographics_analysis_*.png
    ├── account_lifecycle_analysis_*.png
    ├── portfolio_performance_analysis_*.png
    └── account_model_performance_*.png
```

## Quick Start

### 🚀 Method 1: Complete Account-Level Pipeline (Recommended)
```bash
# 1. Clone the project
git clone https://github.com/your-username/customer_churn_prediction.git
cd customer_churn_prediction

# 2. Install dependencies
pip install -r requirements.txt

# 3. Run the complete account-level churn prediction pipeline
cd src
python run_account_churn_pipeline.py
```

### 🛠️ Method 2: Oracle Environment Auto-Setup
```bash
# 1. Run Oracle environment setup (if using real data)
python setup_oracle.py

# 2. Follow prompts to configure Oracle connection
# 3. Run the pipeline with Oracle data
cd src
python run_account_churn_pipeline.py
```

### 🛠️ 方式2: 手动安装配置

#### 1. 克隆项目
```bash
git clone https://github.com/your-username/customer_churn_prediction.git
cd customer_churn_prediction
```

#### 2. 创建虚拟环境
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
# 或
venv\Scripts\activate     # Windows
```

#### 3. 安装依赖
```bash
pip install -r requirements.txt
```

#### 4. Oracle环境配置（可选）
如需使用Oracle数据库：
- 下载并安装 [Oracle Instant Client](https://www.oracle.com/database/technologies/instant-client/downloads.html)
- 解压到 `C:\oracle\instantclient_21_18` (Windows) 或 `/usr/local/oracle/instantclient_21_18` (Linux/macOS)
- 配置环境变量PATH

#### 5. 数据库配置（可选）
- 修改 `src/oracle_data_extractor.py` 中的数据库连接信息
- 确保有相关表的访问权限
- 参考 `docs/SQL_Data_Export_Guide.md` 进行数据导出

## 使用方法

### 数据源配置

项目支持两种数据源：

#### 🔷 方式1: Oracle数据库（推荐用于生产环境）
1. **安装Oracle Instant Client**
   - 下载并解压Oracle Instant Client到 `C:\oracle\instantclient_21_18`
   - 或修改 `src/oracle_data_extractor.py` 中的路径配置

2. **配置数据库连接**
   ```python
   # 在 oracle_data_extractor.py 中配置
   username = "BGRO_citangk"
   password = "Cici0511"
   dsn = "UAT7ora:1521/ORAUAT7PRIV"
   ```

3. **运行数据提取**
   ```bash
   cd src
   python oracle_data_extractor.py
   ```

#### 🔷 方式2: 样本CSV文件（用于测试和开发）
使用项目根目录下的样本数据文件进行测试。

### 核心流程

#### 1. 数据预处理和特征工程
```bash
cd src
# 交互式选择数据源
python run_feature_engineering.py

# 或直接指定数据源
python tier1_feature_engineering.py  # 使用样本数据
```

#### 2. 探索性数据分析
```bash
cd src
python user_level_eda.py
```

#### 3. 模型训练
```bash
cd src
python baseline_model_development.py
```

#### 4. 数据架构验证
```bash
cd src
python data_architecture_validation.py
```

## 核心功能

### 🔍 特征工程
- **用户参与度评分**: 基于联系信息完整度、安全设置等
- **交易行为分析**: 频率衰退、金额波动、时间模式
- **投资表现指标**: 收益率、风险调整收益、最大回撤
- **资产价值趋势**: 市值变化、未实现损益、投资组合稳定性

### 📈 模型算法
- **逻辑回归**: 基线模型，提供良好的可解释性
- **随机森林**: 处理非线性关系和特征交互
- **XGBoost**: 高性能梯度提升算法
- **LightGBM**: 快速训练的梯度提升框架

### 📊 评估指标
- **准确率 (Accuracy)**: 整体预测正确率
- **精确率 (Precision)**: 流失预测的准确性
- **召回率 (Recall)**: 流失客户的识别率
- **F1-Score**: 精确率和召回率的调和平均
- **AUC-ROC**: 模型区分能力评估

## 业务价值

### 💼 应用场景
1. **客户保留策略**: 识别高风险客户，制定个性化保留方案
2. **资源优化配置**: 将有限的客户服务资源投入到关键客户
3. **产品改进指导**: 基于流失原因分析改进产品和服务
4. **收入预测**: 预测客户流失对收入的影响

### 📋 输出结果
- **客户风险评分**: 0-1之间的流失概率评分
- **风险因素分析**: 主要影响流失的特征因素
- **客户分层**: 基于风险评分的客户分层管理
- **预警报告**: 定期的高风险客户预警列表

## 贡献指南

1. Fork 项目
2. 创建功能分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 创建 Pull Request

## 许可证

本项目采用 MIT 许可证 - 详见 [LICENSE](LICENSE) 文件

## 联系信息

- 项目维护者: [Your Name]
- 邮箱: [your.email@example.com]
- 项目链接: [https://github.com/your-username/customer_churn_prediction](https://github.com/your-username/customer_churn_prediction)

## 更新日志

### v1.0.0 (2024-12-19)
- 初始版本发布
- 完成基础特征工程和模型开发
- 实现用户级别流失预测
- 添加数据架构验证功能

---

**注意**: 本项目包含敏感的客户数据，请确保在使用过程中遵守相关的数据保护法规和公司政策。 