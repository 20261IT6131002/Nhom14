import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from datetime import datetime
import csv

# Thử import matplotlib để vẽ biểu đồ, nếu chưa cài sẽ có thông báo hướng dẫn
try:
    import matplotlib
    matplotlib.use("TkAgg")
    from matplotlib.figure import Figure
    from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
    MATPLOTLIB_AVAILABLE = True
except ImportError:
    MATPLOTLIB_AVAILABLE = False

# Thử import openpyxl để xuất Excel
try:
    import openpyxl
    OPENPYXL_AVAILABLE = True
except ImportError:
    OPENPYXL_AVAILABLE = False


class BudgetBuddyApp(tk.Tk):
    def __init__(self, db_manager):
        super().__init__()
        self.db = db_manager

        self.title("BudgetBuddy - Ứng dụng Quản lý Chi tiêu Cá nhân")
        self.geometry("1180x720")
        self.minsize(1000, 650)

        # Style chung
        self._setup_styles()

        # Dữ liệu cache
        self.selected_transaction_id = None
        self.categories_cache = []

        # Tạo giao diện
        self._build_ui()

        # Tải dữ liệu ban đầu
        self.load_categories()
        self.refresh_dashboard()
        self.filter_transactions()

    def _setup_styles(self):
        style = ttk.Style(self)
        style.theme_use("clam")

        # Cấu hình màu sắc
        style.configure("Treeview.Heading", font=("Segoe UI", 10, "bold"), background="#e0e0e0")
        style.configure("Treeview", font=("Segoe UI", 10), rowheight=26)
        style.map("Treeview", background=[("selected", "#3f51b5")])

        style.configure("TNotebook.Tab", font=("Segoe UI", 10, "bold"), padding=[12, 6])
        style.configure("Header.TLabel", font=("Segoe UI", 16, "bold"), foreground="#1a237e")
        style.configure("CardTitle.TLabel", font=("Segoe UI", 10), foreground="#555555")
        style.configure("CardValue.TLabel", font=("Segoe UI", 14, "bold"))

    def _build_ui(self):
        # 1. Header Banner & Thống kê nhanh
        self.header_frame = ttk.Frame(self, padding=(15, 10))
        self.header_frame.pack(fill=tk.X)

        title_lbl = ttk.Label(self.header_frame, text="💰 BUDGETBUDDY - QUẢN LÝ TÀI CHÍNH CÁ NHÂN", style="Header.TLabel")
        title_lbl.pack(side=tk.LEFT, pady=5)

        # 3 Thẻ thống kê nhanh trên góc phải
        self.stat_cards_frame = ttk.Frame(self.header_frame)
        self.stat_cards_frame.pack(side=tk.RIGHT)

        self.lbl_income_stat = tk.Label(self.stat_cards_frame, text="Thu: 0 đ", font=("Segoe UI", 11, "bold"),
                                        fg="#2e7d32", bg="#e8f5e9", padx=10, pady=5, relief="groove")
        self.lbl_income_stat.pack(side=tk.LEFT, padx=5)

        self.lbl_expense_stat = tk.Label(self.stat_cards_frame, text="Chi: 0 đ", font=("Segoe UI", 11, "bold"),
                                         fg="#c62828", bg="#ffebee", padx=10, pady=5, relief="groove")
        self.lbl_expense_stat.pack(side=tk.LEFT, padx=5)

        self.lbl_balance_stat = tk.Label(self.stat_cards_frame, text="Số dư: 0 đ", font=("Segoe UI", 11, "bold"),
                                         fg="#1565c0", bg="#e3f2fd", padx=10, pady=5, relief="groove")
        self.lbl_balance_stat.pack(side=tk.LEFT, padx=5)

        # 2. Main Tabs
        self.notebook = ttk.Notebook(self)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

        self.tab_transactions = ttk.Frame(self.notebook, padding=10)
        self.tab_charts = ttk.Frame(self.notebook, padding=10)
        self.tab_budget = ttk.Frame(self.notebook, padding=10)
        self.tab_reports = ttk.Frame(self.notebook, padding=10)

        self.notebook.add(self.tab_transactions, text="📝 Quản lý Thu / Chi")
        self.notebook.add(self.tab_charts, text="📊 Biểu đồ & Phân tích")
        self.notebook.add(self.tab_budget, text="🎯 Hạn mức Ngân sách")
        self.notebook.add(self.tab_reports, text="📄 Xuất Báo cáo & Cài đặt")

        # Xây dựng nội dung từng Tab
        self._build_transactions_tab()
        self._build_charts_tab()
        self._build_budget_tab()
        self._build_reports_tab()

    # ================= TAB 1: QUẢN LÝ THU / CHI =================
    def _build_transactions_tab(self):
        # Chia 2 cột: Cột trái (Form nhập liệu), Cột phải (Danh sách & Tìm kiếm)
        paned = ttk.PanedWindow(self.tab_transactions, orient=tk.HORIZONTAL)
        paned.pack(fill=tk.BOTH, expand=True)

        # --- Khung Form Trái ---
        left_frame = ttk.LabelFrame(paned, text="Thông tin giao dịch", padding=12)
        paned.add(left_frame, weight=1)

        ttk.Label(left_frame, text="Tiêu đề giao dịch: *").pack(anchor=tk.W, pady=(0, 2))
        self.entry_title = ttk.Entry(left_frame, font=("Segoe UI", 10))
        self.entry_title.pack(fill=tk.X, pady=(0, 10))

        ttk.Label(left_frame, text="Số tiền (VND): *").pack(anchor=tk.W, pady=(0, 2))
        self.entry_amount = ttk.Entry(left_frame, font=("Segoe UI", 10))
        self.entry_amount.pack(fill=tk.X, pady=(0, 10))

        ttk.Label(left_frame, text="Loại giao dịch:").pack(anchor=tk.W, pady=(0, 2))
        self.var_trans_type = tk.StringVar(value="EXPENSE")
        type_frame = ttk.Frame(left_frame)
        type_frame.pack(fill=tk.X, pady=(0, 10))
        ttk.Radiobutton(type_frame, text="Chi tiêu (-)", variable=self.var_trans_type, value="EXPENSE",
                        command=self._on_type_change).pack(side=tk.LEFT, padx=(0, 15))
        ttk.Radiobutton(type_frame, text="Thu nhập (+)", variable=self.var_trans_type, value="INCOME",
                        command=self._on_type_change).pack(side=tk.LEFT)

        ttk.Label(left_frame, text="Danh mục: *").pack(anchor=tk.W, pady=(0, 2))
        self.cbo_category = ttk.Combobox(left_frame, state="readonly", font=("Segoe UI", 10))
        self.cbo_category.pack(fill=tk.X, pady=(0, 10))

        ttk.Label(left_frame, text="Ngày giao dịch (YYYY-MM-DD):").pack(anchor=tk.W, pady=(0, 2))
        self.entry_date = ttk.Entry(left_frame, font=("Segoe UI", 10))
        self.entry_date.insert(0, datetime.now().strftime("%Y-%m-%d"))
        self.entry_date.pack(fill=tk.X, pady=(0, 10))

        ttk.Label(left_frame, text="Ghi chú thêm:").pack(anchor=tk.W, pady=(0, 2))
        self.entry_note = ttk.Entry(left_frame, font=("Segoe UI", 10))
        self.entry_note.pack(fill=tk.X, pady=(0, 15))

        # Các nút bấm chức năng CRUD
        btn_frame = ttk.Frame(left_frame)
        btn_frame.pack(fill=tk.X, pady=5)

        self.btn_add = tk.Button(btn_frame, text="➕ Thêm mới", bg="#2e7d32", fg="white", font=("Segoe UI", 9, "bold"),
                                 relief="flat", pady=6, cursor="hand2", command=self.add_transaction)
        self.btn_add.pack(fill=tk.X, pady=3)

        self.btn_update = tk.Button(btn_frame, text="✏️ Cập nhật", bg="#1976d2", fg="white", font=("Segoe UI", 9, "bold"),
                                    relief="flat", pady=6, cursor="hand2", command=self.update_transaction)
        self.btn_update.pack(fill=tk.X, pady=3)

        self.btn_delete = tk.Button(btn_frame, text="🗑️ Xóa giao dịch", bg="#c62828", fg="white", font=("Segoe UI", 9, "bold"),
                                    relief="flat", pady=6, cursor="hand2", command=self.delete_transaction)
        self.btn_delete.pack(fill=tk.X, pady=3)

        self.btn_reset = tk.Button(btn_frame, text="🔄 Làm mới form", bg="#757575", fg="white", font=("Segoe UI", 9),
                                   relief="flat", pady=4, cursor="hand2", command=self.clear_form)
        self.btn_reset.pack(fill=tk.X, pady=3)

        # --- Khung Danh sách Phải ---
        right_frame = ttk.Frame(paned, padding=5)
        paned.add(right_frame, weight=3)

        # Bộ lọc tìm kiếm
        filter_bar = ttk.LabelFrame(right_frame, text="Tìm kiếm & Bộ lọc", padding=8)
        filter_bar.pack(fill=tk.X, pady=(0, 8))

        ttk.Label(filter_bar, text="Từ khóa:").grid(row=0, column=0, padx=4, sticky=tk.W)
        self.entry_search = ttk.Entry(filter_bar, width=15)
        self.entry_search.grid(row=0, column=1, padx=4)

        ttk.Label(filter_bar, text="Tháng:").grid(row=0, column=2, padx=4, sticky=tk.W)
        current_month = str(datetime.now().month)
        self.cbo_filter_month = ttk.Combobox(filter_bar, values=["Tất cả"] + [str(i) for i in range(1, 13)], width=6, state="readonly")
        self.cbo_filter_month.set(current_month)
        self.cbo_filter_month.grid(row=0, column=3, padx=4)

        ttk.Label(filter_bar, text="Năm:").grid(row=0, column=4, padx=4, sticky=tk.W)
        current_year = str(datetime.now().year)
        self.cbo_filter_year = ttk.Combobox(filter_bar, values=["Tất cả", "2024", "2025", "2026", "2027"], width=6, state="readonly")
        self.cbo_filter_year.set(current_year)
        self.cbo_filter_year.grid(row=0, column=5, padx=4)

        ttk.Label(filter_bar, text="Loại:").grid(row=0, column=6, padx=4, sticky=tk.W)
        self.cbo_filter_type = ttk.Combobox(filter_bar, values=["Tất cả", "EXPENSE", "INCOME"], width=8, state="readonly")
        self.cbo_filter_type.set("Tất cả")
        self.cbo_filter_type.grid(row=0, column=7, padx=4)

        btn_filter = tk.Button(filter_bar, text="🔍 Lọc", bg="#3f51b5", fg="white", font=("Segoe UI", 9, "bold"),
                               relief="flat", padx=10, cursor="hand2", command=self.filter_transactions)
        btn_filter.grid(row=0, column=8, padx=6)

        btn_filter_reset = tk.Button(filter_bar, text="✖ Reset", bg="#9e9e9e", fg="white", font=("Segoe UI", 9),
                                     relief="flat", padx=6, cursor="hand2", command=self.reset_filter)
        btn_filter_reset.grid(row=0, column=9, padx=2)

        # Bảng dữ liệu Treeview
        tree_frame = ttk.Frame(right_frame)
        tree_frame.pack(fill=tk.BOTH, expand=True)

        columns = ("id", "date", "title", "type", "category", "amount", "note")
        self.tree = ttk.Treeview(tree_frame, columns=columns, show="headings", selectmode="browse")

        self.tree.heading("id", text="ID")
        self.tree.heading("date", text="Ngày")
        self.tree.heading("title", text="Tiêu đề")
        self.tree.heading("type", text="Loại")
        self.tree.heading("category", text="Danh mục")
        self.tree.heading("amount", text="Số tiền (đ)")
        self.tree.heading("note", text="Ghi chú")

        self.tree.column("id", width=40, anchor=tk.CENTER)
        self.tree.column("date", width=85, anchor=tk.CENTER)
        self.tree.column("title", width=180, anchor=tk.W)
        self.tree.column("type", width=75, anchor=tk.CENTER)
        self.tree.column("category", width=130, anchor=tk.W)
        self.tree.column("amount", width=110, anchor=tk.E)
        self.tree.column("note", width=150, anchor=tk.W)

        # Thanh cuộn
        scrollbar = ttk.Scrollbar(tree_frame, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # Màu sắc tag cho dòng Thu nhập / Chi tiêu
        self.tree.tag_configure("INCOME", foreground="#2e7d32")
        self.tree.tag_configure("EXPENSE", foreground="#c62828")

        # Sự kiện click dòng
        self.tree.bind("<<TreeviewSelect>>", self._on_tree_select)

    # ================= TAB 2: BIỂU ĐỒ & PHÂN TÍCH =================
    def _build_charts_tab(self):
        ctrl_frame = ttk.Frame(self.tab_charts, padding=6)
        ctrl_frame.pack(fill=tk.X)

        ttk.Label(ctrl_frame, text="Xem biểu đồ chi tiêu Tháng:", font=("Segoe UI", 10, "bold")).pack(side=tk.LEFT, padx=5)
        self.cbo_chart_month = ttk.Combobox(ctrl_frame, values=[str(i) for i in range(1, 13)], width=5, state="readonly")
        self.cbo_chart_month.set(str(datetime.now().month))
        self.cbo_chart_month.pack(side=tk.LEFT, padx=4)

        ttk.Label(ctrl_frame, text="Năm:").pack(side=tk.LEFT, padx=5)
        self.cbo_chart_year = ttk.Combobox(ctrl_frame, values=["2024", "2025", "2026", "2027"], width=6, state="readonly")
        self.cbo_chart_year.set(str(datetime.now().year))
        self.cbo_chart_year.pack(side=tk.LEFT, padx=4)

        btn_draw = tk.Button(ctrl_frame, text="📊 Vẽ lại biểu đồ", bg="#673ab7", fg="white", font=("Segoe UI", 9, "bold"),
                             relief="flat", padx=10, cursor="hand2", command=self.draw_chart)
        btn_draw.pack(side=tk.LEFT, padx=10)

        # Khu vực vẽ biểu đồ Matplotlib
        self.chart_container = ttk.Frame(self.tab_charts)
        self.chart_container.pack(fill=tk.BOTH, expand=True, pady=10)
        self.chart_canvas = None

        if not MATPLOTLIB_AVAILABLE:
            lbl_err = ttk.Label(self.chart_container, text="⚠️ Chưa cài đặt thư viện 'matplotlib'. Hãy chạy: pip install matplotlib",
                                font=("Segoe UI", 11), foreground="red")
            lbl_err.pack(expand=True)

    # ================= TAB 3: HẠN MỨC NGÂN SÁCH =================
    def _build_budget_tab(self):
        paned = ttk.PanedWindow(self.tab_budget, orient=tk.HORIZONTAL)
        paned.pack(fill=tk.BOTH, expand=True)

        # Form đặt ngân sách
        left_box = ttk.LabelFrame(paned, text="Thiết lập hạn mức chi tiêu", padding=12)
        paned.add(left_box, weight=1)

        ttk.Label(left_box, text="Chọn Danh mục chi: *").pack(anchor=tk.W, pady=(0, 2))
        self.cbo_budget_cat = ttk.Combobox(left_box, state="readonly", font=("Segoe UI", 10))
        self.cbo_budget_cat.pack(fill=tk.X, pady=(0, 10))

        ttk.Label(left_box, text="Hạn mức tối đa (VND): *").pack(anchor=tk.W, pady=(0, 2))
        self.entry_budget_limit = ttk.Entry(left_box, font=("Segoe UI", 10))
        self.entry_budget_limit.pack(fill=tk.X, pady=(0, 10))

        row_time = ttk.Frame(left_box)
        row_time.pack(fill=tk.X, pady=(0, 15))
        ttk.Label(row_time, text="Tháng:").pack(side=tk.LEFT, padx=(0, 4))
        self.cbo_b_month = ttk.Combobox(row_time, values=[str(i) for i in range(1, 13)], width=4, state="readonly")
        self.cbo_b_month.set(str(datetime.now().month))
        self.cbo_b_month.pack(side=tk.LEFT, padx=(0, 10))

        ttk.Label(row_time, text="Năm:").pack(side=tk.LEFT, padx=(0, 4))
        self.cbo_b_year = ttk.Combobox(row_time, values=["2024", "2025", "2026", "2027"], width=6, state="readonly")
        self.cbo_b_year.set(str(datetime.now().year))
        self.cbo_b_year.pack(side=tk.LEFT)

        btn_save_budget = tk.Button(left_box, text="💾 Lưu hạn mức", bg="#00796b", fg="white", font=("Segoe UI", 10, "bold"),
                                    relief="flat", pady=6, cursor="hand2", command=self.save_budget)
        btn_save_budget.pack(fill=tk.X, pady=5)

        btn_del_budget = tk.Button(left_box, text="🗑️ Xóa hạn mức", bg="#d32f2f", fg="white", font=("Segoe UI", 9),
                                   relief="flat", pady=4, cursor="hand2", command=self.delete_budget)
        btn_del_budget.pack(fill=tk.X, pady=5)

        # Bảng theo dõi ngân sách & Cảnh báo
        right_box = ttk.LabelFrame(paned, text="Tình hình chi tiêu so với hạn mức trong tháng", padding=10)
        paned.add(right_box, weight=3)

        b_filter_frame = ttk.Frame(right_box)
        b_filter_frame.pack(fill=tk.X, pady=(0, 8))

        btn_load_b = tk.Button(b_filter_frame, text="🔄 Tải danh sách ngân sách", bg="#455a64", fg="white", font=("Segoe UI", 9, "bold"),
                               relief="flat", padx=10, cursor="hand2", command=self.load_budgets)
        btn_load_b.pack(side=tk.LEFT)

        b_tree_frame = ttk.Frame(right_box)
        b_tree_frame.pack(fill=tk.BOTH, expand=True)

        b_cols = ("cat", "limit", "spent", "remaining", "percent", "status")
        self.tree_budget = ttk.Treeview(b_tree_frame, columns=b_cols, show="headings")
        self.tree_budget.heading("cat", text="Danh mục")
        self.tree_budget.heading("limit", text="Hạn mức (đ)")
        self.tree_budget.heading("spent", text="Đã chi (đ)")
        self.tree_budget.heading("remaining", text="Còn lại (đ)")
        self.tree_budget.heading("percent", text="Tiến độ (%)")
        self.tree_budget.heading("status", text="Cảnh báo trạng thái")

        self.tree_budget.column("cat", width=140)
        self.tree_budget.column("limit", width=110, anchor=tk.E)
        self.tree_budget.column("spent", width=110, anchor=tk.E)
        self.tree_budget.column("remaining", width=110, anchor=tk.E)
        self.tree_budget.column("percent", width=90, anchor=tk.CENTER)
        self.tree_budget.column("status", width=160, anchor=tk.CENTER)

        self.tree_budget.tag_configure("SAFE", foreground="#2e7d32")
        self.tree_budget.tag_configure("WARNING", foreground="#e65100", font=("Segoe UI", 10, "bold"))
        self.tree_budget.tag_configure("DANGER", foreground="#b71c1c", font=("Segoe UI", 10, "bold"))

        self.tree_budget.pack(fill=tk.BOTH, expand=True)

    # ================= TAB 4: BÁO CÁO & CÀI ĐẶT =================
    def _build_reports_tab(self):
        box_export = ttk.LabelFrame(self.tab_reports, text="Xuất dữ liệu giao dịch", padding=15)
        box_export.pack(fill=tk.X, pady=10)

        desc = ttk.Label(box_export, text="Bạn có thể xuất toàn bộ dữ liệu chi tiêu ra file Excel (.xlsx) hoặc file CSV để nộp báo cáo cho giảng viên.")
        desc.pack(anchor=tk.W, pady=(0, 10))

        btn_row = ttk.Frame(box_export)
        btn_row.pack(fill=tk.X)

        btn_export_csv = tk.Button(btn_row, text="📄 Xuất file CSV (Excel tiếng Việt)", bg="#00897b", fg="white",
                                   font=("Segoe UI", 10, "bold"), relief="flat", padx=15, pady=8, cursor="hand2",
                                   command=self.export_csv)
        btn_export_csv.pack(side=tk.LEFT, padx=10)

        btn_export_excel = tk.Button(btn_row, text="📊 Xuất file Excel (.xlsx)", bg="#1b5e20", fg="white",
                                     font=("Segoe UI", 10, "bold"), relief="flat", padx=15, pady=8, cursor="hand2",
                                     command=self.export_excel)
        btn_export_excel.pack(side=tk.LEFT, padx=10)

        box_db = ttk.LabelFrame(self.tab_reports, text="Thông tin kết nối CSDL SQL Server", padding=15)
        box_db.pack(fill=tk.X, pady=10)

        self.lbl_db_info = ttk.Label(box_db, text="Nhấn nút bên dưới để kiểm tra tình trạng kết nối tới SQL Server:")
        self.lbl_db_info.pack(anchor=tk.W, pady=(0, 8))

        btn_test_db = tk.Button(box_db, text="🔌 Kiểm tra kết nối SQL Server", bg="#37474f", fg="white",
                                font=("Segoe UI", 9, "bold"), relief="flat", padx=12, pady=6, cursor="hand2",
                                command=self.check_db_connection)
        btn_test_db.pack(anchor=tk.W)

    # ================= LOGIC & SỰ KIỆN =================
    def _on_type_change(self):
        """Khi đổi loại (Thu/Chi), cập nhật lại danh mục tương ứng trong combobox"""
        selected_type = self.var_trans_type.get()
        filtered = [cat for cat in self.categories_cache if cat[2] == selected_type]
        self.cbo_category['values'] = [cat[1] for cat in filtered]
        if filtered:
            self.cbo_category.set(filtered[0][1])

    def load_categories(self):
        try:
            self.categories_cache = self.db.get_categories()
            self._on_type_change()

            # Đổ dữ liệu vào combobox bên Tab Budget (chỉ các danh mục Chi tiêu)
            expense_cats = [cat[1] for cat in self.categories_cache if cat[2] == "EXPENSE"]
            self.cbo_budget_cat['values'] = expense_cats
            if expense_cats:
                self.cbo_budget_cat.set(expense_cats[0])
        except Exception as e:
            messagebox.showwarning("Cảnh báo CSDL", f"Không thể tải danh mục từ SQL Server:\n{e}\nVui lòng kiểm tra file config.py và đảm bảo SQL Server đang chạy.")

    def refresh_dashboard(self):
        """Tính lại tổng thu, tổng chi và số dư ví"""
        try:
            # Lấy thống kê theo tháng được chọn ở filter nếu có
            m = self.cbo_filter_month.get()
            y = self.cbo_filter_year.get()
            month_val = int(m) if m != "Tất cả" else None
            year_val = int(y) if y != "Tất cả" else None

            inc, exp, bal = self.db.get_summary_stats(month=month_val, year=year_val)
            self.lbl_income_stat.config(text=f"Thu: {inc:,.0f} đ")
            self.lbl_expense_stat.config(text=f"Chi: {exp:,.0f} đ")
            self.lbl_balance_stat.config(text=f"Số dư: {bal:,.0f} đ")
        except Exception:
            pass

    def filter_transactions(self):
        """Lọc và hiển thị danh sách giao dịch lên bảng"""
        try:
            m = self.cbo_filter_month.get()
            y = self.cbo_filter_year.get()
            t = self.cbo_filter_type.get()
            kw = self.entry_search.get().strip()

            month_val = int(m) if m != "Tất cả" else None
            year_val = int(y) if y != "Tất cả" else None
            type_val = t if t != "Tất cả" else None
            keyword_val = kw if kw else None

            rows = self.db.get_transactions(month=month_val, year=year_val, trans_type=type_val, search_keyword=keyword_val)

            # Xóa các dòng cũ
            for item in self.tree.get_children():
                self.tree.delete(item)

            for r in rows:
                trans_id, t_date, title, cat_type, cat_name, amount, note, _ = r
                date_str = str(t_date)
                amount_str = f"{float(amount):,.0f}"
                type_display = "Thu nhập (+)" if cat_type == "INCOME" else "Chi tiêu (-)"

                self.tree.insert("", tk.END, values=(trans_id, date_str, title, type_display, cat_name, amount_str, note or ""),
                                 tags=(cat_type,))

            self.refresh_dashboard()
        except Exception as e:
            messagebox.showerror("Lỗi", f"Không thể lấy danh sách giao dịch:\n{e}")

    def reset_filter(self):
        self.entry_search.delete(0, tk.END)
        self.cbo_filter_month.set("Tất cả")
        self.cbo_filter_year.set(str(datetime.now().year))
        self.cbo_filter_type.set("Tất cả")
        self.filter_transactions()

    def _on_tree_select(self, event):
        selected = self.tree.selection()
        if not selected:
            return
        item = self.tree.item(selected[0])
        values = item['values']
        if not values:
            return

        self.selected_transaction_id = values[0]
        self.entry_date.delete(0, tk.END)
        self.entry_date.insert(0, values[1])

        self.entry_title.delete(0, tk.END)
        self.entry_title.insert(0, values[2])

        # Loại
        is_income = "Thu nhập" in values[3]
        self.var_trans_type.set("INCOME" if is_income else "EXPENSE")
        self._on_type_change()

        self.cbo_category.set(values[4])

        amount_clean = str(values[5]).replace(",", "").replace(".", "").replace(" ", "").replace("đ", "")
        self.entry_amount.delete(0, tk.END)
        self.entry_amount.insert(0, amount_clean)

        self.entry_note.delete(0, tk.END)
        self.entry_note.insert(0, values[6] if len(values) > 6 else "")

    def clear_form(self):
        self.selected_transaction_id = None
        self.entry_title.delete(0, tk.END)
        self.entry_amount.delete(0, tk.END)
        self.entry_date.delete(0, tk.END)
        self.entry_date.insert(0, datetime.now().strftime("%Y-%m-%d"))
        self.entry_note.delete(0, tk.END)
        self.tree.selection_remove(self.tree.selection())

    def _get_category_id_by_name(self, name):
        for c in self.categories_cache:
            if c[1] == name:
                return c[0]
        return None

    def add_transaction(self):
        title = self.entry_title.get().strip()
        amount_raw = self.entry_amount.get().strip().replace(",", "").replace(".", "")
        cat_name = self.cbo_category.get()
        t_date = self.entry_date.get().strip()
        note = self.entry_note.get().strip()

        if not title:
            messagebox.showwarning("Thiếu dữ liệu", "Vui lòng nhập tiêu đề giao dịch!")
            return
        try:
            amount = float(amount_raw)
            if amount <= 0:
                raise ValueError()
        except ValueError:
            messagebox.showwarning("Sai định dạng", "Số tiền phải là số lớn hơn 0!")
            return

        cat_id = self._get_category_id_by_name(cat_name)
        if not cat_id:
            messagebox.showwarning("Lỗi", "Vui lòng chọn danh mục hợp lệ!")
            return

        try:
            self.db.add_transaction(title, amount, cat_id, t_date, note)
            messagebox.showinfo("Thành công", "Đã thêm giao dịch thành công!")
            self.clear_form()
            self.filter_transactions()
        except Exception as e:
            messagebox.showerror("Lỗi CSDL", f"Không thể thêm giao dịch:\n{e}")

    def update_transaction(self):
        if not self.selected_transaction_id:
            messagebox.showwarning("Chưa chọn", "Vui lòng chọn 1 dòng trong bảng để cập nhật!")
            return

        title = self.entry_title.get().strip()
        amount_raw = self.entry_amount.get().strip().replace(",", "").replace(".", "")
        cat_name = self.cbo_category.get()
        t_date = self.entry_date.get().strip()
        note = self.entry_note.get().strip()

        if not title:
            messagebox.showwarning("Thiếu dữ liệu", "Vui lòng nhập tiêu đề giao dịch!")
            return
        try:
            amount = float(amount_raw)
            if amount <= 0:
                raise ValueError()
        except ValueError:
            messagebox.showwarning("Sai định dạng", "Số tiền phải là số lớn hơn 0!")
            return

        cat_id = self._get_category_id_by_name(cat_name)
        try:
            self.db.update_transaction(self.selected_transaction_id, title, amount, cat_id, t_date, note)
            messagebox.showinfo("Thành công", "Đã cập nhật giao dịch thành công!")
            self.clear_form()
            self.filter_transactions()
        except Exception as e:
            messagebox.showerror("Lỗi CSDL", f"Không thể cập nhật:\n{e}")

    def delete_transaction(self):
        if not self.selected_transaction_id:
            messagebox.showwarning("Chưa chọn", "Vui lòng chọn 1 dòng trong bảng để xóa!")
            return

        confirm = messagebox.askyesno("Xác nhận", "Bạn có chắc chắn muốn xóa giao dịch này không?")
        if confirm:
            try:
                self.db.delete_transaction(self.selected_transaction_id)
                messagebox.showinfo("Thành công", "Đã xóa giao dịch!")
                self.clear_form()
                self.filter_transactions()
            except Exception as e:
                messagebox.showerror("Lỗi CSDL", f"Không thể xóa:\n{e}")

    # ================= VẼ BIỂU ĐỒ =================
    def draw_chart(self):
        if not MATPLOTLIB_AVAILABLE:
            messagebox.showwarning("Thiếu thư viện", "Vui lòng cài đặt matplotlib bằng lệnh: pip install matplotlib")
            return

        month = int(self.cbo_chart_month.get())
        year = int(self.cbo_chart_year.get())

        data = self.db.get_expense_by_category(month=month, year=year)

        # Xóa canvas cũ nếu có
        for widget in self.chart_container.winfo_children():
            widget.destroy()

        if not data:
            lbl_no_data = ttk.Label(self.chart_container, text=f"Chưa có dữ liệu chi tiêu trong Tháng {month}/{year}.",
                                    font=("Segoe UI", 12, "italic"))
            lbl_no_data.pack(expand=True)
            return

        labels = [d[0] for d in data]
        values = [d[1] for d in data]

        fig = Figure(figsize=(8, 5), dpi=100)
        ax = fig.add_subplot(111)

        colors = ['#ff9999', '#66b3ff', '#99ff99', '#ffcc99', '#c2c2f0', '#ffb3e6', '#c4e17f']
        ax.pie(values, labels=labels, autopct='%1.1f%%', startangle=140, colors=colors[:len(labels)],
               wedgeprops={'edgecolor': 'white', 'linewidth': 1.5})
        ax.set_title(f"Tỷ trọng Chi tiêu Tháng {month}/{year}", fontsize=13, fontweight='bold', pad=15)

        self.chart_canvas = FigureCanvasTkAgg(fig, master=self.chart_container)
        self.chart_canvas.draw()
        self.chart_canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

    # ================= NGÂN SÁCH =================
    def load_budgets(self):
        month = int(self.cbo_b_month.get())
        year = int(self.cbo_b_year.get())

        for item in self.tree_budget.get_children():
            self.tree_budget.delete(item)

        try:
            rows = self.db.get_budgets_with_spent(month, year)
            if not rows:
                messagebox.showinfo("Thông báo", f"Chưa có hạn mức nào được đặt cho Tháng {month}/{year}.")
                return

            for b in rows:
                pct = b["percentage"]
                if pct < 80:
                    status = f"✅ An toàn ({pct:.1f}%)"
                    tag = "SAFE"
                elif pct <= 100:
                    status = f"⚠️ Cảnh báo: Sắp hết! ({pct:.1f}%)"
                    tag = "WARNING"
                else:
                    status = f"🚨 VƯỢT HẠN MỨC! ({pct:.1f}%)"
                    tag = "DANGER"

                self.tree_budget.insert("", tk.END, values=(
                    b["category_name"],
                    f"{b['limit_amount']:,.0f}",
                    f"{b['spent_amount']:,.0f}",
                    f"{b['remaining']:,.0f}",
                    f"{pct:.1f}%",
                    status
                ), tags=(tag,))
        except Exception as e:
            messagebox.showerror("Lỗi", f"Không thể tải ngân sách:\n{e}")

    def save_budget(self):
        cat_name = self.cbo_budget_cat.get()
        limit_raw = self.entry_budget_limit.get().strip().replace(",", "").replace(".", "")
        month = int(self.cbo_b_month.get())
        year = int(self.cbo_b_year.get())

        try:
            limit = float(limit_raw)
            if limit <= 0:
                raise ValueError()
        except ValueError:
            messagebox.showwarning("Lỗi", "Hạn mức phải là số dương!")
            return

        cat_id = self._get_category_id_by_name(cat_name)
        try:
            self.db.set_budget(cat_id, month, year, limit)
            messagebox.showinfo("Thành công", f"Đã lưu hạn mức cho danh mục '{cat_name}' Tháng {month}/{year}!")
            self.entry_budget_limit.delete(0, tk.END)
            self.load_budgets()
        except Exception as e:
            messagebox.showerror("Lỗi", f"Không thể lưu hạn mức:\n{e}")

    def delete_budget(self):
        selected = self.tree_budget.selection()
        if not selected:
            messagebox.showwarning("Chưa chọn", "Vui lòng chọn 1 dòng ngân sách trong bảng để xóa!")
            return
        cat_name = self.tree_budget.item(selected[0])['values'][0]
        cat_id = self._get_category_id_by_name(cat_name)
        month = int(self.cbo_b_month.get())
        year = int(self.cbo_b_year.get())

        if messagebox.askyesno("Xác nhận", f"Bạn có muốn xóa hạn mức của '{cat_name}' trong tháng {month}/{year}?"):
            try:
                # Tìm budget_id
                budgets = self.db.get_budgets_with_spent(month, year)
                for b in budgets:
                    if b["category_id"] == cat_id:
                        self.db.delete_budget(b["budget_id"])
                        break
                messagebox.showinfo("Thành công", "Đã xóa hạn mức thành công!")
                self.load_budgets()
            except Exception as e:
                messagebox.showerror("Lỗi", f"Không thể xóa hạn mức:\n{e}")

    # ================= XUẤT BÁO CÁO =================
    def export_csv(self):
        file_path = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV Files", "*.csv")],
                                                 initialfile=f"BaoCaoChiTieu_{datetime.now().strftime('%Y%m%d')}.csv")
        if not file_path:
            return

        try:
            rows = self.db.get_transactions()
            with open(file_path, mode="w", newline="", encoding="utf-8-sig") as f:
                writer = csv.writer(f)
                writer.writerow(["Mã GD", "Ngày", "Tiêu đề", "Loại", "Danh mục", "Số tiền (VND)", "Ghi chú"])
                for r in rows:
                    trans_id, t_date, title, cat_type, cat_name, amount, note, _ = r
                    type_str = "Thu nhập" if cat_type == "INCOME" else "Chi tiêu"
                    writer.writerow([trans_id, t_date, title, type_str, cat_name, f"{float(amount):,.0f}", note or ""])
            messagebox.showinfo("Thành công", f"Đã xuất dữ liệu ra file:\n{file_path}")
        except Exception as e:
            messagebox.showerror("Lỗi", f"Không thể xuất file CSV:\n{e}")

    def export_excel(self):
        if not OPENPYXL_AVAILABLE:
            messagebox.showwarning("Thiếu thư viện", "Cần cài thư viện openpyxl:\npip install openpyxl")
            return

        file_path = filedialog.asksaveasfilename(defaultextension=".xlsx", filetypes=[("Excel Files", "*.xlsx")],
                                                 initialfile=f"BaoCaoChiTieu_{datetime.now().strftime('%Y%m%d')}.xlsx")
        if not file_path:
            return

        try:
            wb = openpyxl.Workbook()
            ws = wb.active
            ws.title = "Giao dịch chi tiêu"

            # Tiêu đề cột
            headers = ["Mã GD", "Ngày", "Tiêu đề", "Loại", "Danh mục", "Số tiền (VND)", "Ghi chú"]
            ws.append(headers)

            rows = self.db.get_transactions()
            for r in rows:
                trans_id, t_date, title, cat_type, cat_name, amount, note, _ = r
                type_str = "Thu nhập" if cat_type == "INCOME" else "Chi tiêu"
                ws.append([trans_id, str(t_date), title, type_str, cat_name, float(amount), note or ""])

            wb.save(file_path)
            messagebox.showinfo("Thành công", f"Đã xuất file Excel thành công:\n{file_path}")
        except Exception as e:
            messagebox.showerror("Lỗi", f"Không thể xuất file Excel:\n{e}")

    def check_db_connection(self):
        ok, msg = self.db.test_connection()
        if ok:
            messagebox.showinfo("Kết nối CSDL", f"✅ {msg}")
        else:
            messagebox.showerror("Lỗi kết nối", f"❌ {msg}\n\nVui lòng kiểm tra lại thông tin cấu hình trong file 'config.py'.")
