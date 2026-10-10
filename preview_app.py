"""
================================================================================
BUDGETBUDDY - MÀN HÌNH GIẢ LẬP GIAO DIỆN PYTHON TKINTER HOÀN CHỈNH
Môn học: Lập trình Python nâng cao (Nhóm 14)
File độc lập chạy trực tiếp không cần cài SQL Server: python preview_app.py
================================================================================
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from datetime import datetime
import csv
import math

# Thử import matplotlib, nếu máy chưa cài thì sẽ tự động vẽ bằng Tkinter Canvas
try:
    import matplotlib
    matplotlib.use("TkAgg")
    from matplotlib.figure import Figure
    from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
    HAS_MATPLOTLIB = True
except ImportError:
    HAS_MATPLOTLIB = False


class BudgetBuddyPreviewApp(tk.Tk):
    def __init__(self):
        super().__init__()

        self.title("BudgetBuddy v1.0.0 — Quản lý Chi tiêu Cá nhân (Nhóm 14)")
        self.geometry("1100x700")
        self.minsize(980, 620)

        # Dữ liệu giả lập ban đầu
        self.transactions = [
            {"id": 1, "date": "2026-10-01", "title": "Lương làm thêm part-time", "type": "INCOME", "category": "Lương / Thưởng", "amount": 8000000, "note": "Lương tháng 9 nhận đầu tháng 10"},
            {"id": 2, "date": "2026-10-02", "title": "Tiền trọ tháng 10", "type": "EXPENSE", "category": "Tiền trọ / Điện nước", "amount": 3000000, "note": "Đã chuyển khoản cho chủ nhà"},
            {"id": 3, "date": "2026-10-03", "title": "Trợ cấp sinh hoạt gia đình", "type": "INCOME", "category": "Trợ cấp", "amount": 7500000, "note": "Tiền bố mẹ gửi sinh hoạt"},
            {"id": 4, "date": "2026-10-05", "title": "Mua giáo trình Python nâng cao", "type": "EXPENSE", "category": "Học tập & Sách vở", "amount": 1500000, "note": "Sách chuyên ngành & tài liệu"},
            {"id": 5, "date": "2026-10-08", "title": "Bảo dưỡng xe máy & xăng", "type": "EXPENSE", "category": "Đi lại / Xăng xe", "amount": 1200000, "note": "Thay nhớt & đổ xăng tuần"},
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
        self.chart_canvas = None

        # Thiết lập giao diện
        self._setup_styles()
        self._build_header_cards()
        self._build_main_notebook()

        # Nạp dữ liệu ban đầu
        self.update_stats()
        self.render_treeview()
        self.draw_chart()
        self.render_budgets()

    def _setup_styles(self):
        """Định dạng Style cho các widget TTK hiện đại"""
        self.style = ttk.Style(self)
        self.style.theme_use("clam")

        self.configure(bg="#f4f6f9")

        # Cấu hình Tab Notebook
        self.style.configure("TNotebook", background="#f4f6f9", borderwidth=0)
        self.style.configure("TNotebook.Tab", font=("Segoe UI", 10, "bold"), padding=[16, 8], background="#e2e8f0")
        self.style.map("TNotebook.Tab",
                       background=[("selected", "#ffffff")],
                       foreground=[("selected", "#1e40af")])

        # Cấu hình Treeview
        self.style.configure("Treeview.Heading", font=("Segoe UI", 10, "bold"), background="#e2e8f0", foreground="#1e293b", relief="flat")
        self.style.configure("Treeview", font=("Segoe UI", 9), rowheight=28, background="#ffffff", fieldbackground="#ffffff")
        self.style.map("Treeview", background=[("selected", "#3b82f6")], foreground=[("selected", "#ffffff")])

        # Nút bấm TTK
        self.style.configure("Primary.TButton", font=("Segoe UI", 9, "bold"), padding=6)

    def _build_header_cards(self):
        """Xây dựng 3 Thẻ thống kê KPI trên cùng"""
        top_frame = tk.Frame(self, bg="#ffffff", bd=1, relief="solid", highlightthickness=0)
        top_frame.pack(fill=tk.X, padx=12, pady=(10, 6))

        # Tiêu đề bên trái
        title_box = tk.Frame(top_frame, bg="#ffffff")
        title_box.pack(side=tk.LEFT, padx=16, pady=10)

        lbl_app = tk.Label(title_box, text="💰 BUDGETBUDDY", font=("Segoe UI", 14, "bold"), fg="#1e3a8a", bg="#ffffff")
        lbl_app.pack(anchor=tk.W)
        lbl_sub = tk.Label(title_box, text="Ứng dụng Quản lý Tài chính & Chi tiêu Cá nhân", font=("Segoe UI", 9), fg="#64748b", bg="#ffffff")
        lbl_sub.pack(anchor=tk.W)

        # 3 Thẻ KPI bên phải
        cards_frame = tk.Frame(top_frame, bg="#ffffff")
        cards_frame.pack(side=tk.RIGHT, padx=16, pady=8)

        # Card 1: Thu nhập
        c1 = tk.Frame(cards_frame, bg="#ecfdf5", bd=1, relief="solid", padx=12, pady=6)
        c1.pack(side=tk.LEFT, padx=6)
        tk.Label(c1, text="TỔNG THU NHẬP", font=("Segoe UI", 8, "bold"), fg="#047857", bg="#ecfdf5").pack(anchor=tk.W)
        self.lbl_income = tk.Label(c1, text="+0 đ", font=("Segoe UI", 12, "bold"), fg="#059669", bg="#ecfdf5")
        self.lbl_income.pack(anchor=tk.W)

        # Card 2: Chi tiêu
        c2 = tk.Frame(cards_frame, bg="#fff1f2", bd=1, relief="solid", padx=12, pady=6)
        c2.pack(side=tk.LEFT, padx=6)
        tk.Label(c2, text="TỔNG CHI TIÊU", font=("Segoe UI", 8, "bold"), fg="#be123c", bg="#fff1f2").pack(anchor=tk.W)
        self.lbl_expense = tk.Label(c2, text="-0 đ", font=("Segoe UI", 12, "bold"), fg="#e11d48", bg="#fff1f2")
        self.lbl_expense.pack(anchor=tk.W)

        # Card 3: Số dư
        c3 = tk.Frame(cards_frame, bg="#eff6ff", bd=1, relief="solid", padx=12, pady=6)
        c3.pack(side=tk.LEFT, padx=6)
        tk.Label(c3, text="SỐ DƯ KHẢ DỤNG", font=("Segoe UI", 8, "bold"), fg="#1d4ed8", bg="#eff6ff").pack(anchor=tk.W)
        self.lbl_balance = tk.Label(c3, text="0 đ", font=("Segoe UI", 12, "bold"), fg="#2563eb", bg="#eff6ff")
        self.lbl_balance.pack(anchor=tk.W)

    def _build_main_notebook(self):
        """Khung Tab chính"""
        self.notebook = ttk.Notebook(self)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=12, pady=6)

        # 4 Tabs
        self.tab_trans = tk.Frame(self.notebook, bg="#f8fafc")
        self.tab_chart = tk.Frame(self.notebook, bg="#f8fafc")
        self.tab_budget = tk.Frame(self.notebook, bg="#f8fafc")
        self.tab_export = tk.Frame(self.notebook, bg="#f8fafc")

        self.notebook.add(self.tab_trans, text=" 📝 Quản lý Thu / Chi ")
        self.notebook.add(self.tab_chart, text=" 📊 Biểu đồ & Phân tích ")
        self.notebook.add(self.tab_budget, text=" 🎯 Hạn mức Ngân sách ")
        self.notebook.add(self.tab_export, text=" 📄 Xuất Báo cáo ")

        self._build_tab_transactions()
        self._build_tab_charts()
        self._build_tab_budgets()
        self._build_tab_export()

    # ================= TAB 1: GIAO DỊCH =================
    def _build_tab_transactions(self):
        # Chia 2 cột: Cột trái (Form nhập - 350px), Cột phải (Bảng dữ liệu Treeview)
        left_box = tk.LabelFrame(self.tab_trans, text=" Form Nhập Liệu Giao Dịch ", font=("Segoe UI", 10, "bold"),
                                 bg="#ffffff", fg="#1e293b", padx=12, pady=10)
        left_box.pack(side=tk.LEFT, fill=tk.Y, padx=(10, 5), pady=10)

        # 1. Tiêu đề
        tk.Label(left_box, text="Tiêu đề giao dịch: *", font=("Segoe UI", 9), bg="#ffffff").pack(anchor=tk.W, pady=(2, 1))
        self.ent_title = ttk.Entry(left_box, width=32, font=("Segoe UI", 9))
        self.ent_title.pack(fill=tk.X, pady=(0, 6))

        # 2. Số tiền
        tk.Label(left_box, text="Số tiền (VNĐ): *", font=("Segoe UI", 9), bg="#ffffff").pack(anchor=tk.W, pady=(2, 1))
        self.ent_amount = ttk.Entry(left_box, width=32, font=("Segoe UI", 9))
        self.ent_amount.pack(fill=tk.X, pady=(0, 6))

        # 3. Loại giao dịch (Radio)
        tk.Label(left_box, text="Loại giao dịch:", font=("Segoe UI", 9), bg="#ffffff").pack(anchor=tk.W, pady=(2, 1))
        self.var_type = tk.StringVar(value="EXPENSE")
        type_f = tk.Frame(left_box, bg="#ffffff")
        type_f.pack(fill=tk.X, pady=(0, 6))
        tk.Radiobutton(type_f, text="🔴 Chi tiêu (-)", variable=self.var_type, value="EXPENSE",
                       bg="#ffffff", font=("Segoe UI", 9), command=self._on_type_toggle).pack(side=tk.LEFT, padx=(0, 10))
        tk.Radiobutton(type_f, text="🟢 Thu nhập (+)", variable=self.var_type, value="INCOME",
                       bg="#ffffff", font=("Segoe UI", 9), command=self._on_type_toggle).pack(side=tk.LEFT)

        # 4. Danh mục (Combobox)
        tk.Label(left_box, text="Danh mục: *", font=("Segoe UI", 9), bg="#ffffff").pack(anchor=tk.W, pady=(2, 1))
        self.cbo_cat = ttk.Combobox(left_box, state="readonly", font=("Segoe UI", 9))
        self.cbo_cat.pack(fill=tk.X, pady=(0, 6))
        self._on_type_toggle()

        # 5. Ngày giao dịch
        tk.Label(left_box, text="Ngày giao dịch (YYYY-MM-DD):", font=("Segoe UI", 9), bg="#ffffff").pack(anchor=tk.W, pady=(2, 1))
        self.ent_date = ttk.Entry(left_box, width=32, font=("Segoe UI", 9))
        self.ent_date.insert(0, datetime.now().strftime("%Y-%m-%d"))
        self.ent_date.pack(fill=tk.X, pady=(0, 6))

        # 6. Ghi chú
        tk.Label(left_box, text="Ghi chú thêm:", font=("Segoe UI", 9), bg="#ffffff").pack(anchor=tk.W, pady=(2, 1))
        self.ent_note = ttk.Entry(left_box, width=32, font=("Segoe UI", 9))
        self.ent_note.pack(fill=tk.X, pady=(0, 10))

        # Buttons CRUD
        btn_box = tk.Frame(left_box, bg="#ffffff")
        btn_box.pack(fill=tk.X, pady=4)

        btn_add = tk.Button(btn_box, text="➕ Thêm mới", bg="#059669", fg="#ffffff", font=("Segoe UI", 9, "bold"),
                            relief="flat", cursor="hand2", padx=10, pady=5, command=self.add_transaction)
        btn_add.pack(fill=tk.X, pady=2)

        btn_edit = tk.Button(btn_box, text="✏️ Cập nhật", bg="#2563eb", fg="#ffffff", font=("Segoe UI", 9, "bold"),
                             relief="flat", cursor="hand2", padx=10, pady=5, command=self.update_transaction)
        btn_edit.pack(fill=tk.X, pady=2)

        btn_del = tk.Button(btn_box, text="🗑️ Xóa dòng", bg="#e11d48", fg="#ffffff", font=("Segoe UI", 9, "bold"),
                            relief="flat", cursor="hand2", padx=10, pady=5, command=self.delete_transaction)
        btn_del.pack(fill=tk.X, pady=2)

        btn_clear = tk.Button(btn_box, text="🔄 Làm mới form", bg="#64748b", fg="#ffffff", font=("Segoe UI", 9),
                              relief="flat", cursor="hand2", padx=10, pady=4, command=self.clear_form)
        btn_clear.pack(fill=tk.X, pady=2)

        # Cột Phải: Bảng Danh Sách & Tìm kiếm
        right_box = tk.Frame(self.tab_trans, bg="#f8fafc")
        right_box.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=(5, 10), pady=10)

        # Bộ lọc phía trên
        filter_bar = tk.Frame(right_box, bg="#ffffff", bd=1, relief="solid", padx=8, pady=6)
        filter_bar.pack(fill=tk.X, pady=(0, 6))

        tk.Label(filter_bar, text="🔍 Tìm:", bg="#ffffff", font=("Segoe UI", 9, "bold")).pack(side=tk.LEFT, padx=(0, 4))
        self.ent_search = ttk.Entry(filter_bar, width=16, font=("Segoe UI", 9))
        self.ent_search.pack(side=tk.LEFT, padx=(0, 8))
        self.ent_search.bind("<KeyRelease>", lambda e: self.render_treeview())

        tk.Label(filter_bar, text="Loại:", bg="#ffffff", font=("Segoe UI", 9)).pack(side=tk.LEFT, padx=(4, 2))
        self.cbo_filter_type = ttk.Combobox(filter_bar, values=["Tất cả", "Chi tiêu", "Thu nhập"], width=8, state="readonly")
        self.cbo_filter_type.set("Tất cả")
        self.cbo_filter_type.pack(side=tk.LEFT, padx=(0, 8))
        self.cbo_filter_type.bind("<<ComboboxSelected>>", lambda e: self.render_treeview())

        btn_filter_reset = tk.Button(filter_bar, text="✖ Đặt lại", bg="#94a3b8", fg="white", font=("Segoe UI", 8),
                                     relief="flat", cursor="hand2", command=self.reset_filter)
        btn_filter_reset.pack(side=tk.LEFT)

        # Bảng Treeview
        tree_container = tk.Frame(right_box, bg="#ffffff", bd=1, relief="solid")
        tree_container.pack(fill=tk.BOTH, expand=True)

        cols = ("id", "date", "title", "cat", "amount", "note")
        self.tree = ttk.Treeview(tree_container, columns=cols, show="headings", selectmode="browse")

        self.tree.heading("id", text="#", anchor=tk.CENTER)
        self.tree.heading("date", text="Ngày GD", anchor=tk.CENTER)
        self.tree.heading("title", text="Tiêu đề giao dịch", anchor=tk.W)
        self.tree.heading("cat", text="Danh mục", anchor=tk.W)
        self.tree.heading("amount", text="Số tiền (đ)", anchor=tk.E)
        self.tree.heading("note", text="Ghi chú", anchor=tk.W)

        self.tree.column("id", width=35, anchor=tk.CENTER)
        self.tree.column("date", width=85, anchor=tk.CENTER)
        self.tree.column("title", width=190, anchor=tk.W)
        self.tree.column("cat", width=140, anchor=tk.W)
        self.tree.column("amount", width=120, anchor=tk.E)
        self.tree.column("note", width=160, anchor=tk.W)

        sb = ttk.Scrollbar(tree_container, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscrollcommand=sb.set)

        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        sb.pack(side=tk.RIGHT, fill=tk.Y)

        self.tree.tag_configure("INCOME", foreground="#059669")
        self.tree.tag_configure("EXPENSE", foreground="#e11d48")

        self.tree.bind("<<TreeviewSelect>>", self._on_tree_select)

    def _on_type_toggle(self):
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

        for t in self.transactions:
            match_kw = kw in t["title"].lower() or kw in t["note"].lower() or kw in t["category"].lower()
            match_type = True
            if f_type == "Chi tiêu" and t["type"] != "EXPENSE": match_type = False
            if f_type == "Thu nhập" and t["type"] != "INCOME": match_type = False

            if match_kw and match_type:
                prefix = "+" if t["type"] == "INCOME" else "-"
                amt_str = f"{prefix}{t['amount']:,.0f}"
                self.tree.insert("", tk.END, values=(t["id"], t["date"], t["title"], t["category"], amt_str, t["note"]), tags=(t["type"],))

    def _on_tree_select(self, event):
        sel = self.tree.selection()
        if not sel: return
        vals = self.tree.item(sel[0], "values")
        if not vals: return

        self.selected_trans_id = int(vals[0])
        self.ent_title.delete(0, tk.END); self.ent_title.insert(0, vals[2])
        self.ent_date.delete(0, tk.END); self.ent_date.insert(0, vals[1])
        self.ent_note.delete(0, tk.END); self.ent_note.insert(0, vals[5])

        # Tìm item gốc
        item = next((x for x in self.transactions if x["id"] == self.selected_trans_id), None)
        if item:
            self.var_type.set(item["type"])
            self._on_type_toggle()
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

        messagebox.showinfo("Thành công", f"Đã thêm giao dịch: {title}")
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
        if messagebox.askyesno("Xác nhận xóa", "Bạn có chắc chắn muốn xóa giao dịch này không?"):
            self.transactions = [t for t in self.transactions if t["id"] != self.selected_trans_id]
            self.clear_form()
            self.update_stats()
            self.render_treeview()
            self.draw_chart()
            self.render_budgets()

    # ================= TAB 2: BIỂU ĐỒ =================
    def _build_tab_charts(self):
        header_f = tk.Frame(self.tab_chart, bg="#f8fafc")
        header_f.pack(fill=tk.X, padx=16, pady=(12, 6))

        tk.Label(header_f, text="📊 Phân tích Tỷ trọng Chi tiêu Theo Danh mục", font=("Segoe UI", 12, "bold"),
                 bg="#f8fafc", fg="#1e293b").pack(side=tk.LEFT)

        btn_redraw = tk.Button(header_f, text="🔄 Vẽ lại biểu đồ", bg="#4f46e5", fg="white", font=("Segoe UI", 9, "bold"),
                               relief="flat", cursor="hand2", padx=10, pady=4, command=self.draw_chart)
        btn_redraw.pack(side=tk.RIGHT)

        self.chart_area = tk.Frame(self.tab_chart, bg="#ffffff", bd=1, relief="solid")
        self.chart_area.pack(fill=tk.BOTH, expand=True, padx=16, pady=10)

    def draw_chart(self):
        for widget in self.chart_area.winfo_children():
            widget.destroy()

        # Tính tổng chi theo từng danh mục
        cat_sums = {}
        for t in self.transactions:
            if t["type"] == "EXPENSE":
                c = t["category"]
                cat_sums[c] = cat_sums.get(c, 0) + t["amount"]

        if not cat_sums:
            lbl = tk.Label(self.chart_area, text="Chưa có dữ liệu chi tiêu để vẽ biểu đồ.", font=("Segoe UI", 11), bg="#ffffff", fg="#64748b")
            lbl.pack(expand=True)
            return

        labels = list(cat_sums.keys())
        values = list(cat_sums.values())

        if HAS_MATPLOTLIB:
            # Dùng Matplotlib
            fig = Figure(figsize=(7, 4.5), dpi=95)
            ax = fig.add_subplot(111)
            colors = ["#f43f5e", "#f59e0b", "#3b82f6", "#10b981", "#8b5cf6", "#ec4899"]
            wedges, texts, autotexts = ax.pie(values, labels=labels, autopct="%1.1f%%", startangle=140,
                                              colors=colors[:len(labels)], wedgeprops=dict(width=0.45, edgecolor="white", linewidth=2))
            for at in autotexts:
                at.set_fontsize(9)
                at.set_weight("bold")
            ax.set_title("Cơ cấu Chi tiêu Tháng 10/2026", fontsize=11, fontweight="bold", pad=12)

            canvas = FigureCanvasTkAgg(fig, master=self.chart_area)
            canvas.draw()
            canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        else:
            # Fallback Tkinter Canvas (chạy được trên máy chưa cài matplotlib)
            cv = tk.Canvas(self.chart_area, bg="#ffffff", highlightthickness=0)
            cv.pack(fill=tk.BOTH, expand=True)
            total = sum(values)
            start_ang = 0
            cx, cy, r = 260, 180, 120
            colors = ["#f43f5e", "#f59e0b", "#3b82f6", "#10b981", "#8b5cf6", "#ec4899"]

            for i, (lab, val) in enumerate(zip(labels, values)):
                extent = (val / total) * 360
                color = colors[i % len(colors)]
                cv.create_arc(cx - r, cy - r, cx + r, cy + r, start=start_ang, extent=extent, fill=color, outline="white", width=2)
                # Chú thích bên phải
                ly = 90 + i * 35
                cv.create_rectangle(450, ly, 465, ly + 15, fill=color, outline="")
                pct = (val / total) * 100
                cv.create_text(475, ly + 8, text=f"{lab}: {val:,.0f} đ ({pct:.1f}%)", anchor=tk.W, font=("Segoe UI", 9, "bold"))
                start_ang += extent

            # Lỗ Donut
            r_in = 60
            cv.create_oval(cx - r_in, cy - r_in, cx + r_in, cy + r_in, fill="#ffffff", outline="")
            cv.create_text(cx, cy, text=f"Tổng chi\n{total:,.0f} đ", justify=tk.CENTER, font=("Segoe UI", 9, "bold"), fill="#be123c")

    # ================= TAB 3: HẠN MỨC NGÂN SÁCH =================
    def _build_tab_budgets(self):
        pad_f = tk.Frame(self.tab_budget, bg="#f8fafc")
        pad_f.pack(fill=tk.BOTH, expand=True, padx=20, pady=16)

        tk.Label(pad_f, text="🎯 Theo dõi Tiến độ & Cảnh báo Hạn mức Chi tiêu", font=("Segoe UI", 12, "bold"),
                 bg="#f8fafc", fg="#1e293b").pack(anchor=tk.W, pady=(0, 12))

        self.budget_container = tk.Frame(pad_f, bg="#ffffff", bd=1, relief="solid", padx=16, pady=14)
        self.budget_container.pack(fill=tk.BOTH, expand=True)

    def render_budgets(self):
        for widget in self.budget_container.winfo_children():
            widget.destroy()

        # Tính tiền đã chi theo danh mục
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

            row_f = tk.Frame(self.budget_container, bg="#ffffff")
            row_f.pack(fill=tk.X, pady=8)

            # Tiêu đề hàng & trạng thái
            if pct < 80:
                status_txt = f"✅ An toàn ({pct:.1f}%)"
                status_color = "#059669"
            elif pct <= 100:
                status_txt = f"⚠️ Cảnh báo: Sắp hết! ({pct:.1f}%)"
                status_color = "#d97706"
            else:
                status_txt = f"🚨 VƯỢT HẠN MỨC! ({pct:.1f}%)"
                status_color = "#dc2626"

            header_row = tk.Frame(row_f, bg="#ffffff")
            header_row.pack(fill=tk.X)
            tk.Label(header_row, text=f"{cat} (Đã tiêu: {spent:,.0f} đ / Hạn mức: {limit:,.0f} đ)",
                     font=("Segoe UI", 9, "bold"), bg="#ffffff", fg="#334155").pack(side=tk.LEFT)
            tk.Label(header_row, text=status_txt, font=("Segoe UI", 9, "bold"), bg="#ffffff", fg=status_color).pack(side=tk.RIGHT)

            # Thanh tiến độ
            pb = ttk.Progressbar(row_f, maximum=100, value=min(pct, 100), length=400)
            pb.pack(fill=tk.X, pady=(4, 0))

    # ================= TAB 4: XUẤT BÁO CÁO =================
    def _build_tab_export(self):
        wrap = tk.Frame(self.tab_export, bg="#f8fafc")
        wrap.pack(fill=tk.BOTH, expand=True, padx=40, pady=30)

        card = tk.Frame(wrap, bg="#ffffff", bd=1, relief="solid", padx=24, pady=24)
        card.pack(fill=tk.X)

        tk.Label(card, text="📄 Xuất Dữ liệu Giao dịch Tài chính", font=("Segoe UI", 12, "bold"),
                 bg="#ffffff", fg="#1e293b").pack(anchor=tk.W, pady=(0, 6))
        tk.Label(card, text="Bạn có thể xuất toàn bộ dữ liệu sao kê ra file Excel hoặc CSV tiếng Việt để đính kèm vào báo cáo thực nghiệm.",
                 font=("Segoe UI", 9), bg="#ffffff", fg="#64748b").pack(anchor=tk.W, pady=(0, 16))

        btn_row = tk.Frame(card, bg="#ffffff")
        btn_row.pack(anchor=tk.W)

        btn_csv = tk.Button(btn_row, text="📄 Xuất file CSV (Excel tiếng Việt)", bg="#0284c7", fg="white",
                            font=("Segoe UI", 9, "bold"), relief="flat", cursor="hand2", padx=16, pady=8, command=self.export_csv)
        btn_csv.pack(side=tk.LEFT, padx=(0, 10))

        btn_sample = tk.Button(btn_row, text="💾 Lưu bản sao CSDL dự phòng", bg="#059669", fg="white",
                               font=("Segoe UI", 9, "bold"), relief="flat", cursor="hand2", padx=16, pady=8,
                               command=lambda: messagebox.showinfo("Thông báo", "Đã tạo bản sao lưu dữ liệu thành công!"))
        btn_sample.pack(side=tk.LEFT)

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
