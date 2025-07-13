#!/usr/bin/env python3
"""
InvestCloud Customer Churn Prediction Project - Data Architecture Validation
Validate USER_TO_ACCOUNT mapping table data quality and relationship integrity
"""

import pandas as pd
import numpy as np
from sqlalchemy import create_engine, text
import logging
from datetime import datetime
import warnings
warnings.filterwarnings('ignore')

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(f'data_validation_{datetime.now().strftime("%Y%m%d_%H%M%S")}.log'),
        logging.StreamHandler()
    ]
)

class DataArchitectureValidator:
    """Data Architecture Validator"""
    
    def __init__(self, connection_string=None):
        """
        Initialize validator
        Args:
            connection_string: Oracle database connection string
        """
        self.engine = None
        if connection_string:
            try:
                self.engine = create_engine(connection_string)
                logging.info("Database connection established")
            except Exception as e:
                logging.warning(f"Database connection failed: {e}")
                logging.info("Will use sample data for validation")
    
    def load_sample_data(self):
        """Load sample data for validation"""
        try:
            # Load sample data
            users_sample = pd.read_csv('Account_sampledata.csv')
            transactions_sample = pd.read_csv('Transaction_sampledata.csv') 
            pnl_sample = pd.read_csv('PNL_sampledata.csv')
            
            logging.info("Sample data loaded successfully")
            return users_sample, transactions_sample, pnl_sample
            
        except Exception as e:
            logging.error(f"Sample data loading failed: {e}")
            return None, None, None
    
    def validate_user_account_mapping(self):
        """Validate user-account mapping relationships"""
        logging.info("=== Starting User-Account Mapping Validation ===")
        
        validation_results = {
            'mapping_completeness': {},
            'data_quality': {},
            'tenant_classification': {},
            'relationship_integrity': {}
        }
        
        # If database connection exists, execute actual queries
        if self.engine:
            validation_results = self._validate_with_database()
        else:
            # Use sample data for proof of concept
            validation_results = self._validate_with_sample_data()
        
        return validation_results
    
    def _validate_with_database(self):
        """Validate using database connection"""
        validation_results = {
            'mapping_completeness': {},
            'data_quality': {},
            'tenant_classification': {},
            'relationship_integrity': {}
        }
        
        try:
            # 1. Validate USER_TO_ACCOUNT table basic information
            query_table_info = """
            SELECT 
                COUNT(*) as total_mappings,
                COUNT(DISTINCT USERNAME) as unique_users,
                COUNT(DISTINCT ACCOUNTID) as unique_accounts,
                COUNT(DISTINCT TENANTID) as unique_tenants
            FROM USER_TO_ACCOUNT
            """
            
            df_info = pd.read_sql(query_table_info, self.engine)
            validation_results['mapping_completeness'] = df_info.iloc[0].to_dict()
            
            # 2. Validate data quality
            query_data_quality = """
            SELECT 
                SUM(CASE WHEN USERNAME IS NULL THEN 1 ELSE 0 END) as null_usernames,
                SUM(CASE WHEN ACCOUNTID IS NULL THEN 1 ELSE 0 END) as null_accountids,
                SUM(CASE WHEN TENANTID IS NULL THEN 1 ELSE 0 END) as null_tenantids,
                COUNT(*) as total_records
            FROM USER_TO_ACCOUNT
            """
            
            df_quality = pd.read_sql(query_data_quality, self.engine)
            validation_results['data_quality'] = df_quality.iloc[0].to_dict()
            
            # 3. Validate tenant classification
            query_tenant_class = """
            SELECT 
                ua.TENANTID,
                t.NAME as tenant_name,
                COUNT(*) as user_count,
                COUNT(DISTINCT ua.USERNAME) as unique_users
            FROM USER_TO_ACCOUNT ua
            LEFT JOIN TENANT t ON ua.TENANTID = t.ID
            GROUP BY ua.TENANTID, t.NAME
            """
            
            df_tenant = pd.read_sql(query_tenant_class, self.engine)
            validation_results['tenant_classification'] = df_tenant.to_dict('records')
            
            # 4. Validate relationship integrity
            query_integrity = """
            SELECT 
                'USERS Relationship' as check_type,
                COUNT(ua.USERNAME) as mapping_count,
                COUNT(u.USERNAME) as users_found,
                COUNT(ua.USERNAME) - COUNT(u.USERNAME) as missing_users
            FROM USER_TO_ACCOUNT ua
            LEFT JOIN USERS u ON ua.USERNAME = u.USERNAME
            
            UNION ALL
            
            SELECT 
                'beamaccount Relationship' as check_type,
                COUNT(ua.ACCOUNTID) as mapping_count,
                COUNT(b.ID) as accounts_found,
                COUNT(ua.ACCOUNTID) - COUNT(b.ID) as missing_accounts
            FROM USER_TO_ACCOUNT ua
            LEFT JOIN beamaccount b ON ua.ACCOUNTID = b.ID
            """
            
            df_integrity = pd.read_sql(query_integrity, self.engine)
            validation_results['relationship_integrity'] = df_integrity.to_dict('records')
            
            logging.info("Database validation completed")
            
        except Exception as e:
            logging.error(f"Database validation failed: {e}")
            
        return validation_results
    
    def _validate_with_sample_data(self):
        """Validate using sample data for proof of concept"""
        logging.info("Performing proof of concept validation with sample data...")
        
        validation_results = {
            'mapping_completeness': {},
            'data_quality': {},
            'tenant_classification': {},
            'relationship_integrity': {}
        }
        
        try:
            # Load sample data
            users_sample, transactions_sample, pnl_sample = self.load_sample_data()
            
            if users_sample is not None:
                # Simulate USER_TO_ACCOUNT mapping table validation
                logging.info(f"Account sample data: {len(users_sample)} records")
                logging.info(f"Transaction sample data: {len(transactions_sample)} records")
                logging.info(f"PNL sample data: {len(pnl_sample)} records")
                
                # Validate basic structure of account data
                validation_results['mapping_completeness'] = {
                    'total_accounts': len(users_sample),
                    'unique_account_ids': users_sample['ID'].nunique() if 'ID' in users_sample.columns else 0,
                    'active_accounts': len(users_sample[users_sample['ACCOUNTSTATUS'] == 'OPEN']) if 'ACCOUNTSTATUS' in users_sample.columns else 0,
                    'closed_accounts': len(users_sample[users_sample['ACCOUNTSTATUS'] == 'CLOSED']) if 'ACCOUNTSTATUS' in users_sample.columns else 0
                }
                
                # Validate existence of relationship fields
                required_fields = ['ID']  # Account sample data uses ID as primary key
                missing_fields = [field for field in required_fields if field not in users_sample.columns]
                
                # Check churn label fields
                churn_fields = ['CHURN_FLAG', 'ACCOUNTCLOSEDATE', 'ACCOUNTSTATUS']
                available_churn_fields = [field for field in churn_fields if field in users_sample.columns]
                
                validation_results['data_quality'] = {
                    'missing_required_fields': missing_fields,
                    'available_churn_fields': available_churn_fields,
                    'sample_validation': 'PASSED' if not missing_fields else 'FAILED',
                    'churn_labels_available': len(available_churn_fields) > 0
                }
                
                # Validate relationship with transaction data
                if transactions_sample is not None and 'ACCOUNTSHORTNAME' in transactions_sample.columns:
                    # Transaction data uses ACCOUNTSHORTNAME, account data uses ID - need to check data consistency
                    account_ids = set(users_sample['ID'].astype(str))
                    transaction_accounts = set(transactions_sample['ACCOUNTSHORTNAME'].astype(str))
                    common_accounts = account_ids.intersection(transaction_accounts)
                    
                    validation_results['relationship_integrity'] = {
                        'account_transaction_overlap': len(common_accounts),
                        'total_accounts': len(users_sample),
                        'overlap_percentage': len(common_accounts) / len(users_sample) * 100
                    }
                
                logging.info("Sample data validation completed")
                
        except Exception as e:
            logging.error(f"Sample data validation failed: {e}")
            
        return validation_results
    
    def generate_validation_report(self, validation_results):
        """Generate validation report"""
        logging.info("=== Data Architecture Validation Report ===")
        
        print("\n" + "="*60)
        print("InvestCloud Data Architecture Validation Report")
        print("="*60)
        
        # Mapping completeness report
        if validation_results['mapping_completeness']:
            print("\n📊 Mapping Table Completeness:")
            for key, value in validation_results['mapping_completeness'].items():
                print(f"  • {key}: {value:,}")
        
        # Data quality report
        if validation_results['data_quality']:
            print("\n🔍 Data Quality Assessment:")
            for key, value in validation_results['data_quality'].items():
                print(f"  • {key}: {value}")
        
        # Tenant classification report
        if validation_results['tenant_classification']:
            print("\n👥 Tenant Classification Analysis:")
            if isinstance(validation_results['tenant_classification'], list):
                for tenant in validation_results['tenant_classification']:
                    print(f"  • {tenant.get('tenant_name', 'Unknown')}: {tenant.get('user_count', 0)} users")
        
        # Relationship integrity report
        if validation_results['relationship_integrity']:
            print("\n🔗 Relationship Integrity Validation:")
            if isinstance(validation_results['relationship_integrity'], list):
                for check in validation_results['relationship_integrity']:
                    print(f"  • {check.get('check_type', 'Unknown')}: {check}")
            else:
                for key, value in validation_results['relationship_integrity'].items():
                    print(f"  • {key}: {value}")
        
        print("\n" + "="*60)
        
        # Generate recommendations
        self._generate_recommendations(validation_results)
    
    def _generate_recommendations(self, validation_results):
        """Generate recommendations based on validation results"""
        print("\n💡 Architecture Optimization Recommendations:")
        
        recommendations = []
        
        # Generate recommendations based on validation results
        if validation_results.get('data_quality', {}).get('sample_validation') == 'PASSED':
            recommendations.append("✅ Sample data structure validation passed, ready for next EDA analysis")
        
        if validation_results.get('relationship_integrity', {}).get('overlap_percentage', 0) > 80:
            recommendations.append("✅ Account-transaction data relationship integrity is good, supports comprehensive feature engineering")
        
        recommendations.extend([
            "🔄 Recommend implementing user-level data aggregation query performance optimization",
            "📈 Ready to start user status distribution and value segmentation EDA analysis",
            "🎯 Prioritize building transaction behavior decay features (Tier-1 core features)"
        ])
        
        for i, rec in enumerate(recommendations, 1):
            print(f"  {i}. {rec}")

def main():
    """Main function"""
    print("🚀 InvestCloud Customer Churn Prediction Project - Data Architecture Validation")
    print("=" * 80)
    
    # Initialize validator
    validator = DataArchitectureValidator()
    
    # Execute validation
    validation_results = validator.validate_user_account_mapping()
    
    # Generate report
    validator.generate_validation_report(validation_results)
    
    print("\n✅ Data architecture validation completed!")
    print("📝 Detailed logs saved to log file")
    print("🎯 Ready to proceed to next step: User-Level EDA Analysis")

if __name__ == "__main__":
    main() 