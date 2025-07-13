import pandas as pd

# Load the CSVs
df_accounts = pd.read_csv('Sample_DATA/Account_sampledata.csv')
df_pnl = pd.read_csv('Sample_DATA/PNL_sampledata.csv')
df_transactions = pd.read_csv('Sample_DATA/Transaction_sampledata.csv')


# Function: Aggregate PNL monthly per account
def aggregate_pnl_monthly(df_pnl):
    df = df_pnl.copy()
    df['BE_ASOF'] = pd.to_datetime(df['BE_ASOF'])
    df = df.sort_values(['ACCOUNTID', 'BE_ASOF'])

    df['ACCOUNTID_MONTH'] = df['ACCOUNTID'].astype(str) + '_' + df['BE_ASOF'].dt.to_period('M').astype(str)

    grouped = df.groupby('ACCOUNTID_MONTH')

    agg = grouped.agg(
        ACCOUNTID=('ACCOUNTID', 'first'),
        MONTH=('BE_ASOF', lambda x: x.max().strftime('%Y-%m')),
        NUMBER_OF_POSITION=('ASSETCLASSLEVEL1', 'nunique'),
        END_BOOKUGL=('DAILY_BOOKUGL', 'last'),
        START_BOOKUGL=('DAILY_BOOKUGL', 'first'),
        MAX_BOOKUGL=('DAILY_BOOKUGL', 'max'),
        UGL_STD=('DAILY_BOOKUGL', 'std'),
        GAIN_DAYS=('DAILY_BOOKUGL', lambda x: (x > 0).sum()),
        LOSS_DAYS=('DAILY_BOOKUGL', lambda x: (x < 0).sum()),
        LAST_QUANTITY=('TOTAL_DAILY_QUANTITY', 'last'),
        FIRST_QUANTITY=('TOTAL_DAILY_QUANTITY', 'first'),
        QUANTITY_CHANGE_COUNT=('TOTAL_DAILY_QUANTITY', lambda x: (x != x.shift()).sum()),
        LAST_MARKET_VALUE=('DAY_BOOK_MARKET_VALUE', 'last'),
        FIRST_MARKET_VALUE=('DAY_BOOK_MARKET_VALUE', 'first'),
        MAX_MARKET_VALUE=('DAY_BOOK_MARKET_VALUE', 'max'),
        MIN_MARKET_VALUE=('DAY_BOOK_MARKET_VALUE', 'min'),
        ORIGINAL_INVESTED=('DAILY_ORIGINAL_COST_SUM', 'first'),
        AVG_PRICE_PERIODEND=('AVG_BOOK_PRICE_PERIODEND', 'mean'),
        AVG_UNIT_COST=('AVG_BOOK_UNIT_COST', 'mean'),
    ).reset_index()

    # Derived features
    agg['UGL_CHANGE_PCT'] = (agg['END_BOOKUGL'] - agg['START_BOOKUGL']) / agg['START_BOOKUGL'].abs().replace(0, pd.NA)
    agg['UGL_MAX_OPPORTUNITY_LOSS'] = agg['MAX_BOOKUGL'] - agg['END_BOOKUGL']
    agg['QUANTITY_NET_CHANGE'] = agg['LAST_QUANTITY'] - agg['FIRST_QUANTITY']
    agg['QUANTITY_CHANGE_PCT'] = agg['QUANTITY_NET_CHANGE'] / agg['FIRST_QUANTITY'].replace(0, pd.NA)
    agg['MARKET_VALUE_NET_CHANGE'] = agg['LAST_MARKET_VALUE'] - agg['FIRST_MARKET_VALUE']
    agg['MARKET_VALUE_CHANGE_PCT'] = (agg['LAST_MARKET_VALUE'] - agg['FIRST_MARKET_VALUE']) / agg[
        'FIRST_MARKET_VALUE'].replace(0, pd.NA)
    agg['MAX_DRAW_DOWN'] = agg['MAX_MARKET_VALUE'] - agg['MIN_MARKET_VALUE']
    agg['PRICE_TO_COST_RATIO'] = agg['AVG_PRICE_PERIODEND'] / agg['AVG_UNIT_COST'].replace(0, pd.NA)

    # Drop intermediate columns if not needed
    agg.drop(columns=[
        'START_BOOKUGL', 'FIRST_QUANTITY', 'LAST_MARKET_VALUE',
        'FIRST_MARKET_VALUE', 'MAX_MARKET_VALUE', 'MIN_MARKET_VALUE',
        'AVG_PRICE_PERIODEND', 'AVG_UNIT_COST'
    ], inplace=True)

    return agg


# Run the aggregation
pnl_agg = aggregate_pnl_monthly(df_pnl)

# Save to CSV
pnl_agg.to_csv('PNL_monthly_aggregated.csv', index=False)
print("PNL monthly aggregated data saved as 'PNL_monthly_aggregated.csv'")

def aggregate_transactions_monthly(df_transactions):
    df = df_transactions.copy()
    df['EVENTDATE'] = pd.to_datetime(df['EVENTDATE'])
    df['ACCOUNTID'] = df['ACCOUNTID'].astype(str)

    df['ACCOUNTID_MONTH'] = df['ACCOUNTID'] + '_' + df['EVENTDATE'].dt.to_period('M').astype(str)

    transaction_amount_total = df.groupby('ACCOUNTID_MONTH')['BOOKAMOUNT'].apply(lambda x: x.abs().sum())

    grouped = df.groupby('ACCOUNTID_MONTH')

    agg = grouped.agg(
        ACCOUNTID=('ACCOUNTID', 'first'),
        MONTH=('EVENTDATE', lambda x: x.max().strftime('%Y-%m')),
        NUM_TRANSACTIONS=('BOOKAMOUNT', 'count'),
        TRADE_DAYS=('EVENTDATE', lambda x: x.dt.date.nunique()),
        TRADED_ASSET_CLASSES=('ASSETCLASSLEVEL1', 'nunique'),
        CASH_FLOW=('BOOKAMOUNT', 'sum'),  # net cash in/out
        AVG_BOOKAMOUNT=('BOOKAMOUNT', 'mean'),
        TOTAL_QUANTITY_TRADED=('QUANTITY', 'sum'),
        AVG_QUANTITY_TRADED=('QUANTITY', 'mean'),
        REALIZED_GAIN=('BOOKTOTALGAIN', 'sum'),
        REALIZED_LOSS=('BOOKTOTALLOSS', 'sum')
    ).reset_index()

    agg['TRANSACTION_AMOUNT_TOTAL'] = agg['ACCOUNTID_MONTH'].map(transaction_amount_total)

    agg['NET_REALIZED_PNL'] = agg['REALIZED_GAIN'] + agg['REALIZED_LOSS']

    agg['NET_REALIZED_PNL_PCT'] = agg['NET_REALIZED_PNL'] / agg['TRANSACTION_AMOUNT_TOTAL'].replace(0, pd.NA)
    return agg

transaction_agg = aggregate_transactions_monthly(df_transactions)

# Save to CSV
transaction_agg.to_csv('Transaction_monthly_aggregated.csv', index=False)
print("Transaction monthly aggregated saved as 'Transaction_monthly_aggregated.csv'")

from pandas.tseries.offsets import MonthEnd

# === 2. Parse Dates ===
df_accounts['ACCOUNTCLOSEDATE'] = pd.to_datetime(df_accounts['ACCOUNTCLOSEDATE'], errors='coerce')
df_accounts['ACCOUNTOPENDATE'] = pd.to_datetime(df_accounts['ACCOUNTOPENDATE'], errors='coerce')

# === 3. Set Today's Date for Reference ===
today = pd.Timestamp.today().replace(hour=0, minute=0, second=0, microsecond=0)

# === 4. Function to Generate Monthly Rows for Each Account ===
def generate_monthly_rows(row, today=today):
    if pd.isnull(row['ACCOUNTOPENDATE']):
        return []
    if pd.notnull(row['ACCOUNTCLOSEDATE']):
        end_month = row['ACCOUNTCLOSEDATE'].replace(day=1) + MonthEnd(0)
    else:
        end_month = today.replace(day=1) + MonthEnd(0)
    start_month = max(row['ACCOUNTOPENDATE'].replace(day=1) + MonthEnd(0), end_month - pd.DateOffset(months=11))
    if start_month > end_month:
        return []
    months = pd.date_range(start=start_month, end=end_month, freq='ME')
    churn_flags = [
        1 if (pd.notnull(row['ACCOUNTCLOSEDATE']) and m.year == row['ACCOUNTCLOSEDATE'].year and m.month == row['ACCOUNTCLOSEDATE'].month)
        else 0
        for m in months
    ]
    base_row = row.to_dict()
    rows = []
    for m, churn in zip(months, churn_flags):
        row_dict = {**base_row}
        row_dict['ACCOUNT_MONTH'] = m
        row_dict['CHURN_FLAG'] = churn
        # Update ACCOUNT_AGE_DAYS to be days from open to this month end
        row_dict['ACCOUNT_AGE_DAYS'] = (m - row['ACCOUNTOPENDATE']).days
        rows.append(row_dict)
    return rows

# === 5. Apply Function to All Accounts and Flatten ===
rows = []
for _, row in df_accounts.iterrows():
    rows.extend(generate_monthly_rows(row))

Account_monthly_aggregated = pd.DataFrame(rows)

# === 6. Create ACCOUNTID_MONTH Column ===
Account_monthly_aggregated['ACCOUNTID_MONTH'] = (
    Account_monthly_aggregated['ID'].astype(str) + '_' +
    Account_monthly_aggregated['ACCOUNT_MONTH'].dt.strftime('%Y-%m')
)

# === 7. Reorder Columns (ACCOUNTID_MONTH First, Remove ACCOUNT_MONTH) ===
cols = ['ACCOUNTID_MONTH'] + [col for col in Account_monthly_aggregated.columns if col not in ['ACCOUNTID_MONTH', 'ACCOUNT_MONTH']]
Account_monthly_aggregated = Account_monthly_aggregated[cols]

# === 8. Export to CSV ===
Account_monthly_aggregated.to_csv('Account_monthly_aggregated.csv', index=False)
print("Exported to Account_monthly_aggregated.csv")

# === 9. Show Sample Output ===
print(Account_monthly_aggregated.head())
print(f"Total rows: {len(Account_monthly_aggregated)}")

# Merge accounts with PNL (left join)
df_merged = pd.merge(Account_monthly_aggregated, pnl_agg, on='ACCOUNTID_MONTH', how='left', suffixes=('', '_PNL'))

# Merge the result with transactions (left join)
df_merged = pd.merge(df_merged, transaction_agg, on='ACCOUNTID_MONTH', how='left', suffixes=('', '_TRANS'))

# Save the final merged table to CSV
df_merged.to_csv('Merged_sampledata.csv', index=False)
print("Exported to Merged_sampledata.csv")
