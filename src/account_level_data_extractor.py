#!/usr/bin/env python3
"""
InvestCloud Customer Churn Prediction Project - Account-Level Data Extractor
Oracle Database connector for extracting account-level data for churn prediction analysis.
Connects to UAT environment and extracts core tables: BEAMACCOUNT, PROFITANDLOSSLITE, IDRTRANSACTION.

Author: InvestCloud Intern
Purpose: Account-level churn prediction model development
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
        logging.FileHandler(f'account_data_extraction_{datetime.now().strftime("%Y%m%d_%H%M%S")}.log'),
        logging.StreamHandler(sys.stdout)
    ]
)

class AccountLevelDataExtractor:
    """
    Oracle database data extractor for account-level churn prediction.
    Extracts and processes core tables for building account churn features.
    """
    
    def __init__(self, oracle_client_path=None):
        """
        Initialize the account-level data extractor.
        
        Args:
            oracle_client_path (str): Path to Oracle Instant Client (defaults to standard Windows path)
        """
        # Oracle client configuration
        if oracle_client_path is None:
            oracle_client_path = r"C:\oracle\instantclient_21_18"
        
        self.oracle_client_path = oracle_client_path
        
        # Database connection configuration for UAT environment
        self.username = "BGRO_citangk"
        self.password = "Cici0511"
        self.dsn = "UAT7ora:1521/ORAUAT7PRIV"
        
        # Tenant IDs for the analysis (InvestCloud business units)
        self.tenant_ids = [58857, 58877, 58878, 78879]
        
        # Data storage
        self.connection = None
        self.data_cache = {}
        
        # Analysis parameters
        self.lookback_days = 730  # 2 years of historical data
        self.churn_definition_days = 90  # Account considered churned if closed 90+ days ago
        
    def initialize_oracle_client(self):
        """Initialize Oracle Instant Client."""
        try:
            logging.info(f"Initializing Oracle client at path: {self.oracle_client_path}")
            oracledb.init_oracle_client(lib_dir=self.oracle_client_path)
            logging.info("Oracle client initialization successful")
            return True
        except Exception as e:
            logging.error(f"Oracle client initialization failed: {e}")
            return False
    
    def connect_database(self):
        """Establish connection to Oracle database."""
        try:
            logging.info("Connecting to Oracle UAT database...")
            self.connection = oracledb.connect(
                user=self.username, 
                password=self.password, 
                dsn=self.dsn
            )
            logging.info("Database connection successful")
            return True
        except Exception as e:
            logging.error(f"Database connection failed: {e}")
            return False
    
    def disconnect_database(self):
        """Close database connection."""
        if self.connection:
            self.connection.close()
            logging.info("Database connection closed")
    
    def extract_account_data(self, save_to_csv=True):
        """
        Extract BEAMACCOUNT table data for account-level churn analysis.
        Focus on account lifecycle, demographics, and basic characteristics.
        
        Args:
            save_to_csv (bool): Whether to save data to CSV file
            
        Returns:
            pd.DataFrame: Account master data
        """
        logging.info("Extracting BEAMACCOUNT table data for account-level analysis...")
        
        query = """
        SELECT
           acc.ACCOUNTID,
           acc.ACCOUNTSHORTNAME,
           acc.CLIENTID,
           acc.ACCOUNTTYPE,
           acc.ACCOUNTOWNERTYPE,
           acc.CLASSIFICATION1,
           acc.ACCOUNTOPENDATE,
           acc.ACCOUNTCLOSEDATE,
           acc.ACCOUNTSTATUS,
           acc.ACCOUNTREOPENDATE,
           acc.DOMICILECOUNTRY,
           acc.DOMICILESTATE,
           acc.LOCATION,
           acc.BOOKCCY,
           acc.CUSTOMERTAXSTATUS,
           acc.ACCOUNTOBJECTIVE,
           acc.ACCOUNTSUBOBJECTIVE,
           acc.ACCOUNTSTRATEGYNAME,
           acc.CAPITALCOMMITMENTAMOUNT,
           acc.CAPITALCOMMITMENTDATE,
           acc.BILLINGINCEPTIONDATE,
           acc.INVESTMENTADVISORYTERMDATE,
           acc.PERFBEGINDATE,
           acc.CREATEDDATE,
           acc.MODIFIEDDATE,
           acc.TENANTID
        FROM SNAPSHOT sn
        JOIN BEAMACCOUNT acc ON acc.BE_SNAPSHOTID = sn.ID
        WHERE acc.TENANTID IN ({})
           AND sn.BE_CURRIND = 'Y'
           AND sn.DATACLASS = 'BEAMACCOUNT'
           AND acc.ACCOUNTOPENDATE >= DATE '{}' - INTERVAL '{}' DAY
        """.format(
            ','.join(map(str, self.tenant_ids)),
            datetime.now().strftime('%Y-%m-%d'),
            self.lookback_days
        )
        
        try:
            logging.info("Executing account data query...")
            df = pd.read_sql(query, self.connection)
            
            # Create churn flag based on account close date
            current_date = datetime.now()
            churn_cutoff = current_date - timedelta(days=self.churn_definition_days)
            
            df['CHURN_FLAG'] = np.where(
                (df['ACCOUNTCLOSEDATE'].notna()) & 
                (pd.to_datetime(df['ACCOUNTCLOSEDATE']) <= churn_cutoff), 
                1, 0
            )
            
            logging.info(f"Account data extraction successful: {len(df):,} records")
            logging.info(f"Unique accounts: {df['ACCOUNTID'].nunique():,}")
            logging.info(f"Churned accounts: {df['CHURN_FLAG'].sum():,} ({df['CHURN_FLAG'].mean()*100:.1f}%)")
            
            if save_to_csv:
                filename = '../data/raw/account_master.csv'
                os.makedirs(os.path.dirname(filename), exist_ok=True)
                df.to_csv(filename, index=False)
                logging.info(f"Account data saved to: {filename}")
            
            self.data_cache['account'] = df
            return df
            
        except Exception as e:
            logging.error(f"Account data extraction failed: {e}")
            return None
    
    def extract_account_performance_data(self, save_to_csv=True):
        """
        Extract PROFITANDLOSSLITE table data for account performance analysis.
        Focus on market values, P&L, and asset allocation patterns.
        
        Args:
            save_to_csv (bool): Whether to save data to CSV file
            
        Returns:
            pd.DataFrame: Account performance time series data
        """
        logging.info("Extracting PROFITANDLOSSLITE table for account performance analysis...")
        
        # Calculate date range for analysis
        end_date = datetime.now()
        start_date = end_date - timedelta(days=self.lookback_days)
        
        query = """
        SELECT
           pnl.ACCOUNTSHORTNAME,
           pnl.BE_ASOF,
           pnl.ASSETCLASSLEVEL1,
           pnl.ASSETCLASSLEVEL2,
           pnl.ASSETCLASSLEVEL3,
           pnl.STRATEGYNAME,
           pnl.BOOKMARKETVALUEPERIODEND,
           pnl.BOOKUGL,
           pnl.QUANTITY,
           pnl.AVERAGEBOOKUNITCOST,
           pnl.BOOKPRICEPERIODEND,
           pnl.ORIGINALCOST,
           pnl.BOOKAMORTIZEDCOSTPERIODEND,
           pnl.ANNUALINCOME,
           pnl.BOOKCCY,
           pnl.LOCALCCY,
           pnl.FXRATE,
           pnl.TENANTID
        FROM SNAPSHOT sn
        JOIN PROFITANDLOSSLITE pnl ON pnl.BE_SNAPSHOTID = sn.ID
        WHERE pnl.TENANTID IN ({})
           AND sn.BE_CURRIND = 'Y'
           AND sn.DATACLASS = 'PROFITANDLOSSLITE'
           AND pnl.BE_ASOF >= DATE '{}'
           AND pnl.BE_ASOF <= DATE '{}'
        """.format(
            ','.join(map(str, self.tenant_ids)),
            start_date.strftime('%Y-%m-%d'),
            end_date.strftime('%Y-%m-%d')
        )
        
        try:
            logging.info("Executing performance data query (this may take 5-10 minutes)...")
            df = pd.read_sql(query, self.connection)
            
            # Convert date column
            df['BE_ASOF'] = pd.to_datetime(df['BE_ASOF'])
            
            logging.info(f"Performance data extraction successful: {len(df):,} records")
            logging.info(f"Unique accounts: {df['ACCOUNTSHORTNAME'].nunique():,}")
            logging.info(f"Date range: {df['BE_ASOF'].min()} to {df['BE_ASOF'].max()}")
            logging.info(f"Total market value: ${df['BOOKMARKETVALUEPERIODEND'].sum():,.2f}")
            
            if save_to_csv:
                filename = '../data/raw/account_performance.csv'
                os.makedirs(os.path.dirname(filename), exist_ok=True)
                df.to_csv(filename, index=False)
                logging.info(f"Performance data saved to: {filename}")
            
            self.data_cache['performance'] = df
            return df
            
        except Exception as e:
            logging.error(f"Performance data extraction failed: {e}")
            return None
    
    def extract_account_transaction_data(self, save_to_csv=True):
        """
        Extract IDRTRANSACTION table data for account transaction behavior analysis.
        Focus on transaction patterns, frequency, and volumes.
        
        Args:
            save_to_csv (bool): Whether to save data to CSV file
            
        Returns:
            pd.DataFrame: Account transaction history data
        """
        logging.info("Extracting IDRTRANSACTION table for transaction behavior analysis...")
        
        # Calculate date range for analysis
        end_date = datetime.now()
        start_date = end_date - timedelta(days=self.lookback_days)
        
        query = """
        SELECT
           txn.ACCOUNTSHORTNAME,
           txn.TRANSACTIONDATE,
           txn.EFFECTIVEDATE,
           txn.EVENTTYPE,
           txn.BOOKAMOUNT,
           txn.LOCALAMOUNT,
           txn.BOOKNETCASH,
           txn.QUANTITY,
           txn.FOREIGNACCOUNTINGKEY,
           txn.BOOKCCY,
           txn.LOCALCCY,
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
            logging.info("Executing transaction data query...")
            df = pd.read_sql(query, self.connection)
            
            # Convert date columns
            df['TRANSACTIONDATE'] = pd.to_datetime(df['TRANSACTIONDATE'])
            df['EFFECTIVEDATE'] = pd.to_datetime(df['EFFECTIVEDATE'])
            
            logging.info(f"Transaction data extraction successful: {len(df):,} records")
            logging.info(f"Unique accounts: {df['ACCOUNTSHORTNAME'].nunique():,}")
            logging.info(f"Total transaction amount: ${df['BOOKAMOUNT'].abs().sum():,.2f}")
            logging.info(f"Date range: {df['TRANSACTIONDATE'].min()} to {df['TRANSACTIONDATE'].max()}")
            
            if save_to_csv:
                filename = '../data/raw/account_transactions.csv'
                os.makedirs(os.path.dirname(filename), exist_ok=True)
                df.to_csv(filename, index=False)
                logging.info(f"Transaction data saved to: {filename}")
            
            self.data_cache['transaction'] = df
            return df
            
        except Exception as e:
            logging.error(f"Transaction data extraction failed: {e}")
            return None
    
    def extract_all_account_data(self):
        """
        Extract all core data tables for account-level churn analysis.
        
        Returns:
            dict: Dictionary containing all extracted dataframes
        """
        logging.info("Starting comprehensive account-level data extraction...")
        
        results = {}
        
        # Extract account master data
        results['account'] = self.extract_account_data()
        
        # Extract account performance data
        results['performance'] = self.extract_account_performance_data()
        
        # Extract account transaction data
        results['transaction'] = self.extract_account_transaction_data()
        
        # Generate data quality report
        self.generate_data_quality_report(results)
        
        return results
    
    def generate_data_quality_report(self, data_dict):
        """
        Generate comprehensive data quality report for extracted data.
        
        Args:
            data_dict (dict): Dictionary of extracted dataframes
        """
        logging.info("Generating data quality report...")
        
        report = []
        report.append("=" * 80)
        report.append("ACCOUNT-LEVEL CHURN PREDICTION - DATA QUALITY REPORT")
        report.append("=" * 80)
        report.append(f"Extraction Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report.append(f"Tenant IDs: {', '.join(map(str, self.tenant_ids))}")
        report.append(f"Analysis Period: {self.lookback_days} days")
        report.append(f"Churn Definition: Account closed {self.churn_definition_days}+ days ago")
        report.append("")
        
        for table_name, df in data_dict.items():
            if df is not None:
                report.append(f"{table_name.upper()} TABLE:")
                report.append(f"  - Total Records: {len(df):,}")
                report.append(f"  - Columns: {len(df.columns)}")
                
                if table_name == 'account':
                    report.append(f"  - Unique Accounts: {df['ACCOUNTID'].nunique():,}")
                    if 'CHURN_FLAG' in df.columns:
                        churn_rate = df['CHURN_FLAG'].mean() * 100
                        report.append(f"  - Churned Accounts: {df['CHURN_FLAG'].sum():,} ({churn_rate:.1f}%)")
                
                elif table_name == 'performance':
                    report.append(f"  - Unique Accounts: {df['ACCOUNTSHORTNAME'].nunique():,}")
                    report.append(f"  - Date Range: {df['BE_ASOF'].min()} to {df['BE_ASOF'].max()}")
                    total_mv = df['BOOKMARKETVALUEPERIODEND'].sum()
                    report.append(f"  - Total Market Value: ${total_mv:,.2f}")
                
                elif table_name == 'transaction':
                    report.append(f"  - Unique Accounts: {df['ACCOUNTSHORTNAME'].nunique():,}")
                    report.append(f"  - Date Range: {df['TRANSACTIONDATE'].min()} to {df['TRANSACTIONDATE'].max()}")
                    total_amt = df['BOOKAMOUNT'].abs().sum()
                    report.append(f"  - Total Transaction Volume: ${total_amt:,.2f}")
                
                # Check for missing values
                null_counts = df.isnull().sum()
                high_null_cols = null_counts[null_counts > len(df) * 0.3].index.tolist()
                if high_null_cols:
                    report.append(f"  - High Missing Value Columns (>30%): {', '.join(high_null_cols[:3])}")
                
                report.append("")
            else:
                report.append(f"{table_name.upper()} TABLE: EXTRACTION FAILED")
                report.append("")
        
        report_text = "\n".join(report)
        
        # Save report
        report_filename = f'../data/reports/account_data_quality_report_{datetime.now().strftime("%Y%m%d_%H%M%S")}.txt'
        os.makedirs(os.path.dirname(report_filename), exist_ok=True)
        
        with open(report_filename, 'w', encoding='utf-8') as f:
            f.write(report_text)
        
        logging.info(f"Data quality report saved to: {report_filename}")
        print(report_text)

def main():
    """
    Main function for account-level data extraction.
    """
    print("InvestCloud Customer Churn Prediction - Account-Level Data Extractor")
    print("=" * 80)
    
    # Create data extractor
    extractor = AccountLevelDataExtractor()
    
    try:
        # Initialize Oracle client
        if not extractor.initialize_oracle_client():
            print("Oracle client initialization failed. Please check configuration.")
            return
        
        # Connect to database
        if not extractor.connect_database():
            print("Database connection failed. Please check connection details.")
            return
        
        # Extract all account-level data
        results = extractor.extract_all_account_data()
        
        # Summary statistics
        success_count = sum(1 for df in results.values() if df is not None)
        total_count = len(results)
        
        print(f"\nData extraction completed: {success_count}/{total_count} tables successfully extracted")
        
        if success_count > 0:
            print("\nAll data saved to ../data/raw/ directory")
            print("Ready to proceed with account-level feature engineering")
        
    except Exception as e:
        logging.error(f"Data extraction error: {e}")
        print(f"Error: {e}")
    
    finally:
        # Close database connection
        extractor.disconnect_database()

if __name__ == "__main__":
    main() 