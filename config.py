"""
Cấu hình kết nối Cơ sở dữ liệu SQL Server cho BudgetBuddy
"""

# Tên Server SQL Server của bạn (ví dụ: 'localhost', '127.0.0.1', 'DESKTOP-XYZ\\SQLEXPRESS')
DB_SERVER = "localhost"

# Tên Cơ sở dữ liệu
DB_NAME = "BudgetBuddyDB"

# Sử dụng xác thực Windows (True nếu đăng nhập bằng tài khoản Windows không cần mật khẩu)
# Đặt thành False nếu dùng tài khoản 'sa' hoặc tài khoản SQL Server riêng
USE_WINDOWS_AUTH = True

# Thông tin tài khoản SQL Server (Chỉ dùng khi USE_WINDOWS_AUTH = False)
DB_USER = "sa"
DB_PASSWORD = "your_password"

# Danh sách Driver ODBC SQL Server ưu tiên tự động chọn
PREFERRED_DRIVERS = [
    "ODBC Driver 18 for SQL Server",
    "ODBC Driver 17 for SQL Server",
    "SQL Server Native Client 11.0",
    "SQL Server",
]
