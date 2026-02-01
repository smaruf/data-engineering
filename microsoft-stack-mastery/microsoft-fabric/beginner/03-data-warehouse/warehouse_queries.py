"""
Microsoft Fabric Data Warehouse Queries Module

This module demonstrates querying Fabric Data Warehouses using T-SQL,
including cross-database queries and analytics patterns.

Author: Data Engineering Team
License: MIT
"""

import os
import logging
from typing import Optional, List, Dict, Any
import pandas as pd
from dotenv import load_dotenv

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()


def show_query_examples():
    """
    Display comprehensive T-SQL query examples for Fabric Warehouse.
    """
    print("=" * 80)
    print("Microsoft Fabric Data Warehouse Query Examples")
    print("=" * 80)
    
    print("\n1. Basic SELECT Queries")
    print("-" * 80)
    print("""
    -- Simple select with filtering
    SELECT 
        CustomerName,
        Email,
        Country
    FROM [dw].[DimCustomer]
    WHERE Country = 'USA' AND IsCurrent = 1;
    
    -- Aggregation query
    SELECT 
        Category,
        COUNT(*) AS ProductCount,
        AVG(UnitPrice) AS AvgPrice,
        MAX(UnitPrice) AS MaxPrice
    FROM [dw].[DimProduct]
    GROUP BY Category
    ORDER BY ProductCount DESC;
    """)
    
    print("\n2. JOIN Operations")
    print("-" * 80)
    print("""
    -- Sales with customer and product details
    SELECT 
        c.CustomerName,
        p.ProductName,
        d.Date,
        f.Quantity,
        f.TotalAmount
    FROM [dw].[FactSales] f
    INNER JOIN [dw].[DimCustomer] c ON f.CustomerKey = c.CustomerKey
    INNER JOIN [dw].[DimProduct] p ON f.ProductKey = p.ProductKey
    INNER JOIN [dw].[DimDate] d ON f.DateKey = d.DateKey
    WHERE c.IsCurrent = 1
        AND d.Year = 2024;
    """)
    
    print("\n3. Window Functions")
    print("-" * 80)
    print("""
    -- Running total and rank
    SELECT 
        CustomerName,
        OrderDate,
        TotalAmount,
        SUM(TotalAmount) OVER (
            PARTITION BY CustomerKey 
            ORDER BY OrderDate
            ROWS UNBOUNDED PRECEDING
        ) AS RunningTotal,
        RANK() OVER (
            PARTITION BY YEAR(OrderDate)
            ORDER BY TotalAmount DESC
        ) AS SalesRank
    FROM [reporting].[vw_CustomerOrders];
    
    -- Moving average
    SELECT 
        Date,
        TotalSales,
        AVG(TotalSales) OVER (
            ORDER BY Date
            ROWS BETWEEN 6 PRECEDING AND CURRENT ROW
        ) AS MovingAvg7Days
    FROM [reporting].[vw_DailySales];
    """)
    
    print("\n4. Common Table Expressions (CTEs)")
    print("-" * 80)
    print("""
    -- Recursive CTE for hierarchical data
    WITH ProductHierarchy AS (
        -- Anchor member
        SELECT 
            ProductID,
            ProductName,
            Category,
            0 AS Level
        FROM [dw].[DimProduct]
        WHERE ParentProductID IS NULL
        
        UNION ALL
        
        -- Recursive member
        SELECT 
            p.ProductID,
            p.ProductName,
            p.Category,
            ph.Level + 1
        FROM [dw].[DimProduct] p
        INNER JOIN ProductHierarchy ph ON p.ParentProductID = ph.ProductID
    )
    SELECT * FROM ProductHierarchy;
    
    -- Multiple CTEs
    WITH 
    MonthlySales AS (
        SELECT 
            YEAR(d.Date) AS Year,
            MONTH(d.Date) AS Month,
            SUM(f.TotalAmount) AS MonthlyRevenue
        FROM [dw].[FactSales] f
        INNER JOIN [dw].[DimDate] d ON f.DateKey = d.DateKey
        GROUP BY YEAR(d.Date), MONTH(d.Date)
    ),
    YearlySales AS (
        SELECT 
            Year,
            SUM(MonthlyRevenue) AS YearlyRevenue
        FROM MonthlySales
        GROUP BY Year
    )
    SELECT 
        m.Year,
        m.Month,
        m.MonthlyRevenue,
        y.YearlyRevenue,
        (m.MonthlyRevenue / y.YearlyRevenue * 100) AS PercentOfYearly
    FROM MonthlySales m
    INNER JOIN YearlySales y ON m.Year = y.Year;
    """)
    
    print("\n5. Cross-Database Queries")
    print("-" * 80)
    print("""
    -- Query across warehouse and lakehouse
    SELECT 
        w.CustomerKey,
        w.CustomerName,
        l.LastLoginDate,
        l.TotalLogins
    FROM [my_warehouse].[dw].[DimCustomer] w
    INNER JOIN [my_lakehouse].[customer_activity] l 
        ON w.CustomerID = l.customer_id
    WHERE l.LastLoginDate >= DATEADD(day, -30, GETDATE());
    
    -- Join warehouse with external table in lakehouse
    SELECT 
        p.ProductName,
        s.StockLevel,
        s.ReorderPoint,
        CASE 
            WHEN s.StockLevel < s.ReorderPoint THEN 'Reorder'
            ELSE 'Sufficient'
        END AS StockStatus
    FROM [warehouse].[dw].[DimProduct] p
    LEFT JOIN [lakehouse].[inventory_snapshot] s 
        ON p.ProductID = s.product_id;
    """)
    
    print("\n6. Analytical Functions")
    print("-" * 80)
    print("""
    -- Year-over-year comparison
    WITH SalesByYear AS (
        SELECT 
            d.Year,
            d.Month,
            SUM(f.TotalAmount) AS TotalSales
        FROM [dw].[FactSales] f
        INNER JOIN [dw].[DimDate] d ON f.DateKey = d.DateKey
        GROUP BY d.Year, d.Month
    )
    SELECT 
        s1.Year,
        s1.Month,
        s1.TotalSales AS CurrentYearSales,
        s2.TotalSales AS PreviousYearSales,
        ((s1.TotalSales - s2.TotalSales) / s2.TotalSales * 100) AS YoYGrowthPercent
    FROM SalesByYear s1
    LEFT JOIN SalesByYear s2 
        ON s1.Month = s2.Month AND s1.Year = s2.Year + 1;
    
    -- Customer segmentation
    SELECT 
        CustomerKey,
        CustomerName,
        TotalPurchases,
        NTILE(4) OVER (ORDER BY TotalPurchases DESC) AS CustomerSegment
    FROM (
        SELECT 
            c.CustomerKey,
            c.CustomerName,
            SUM(f.TotalAmount) AS TotalPurchases
        FROM [dw].[DimCustomer] c
        INNER JOIN [dw].[FactSales] f ON c.CustomerKey = f.CustomerKey
        WHERE c.IsCurrent = 1
        GROUP BY c.CustomerKey, c.CustomerName
    ) CustomerSummary;
    """)
    
    print("\n7. Performance Optimization")
    print("-" * 80)
    print("""
    -- Use columnstore index for large fact tables
    CREATE CLUSTERED COLUMNSTORE INDEX CCI_FactSales 
    ON [dw].[FactSales];
    
    -- Create statistics
    CREATE STATISTICS stat_customer_country 
    ON [dw].[DimCustomer](Country);
    
    -- Update statistics
    UPDATE STATISTICS [dw].[FactSales];
    
    -- Query with OPTION hints
    SELECT 
        c.CustomerName,
        SUM(f.TotalAmount) AS TotalRevenue
    FROM [dw].[FactSales] f
    INNER JOIN [dw].[DimCustomer] c ON f.CustomerKey = c.CustomerKey
    GROUP BY c.CustomerName
    OPTION (MAXDOP 4);  -- Limit parallelism
    """)
    
    print("\n8. Data Quality Queries")
    print("-" * 80)
    print("""
    -- Find duplicate records
    SELECT 
        CustomerID,
        COUNT(*) AS DuplicateCount
    FROM [dw].[DimCustomer]
    WHERE IsCurrent = 1
    GROUP BY CustomerID
    HAVING COUNT(*) > 1;
    
    -- Find orphaned records
    SELECT 
        f.SalesKey,
        f.CustomerKey
    FROM [dw].[FactSales] f
    LEFT JOIN [dw].[DimCustomer] c ON f.CustomerKey = c.CustomerKey
    WHERE c.CustomerKey IS NULL;
    
    -- Check for NULL values
    SELECT 
        'CustomerName' AS ColumnName,
        COUNT(*) AS NullCount
    FROM [dw].[DimCustomer]
    WHERE CustomerName IS NULL
    UNION ALL
    SELECT 
        'Email',
        COUNT(*)
    FROM [dw].[DimCustomer]
    WHERE Email IS NULL;
    """)
    
    print("\n9. Date/Time Queries")
    print("-" * 80)
    print("""
    -- Sales by day of week
    SELECT 
        d.DayName,
        d.DayOfWeek,
        COUNT(*) AS OrderCount,
        SUM(f.TotalAmount) AS TotalSales
    FROM [dw].[FactSales] f
    INNER JOIN [dw].[DimDate] d ON f.DateKey = d.DateKey
    GROUP BY d.DayName, d.DayOfWeek
    ORDER BY d.DayOfWeek;
    
    -- Sales trend by quarter
    SELECT 
        d.Year,
        d.Quarter,
        SUM(f.TotalAmount) AS QuarterlySales,
        LAG(SUM(f.TotalAmount)) OVER (ORDER BY d.Year, d.Quarter) AS PreviousQuarter,
        SUM(f.TotalAmount) - LAG(SUM(f.TotalAmount)) OVER (ORDER BY d.Year, d.Quarter) AS Growth
    FROM [dw].[FactSales] f
    INNER JOIN [dw].[DimDate] d ON f.DateKey = d.DateKey
    GROUP BY d.Year, d.Quarter;
    """)
    
    print("\n10. Advanced Analytics")
    print("-" * 80)
    print("""
    -- Customer lifetime value
    WITH CustomerMetrics AS (
        SELECT 
            c.CustomerKey,
            c.CustomerName,
            MIN(d.Date) AS FirstPurchase,
            MAX(d.Date) AS LastPurchase,
            COUNT(DISTINCT f.OrderID) AS TotalOrders,
            SUM(f.TotalAmount) AS TotalSpent,
            AVG(f.TotalAmount) AS AvgOrderValue
        FROM [dw].[DimCustomer] c
        INNER JOIN [dw].[FactSales] f ON c.CustomerKey = f.CustomerKey
        INNER JOIN [dw].[DimDate] d ON f.DateKey = d.DateKey
        WHERE c.IsCurrent = 1
        GROUP BY c.CustomerKey, c.CustomerName
    )
    SELECT 
        CustomerKey,
        CustomerName,
        TotalOrders,
        TotalSpent,
        AvgOrderValue,
        DATEDIFF(day, FirstPurchase, LastPurchase) AS CustomerTenureDays,
        TotalSpent / NULLIF(DATEDIFF(day, FirstPurchase, LastPurchase), 0) AS DailyValue
    FROM CustomerMetrics
    WHERE DATEDIFF(day, FirstPurchase, LastPurchase) > 0
    ORDER BY TotalSpent DESC;
    """)


def main():
    """
    Run query examples.
    """
    show_query_examples()
    
    print("\n" + "=" * 80)
    print("Query examples completed")
    print("=" * 80)


if __name__ == "__main__":
    main()
