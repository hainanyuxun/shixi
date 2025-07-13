WITH sampled_accounts AS (
    SELECT
        a.ID AS ACCOUNT_ID,
        a.ACCOUNTCLOSEDATE,
        CASE WHEN a.ACCOUNTCLOSEDATE IS NULL THEN 0 ELSE 1 END AS churn_flag
    FROM (
        SELECT
            a.*,
            ROW_NUMBER() OVER (
                PARTITION BY CASE WHEN a.ACCOUNTCLOSEDATE IS NULL THEN 0 ELSE 1 END
                ORDER BY ORA_HASH(a.ID)
            ) AS rn
        FROM beamaccount a
        WHERE a.TENANTID IN (58857, 58877, 58878, 78879)
    ) a
    WHERE a.rn <= 15
)
SELECT
    t.ACCOUNTID,
    t.BOOKAMOUNT,
    t.ASSETCLASSLEVEL1,
    t.EVENTDATE,
    t.TRADEDATE,
    t.QUANTITY,
    t.BOOKTOTALLOSS,
    t.BOOKTOTALGAIN
FROM sampled_accounts sa
JOIN IDRTRANSACTION t ON sa.ACCOUNT_ID = t.ACCOUNTID
WHERE (
    sa.churn_flag = 1
    AND t.EVENTDATE >= ADD_MONTHS(sa.ACCOUNTCLOSEDATE, -12)
    AND t.EVENTDATE <= sa.ACCOUNTCLOSEDATE
)
OR (
    sa.churn_flag = 0
    AND t.EVENTDATE >= ADD_MONTHS(TRUNC(SYSDATE), -12)
)
ORDER BY t.ACCOUNTID, t.EVENTDATE;
