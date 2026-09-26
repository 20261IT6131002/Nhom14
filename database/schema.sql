-- =======================================================
-- KỊCH BẢN TẠO CƠ SỞ DỮ LIỆU BUDGETBUDDY TRÊN SQL SERVER
-- =======================================================

-- 1. Tạo cơ sở dữ liệu nếu chưa tồn tại
IF NOT EXISTS (SELECT * FROM sys.databases WHERE name = 'BudgetBuddyDB')
BEGIN
    CREATE DATABASE BudgetBuddyDB;
END
GO

USE BudgetBuddyDB;
GO

-- 2. Tạo bảng Danh mục (Categories)
IF NOT EXISTS (SELECT * FROM sys.tables WHERE name = 'Categories')
BEGIN
    CREATE TABLE Categories (
        CategoryID INT IDENTITY(1,1) PRIMARY KEY,
        CategoryName NVARCHAR(100) NOT NULL,
        CategoryType NVARCHAR(20) NOT NULL CHECK (CategoryType IN (N'EXPENSE', N'INCOME')),
        Description NVARCHAR(255) NULL
    );
END
GO

-- 3. Tạo bảng Giao dịch thu chi (Transactions)
IF NOT EXISTS (SELECT * FROM sys.tables WHERE name = 'Transactions')
BEGIN
    CREATE TABLE Transactions (
        TransactionID INT IDENTITY(1,1) PRIMARY KEY,
        Title NVARCHAR(200) NOT NULL,
        Amount DECIMAL(18, 2) NOT NULL CHECK (Amount > 0),
        CategoryID INT NOT NULL,
        TransactionDate DATE NOT NULL DEFAULT GETDATE(),
        Note NVARCHAR(500) NULL,
        CreatedAt DATETIME NOT NULL DEFAULT GETDATE(),
        CONSTRAINT FK_Transactions_Categories FOREIGN KEY (CategoryID) 
            REFERENCES Categories(CategoryID) ON DELETE CASCADE
    );
END
GO

-- 4. Tạo bảng Ngân sách hạn mức tháng (Budgets)
IF NOT EXISTS (SELECT * FROM sys.tables WHERE name = 'Budgets')
BEGIN
    CREATE TABLE Budgets (
        BudgetID INT IDENTITY(1,1) PRIMARY KEY,
        CategoryID INT NOT NULL,
        Month INT NOT NULL CHECK (Month BETWEEN 1 AND 12),
        Year INT NOT NULL CHECK (Year >= 2000),
        LimitAmount DECIMAL(18, 2) NOT NULL CHECK (LimitAmount > 0),
        CreatedAt DATETIME NOT NULL DEFAULT GETDATE(),
        CONSTRAINT UQ_Category_Month_Year UNIQUE (CategoryID, Month, Year),
        CONSTRAINT FK_Budgets_Categories FOREIGN KEY (CategoryID) 
            REFERENCES Categories(CategoryID) ON DELETE CASCADE
    );
END
GO

-- 5. Thêm danh mục mặc định ban đầu nếu bảng còn trống
IF NOT EXISTS (SELECT 1 FROM Categories)
BEGIN
    -- Danh mục Chi tiêu (EXPENSE)
    INSERT INTO Categories (CategoryName, CategoryType, Description) VALUES
    (N'Ăn uống', N'EXPENSE', N'Tiền cơm, cà phê, ăn vặt hàng ngày'),
    (N'Tiền trọ / Điện nước', N'EXPENSE', N'Chi phí thuê nhà và sinh hoạt'),
    (N'Học tập & Sách vở', N'EXPENSE', N'Học phí, tài liệu, đồ dùng học tập'),
    (N'Đi lại / Xăng xe', N'EXPENSE', N'Tiền xăng, vé xe buýt, bảo dưỡng xe'),
    (N'Mua sắm & Giải trí', N'EXPENSE', N'Quần áo, xem phim, tụ tập bạn bè'),
    (N'Y tế & Sức khỏe', N'EXPENSE', N'Thuốc men, khám bệnh, phòng tập');

    -- Danh mục Thu nhập (INCOME)
    INSERT INTO Categories (CategoryName, CategoryType, Description) VALUES
    (N'Lương / Làm thêm', N'INCOME', N'Lương nhận được từ công việc làm thêm'),
    (N'Trợ cấp từ gia đình', N'INCOME', N'Tiền bố mẹ gửi hàng tháng'),
    (N'Học bổng & Thưởng', N'INCOME', N'Học bổng trường, tiền thưởng'),
    (N'Thu nhập khác', N'INCOME', N'Các khoản thu lặt vặt khác');
END
GO
