SELECT
    ID,
    ACCOUNTCLOSEDATE,
    ACCOUNTOPENDATE,
    BOOKCCY,
    CLASSIFICATION1,
    DOMICILECOUNTRY,
    DOMICILESTATE,
    ACCOUNTSTATUS,
    churn_flag,
    account_age_days
FROM (
    SELECT
        a.ID,
        a.ACCOUNTCLOSEDATE,
        a.ACCOUNTOPENDATE,
        a.BOOKCCY,
        a.CLASSIFICATION1,
        a.DOMICILECOUNTRY,
        a.DOMICILESTATE,
        a.ACCOUNTSTATUS,
        CASE WHEN a.ACCOUNTCLOSEDATE IS NULL THEN 0 ELSE 1 END AS churn_flag,
        FLOOR(
            CASE 
                WHEN a.ACCOUNTCLOSEDATE IS NULL 
                THEN SYSDATE - a.ACCOUNTOPENDATE 
                ELSE a.ACCOUNTCLOSEDATE - a.ACCOUNTOPENDATE 
            END
        ) AS account_age_days,
        ROW_NUMBER() OVER (
            PARTITION BY CASE WHEN a.ACCOUNTCLOSEDATE IS NULL THEN 0 ELSE 1 END
            ORDER BY ORA_HASH(a.ID)
        ) AS rn
    FROM beamaccount a
    WHERE a.TENANTID IN (58857, 58877, 58878, 78879)
)
WHERE rn <= 15
ORDER BY churn_flag, ID;
