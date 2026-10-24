"""
================================================================================
BUDGETBUDDY - MÀN HÌNH GIAO DIỆN HIỆN ĐẠI (MODERN UI REDESIGN)
Môn học: Lập trình Python nâng cao (Nhóm 14)
Chạy trực tiếp: python preview_app.py
================================================================================
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from datetime import datetime
import csv

# Thử import matplotlib để vẽ biểu đồ tròn Donut
try:
    import matplotlib
    matplotlib.use("TkAgg")
    from matplotlib.figure import Figure
    from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
    HAS_MATPLOTLIB = True
except ImportError:
    HAS_MATPLOTLIB = False


# Bảng mã màu hiện đại (Modern SaaS Palette)
COLORS = {
    "bg_main": "#f8fafc",        # Slate 50 (Nền tổng thể)
    "card_bg": "#ffffff",        # Trắng tinh khiết
    "border": "#e2e8f0",         # Slate 200 (Viền tinh tế)
    "border_focus": "#3b82f6",   # Xanh dương nhấn
    "text_main": "#0f172a",      # Slate 900 (Chữ đậm)
    "text_muted": "#64748b",     # Slate 500 (Chữ phụ)
    
    # Header & Accent
    "header_bg": "#1e293b",      # Slate 800
    "accent_blue": "#2563eb",    # Blue 600
    
    # Trạng thái
    "income_bg": "#ecfdf5",      # Emerald 50
    "income_border": "#a7f3d0",  # Emerald 200
    "income_text": "#059669",    # Emerald 600
    "income_badge": "#10b981",   # Emerald 500
    
    "expense_bg": "#fff1f2",     # Rose 50
    "expense_border": "#fecdd3", # Rose 200
    "expense_text": "#e11d48",   # Rose 600
    "expense_badge": "#f43f5e",  # Rose 500
    
    "balance_bg": "#eff6ff",     # Blue 50
    "balance_border": "#bfdbfe", # Blue 200
    "balance_text": "#1d4ed8",   # Blue 700
    
    # Nút bấm & Hiệu ứng Hover
    "btn_add": "#059669",
    "btn_add_hover": "#047857",
    "btn_edit": "#2563eb",
    "btn_edit_hover": "#1d4ed8",
    "btn_del": "#e11d48",
    "btn_del_hover": "#be123c",
    "btn_clear": "#64748b",
    "btn_clear_hover": "#475569",
}


class HoverButton(tk.Button):
    """Nút bấm tùy biến có hiệu ứng Hover đổi màu mượt mà"""
    def __init__(self, master, default_bg, hover_bg, **kw):
        super().__init__(master, bg=default_bg, activebackground=hover_bg, relief="flat", cursor="hand2", **kw)
        self.default_bg = default_bg
        self.hover_bg = hover_bg
        self.bind("<Enter>", lambda e: self.config(bg=self.hover_bg))
        self.bind("<Leave>", lambda e: self.config(bg=self.default_bg))


class BudgetBuddyPreviewApp(tk.Tk):
    def __init__(self):
        super().__init__()

        self.title("BudgetBuddy v1.0.0 — Quản lý Chi tiêu Cá nhân (Nhóm 14)")
        self.geometry("1140x720")
        self.minsize(1020, 660)
        self.configure(bg=COLORS["bg_main"])

        # Dữ liệu giả lập ban đầu
        self.transactions = [
            {"id": 1, "date": "2026-10-01", "title": "Lương làm thêm part-time", "type": "INCOME", "category": "Lương / Thưởng", "amount": 8000000, "note": "Lương tháng 9 nhận đầu tháng 10"},
            {"id": 2, "date": "2026-10-02", "title": "Tiền trọ tháng 10", "type": "EXPENSE", "category": "Tiền trọ / Điện nước", "amount": 3000000, "note": "Đã chuyển khoản cho chủ nhà"},
            {"id": 3, "date": "2026-10-03", "title": "Trợ cấp sinh hoạt gia đình", "type": "INCOME", "category": "Trợ cấp", "amount": 7500000, "note": "Tiền bố mẹ gửi sinh hoạt"},
            {"id": 4, "date": "2026-10-05", "title": "Mua giáo trình Python nâng cao", "type": "EXPENSE", "category": "Học tập & Sách vở", "amount": 1500000, "note": "Sách chuyên ngành & tài liệu"},
            {"id": 5, "date": "2026-10-08", "title": "Bảo dưỡng xe máy & xăng xe", "type": "EXPENSE", "category": "Đi lại / Xăng xe", "amount": 1200000, "note": "Thay nhớt & đổ xăng"},
            {"id": 6, "date": "2026-10-10", "title": "Đi siêu thị & ăn uống cả tuần", "type": "EXPENSE", "category": "Ăn uống", "amount": 2500000, "note": "Cơm trưa, cà phê bạn bè"}
        ]

        self.budgets = [
            {"category": "Ăn uống", "limit": 3000000},
            {"category": "Tiền trọ / Điện nước", "limit": 3000000},
            {"category": "Đi lại / Xăng xe", "limit": 2000000},
            {"category": "Học tập & Sách vở", "limit": 2000000},
            {"category": "Mua sắm & Giải trí", "limit": 1500000}
        ]

        self.selected_trans_id = None

        self._setup_ttk_styles()
        self._build_top_banner()
        self._build_kpi_cards()
        self._build_tabs()

        self.update_stats()
        self.render_treeview()
        self.draw_chart()
        self.render_budgets()

    def _setup_ttk_styles(self):
        self.style = ttk.Style(self)
        self.style.theme_use("clam")

        # Cấu hình Tabs
        self.style.configure("TNotebook", background=COLORS["bg_main"], borderwidth=0)
        self.style.configure("TNotebook.Tab", font=("Segoe UI", 10, "bold"), padding=[20, 10],
                             background="#e2e8f0", foreground=COLORS["text_muted"])
        self.style.map("TNotebook.Tab",
                       background=[("selected", COLORS["card_bg"])],
                       foreground=[("selected", COLORS["accent_blue"])])

        # Cấu hình Treeview
        self.style.configure("Treeview.Heading", font=("Segoe UI", 10, "bold"),
                             background="#f1f5f9", foreground=COLORS["text_main"], relief="flat", padding=[8, 6])
        self.style.configure("Treeview", font=("Segoe UI", 9), rowheight=32,
                             background=COLORS["card_bg"], fieldbackground=COLORS["card_bg"], borderwidth=0)
        self.style.map("Treeview",
                       background=[("selected", "#dbeafe")],
                       foreground=[("selected", "#1e3a8a")])

        # Scrollbar
        self.style.configure("Vertical.TScrollbar", gripcount=0, background="#cbd5e1", troughcolor="#f1f5f9", borderwidth=0)

    def _build_top_banner(self):
        """Thanh Banner trên cùng kiểu phần mềm chuyên nghiệp"""
        banner = tk.Frame(self, bg=COLORS["header_bg"], height=48)
        banner.pack(fill=tk.X)

        left_f = tk.Frame(banner, bg=COLORS["header_bg"])
        left_f.pack(side=tk.LEFT, padx=16, pady=8)

        # Biểu tượng & Tên
        tk.Label(left_f, text="💎 BUDGETBUDDY", font=("Segoe UI", 13, "bold"), fg="#ffffff", bg=COLORS["header_bg"]).pack(side=tk.LEFT)
        tk.Label(left_f, text=" | Hệ thống Quản lý Chi tiêu Cá nhân", font=("Segoe UI", 9), fg="#94a3b8", bg=COLORS["header_bg"]).pack(side=tk.LEFT, padx=6)

        # Trạng thái bên phải
        right_f = tk.Frame(banner, bg=COLORS["header_bg"])
        right_f.pack(side=tk.RIGHT, padx=16, pady=8)

        status_badge = tk.Frame(right_f, bg="#064e3b", padx=8, pady=3, bd=1, relief="flat")
        status_badge.pack(side=tk.RIGHT)
        tk.Label(status_badge, text="● CSDL: Kết nối sẵn sàng", font=("Segoe UI", 8, "bold"), fg="#34d399", bg="#064e3b").pack()

    def _build_kpi_cards(self):
        """Khung hiển thị 3 Thẻ KPI tài chính nổi bật"""
        kpi_wrap = tk.Frame(self, bg=COLORS["bg_main"])
        kpi_wrap.pack(fill=tk.X, padx=16, pady=(12, 6))

        # Card 1: Thu nhập
        c1 = tk.Frame(kpi_wrap, bg=COLORS["income_bg"], bd=1, relief="solid", highlightbackground=COLORS["income_border"], highlightthickness=1)
        c1.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 8), ipady=8, ipadx=12)

        tk.Label(c1, text="TỔNG THU NHẬP", font=("Segoe UI", 8, "bold"), fg=COLORS["income_text"], bg=COLORS["income_bg"]).pack(anchor=tk.W, padx=8, pady=(4, 0))
        self.lbl_income = tk.Label(c1, text="+0 đ", font=("Segoe UI", 16, "bold"), fg=COLORS["income_text"], bg=COLORS["income_bg"])
        self.lbl_income.pack(anchor=tk.W, padx=8)

        # Card 2: Chi tiêu
        c2 = tk.Frame(kpi_wrap, bg=COLORS["expense_bg"], bd=1, relief="solid", highlightbackground=COLORS["expense_border"], highlightthickness=1)
        c2.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=4, ipady=8, ipadx=12)

        tk.Label(c2, text="TỔNG CHI TIÊU", font=("Segoe UI", 8, "bold"), fg=COLORS["expense_text"], bg=COLORS["expense_bg"]).pack(anchor=tk.W, padx=8, pady=(4, 0))
        self.lbl_expense = tk.Label(c2, text="-0 đ", font=("Segoe UI", 16, "bold"), fg=COLORS["expense_text"], bg=COLORS["expense_bg"])
        self.lbl_expense.pack(anchor=tk.W, padx=8)

        # Card 3: Số dư
        c3 = tk.Frame(kpi_wrap, bg=COLORS["balance_bg"], bd=1, relief="solid", highlightbackground=COLORS["balance_border"], highlightthickness=1)
        c3.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(8, 0), ipady=8, ipadx=12)

        tk.Label(c3, text="SỐ DƯ KHẢ DỤNG", font=("Segoe UI", 8, "bold"), fg=COLORS["balance_text"], bg=COLORS["balance_bg"]).pack(anchor=tk.W, padx=8, pady=(4, 0))
        self.lbl_balance = tk.Label(c3, text="0 đ", font=("Segoe UI", 16, "bold"), fg=COLORS["balance_text"], bg=COLORS["balance_bg"])
        self.lbl_balance.pack(anchor=tk.W, padx=8)

    def _build_tabs(self):
        self.notebook = ttk.Notebook(self)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=16, pady=8)

        self.tab_trans = tk.Frame(self.notebook, bg=COLORS["bg_main"])
        self.tab_chart = tk.Frame(self.notebook, bg=COLORS["bg_main"])
        self.tab_budget = tk.Frame(self.notebook, bg=COLORS["bg_main"])
        self.tab_export = tk.Frame(self.notebook, bg=COLORS["bg_main"])

        self.notebook.add(self.tab_trans, text="  📝 Quản lý Thu / Chi  ")
        self.notebook.add(self.tab_chart, text="  📊 Biểu đồ & Phân tích  ")
        self.notebook.add(self.tab_budget, text="  🎯 Hạn mức Ngân sách  ")
        self.notebook.add(self.tab_export, text="  📄 Xuất Báo cáo  ")

        self._build_tab_trans()
        self._build_tab_chart()
        self._build_tab_budget()
        self._build_tab_export()

    # ================= TAB 1: GIAO DỊCH =================
    def _build_tab_trans(self):
        # Card Form bên trái
        left_card = tk.Frame(self.tab_trans, bg=COLORS["card_bg"], bd=1, relief="solid",
                             highlightbackground=COLORS["border"], highlightthickness=1, padx=16, pady=14)
        left_card.pack(side=tk.LEFT, fill=tk.Y, padx=(4, 8), pady=8)

        tk.Label(left_card, text="✍️ Nhập Giao Dịch Mới", font=("Segoe UI", 11, "bold"),
                 fg=COLORS["text_main"], bg=COLORS["card_bg"]).pack(anchor=tk.W, pady=(0, 10))

        # Tiêu đề
        tk.Label(left_card, text="Tiêu đề giao dịch: *", font=("Segoe UI", 9, "bold"),
                 fg=COLORS["text_muted"], bg=COLORS["card_bg"]).pack(anchor=tk.W, pady=(2, 2))
        self.ent_title = ttk.Entry(left_card, width=32, font=("Segoe UI", 9))
        self.ent_title.pack(fill=tk.X, pady=(0, 8))

        # Số tiền
        tk.Label(left_card, text="Số tiền (VNĐ): *", font=("Segoe UI", 9, "bold"),
                 fg=COLORS["text_muted"], bg=COLORS["card_bg"]).pack(anchor=tk.W, pady=(2, 2))
        self.ent_amount = ttk.Entry(left_card, width=32, font=("Segoe UI", 9))
        self.ent_amount.pack(fill=tk.X, pady=(0, 8))

        # Loại
        tk.Label(left_card, text="Loại giao dịch:", font=("Segoe UI", 9, "bold"),
                 fg=COLORS["text_muted"], bg=COLORS["card_bg"]).pack(anchor=tk.W, pady=(2, 2))
        self.var_type = tk.StringVar(value="EXPENSE")
        type_f = tk.Frame(left_card, bg=COLORS["card_bg"])
        type_f.pack(fill=tk.X, pady=(0, 8))
        tk.Radiobutton(type_f, text="🔴 Chi tiêu (-)", variable=self.var_type, value="EXPENSE",
                       bg=COLORS["card_bg"], fg=COLORS["expense_text"], font=("Segoe UI", 9, "bold"),
                       command=self._on_type_change).pack(side=tk.LEFT, padx=(0, 10))
        tk.Radiobutton(type_f, text="🟢 Thu nhập (+)", variable=self.var_type, value="INCOME",
                       bg=COLORS["card_bg"], fg=COLORS["income_text"], font=("Segoe UI", 9, "bold"),
                       command=self._on_type_change).pack(side=tk.LEFT)

        # Danh mục
        tk.Label(left_card, text="Danh mục: *", font=("Segoe UI", 9, "bold"),
                 fg=COLORS["text_muted"], bg=COLORS["card_bg"]).pack(anchor=tk.W, pady=(2, 2))
        self.cbo_cat = ttk.Combobox(left_card, state="readonly", font=("Segoe UI", 9))
        self.cbo_cat.pack(fill=tk.X, pady=(0, 8))
        self._on_type_change()

        # Ngày
        tk.Label(left_card, text="Ngày giao dịch:", font=("Segoe UI", 9, "bold"),
                 fg=COLORS["text_muted"], bg=COLORS["card_bg"]).pack(anchor=tk.W, pady=(2, 2))
        self.ent_date = ttk.Entry(left_card, width=32, font=("Segoe UI", 9))
        self.ent_date.insert(0, datetime.now().strftime("%Y-%m-%d"))
        self.ent_date.pack(fill=tk.X, pady=(0, 8))

        # Ghi chú
        tk.Label(left_card, text="Ghi chú thêm:", font=("Segoe UI", 9, "bold"),
                 fg=COLORS["text_muted"], bg=COLORS["card_bg"]).pack(anchor=tk.W, pady=(2, 2))
        self.ent_note = ttk.Entry(left_card, width=32, font=("Segoe UI", 9))
        self.ent_note.pack(fill=tk.X, pady=(0, 14))

        # Action Buttons với Hover
        HoverButton(left_card, default_bg=COLORS["btn_add"], hover_bg=COLORS["btn_add_hover"],
                    text="➕  Thêm Giao Dịch", fg="#ffffff", font=("Segoe UI", 9, "bold"),
                    pady=6, command=self.add_transaction).pack(fill=tk.X, pady=3)

        HoverButton(left_card, default_bg=COLORS["btn_edit"], hover_bg=COLORS["btn_edit_hover"],
                    text="✏️  Cập Nhật Dòng Chọn", fg="#ffffff", font=("Segoe UI", 9, "bold"),
                    pady=6, command=self.update_transaction).pack(fill=tk.X, pady=3)

        HoverButton(left_card, default_bg=COLORS["btn_del"], hover_bg=COLORS["btn_del_hover"],
                    text="🗑️  Xóa Giao Dịch", fg="#ffffff", font=("Segoe UI", 9, "bold"),
                    pady=6, command=self.delete_transaction).pack(fill=tk.X, pady=3)

        HoverButton(left_card, default_bg=COLORS["btn_clear"], hover_bg=COLORS["btn_clear_hover"],
                    text="🔄  Làm Mới Form", fg="#ffffff", font=("Segoe UI", 9),
                    pady=5, command=self.clear_form).pack(fill=tk.X, pady=(6, 0))

        # Cột Bảng Treeview bên phải
        right_wrap = tk.Frame(self.tab_trans, bg=COLORS["bg_main"])
        right_wrap.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=(4, 4), pady=8)

        # Thanh tìm kiếm & bộ lọc
        search_bar = tk.Frame(right_wrap, bg=COLORS["card_bg"], bd=1, relief="solid",
                              highlightbackground=COLORS["border"], highlightthickness=1, padx=10, pady=8)
        search_bar.pack(fill=tk.X, pady=(0, 8))

        tk.Label(search_bar, text="🔍 Tìm kiếm:", font=("Segoe UI", 9, "bold"),
                 fg=COLORS["text_muted"], bg=COLORS["card_bg"]).pack(side=tk.LEFT, padx=(0, 6))

        self.ent_search = ttk.Entry(search_bar, width=18, font=("Segoe UI", 9))
        self.ent_search.pack(side=tk.LEFT, padx=(0, 10))
        self.ent_search.bind("<KeyRelease>", lambda e: self.render_treeview())

        tk.Label(search_bar, text="Lọc:", font=("Segoe UI", 9),
                 fg=COLORS["text_muted"], bg=COLORS["card_bg"]).pack(side=tk.LEFT, padx=(0, 4))

        self.cbo_filter_type = ttk.Combobox(search_bar, values=["Tất cả", "Chi tiêu", "Thu nhập"], width=9, state="readonly")
        self.cbo_filter_type.set("Tất cả")
        self.cbo_filter_type.pack(side=tk.LEFT, padx=(0, 8))
        self.cbo_filter_type.bind("<<ComboboxSelected>>", lambda e: self.render_treeview())

        HoverButton(search_bar, default_bg="#94a3b8", hover_bg="#64748b", text="✖ Đặt lại",
                    fg="#ffffff", font=("Segoe UI", 8), padx=8, pady=2, command=self.reset_filter).pack(side=tk.LEFT)

        # Bảng dữ liệu Treeview
        tree_card = tk.Frame(right_wrap, bg=COLORS["card_bg"], bd=1, relief="solid",
                             highlightbackground=COLORS["border"], highlightthickness=1)
        tree_card.pack(fill=tk.BOTH, expand=True)

        cols = ("id", "date", "title", "cat", "amount", "note")
        self.tree = ttk.Treeview(tree_card, columns=cols, show="headings", selectmode="browse")

        self.tree.heading("id", text="#", anchor=tk.CENTER)
        self.tree.heading("date", text="Ngày GD", anchor=tk.CENTER)
        self.tree.heading("title", text="Tiêu đề giao dịch", anchor=tk.W)
        self.tree.heading("cat", text="Danh mục", anchor=tk.W)
        self.tree.heading("amount", text="Số tiền (đ)", anchor=tk.E)
        self.tree.heading("note", text="Ghi chú chi tiết", anchor=tk.W)

        self.tree.column("id", width=36, anchor=tk.CENTER)
        self.tree.column("date", width=85, anchor=tk.CENTER)
        self.tree.column("title", width=190, anchor=tk.W)
        self.tree.column("cat", width=130, anchor=tk.W)
        self.tree.column("amount", width=120, anchor=tk.E)
        self.tree.column("note", width=160, anchor=tk.W)

        sb = ttk.Scrollbar(tree_card, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscrollcommand=sb.set)

        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        sb.pack(side=tk.RIGHT, fill=tk.Y)

        # Tag phân màu chữ
        self.tree.tag_configure("INCOME_ODD", foreground="#059669", background="#ffffff")
        self.tree.tag_configure("INCOME_EVEN", foreground="#059669", background="#f8fafc")
        self.tree.tag_configure("EXPENSE_ODD", foreground="#e11d48", background="#ffffff")
        self.tree.tag_configure("EXPENSE_EVEN", foreground="#e11d48", background="#f8fafc")

        self.tree.bind("<<TreeviewSelect>>", self._on_tree_select)

    def _on_type_change(self):
        t = self.var_type.get()
        if t == "EXPENSE":
            cats = ["Ăn uống", "Tiền trọ / Điện nước", "Học tập & Sách vở", "Đi lại / Xăng xe", "Mua sắm & Giải trí", "Y tế & Sức khỏe"]
        else:
            cats = ["Lương / Thưởng", "Trợ cấp", "Học bổng", "Thu nhập khác"]
        self.cbo_cat["values"] = cats
        if cats:
            self.cbo_cat.set(cats[0])

    def render_treeview(self):
        for row in self.tree.get_children():
            self.tree.delete(row)

        kw = self.ent_search.get().lower().strip()
        f_type = self.cbo_filter_type.get()

        for idx, t in enumerate(self.transactions):
            match_kw = kw in t["title"].lower() or kw in t["note"].lower() or kw in t["category"].lower()
            match_type = True
            if f_type == "Chi tiêu" and t["type"] != "EXPENSE": match_type = False
            if f_type == "Thu nhập" and t["type"] != "INCOME": match_type = False

            if match_kw and match_type:
                prefix = "+" if t["type"] == "INCOME" else "-"
                amt_str = f"{prefix}{t['amount']:,.0f}"
                is_even = (idx % 2 == 0)
                tag = f"{t['type']}_{'EVEN' if is_even else 'ODD'}"
                self.tree.insert("", tk.END, values=(t["id"], t["date"], t["title"], t["category"], amt_str, t["note"]), tags=(tag,))

    def _on_tree_select(self, event):
        sel = self.tree.selection()
        if not sel: return
        vals = self.tree.item(sel[0], "values")
        if not vals: return

        self.selected_trans_id = int(vals[0])
        self.ent_title.delete(0, tk.END); self.ent_title.insert(0, vals[2])
        self.ent_date.delete(0, tk.END); self.ent_date.insert(0, vals[1])
        self.ent_note.delete(0, tk.END); self.ent_note.insert(0, vals[5])

        item = next((x for x in self.transactions if x["id"] == self.selected_trans_id), None)
        if item:
            self.var_type.set(item["type"])
            self._on_type_change()
            self.cbo_cat.set(item["category"])
            self.ent_amount.delete(0, tk.END)
            self.ent_amount.insert(0, str(item["amount"]))

    def clear_form(self):
        self.selected_trans_id = None
        self.ent_title.delete(0, tk.END)
        self.ent_amount.delete(0, tk.END)
        self.ent_note.delete(0, tk.END)
        self.ent_date.delete(0, tk.END)
        self.ent_date.insert(0, datetime.now().strftime("%Y-%m-%d"))
        if self.tree.selection():
            self.tree.selection_remove(self.tree.selection())

    def reset_filter(self):
        self.ent_search.delete(0, tk.END)
        self.cbo_filter_type.set("Tất cả")
        self.render_treeview()

    def update_stats(self):
        inc = sum(t["amount"] for t in self.transactions if t["type"] == "INCOME")
        exp = sum(t["amount"] for t in self.transactions if t["type"] == "EXPENSE")
        bal = inc - exp

        self.lbl_income.config(text=f"+{inc:,.0f} đ")
        self.lbl_expense.config(text=f"-{exp:,.0f} đ")
        self.lbl_balance.config(text=f"{bal:,.0f} đ")

    def add_transaction(self):
        title = self.ent_title.get().strip()
        amt_raw = self.ent_amount.get().strip().replace(",", "")
        cat = self.cbo_cat.get()
        date = self.ent_date.get().strip()
        note = self.ent_note.get().strip()

        if not title:
            messagebox.showwarning("Thiếu dữ liệu", "Vui lòng nhập tiêu đề giao dịch!")
            return
        try:
            amt = float(amt_raw)
            if amt <= 0: raise ValueError()
        except ValueError:
            messagebox.showwarning("Sai định dạng", "Số tiền phải là số lớn hơn 0!")
            return

        next_id = max([t["id"] for t in self.transactions], default=0) + 1
        self.transactions.insert(0, {
            "id": next_id, "date": date, "title": title, "type": self.var_type.get(),
            "category": cat, "amount": amt, "note": note
        })

        messagebox.showinfo("Thành công", f"Đã thêm thành công giao dịch: {title}")
        self.clear_form()
        self.update_stats()
        self.render_treeview()
        self.draw_chart()
        self.render_budgets()

    def update_transaction(self):
        if not self.selected_trans_id:
            messagebox.showwarning("Chưa chọn", "Vui lòng click chọn 1 giao dịch trong bảng để cập nhật!")
            return
        title = self.ent_title.get().strip()
        amt_raw = self.ent_amount.get().strip().replace(",", "")
        cat = self.cbo_cat.get()
        date = self.ent_date.get().strip()
        note = self.ent_note.get().strip()

        try:
            amt = float(amt_raw)
            if amt <= 0: raise ValueError()
        except ValueError:
            messagebox.showwarning("Sai định dạng", "Số tiền phải là số lớn hơn 0!")
            return

        for t in self.transactions:
            if t["id"] == self.selected_trans_id:
                t["title"] = title
                t["amount"] = amt
                t["category"] = cat
                t["date"] = date
                t["note"] = note
                t["type"] = self.var_type.get()
                break

        messagebox.showinfo("Thành công", "Đã cập nhật giao dịch thành công!")
        self.clear_form()
        self.update_stats()
        self.render_treeview()
        self.draw_chart()
        self.render_budgets()

    def delete_transaction(self):
        if not self.selected_trans_id:
            messagebox.showwarning("Chưa chọn", "Vui lòng click chọn 1 giao dịch trong bảng để xóa!")
            return
        if messagebox.askyesno("Xác nhận xóa", "Bạn có chắc chắn muốn xóa giao dịch này?"):
            self.transactions = [t for t in self.transactions if t["id"] != self.selected_trans_id]
            self.clear_form()
            self.update_stats()
            self.render_treeview()
            self.draw_chart()
            self.render_budgets()

    # ================= TAB 2: BIỂU ĐỒ =================
    def _build_tab_chart(self):
        card = tk.Frame(self.tab_chart, bg=COLORS["card_bg"], bd=1, relief="solid",
                        highlightbackground=COLORS["border"], highlightthickness=1)
        card.pack(fill=tk.BOTH, expand=True, padx=12, pady=10)

        top_f = tk.Frame(card, bg=COLORS["card_bg"], padx=16, pady=12)
        top_f.pack(fill=tk.X)

        tk.Label(top_f, text="📊 Cơ cấu Tỷ trọng Chi tiêu Theo Danh mục", font=("Segoe UI", 12, "bold"),
                 bg=COLORS["card_bg"], fg=COLORS["text_main"]).pack(side=tk.LEFT)

        HoverButton(top_f, default_bg=COLORS["accent_blue"], hover_bg="#1d4ed8",
                    text="🔄 Làm mới biểu đồ", fg="#ffffff", font=("Segoe UI", 9, "bold"),
                    padx=12, pady=5, command=self.draw_chart).pack(side=tk.RIGHT)

        self.chart_area = tk.Frame(card, bg=COLORS["card_bg"])
        self.chart_area.pack(fill=tk.BOTH, expand=True, padx=16, pady=(0, 16))

    def draw_chart(self):
        for widget in self.chart_area.winfo_children():
            widget.destroy()

        cat_sums = {}
        for t in self.transactions:
            if t["type"] == "EXPENSE":
                c = t["category"]
                cat_sums[c] = cat_sums.get(c, 0) + t["amount"]

        if not cat_sums:
            lbl = tk.Label(self.chart_area, text="Chưa có dữ liệu chi tiêu để phân tích.", font=("Segoe UI", 11), bg=COLORS["card_bg"], fg=COLORS["text_muted"])
            lbl.pack(expand=True)
            return

        labels = list(cat_sums.keys())
        values = list(cat_sums.values())
        palette = ["#f43f5e", "#f59e0b", "#3b82f6", "#10b981", "#8b5cf6", "#06b6d4"]

        if HAS_MATPLOTLIB:
            fig = Figure(figsize=(7, 4.4), dpi=95, facecolor="#ffffff")
            ax = fig.add_subplot(111)
            wedges, texts, autotexts = ax.pie(values, labels=labels, autopct="%1.1f%%", startangle=140,
                                              colors=palette[:len(labels)],
                                              wedgeprops=dict(width=0.45, edgecolor="white", linewidth=2.5))
            for at in autotexts:
                at.set_fontsize(9)
                at.set_weight("bold")
            ax.set_title("Tỷ trọng Khoản chi tiêu Tháng 10/2026", fontsize=11, fontweight="bold", pad=12)

            canvas = FigureCanvasTkAgg(fig, master=self.chart_area)
            canvas.draw()
            canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        else:
            # Fallback Tkinter Canvas đẹp mắt
            cv = tk.Canvas(self.chart_area, bg=COLORS["card_bg"], highlightthickness=0)
            cv.pack(fill=tk.BOTH, expand=True)
            total = sum(values)
            start_ang = 0
            cx, cy, r = 260, 180, 120

            for i, (lab, val) in enumerate(zip(labels, values)):
                extent = (val / total) * 360
                color = palette[i % len(palette)]
                cv.create_arc(cx - r, cy - r, cx + r, cy + r, start=start_ang, extent=extent, fill=color, outline="white", width=2)
                
                # Legend bên phải
                ly = 80 + i * 36
                cv.create_rectangle(450, ly, 466, ly + 16, fill=color, outline="")
                pct = (val / total) * 100
                cv.create_text(478, ly + 8, text=f"{lab}: {val:,.0f} đ ({pct:.1f}%)", anchor=tk.W, font=("Segoe UI", 9, "bold"), fill=COLORS["text_main"])
                start_ang += extent

            # Center Hole
            r_in = 65
            cv.create_oval(cx - r_in, cy - r_in, cx + r_in, cy + r_in, fill="#ffffff", outline="")
            cv.create_text(cx, cy, text=f"TỔNG CHI\n{total:,.0f} đ", justify=tk.CENTER, font=("Segoe UI", 10, "bold"), fill=COLORS["expense_text"])

    # ================= TAB 3: HẠN MỨC NGÂN SÁCH =================
    def _build_tab_budget(self):
        card = tk.Frame(self.tab_budget, bg=COLORS["card_bg"], bd=1, relief="solid",
                        highlightbackground=COLORS["border"], highlightthickness=1, padx=20, pady=16)
        card.pack(fill=tk.BOTH, expand=True, padx=12, pady=10)

        tk.Label(card, text="🎯 Tiến Độ & Cảnh Báo Hạn Mức Ngân Sách Tháng 10/2026",
                 font=("Segoe UI", 12, "bold"), bg=COLORS["card_bg"], fg=COLORS["text_main"]).pack(anchor=tk.W, pady=(0, 14))

        self.budget_box = tk.Frame(card, bg=COLORS["card_bg"])
        self.budget_box.pack(fill=tk.BOTH, expand=True)

    def render_budgets(self):
        for w in self.budget_box.winfo_children():
            w.destroy()

        spent_map = {}
        for t in self.transactions:
            if t["type"] == "EXPENSE":
                c = t["category"]
                spent_map[c] = spent_map.get(c, 0) + t["amount"]

        for b in self.budgets:
            cat = b["category"]
            limit = b["limit"]
            spent = spent_map.get(cat, 0)
            pct = (spent / limit * 100) if limit > 0 else 0

            row_f = tk.Frame(self.budget_box, bg=COLORS["card_bg"], bd=1, relief="solid",
                             highlightbackground=COLORS["border"], highlightthickness=1, padx=12, pady=8)
            row_f.pack(fill=tk.X, pady=6)

            if pct < 80:
                status_txt = f"✅ An toàn ({pct:.1f}%)"
                status_color = COLORS["income_text"]
            elif pct <= 100:
                status_txt = f"⚠️ Cảnh báo: Sắp hết! ({pct:.1f}%)"
                status_color = "#d97706"
            else:
                status_txt = f"🚨 VƯỢT HẠN MỨC! ({pct:.1f}%)"
                status_color = COLORS["expense_text"]

            top_row = tk.Frame(row_f, bg=COLORS["card_bg"])
            top_row.pack(fill=tk.X)
            tk.Label(top_row, text=f"{cat} (Đã tiêu: {spent:,.0f} đ / Hạn mức: {limit:,.0f} đ)",
                     font=("Segoe UI", 9, "bold"), bg=COLORS["card_bg"], fg=COLORS["text_main"]).pack(side=tk.LEFT)
            tk.Label(top_row, text=status_txt, font=("Segoe UI", 9, "bold"), bg=COLORS["card_bg"], fg=status_color).pack(side=tk.RIGHT)

            pb = ttk.Progressbar(row_f, maximum=100, value=min(pct, 100), length=400)
            pb.pack(fill=tk.X, pady=(6, 2))

    # ================= TAB 4: XUẤT BÁO CÁO =================
    def _build_tab_export(self):
        wrap = tk.Frame(self.tab_export, bg=COLORS["card_bg"], bd=1, relief="solid",
                        highlightbackground=COLORS["border"], highlightthickness=1, padx=24, pady=24)
        wrap.pack(fill=tk.X, padx=20, pady=20)

        tk.Label(wrap, text="📄 Xuất Báo Cáo Dữ Liệu Tài Chính", font=("Segoe UI", 12, "bold"),
                 bg=COLORS["card_bg"], fg=COLORS["text_main"]).pack(anchor=tk.W, pady=(0, 6))
        tk.Label(wrap, text="Dữ liệu được xuất theo chuẩn mã hóa UTF-8 tiếng Việt, tương thích 100% với Microsoft Excel.",
                 font=("Segoe UI", 9), bg=COLORS["card_bg"], fg=COLORS["text_muted"]).pack(anchor=tk.W, pady=(0, 16))

        btn_row = tk.Frame(wrap, bg=COLORS["card_bg"])
        btn_row.pack(anchor=tk.W)

        HoverButton(btn_row, default_bg="#0284c7", hover_bg="#0369a1",
                    text="📄 Xuất file CSV (Excel tiếng Việt)", fg="#ffffff", font=("Segoe UI", 9, "bold"),
                    padx=16, pady=8, command=self.export_csv).pack(side=tk.LEFT, padx=(0, 12))

        HoverButton(btn_row, default_bg=COLORS["btn_add"], hover_bg=COLORS["btn_add_hover"],
                    text="💾 Lưu bản sao dự phòng", fg="#ffffff", font=("Segoe UI", 9, "bold"),
                    padx=16, pady=8, command=lambda: messagebox.showinfo("Thông báo", "Đã tạo bản sao lưu dữ liệu an toàn!")).pack(side=tk.LEFT)

    def export_csv(self):
        file_path = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV Files", "*.csv")],
                                                 initialfile=f"BaoCao_BudgetBuddy_{datetime.now().strftime('%Y%m%d')}.csv")
        if not file_path:
            return
        try:
            with open(file_path, mode="w", newline="", encoding="utf-8-sig") as f:
                writer = csv.writer(f)
                writer.writerow(["Mã GD", "Ngày", "Tiêu đề", "Loại", "Danh mục", "Số tiền (VND)", "Ghi chú"])
                for t in self.transactions:
                    t_str = "Thu nhập" if t["type"] == "INCOME" else "Chi tiêu"
                    writer.writerow([t["id"], t["date"], t["title"], t_str, t["category"], f"{t['amount']:,.0f}", t["note"]])
            messagebox.showinfo("Thành công", f"Đã xuất dữ liệu ra file:\n{file_path}")
        except Exception as e:
            messagebox.showerror("Lỗi", f"Không thể xuất file CSV:\n{e}")


if __name__ == "__main__":
    app = BudgetBuddyPreviewApp()
    app.mainloop()
