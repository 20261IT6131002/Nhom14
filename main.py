"""
BUDGETBUDDY - Ứng dụng Quản lý Chi tiêu Cá nhân
Môn học: Lập trình Python nâng cao (Nhóm 14)
"""
import sys
import tkinter as tk
from tkinter import messagebox
from database.db_manager import DatabaseManager
from gui.main_window import BudgetBuddyApp

def main():
    # 1. Khởi tạo Database Manager
    db = DatabaseManager()

    # 2. Tự động kiểm tra và khởi tạo CSDL & các bảng mặc định
    ok, msg = db.ensure_database_and_tables()
    if not ok:
        # Nếu chưa kết nối được tới SQL Server, hiển thị thông báo thân thiện
        root = tk.Tk()
        root.withdraw()
        messagebox.showerror(
            "Lỗi kết nối SQL Server",
            f"Không thể kết nối hoặc khởi tạo CSDL trên SQL Server!\n\n"
            f"Chi tiết: {msg}\n\n"
            f"👉 Hướng dẫn khắc phục:\n"
            f"1. Mở file 'config.py' để cập nhật tên Server (DB_SERVER) phù hợp với máy của bạn.\n"
            f"2. Đảm bảo dịch vụ SQL Server (MSSQLSERVER hoặc SQLEXPRESS) đang chạy.\n"
            f"3. Hoặc mở SSMS và chạy script trong thư mục 'database/schema.sql'."
        )
        root.destroy()
        sys.exit(1)

    # 3. Khởi chạy ứng dụng giao diện Tkinter
    app = BudgetBuddyApp(db)
    app.mainloop()

if __name__ == "__main__":
    main()
