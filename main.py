import sys
import tkinter as tk
from tkinter import messagebox
from database.db_manager import DatabaseManager
from gui.main_window import BudgetBuddyApp

def main():
    db = DatabaseManager()
    ok, msg = db.ensure_database_and_tables()
    if not ok:
        root = tk.Tk()
        root.withdraw()
        messagebox.showerror(
            "Lỗi kết nối SQL Server",
            f"Không thể kết nối hoặc khởi tạo CSDL trên SQL Server!\n\n"
            f"Chi tiết: {msg}\n\n"
            f"Hướng dẫn khắc phục:\n"
            f"1. Mở file 'config.py' để cập nhật tên Server (DB_SERVER) phù hợp với máy của bạn.\n"
            f"2. Đảm bảo dịch vụ SQL Server (MSSQLSERVER hoặc SQLEXPRESS) đang chạy.\n"
            f"3. Hoặc mở SSMS và chạy script trong thư mục 'database/schema.sql'."
        )
        root.destroy()
        sys.exit(1)

    app = BudgetBuddyApp(db)
    app.mainloop()

if __name__ == "__main__":
    main()
