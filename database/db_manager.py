import pyodbc
from datetime import datetime
import config

class DatabaseManager:
    def __init__(self):
        self.connection = None
        self.driver = self._detect_driver()

    def _detect_driver(self):
        """Tự động tìm kiếm Driver ODBC SQL Server có sẵn trên máy"""
        try:
            available_drivers = pyodbc.drivers()
            for pref in config.PREFERRED_DRIVERS:
                if pref in available_drivers:
                    return pref
            # Nếu không tìm thấy driver cụ thể, tìm driver nào có chữ SQL Server
            for d in available_drivers:
                if "SQL Server" in d:
                    return d
        except Exception:
            pass
        return "ODBC Driver 17 for SQL Server"

    def get_connection_string(self, include_db=True):
        """Xây dựng chuỗi kết nối ODBC tới SQL Server"""
        conn_str = f"DRIVER={{{self.driver}}};SERVER={config.DB_SERVER};"
        if include_db:
            conn_str += f"DATABASE={config.DB_NAME};"

        if config.USE_WINDOWS_AUTH:
            conn_str += "Trusted_Connection=yes;TrustServerCertificate=yes;"
        else:
            conn_str += f"UID={config.DB_USER};PWD={config.DB_PASSWORD};TrustServerCertificate=yes;"
        return conn_str

    def connect(self):
        """Mở kết nối tới cơ sở dữ liệu"""
        try:
            conn_str = self.get_connection_string(include_db=True)
            self.connection = pyodbc.connect(conn_str, autocommit=True)
            return True, "Kết nối thành công!"
        except Exception as e:
            return False, str(e)

    def test_connection(self):
        """Kiểm tra trạng thái kết nối"""
        try:
            conn_str = self.get_connection_string(include_db=False)
            conn = pyodbc.connect(conn_str, timeout=5)
            conn.close()
            return True, "Kết nối tới SQL Server thành công!"
        except Exception as e:
            return False, f"Lỗi kết nối SQL Server: {e}"

    def ensure_database_and_tables(self, schema_file_path=None):
        """Khởi tạo Database và các Bảng mặc định nếu chưa tồn tại"""
        try:
            # Kết nối tới master để kiểm tra và tạo database
            conn_str = self.get_connection_string(include_db=False)
            with pyodbc.connect(conn_str, autocommit=True) as conn:
                with conn.cursor() as cur:
                    cur.execute(f"""
                        IF NOT EXISTS (SELECT * FROM sys.databases WHERE name = '{config.DB_NAME}')
                        BEGIN
                            CREATE DATABASE [{config.DB_NAME}];
                        END
                    """)

            # Kết nối vào database vừa tạo để tạo bảng
            with pyodbc.connect(self.get_connection_string(include_db=True), autocommit=True) as conn:
                with conn.cursor() as cur:
                    # Bảng Categories
                    cur.execute("""
                        IF NOT EXISTS (SELECT * FROM sys.tables WHERE name = 'Categories')
                        BEGIN
                            CREATE TABLE Categories (
                                CategoryID INT IDENTITY(1,1) PRIMARY KEY,
                                CategoryName NVARCHAR(100) NOT NULL,
                                CategoryType NVARCHAR(20) NOT NULL CHECK (CategoryType IN (N'EXPENSE', N'INCOME')),
                                Description NVARCHAR(255) NULL
                            );
                        END
                    """)
                    # Bảng Transactions
                    cur.execute("""
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
                    """)
                    # Bảng Budgets
                    cur.execute("""
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
                    """)
                    # Dữ liệu mặc định
                    cur.execute("SELECT COUNT(*) FROM Categories")
                    count = cur.fetchone()[0]
                    if count == 0:
                        default_categories = [
                            (N'Ăn uống', N'EXPENSE', N'Cơm, cà phê, ăn uống hàng ngày'),
                            (N'Tiền trọ / Điện nước', N'EXPENSE', N'Chi phí phòng ở và sinh hoạt'),
                            (N'Học tập & Sách vở', N'EXPENSE', N'Học phí, giáo trình, dụng cụ'),
                            (N'Đi lại / Xăng xe', N'EXPENSE', N'Xăng xe, xe buýt, sửa chữa xe'),
                            (N'Mua sắm & Giải trí', N'EXPENSE', N'Mua sắm cá nhân, xem phim'),
                            (N'Y tế & Sức khỏe', N'EXPENSE', N'Thuốc men, thể thao'),
                            (N'Lương / Làm thêm', N'INCOME', N'Thu nhập làm thêm, lương tháng'),
                            (N'Trợ cấp gia đình', N'INCOME', N'Bố mẹ gửi chu cấp'),
                            (N'Học bổng & Thưởng', N'INCOME', N'Học bổng, tiền thưởng thành tích'),
                            (N'Thu nhập khác', N'INCOME', N'Khoản thu nhập phát sinh khác')
                        ]
                        for name, cat_type, desc in default_categories:
                            cur.execute(
                                "INSERT INTO Categories (CategoryName, CategoryType, Description) VALUES (?, ?, ?)",
                                name, cat_type, desc
                            )
            return True, "Khởi tạo CSDL hoàn tất!"
        except Exception as e:
            return False, f"Lỗi khởi tạo CSDL: {e}"

    # ================= DANH MỤC (CATEGORIES) =================
    def get_categories(self, category_type=None):
        """Lấy danh sách danh mục (EXPENSE, INCOME hoặc tất cả)"""
        with pyodbc.connect(self.get_connection_string()) as conn:
            with conn.cursor() as cur:
                if category_type:
                    cur.execute(
                        "SELECT CategoryID, CategoryName, CategoryType, Description FROM Categories WHERE CategoryType = ? ORDER BY CategoryName",
                        category_type
                    )
                else:
                    cur.execute(
                        "SELECT CategoryID, CategoryName, CategoryType, Description FROM Categories ORDER BY CategoryType, CategoryName"
                    )
                return cur.fetchall()

    def add_category(self, name, category_type, description=""):
        with pyodbc.connect(self.get_connection_string(), autocommit=True) as conn:
            with conn.cursor() as cur:
                cur.execute(
                    "INSERT INTO Categories (CategoryName, CategoryType, Description) VALUES (?, ?, ?)",
                    name, category_type, description
                )

    # ================= GIAO DỊCH (TRANSACTIONS) =================
    def add_transaction(self, title, amount, category_id, trans_date, note=""):
        with pyodbc.connect(self.get_connection_string(), autocommit=True) as conn:
            with conn.cursor() as cur:
                cur.execute("""
                    INSERT INTO Transactions (Title, Amount, CategoryID, TransactionDate, Note)
                    VALUES (?, ?, ?, ?, ?)
                """, title, amount, category_id, trans_date, note)

    def update_transaction(self, trans_id, title, amount, category_id, trans_date, note=""):
        with pyodbc.connect(self.get_connection_string(), autocommit=True) as conn:
            with conn.cursor() as cur:
                cur.execute("""
                    UPDATE Transactions
                    SET Title = ?, Amount = ?, CategoryID = ?, TransactionDate = ?, Note = ?
                    WHERE TransactionID = ?
                """, title, amount, category_id, trans_date, note, trans_id)

    def delete_transaction(self, trans_id):
        with pyodbc.connect(self.get_connection_string(), autocommit=True) as conn:
            with conn.cursor() as cur:
                cur.execute("DELETE FROM Transactions WHERE TransactionID = ?", trans_id)

    def get_transactions(self, month=None, year=None, category_id=None, trans_type=None, search_keyword=None):
        """Lấy danh sách giao dịch theo bộ lọc"""
        query = """
            SELECT 
                t.TransactionID,
                t.TransactionDate,
                t.Title,
                c.CategoryType,
                c.CategoryName,
                t.Amount,
                t.Note,
                t.CategoryID
            FROM Transactions t
            JOIN Categories c ON t.CategoryID = c.CategoryID
            WHERE 1=1
        """
        params = []

        if month is not None and month != 0:
            query += " AND MONTH(t.TransactionDate) = ?"
            params.append(month)

        if year is not None and year != 0:
            query += " AND YEAR(t.TransactionDate) = ?"
            params.append(year)

        if category_id is not None and category_id != 0:
            query += " AND t.CategoryID = ?"
            params.append(category_id)

        if trans_type:
            query += " AND c.CategoryType = ?"
            params.append(trans_type)

        if search_keyword:
            query += " AND (t.Title LIKE ? OR t.Note LIKE ?)"
            params.extend([f"%{search_keyword}%", f"%{search_keyword}%"])

        query += " ORDER BY t.TransactionDate DESC, t.TransactionID DESC"

        with pyodbc.connect(self.get_connection_string()) as conn:
            with conn.cursor() as cur:
                cur.execute(query, params)
                return cur.fetchall()

    # ================= THỐNG KÊ (STATISTICS & DASHBOARD) =================
    def get_summary_stats(self, month=None, year=None):
        """Tính tổng thu, tổng chi và số dư ví"""
        query = """
            SELECT 
                ISNULL(SUM(CASE WHEN c.CategoryType = N'INCOME' THEN t.Amount ELSE 0 END), 0) AS TotalIncome,
                ISNULL(SUM(CASE WHEN c.CategoryType = N'EXPENSE' THEN t.Amount ELSE 0 END), 0) AS TotalExpense
            FROM Transactions t
            JOIN Categories c ON t.CategoryID = c.CategoryID
            WHERE 1=1
        """
        params = []
        if month is not None and month != 0:
            query += " AND MONTH(t.TransactionDate) = ?"
            params.append(month)
        if year is not None and year != 0:
            query += " AND YEAR(t.TransactionDate) = ?"
            params.append(year)

        with pyodbc.connect(self.get_connection_string()) as conn:
            with conn.cursor() as cur:
                cur.execute(query, params)
                row = cur.fetchone()
                total_income = float(row[0]) if row else 0.0
                total_expense = float(row[1]) if row else 0.0
                balance = total_income - total_expense
                return total_income, total_expense, balance

    def get_expense_by_category(self, month=None, year=None):
        """Lấy dữ liệu chi tiêu theo từng danh mục (để vẽ biểu đồ tròn)"""
        query = """
            SELECT c.CategoryName, SUM(t.Amount) AS TotalSpent
            FROM Transactions t
            JOIN Categories c ON t.CategoryID = c.CategoryID
            WHERE c.CategoryType = N'EXPENSE'
        """
        params = []
        if month is not None and month != 0:
            query += " AND MONTH(t.TransactionDate) = ?"
            params.append(month)
        if year is not None and year != 0:
            query += " AND YEAR(t.TransactionDate) = ?"
            params.append(year)

        query += " GROUP BY c.CategoryName ORDER BY TotalSpent DESC"

        with pyodbc.connect(self.get_connection_string()) as conn:
            with conn.cursor() as cur:
                cur.execute(query, params)
                return [(row[0], float(row[1])) for row in cur.fetchall()]

    # ================= NGÂN SÁCH & CẢNH BÁO (BUDGETS) =================
    def get_budgets_with_spent(self, month, year):
        """Lấy danh sách hạn mức và số tiền thực tế đã chi trong tháng"""
        query = """
            SELECT 
                b.BudgetID,
                b.CategoryID,
                c.CategoryName,
                b.LimitAmount,
                ISNULL((
                    SELECT SUM(t.Amount)
                    FROM Transactions t
                    WHERE t.CategoryID = b.CategoryID
                      AND MONTH(t.TransactionDate) = b.Month
                      AND YEAR(t.TransactionDate) = b.Year
                ), 0) AS SpentAmount
            FROM Budgets b
            JOIN Categories c ON b.CategoryID = c.CategoryID
            WHERE b.Month = ? AND b.Year = ?
            ORDER BY c.CategoryName
        """
        with pyodbc.connect(self.get_connection_string()) as conn:
            with conn.cursor() as cur:
                cur.execute(query, month, year)
                results = []
                for row in cur.fetchall():
                    limit = float(row[3])
                    spent = float(row[4])
                    percent = (spent / limit * 100) if limit > 0 else 0
                    results.append({
                        "budget_id": row[0],
                        "category_id": row[1],
                        "category_name": row[2],
                        "limit_amount": limit,
                        "spent_amount": spent,
                        "remaining": limit - spent,
                        "percentage": percent
                    })
                return results

    def set_budget(self, category_id, month, year, limit_amount):
        """Thêm hoặc cập nhật hạn mức chi tiêu cho 1 danh mục theo tháng/năm"""
        with pyodbc.connect(self.get_connection_string(), autocommit=True) as conn:
            with conn.cursor() as cur:
                cur.execute("""
                    IF EXISTS (SELECT 1 FROM Budgets WHERE CategoryID = ? AND Month = ? AND Year = ?)
                    BEGIN
                        UPDATE Budgets 
                        SET LimitAmount = ?
                        WHERE CategoryID = ? AND Month = ? AND Year = ?
                    END
                    ELSE
                    BEGIN
                        INSERT INTO Budgets (CategoryID, Month, Year, LimitAmount)
                        VALUES (?, ?, ?, ?)
                    END
                """, category_id, month, year, limit_amount, category_id, month, year, category_id, month, year, limit_amount)

    def delete_budget(self, budget_id):
        with pyodbc.connect(self.get_connection_string(), autocommit=True) as conn:
            with conn.cursor() as cur:
                cur.execute("DELETE FROM Budgets WHERE BudgetID = ?", budget_id)
