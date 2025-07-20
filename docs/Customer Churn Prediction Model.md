**Project Title:**  
Customer Churn Prediction Model

**Brief Description/Overview:**  
The objective of this project is to design and implement a predictive analytics solution to identify customers at risk of churning, using historical customer behavior and transaction data. The outcome will enable proactive retention strategies by surfacing early indicators of churn.

**Objectives:**

- Build a robust predictive model for customer churn
- Identify key features influencing churn
- Deploy a prototype to test
- Create a detailed technical documentation and a presentation for non-technical stakeholders
- Stretch goal: implement deployable code, which includes dockerisation and Api endpoints

**Project Components:**

1. **Data Collection & Cleaning**
    - Collect anonymized internal customer datasets (e.g., demographics, transactions, usage history, etc.)
    - EDA (descriptive statistics and visualizations to understand data), handling missing values, outliers, inconsistent records
2. **Feature Engineering**
    - Create new features from raw data (e.g., tenure, usage frequency, interaction recency, etc.)
    - Encode categorical variables, normalize/scale numerical features as needed
    - Feature selection using statistical or model-based techniques
3. **Model Training**
    - Train and compare multiple ML models (e.g., logistic regression, random forest)
    - Use cross-validation and hyperparameter tuning for optimal performance
4. **Model Evaluation**
    - Assess performance using metrics like precision, recall, and AUC
    - Include business-aligned metrics like precision at top N% or lift charts
5. **Deployment**
    - Integrate the best model into a simple web interface
    - Deploy locally in docker
    - Basic validation and error handling

**Data and Tools:**

- **Datasets:** Internal customer records (anonymized)
- **Tools:** Python, scikit-learn, pandas, Flask

**Timeline:**

- **Week 1:** Project onboarding, data collection and cleaning, EDA
- **Week 2:** Feature engineering, initial model training
- **Week 3:** Model tuning and evaluation, interpretation of results and features
- **Week 4:** Deployment of prototype, documentation & presentation

**Expected Deliverables:**

- Cleaned dataset with engineered features
- Trained and evaluated ML models (code + model artifacts)
- Simple web interface for churn prediction
- Project documentation (technical documentation, summary report, presenatation)

**Evaluation Criteria:**

- Model accuracy and business-relevant metrics (e.g., precision at top 10%)
- Usability of the deployed prototype

**References/Notes:**

- Refer to scikit-learn documentation and relevant papers on churn prediction
- Consult with business stakeholders for feedback