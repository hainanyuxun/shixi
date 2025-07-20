#!/usr/bin/env python3
"""
InvestCloud Customer Churn Prediction Project - Account-Level Exploratory Data Analysis
Comprehensive EDA for understanding account-level churn patterns and behaviors.
Analyzes account lifecycle, performance metrics, and transaction patterns.

Author: InvestCloud Intern
Purpose: Account-level churn prediction EDA
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime, timedelta
import warnings
import logging
import os

warnings.filterwarnings('ignore')

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

# Set plotting style
plt.style.use('default')
sns.set_palette("husl")
plt.rcParams['figure.figsize'] = (12, 8)
plt.rcParams['font.size'] = 10

class AccountLevelEDA:
    """
    Account-level exploratory data analysis for churn prediction.
    Provides comprehensive analysis of account characteristics and behaviors.
    """
    
    def __init__(self):
        """Initialize account-level EDA."""
        self.account_df = None
        self.performance_df = None
        self.transaction_df = None
        self.current_date = datetime.now()
        
    def load_data(self, use_oracle=False):
        """
        Load data from Oracle database or sample CSV files.
        
        Args:
            use_oracle (bool): Whether to use Oracle database (True) or sample CSV files (False)
        """
        try:
            if use_oracle:
                logging.info("Loading data from Oracle database...")
                from account_level_data_extractor import AccountLevelDataExtractor
                
                # Create Oracle data extractor
                extractor = AccountLevelDataExtractor()
                
                # Initialize Oracle client
                if not extractor.initialize_oracle_client():
                    logging.error("Oracle client initialization failed, falling back to sample data")
                    return self._load_sample_data()
                
                # Connect to database
                if not extractor.connect_database():
                    logging.error("Database connection failed, falling back to sample data")
                    return self._load_sample_data()
                
                try:
                    # Extract data
                    results = extractor.extract_all_account_data()
                    
                    # Map to class attributes
                    self.account_df = results.get('account')
                    self.performance_df = results.get('performance')
                    self.transaction_df = results.get('transaction')
                    
                    # Check if data was successfully loaded
                    if any(df is None for df in [self.account_df, self.performance_df, self.transaction_df]):
                        logging.warning("Some data tables failed to extract, falling back to sample data")
                        return self._load_sample_data()
                    
                    logging.info("Oracle data loading successful")
                    
                finally:
                    extractor.disconnect_database()
            else:
                return self._load_sample_data()
            
            logging.info(f"Data loading completed - Accounts:{len(self.account_df)}, Performance:{len(self.performance_df)}, Transactions:{len(self.transaction_df)}")
            return True
            
        except Exception as e:
            logging.error(f"Data loading failed: {e}")
            logging.info("Falling back to sample data")
            return self._load_sample_data()
    
    def _load_sample_data(self):
        """Load sample data for EDA testing."""
        try:
            logging.info("Creating sample data for EDA...")
            
            # Create sample datasets
            self.account_df = self._create_sample_account_data()
            self.performance_df = self._create_sample_performance_data()
            self.transaction_df = self._create_sample_transaction_data()
            
            logging.info("Sample data created successfully")
            return True
            
        except Exception as e:
            logging.error(f"Sample data creation failed: {e}")
            return False
    
    def _create_sample_account_data(self):
        """Create sample account data for EDA."""
        np.random.seed(42)
        n_accounts = 2000
        
        # Create account open dates
        open_dates = pd.date_range('2018-01-01', '2023-12-31', periods=n_accounts)
        
        data = {
            'ACCOUNTID': range(1, n_accounts + 1),
            'ACCOUNTSHORTNAME': [f'ACC{i:06d}' for i in range(1, n_accounts + 1)],
            'CLIENTID': np.random.randint(1, 800, n_accounts),
            'ACCOUNTTYPE': np.random.choice(['Individual', 'Joint', 'Trust', 'Corporate', 'IRA'], 
                                          n_accounts, p=[0.4, 0.25, 0.15, 0.1, 0.1]),
            'CLASSIFICATION1': np.random.choice(['INDIVIDUAL', 'JOINT', 'TRUST', 'CORPORATE'], n_accounts),
            'ACCOUNTOPENDATE': open_dates,
            'ACCOUNTCLOSEDATE': [None] * n_accounts,
            'DOMICILECOUNTRY': np.random.choice(['US', 'CA', 'UK', 'DE', 'FR'], 
                                              n_accounts, p=[0.7, 0.1, 0.1, 0.05, 0.05]),
            'DOMICILESTATE': np.random.choice(['NY', 'CA', 'FL', 'TX', 'IL', None], 
                                            n_accounts, p=[0.2, 0.15, 0.1, 0.1, 0.05, 0.4]),
            'BOOKCCY': np.random.choice(['USD', 'EUR', 'GBP', 'CAD'], 
                                      n_accounts, p=[0.8, 0.1, 0.05, 0.05]),
            'CAPITALCOMMITMENTAMOUNT': np.random.lognormal(12, 1.5, n_accounts),
            'ACCOUNTOBJECTIVE': np.random.choice(['Growth', 'Income', 'Balanced', 'Conservative', 'Aggressive'], n_accounts),
            'CHURN_FLAG': np.random.choice([0, 1], n_accounts, p=[0.82, 0.18])
        }
        
        # Simulate churned accounts with close dates
        churn_mask = data['CHURN_FLAG'] == 1
        churn_indices = np.where(churn_mask)[0]
        for idx in churn_indices:
            # Close date between 30 days and 2 years after open
            days_to_close = np.random.randint(30, 730)
            close_date = data['ACCOUNTOPENDATE'][idx] + timedelta(days=days_to_close)
            if close_date <= datetime.now():
                data['ACCOUNTCLOSEDATE'][idx] = close_date
        
        return pd.DataFrame(data)
    
    def _create_sample_performance_data(self):
        """Create sample performance data for EDA."""
        np.random.seed(42)
        n_records = 100000
        
        accounts = [f'ACC{i:06d}' for i in range(1, 2001)]
        dates = pd.date_range('2022-01-01', '2024-01-01', freq='W')  # Weekly data
        
        data = {
            'ACCOUNTSHORTNAME': np.random.choice(accounts, n_records),
            'BE_ASOF': np.random.choice(dates, n_records),
            'ASSETCLASSLEVEL1': np.random.choice(['Equity', 'Fixed Income', 'Alternatives', 'Cash', 'Real Estate'], 
                                              n_records, p=[0.4, 0.25, 0.2, 0.1, 0.05]),
            'ASSETCLASSLEVEL2': np.random.choice(['US Equity', 'International Equity', 'Government Bonds', 
                                                'Corporate Bonds', 'Hedge Funds', 'Private Equity'], n_records),
            'BOOKMARKETVALUEPERIODEND': np.random.lognormal(10, 2, n_records),
            'BOOKUGL': np.random.normal(0, 5000, n_records),
            'QUANTITY': np.random.lognormal(5, 1.5, n_records),
            'ORIGINALCOST': np.random.lognormal(10, 2, n_records)
        }
        
        return pd.DataFrame(data)
    
    def _create_sample_transaction_data(self):
        """Create sample transaction data for EDA."""
        np.random.seed(42)
        n_records = 50000
        
        accounts = [f'ACC{i:06d}' for i in range(1, 2001)]
        dates = pd.date_range('2022-01-01', '2024-01-01', freq='D')
        
        data = {
            'ACCOUNTSHORTNAME': np.random.choice(accounts, n_records),
            'TRANSACTIONDATE': np.random.choice(dates, n_records),
            'EVENTTYPE': np.random.choice(['BUY', 'SELL', 'DIVIDEND', 'DEPOSIT', 'WITHDRAWAL', 'FEE'], 
                                        n_records, p=[0.25, 0.25, 0.15, 0.15, 0.15, 0.05]),
            'BOOKAMOUNT': np.random.normal(0, 50000, n_records),
            'QUANTITY': np.random.lognormal(3, 1, n_records),
            'BOOKCCY': np.random.choice(['USD', 'EUR', 'GBP'], n_records, p=[0.8, 0.15, 0.05])
        }
        
        return pd.DataFrame(data)
    
    def analyze_account_demographics(self):
        """Analyze account demographic characteristics and churn patterns."""
        logging.info("Analyzing account demographics...")
        
        fig, axes = plt.subplots(2, 3, figsize=(18, 12))
        fig.suptitle('Account Demographics Analysis', fontsize=16, fontweight='bold')
        
        # 1. Account Type Distribution
        ax1 = axes[0, 0]
        account_type_counts = self.account_df['ACCOUNTTYPE'].value_counts()
        ax1.pie(account_type_counts.values, labels=account_type_counts.index, autopct='%1.1f%%')
        ax1.set_title('Account Type Distribution')
        
        # 2. Churn Rate by Account Type
        ax2 = axes[0, 1]
        churn_by_type = self.account_df.groupby('ACCOUNTTYPE')['CHURN_FLAG'].agg(['count', 'mean']).reset_index()
        sns.barplot(data=churn_by_type, x='ACCOUNTTYPE', y='mean', ax=ax2)
        ax2.set_title('Churn Rate by Account Type')
        ax2.set_ylabel('Churn Rate')
        ax2.tick_params(axis='x', rotation=45)
        
        # 3. Geographic Distribution
        ax3 = axes[0, 2]
        country_counts = self.account_df['DOMICILECOUNTRY'].value_counts().head(10)
        sns.barplot(x=country_counts.values, y=country_counts.index, ax=ax3)
        ax3.set_title('Top 10 Countries by Account Count')
        ax3.set_xlabel('Number of Accounts')
        
        # 4. Currency Distribution
        ax4 = axes[1, 0]
        currency_counts = self.account_df['BOOKCCY'].value_counts()
        ax4.pie(currency_counts.values, labels=currency_counts.index, autopct='%1.1f%%')
        ax4.set_title('Account Currency Distribution')
        
        # 5. Churn Rate by Country
        ax5 = axes[1, 1]
        churn_by_country = self.account_df.groupby('DOMICILECOUNTRY')['CHURN_FLAG'].agg(['count', 'mean']).reset_index()
        churn_by_country = churn_by_country[churn_by_country['count'] >= 20]  # Filter countries with sufficient data
        sns.barplot(data=churn_by_country, x='DOMICILECOUNTRY', y='mean', ax=ax5)
        ax5.set_title('Churn Rate by Country (>20 accounts)')
        ax5.set_ylabel('Churn Rate')
        
        # 6. Capital Commitment Distribution
        ax6 = axes[1, 2]
        capital_commitment = self.account_df['CAPITALCOMMITMENTAMOUNT'].dropna()
        ax6.hist(np.log10(capital_commitment[capital_commitment > 0]), bins=30, alpha=0.7)
        ax6.set_title('Capital Commitment Distribution (log10)')
        ax6.set_xlabel('Log10(Capital Commitment)')
        ax6.set_ylabel('Frequency')
        
        plt.tight_layout()
        
        # Save plot
        plot_filename = f'../outputs/account_demographics_analysis_{datetime.now().strftime("%Y%m%d_%H%M%S")}.png'
        os.makedirs(os.path.dirname(plot_filename), exist_ok=True)
        plt.savefig(plot_filename, dpi=300, bbox_inches='tight')
        
        logging.info(f"Demographics analysis saved to: {plot_filename}")
        plt.show()
    
    def analyze_account_lifecycle(self):
        """Analyze account lifecycle patterns and churn timing."""
        logging.info("Analyzing account lifecycle...")
        
        # Calculate account age
        self.account_df['ACCOUNT_AGE_DAYS'] = (self.current_date - pd.to_datetime(self.account_df['ACCOUNTOPENDATE'])).dt.days
        self.account_df['ACCOUNT_AGE_YEARS'] = self.account_df['ACCOUNT_AGE_DAYS'] / 365.25
        
        fig, axes = plt.subplots(2, 2, figsize=(15, 12))
        fig.suptitle('Account Lifecycle Analysis', fontsize=16, fontweight='bold')
        
        # 1. Account Age Distribution
        ax1 = axes[0, 0]
        ax1.hist(self.account_df['ACCOUNT_AGE_YEARS'], bins=30, alpha=0.7, color='skyblue')
        ax1.set_title('Account Age Distribution')
        ax1.set_xlabel('Account Age (Years)')
        ax1.set_ylabel('Number of Accounts')
        
        # 2. Churn Rate by Account Age
        ax2 = axes[0, 1]
        age_bins = pd.cut(self.account_df['ACCOUNT_AGE_YEARS'], bins=10)
        churn_by_age = self.account_df.groupby(age_bins)['CHURN_FLAG'].mean()
        churn_by_age.plot(kind='bar', ax=ax2, color='lightcoral')
        ax2.set_title('Churn Rate by Account Age')
        ax2.set_ylabel('Churn Rate')
        ax2.set_xlabel('Account Age (Years)')
        ax2.tick_params(axis='x', rotation=45)
        
        # 3. Account Opening Trend
        ax3 = axes[1, 0]
        self.account_df['OPEN_YEAR_MONTH'] = pd.to_datetime(self.account_df['ACCOUNTOPENDATE']).dt.to_period('M')
        monthly_opens = self.account_df['OPEN_YEAR_MONTH'].value_counts().sort_index()
        monthly_opens.plot(ax=ax3, color='green')
        ax3.set_title('Account Opening Trend Over Time')
        ax3.set_ylabel('Number of New Accounts')
        ax3.tick_params(axis='x', rotation=45)
        
        # 4. Time to Churn Distribution
        ax4 = axes[1, 1]
        churned_accounts = self.account_df[self.account_df['CHURN_FLAG'] == 1].copy()
        if len(churned_accounts) > 0 and 'ACCOUNTCLOSEDATE' in churned_accounts.columns:
            churned_accounts['DAYS_TO_CHURN'] = (
                pd.to_datetime(churned_accounts['ACCOUNTCLOSEDATE']) - 
                pd.to_datetime(churned_accounts['ACCOUNTOPENDATE'])
            ).dt.days
            
            time_to_churn = churned_accounts['DAYS_TO_CHURN'].dropna()
            if len(time_to_churn) > 0:
                ax4.hist(time_to_churn, bins=30, alpha=0.7, color='red')
                ax4.set_title('Time to Churn Distribution')
                ax4.set_xlabel('Days from Open to Close')
                ax4.set_ylabel('Number of Churned Accounts')
            else:
                ax4.text(0.5, 0.5, 'No churn timing data available', 
                        horizontalalignment='center', verticalalignment='center', transform=ax4.transAxes)
        else:
            ax4.text(0.5, 0.5, 'No churn timing data available', 
                    horizontalalignment='center', verticalalignment='center', transform=ax4.transAxes)
        
        plt.tight_layout()
        
        # Save plot
        plot_filename = f'../outputs/account_lifecycle_analysis_{datetime.now().strftime("%Y%m%d_%H%M%S")}.png'
        os.makedirs(os.path.dirname(plot_filename), exist_ok=True)
        plt.savefig(plot_filename, dpi=300, bbox_inches='tight')
        
        logging.info(f"Lifecycle analysis saved to: {plot_filename}")
        plt.show()
    
    def analyze_portfolio_performance(self):
        """Analyze portfolio performance patterns and their relationship to churn."""
        if self.performance_df is None or len(self.performance_df) == 0:
            logging.warning("No performance data available for analysis")
            return
        
        logging.info("Analyzing portfolio performance...")
        
        # Convert date column
        self.performance_df['BE_ASOF'] = pd.to_datetime(self.performance_df['BE_ASOF'])
        
        # Get latest performance for each account
        latest_performance = self.performance_df.sort_values('BE_ASOF').groupby('ACCOUNTSHORTNAME').last().reset_index()
        
        # Merge with account data to get churn flags
        account_performance = self.account_df.merge(
            latest_performance, 
            left_on='ACCOUNTSHORTNAME', 
            right_on='ACCOUNTSHORTNAME', 
            how='inner'
        )
        
        fig, axes = plt.subplots(2, 3, figsize=(18, 12))
        fig.suptitle('Portfolio Performance Analysis', fontsize=16, fontweight='bold')
        
        # 1. Market Value Distribution
        ax1 = axes[0, 0]
        market_values = account_performance['BOOKMARKETVALUEPERIODEND']
        ax1.hist(np.log10(market_values[market_values > 0]), bins=30, alpha=0.7, color='blue')
        ax1.set_title('Portfolio Market Value Distribution (log10)')
        ax1.set_xlabel('Log10(Market Value)')
        ax1.set_ylabel('Number of Accounts')
        
        # 2. P&L Distribution
        ax2 = axes[0, 1]
        pnl_values = account_performance['BOOKUGL']
        ax2.hist(pnl_values, bins=50, alpha=0.7, color='green')
        ax2.set_title('Unrealized P&L Distribution')
        ax2.set_xlabel('Unrealized P&L')
        ax2.set_ylabel('Number of Accounts')
        
        # 3. Asset Class Distribution
        ax3 = axes[0, 2]
        asset_class_counts = self.performance_df['ASSETCLASSLEVEL1'].value_counts()
        ax3.pie(asset_class_counts.values, labels=asset_class_counts.index, autopct='%1.1f%%')
        ax3.set_title('Asset Class Distribution')
        
        # 4. Market Value vs Churn
        ax4 = axes[1, 0]
        churned = account_performance[account_performance['CHURN_FLAG'] == 1]['BOOKMARKETVALUEPERIODEND']
        active = account_performance[account_performance['CHURN_FLAG'] == 0]['BOOKMARKETVALUEPERIODEND']
        
        ax4.boxplot([np.log10(active[active > 0]), np.log10(churned[churned > 0])], 
                   labels=['Active', 'Churned'])
        ax4.set_title('Market Value Distribution by Churn Status')
        ax4.set_ylabel('Log10(Market Value)')
        
        # 5. P&L vs Churn
        ax5 = axes[1, 1]
        churned_pnl = account_performance[account_performance['CHURN_FLAG'] == 1]['BOOKUGL']
        active_pnl = account_performance[account_performance['CHURN_FLAG'] == 0]['BOOKUGL']
        
        ax5.boxplot([active_pnl, churned_pnl], labels=['Active', 'Churned'])
        ax5.set_title('P&L Distribution by Churn Status')
        ax5.set_ylabel('Unrealized P&L')
        
        # 6. Churn Rate by Asset Class
        ax6 = axes[1, 2]
        churn_by_asset = account_performance.groupby('ASSETCLASSLEVEL1')['CHURN_FLAG'].agg(['count', 'mean']).reset_index()
        churn_by_asset = churn_by_asset[churn_by_asset['count'] >= 10]  # Filter for sufficient data
        sns.barplot(data=churn_by_asset, x='ASSETCLASSLEVEL1', y='mean', ax=ax6)
        ax6.set_title('Churn Rate by Primary Asset Class')
        ax6.set_ylabel('Churn Rate')
        ax6.tick_params(axis='x', rotation=45)
        
        plt.tight_layout()
        
        # Save plot
        plot_filename = f'../outputs/portfolio_performance_analysis_{datetime.now().strftime("%Y%m%d_%H%M%S")}.png'
        os.makedirs(os.path.dirname(plot_filename), exist_ok=True)
        plt.savefig(plot_filename, dpi=300, bbox_inches='tight')
        
        logging.info(f"Performance analysis saved to: {plot_filename}")
        plt.show()
    
    def analyze_transaction_behavior(self):
        """Analyze transaction behavior patterns and their relationship to churn."""
        if self.transaction_df is None or len(self.transaction_df) == 0:
            logging.warning("No transaction data available for analysis")
            return
        
        logging.info("Analyzing transaction behavior...")
        
        # Convert date column
        self.transaction_df['TRANSACTIONDATE'] = pd.to_datetime(self.transaction_df['TRANSACTIONDATE'])
        
        # Calculate transaction statistics by account
        txn_stats = self.transaction_df.groupby('ACCOUNTSHORTNAME').agg({
            'TRANSACTIONDATE': ['count', 'max', 'min'],
            'BOOKAMOUNT': ['sum', 'mean', 'std'],
            'EVENTTYPE': 'nunique'
        }).reset_index()
        
        # Flatten column names
        txn_stats.columns = ['ACCOUNTSHORTNAME', 'TXN_COUNT', 'LAST_TXN_DATE', 'FIRST_TXN_DATE',
                            'TOTAL_AMOUNT', 'AVG_AMOUNT', 'STD_AMOUNT', 'NUM_EVENT_TYPES']
        
        # Calculate days since last transaction
        txn_stats['DAYS_SINCE_LAST_TXN'] = (self.current_date - txn_stats['LAST_TXN_DATE']).dt.days
        
        # Merge with account data
        account_txn = self.account_df.merge(txn_stats, on='ACCOUNTSHORTNAME', how='left')
        account_txn = account_txn.fillna(0)
        
        fig, axes = plt.subplots(2, 3, figsize=(18, 12))
        fig.suptitle('Transaction Behavior Analysis', fontsize=16, fontweight='bold')
        
        # 1. Transaction Count Distribution
        ax1 = axes[0, 0]
        txn_counts = account_txn['TXN_COUNT']
        ax1.hist(txn_counts[txn_counts > 0], bins=30, alpha=0.7, color='purple')
        ax1.set_title('Transaction Count Distribution')
        ax1.set_xlabel('Number of Transactions')
        ax1.set_ylabel('Number of Accounts')
        
        # 2. Transaction Types Distribution
        ax2 = axes[0, 1]
        event_type_counts = self.transaction_df['EVENTTYPE'].value_counts()
        ax2.pie(event_type_counts.values, labels=event_type_counts.index, autopct='%1.1f%%')
        ax2.set_title('Transaction Type Distribution')
        
        # 3. Days Since Last Transaction
        ax3 = axes[0, 2]
        days_since_last = account_txn['DAYS_SINCE_LAST_TXN']
        ax3.hist(days_since_last[days_since_last < 365], bins=30, alpha=0.7, color='orange')
        ax3.set_title('Days Since Last Transaction (<1 year)')
        ax3.set_xlabel('Days Since Last Transaction')
        ax3.set_ylabel('Number of Accounts')
        
        # 4. Transaction Activity vs Churn
        ax4 = axes[1, 0]
        churned_txn = account_txn[account_txn['CHURN_FLAG'] == 1]['TXN_COUNT']
        active_txn = account_txn[account_txn['CHURN_FLAG'] == 0]['TXN_COUNT']
        
        ax4.boxplot([active_txn, churned_txn], labels=['Active', 'Churned'])
        ax4.set_title('Transaction Count by Churn Status')
        ax4.set_ylabel('Number of Transactions')
        
        # 5. Days Since Last Transaction vs Churn
        ax5 = axes[1, 1]
        churned_days = account_txn[account_txn['CHURN_FLAG'] == 1]['DAYS_SINCE_LAST_TXN']
        active_days = account_txn[account_txn['CHURN_FLAG'] == 0]['DAYS_SINCE_LAST_TXN']
        
        ax5.boxplot([active_days, churned_days], labels=['Active', 'Churned'])
        ax5.set_title('Days Since Last Transaction by Churn Status')
        ax5.set_ylabel('Days Since Last Transaction')
        
        # 6. Transaction Amount vs Churn
        ax6 = axes[1, 2]
        churned_amt = account_txn[account_txn['CHURN_FLAG'] == 1]['AVG_AMOUNT']
        active_amt = account_txn[account_txn['CHURN_FLAG'] == 0]['AVG_AMOUNT']
        
        ax6.boxplot([active_amt[active_amt != 0], churned_amt[churned_amt != 0]], 
                   labels=['Active', 'Churned'])
        ax6.set_title('Average Transaction Amount by Churn Status')
        ax6.set_ylabel('Average Transaction Amount')
        
        plt.tight_layout()
        
        # Save plot
        plot_filename = f'../outputs/transaction_behavior_analysis_{datetime.now().strftime("%Y%m%d_%H%M%S")}.png'
        os.makedirs(os.path.dirname(plot_filename), exist_ok=True)
        plt.savefig(plot_filename, dpi=300, bbox_inches='tight')
        
        logging.info(f"Transaction analysis saved to: {plot_filename}")
        plt.show()
    
    def generate_eda_summary_report(self):
        """Generate comprehensive EDA summary report."""
        logging.info("Generating EDA summary report...")
        
        report = []
        report.append("=" * 80)
        report.append("ACCOUNT-LEVEL CHURN PREDICTION - EDA SUMMARY REPORT")
        report.append("=" * 80)
        report.append(f"Analysis Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report.append("")
        
        # Account Overview
        report.append("ACCOUNT OVERVIEW:")
        report.append(f"  • Total Accounts: {len(self.account_df):,}")
        report.append(f"  • Churned Accounts: {self.account_df['CHURN_FLAG'].sum():,}")
        report.append(f"  • Overall Churn Rate: {self.account_df['CHURN_FLAG'].mean():.1%}")
        report.append("")
        
        # Account Demographics
        report.append("ACCOUNT DEMOGRAPHICS:")
        top_account_type = self.account_df['ACCOUNTTYPE'].value_counts().index[0]
        report.append(f"  • Most Common Account Type: {top_account_type}")
        
        top_country = self.account_df['DOMICILECOUNTRY'].value_counts().index[0]
        country_pct = self.account_df['DOMICILECOUNTRY'].value_counts().iloc[0] / len(self.account_df) * 100
        report.append(f"  • Most Common Country: {top_country} ({country_pct:.1f}%)")
        
        top_currency = self.account_df['BOOKCCY'].value_counts().index[0]
        currency_pct = self.account_df['BOOKCCY'].value_counts().iloc[0] / len(self.account_df) * 100
        report.append(f"  • Most Common Currency: {top_currency} ({currency_pct:.1f}%)")
        report.append("")
        
        # Account Lifecycle
        if 'ACCOUNT_AGE_YEARS' in self.account_df.columns:
            avg_age = self.account_df['ACCOUNT_AGE_YEARS'].mean()
            report.append("ACCOUNT LIFECYCLE:")
            report.append(f"  • Average Account Age: {avg_age:.1f} years")
            
            # Churn by age groups
            age_groups = pd.cut(self.account_df['ACCOUNT_AGE_YEARS'], bins=[0, 1, 2, 5, float('inf')], 
                              labels=['<1 year', '1-2 years', '2-5 years', '>5 years'])
            churn_by_age_group = self.account_df.groupby(age_groups)['CHURN_FLAG'].mean()
            highest_churn_age = churn_by_age_group.idxmax()
            highest_churn_rate = churn_by_age_group.max()
            report.append(f"  • Highest Churn Age Group: {highest_churn_age} ({highest_churn_rate:.1%})")
            report.append("")
        
        # Performance Insights
        if self.performance_df is not None and len(self.performance_df) > 0:
            report.append("PORTFOLIO PERFORMANCE:")
            
            latest_performance = self.performance_df.sort_values('BE_ASOF').groupby('ACCOUNTSHORTNAME').last()
            total_market_value = latest_performance['BOOKMARKETVALUEPERIODEND'].sum()
            avg_market_value = latest_performance['BOOKMARKETVALUEPERIODEND'].mean()
            
            report.append(f"  • Total Assets Under Management: ${total_market_value:,.0f}")
            report.append(f"  • Average Account Value: ${avg_market_value:,.0f}")
            
            top_asset_class = self.performance_df['ASSETCLASSLEVEL1'].value_counts().index[0]
            asset_class_pct = self.performance_df['ASSETCLASSLEVEL1'].value_counts().iloc[0] / len(self.performance_df) * 100
            report.append(f"  • Most Popular Asset Class: {top_asset_class} ({asset_class_pct:.1f}%)")
            report.append("")
        
        # Transaction Insights
        if self.transaction_df is not None and len(self.transaction_df) > 0:
            report.append("TRANSACTION BEHAVIOR:")
            
            total_transactions = len(self.transaction_df)
            unique_accounts_transacting = self.transaction_df['ACCOUNTSHORTNAME'].nunique()
            avg_transactions_per_account = total_transactions / unique_accounts_transacting
            
            report.append(f"  • Total Transactions: {total_transactions:,}")
            report.append(f"  • Accounts with Transactions: {unique_accounts_transacting:,}")
            report.append(f"  • Average Transactions per Account: {avg_transactions_per_account:.1f}")
            
            top_event_type = self.transaction_df['EVENTTYPE'].value_counts().index[0]
            event_type_pct = self.transaction_df['EVENTTYPE'].value_counts().iloc[0] / len(self.transaction_df) * 100
            report.append(f"  • Most Common Transaction Type: {top_event_type} ({event_type_pct:.1f}%)")
            report.append("")
        
        # Key Insights
        report.append("KEY INSIGHTS FOR CHURN PREDICTION:")
        report.append("  • Focus on accounts with declining transaction activity")
        report.append("  • Monitor accounts with poor performance metrics")
        report.append("  • Pay attention to newer accounts (higher churn risk)")
        report.append("  • Consider geographic and demographic factors in modeling")
        report.append("")
        
        # Next Steps
        report.append("RECOMMENDED NEXT STEPS:")
        report.append("  1. Develop comprehensive feature engineering based on EDA findings")
        report.append("  2. Build predictive models focusing on identified risk factors")
        report.append("  3. Implement early warning system for high-risk accounts")
        report.append("  4. Develop targeted retention strategies by customer segment")
        
        report_text = "\n".join(report)
        
        # Save report
        report_filename = f'../data/reports/account_eda_summary_{datetime.now().strftime("%Y%m%d_%H%M%S")}.txt'
        os.makedirs(os.path.dirname(report_filename), exist_ok=True)
        
        with open(report_filename, 'w', encoding='utf-8') as f:
            f.write(report_text)
        
        logging.info(f"EDA summary report saved to: {report_filename}")
        print(report_text)
    
    def run_complete_eda(self):
        """Run complete exploratory data analysis."""
        logging.info("Starting comprehensive account-level EDA...")
        
        # Run all analysis components
        self.analyze_account_demographics()
        self.analyze_account_lifecycle()
        self.analyze_portfolio_performance()
        self.analyze_transaction_behavior()
        self.generate_eda_summary_report()
        
        logging.info("Complete EDA analysis finished")

def main(use_oracle=False):
    """
    Main function for account-level EDA.
    
    Args:
        use_oracle (bool): Whether to use Oracle database (True) or sample data (False)
    """
    print("📊 InvestCloud Customer Churn Prediction - Account-Level EDA")
    print("=" * 75)
    
    if use_oracle:
        print("📊 Using Oracle database data source")
    else:
        print("📊 Using sample data source")
    
    # Initialize EDA
    eda = AccountLevelEDA()
    
    # Load data
    if not eda.load_data(use_oracle=use_oracle):
        print("❌ Data loading failed, program exiting")
        return
    
    # Run complete EDA
    eda.run_complete_eda()
    
    print("\n✅ Account-level EDA completed!")
    print("🎯 Ready to proceed with feature engineering")

if __name__ == "__main__":
    main() 