# 💰 BudgetBuddy - Ứng dụng Quản lý Chi tiêu Cá nhân

> **Đồ án môn học:** Lập trình Python nâng cao  
> **Nhóm thực hiện:** Nhóm 14  
> **Công nghệ:** Python (Tkinter/TTK) + Microsoft SQL Server + Matplotlib  

---

## 📖 1. Giới thiệu đề tài
**BudgetBuddy** là ứng dụng desktop quản lý tài chính cá nhân toàn diện, hỗ trợ người dùng theo dõi các khoản thu - chi hàng ngày, kiểm soát hạn mức ngân sách thông minh và trực quan hóa chi tiêu qua biểu đồ trực quan. Ứng dụng được thiết kế tối ưu, giao diện thân thiện và dễ sử dụng cho học sinh, sinh viên và người đi làm.

---

## ✨ 2. Các chức năng chính (Bám sát yêu cầu môn học)

1. **Quản lý Thu / Chi (CRUD đầy đủ):**
   - Thêm, sửa, xóa các giao dịch thu nhập và chi tiêu.
   - Phân loại danh mục rõ ràng: Ăn uống, Tiền trọ, Học tập, Đi lại, Lương, Thưởng,...
   - Ghi nhận số tiền, ngày giao dịch và ghi chú chi tiết.
2. **Tìm kiếm & Bộ lọc linh hoạt:**
   - Lọc giao dịch theo Tháng / Năm.
   - Lọc theo loại (Thu nhập / Chi tiêu) hoặc theo danh mục cụ thể.
   - Tìm kiếm giao dịch nhanh theo từ khóa trong tiêu đề và ghi chú.
3. **Dashboard & Thống kê số dư tức thời:**
   - Tự động tính toán: **Tổng Thu**, **Tổng Chi** và **Số dư ví khả dụng**.
4. **Trực quan hóa dữ liệu & Biểu đồ (Matplotlib):**
   - Tích hợp biểu đồ tròn (Pie Chart) trực tiếp trên giao diện để phân tích tỷ trọng chi tiêu của từng danh mục trong tháng.
5. **Hạn mức Ngân sách & Cảnh báo thông minh:**
   - Cho phép thiết lập mức chi tiêu tối đa cho từng danh mục trong tháng.
   - Cảnh báo trực quan theo màu sắc:
     - 🟢 **An toàn (< 80%):** Chi tiêu trong tầm kiểm soát.
     - 🟡 **Cảnh báo (80% - 100%):** Sắp chạm ngưỡng chi tiêu tối đa.
     - 🔴 **Báo động (> 100%):** Đã chi tiêu vượt quá ngân sách!
6. **Báo cáo & Xuất dữ liệu:**
   - Xuất toàn bộ sao kê giao dịch ra file **Excel (`.xlsx`)** và **CSV (`.csv`)** chuẩn tiếng Việt UTF-8.

---

## 🗄️ 3. Thiết kế Cơ sở dữ liệu (SQL Server)

Hệ thống gồm 3 bảng quan hệ:
- **`Categories`**: Lưu danh mục chi tiêu / thu nhập (`CategoryID`, `CategoryName`, `CategoryType`, `Description`).
- **`Transactions`**: Lưu lịch sử giao dịch (`TransactionID`, `Title`, `Amount`, `CategoryID`, `TransactionDate`, `Note`, `CreatedAt`).
- **`Budgets`**: Lưu hạn mức ngân sách tháng (`BudgetID`, `CategoryID`, `Month`, `Year`, `LimitAmount`).

---

## 📁 4. Cấu trúc thư mục dự án

```text
Nhom14-PythonNC/
│
├── config.py                 # File cấu hình kết nối SQL Server
├── main.py                   # File khởi chạy chính của ứng dụng
├── requirements.txt          # Danh sách thư viện Python cần thiết
├── README.md                 # Tài liệu hướng dẫn đồ án
│
├── database/                 # Tầng thao tác Cơ sở dữ liệu
│   ├── __init__.py
│   ├── db_manager.py         # Xử lý kết nối và các câu lệnh SQL (CRUD, thống kê)
│   └── schema.sql            # Script SQL tạo Database và bảng mẫu
│
└── gui/                      # Tầng giao diện người dùng (Tkinter)
    ├── __init__.py
    └── main_window.py        # Toàn bộ giao diện người dùng và sự kiện
```

---

## 🚀 5. Hướng dẫn cài đặt & Khởi chạy

### Bước 1: Cài đặt các thư viện Python
Mở Terminal / Command Prompt tại thư mục dự án và chạy lệnh:
```bash
pip install -r requirements.txt
```
*(Các thư viện chính gồm: `pyodbc`, `matplotlib`, `openpyxl`)*

### Bước 2: Cấu hình kết nối SQL Server
Mở file `config.py` và kiểm tra cấu hình:
- **`DB_SERVER`**: Điền tên máy chủ SQL Server của bạn (mặc định là `localhost` hoặc tên máy `DESKTOP-XXXX\\SQLEXPRESS`).
- **`USE_WINDOWS_AUTH`**: Đặt là `True` nếu dùng Windows Authentication, hoặc đổi sang `False` và điền `DB_USER` / `DB_PASSWORD` (tài khoản `sa`).

*(Lưu ý: Ứng dụng có cơ chế tự động tạo CSDL `BudgetBuddyDB` và tạo sẵn các bảng + danh mục mẫu khi chạy lần đầu, bạn cũng có thể mở SSMS và chạy file `database/schema.sql` nếu muốn tạo thủ công).*

### Bước 3: Chạy ứng dụng
```bash
python main.py
```

---

## 👥 Thành viên thực hiện
- **Nhóm:** 14
- **Môn học:** Lập trình Python nâng cao
