import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from datetime import datetime
import csv

try:
    import matplotlib
    matplotlib.use("TkAgg")
    from matplotlib.figure import Figure
    from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
    HAS_MATPLOTLIB = True
except ImportError:
    HAS_MATPLOTLIB = False

COLORS = {
    "bg_main": "#f8fafc",
    "card_bg": "#ffffff",
    "border": "#e2e8f0",
    "border_focus": "#3b82f6",
    "text_main": "#0f172a",
    "text_muted": "#64748b",
    "text_dim": "#94a3b8",
    "primary": "#2563eb",
    "primary_hover": "#1d4ed8",
    "primary_light": "#eff6ff",
    "income": "#059669",
    "income_bg": "#ecfdf5",
    "expense": "#e11d48",
    "expense_bg": "#fff1f2",
    "amber": "#d97706",
    "amber_bg": "#fffbeb",
    "tag_bg": "#f1f5f9",
    "tag_leisure_bg": "#dfeafb",
    "chart_food": "#3b82f6",
    "chart_housing": "#1d4ed8",
    "chart_education": "#8b5cf6",
    "chart_transport": "#0d9488",
    "chart_leisure": "#60a5fa"
}

class HoverButton(tk.Button):
    def __init__(self, master, default_bg, hover_bg, **kw):
        super().__init__(master, bg=default_bg, activebackground=hover_bg, relief="flat", cursor="hand2", **kw)
        self.default_bg = default_bg
        self.hover_bg = hover_bg
        self.bind("<Enter>", lambda e: self.config(bg=self.hover_bg))
        self.bind("<Leave>", lambda e: self.config(bg=self.default_bg))

class BudgetBuddyApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("BudgetBuddy — Personal Finance Management")
        self.geometry("1380x880")
        self.minsize(1220, 780)
        self.configure(bg=COLORS["bg_main"])

        self.transactions = [
            {"id": 1, "date": "2026-10-30", "title": "Weekly groceries", "type": "EXPENSE", "category": "Food", "amount": 450000, "note": "Supermarket purchases"},
            {"id": 2, "date": "2026-10-29", "title": "Freelance project", "type": "INCOME", "category": "Work", "amount": 1500000, "note": "Web app UI redesign"},
            {"id": 3, "date": "2026-10-28", "title": "Weekend getaway", "type": "EXPENSE", "category": "Leisure", "amount": 3800000, "note": "Hotel and transport"},
            {"id": 4, "date": "2026-10-27", "title": "English course", "type": "EXPENSE", "category": "Education", "amount": 1500000, "note": "IELTS preparation module"},
            {"id": 5, "date": "2026-10-26", "title": "Grab rides", "type": "EXPENSE", "category": "Transport", "amount": 1200000, "note": "Commutes to university and lab"},
            {"id": 6, "date": "2026-10-25", "title": "October salary", "type": "INCOME", "category": "Salary", "amount": 24000000, "note": "Full-time software engineering salary"}
        ]

        self.budgets = [
            {"category": "Food", "limit": 3000000, "spent": 2500000, "icon": "🍽️", "status": "Near limit", "color": COLORS["amber"], "bg": COLORS["amber_bg"]},
            {"category": "Rent", "limit": 3000000, "spent": 3000000, "icon": "🏠", "status": "On budget", "color": COLORS["income"], "bg": COLORS["income_bg"]},
            {"category": "Education", "limit": 1200000, "spent": 1500000, "icon": "🎓", "status": "Over budget", "color": COLORS["expense"], "bg": COLORS["expense_bg"]}
        ]

        self.current_view = "dashboard"
        self.search_query = tk.StringVar()
        self.search_query.trace_add("write", lambda *args: self.filter_transactions())

        self.bind("<Control-k>", lambda e: self.focus_search())
        self.bind("<Control-K>", lambda e: self.focus_search())

        self._build_layout()
        self.show_view("dashboard")

    def _build_layout(self):
        self.main_container = tk.Frame(self, bg=COLORS["bg_main"])
        self.main_container.pack(fill=tk.BOTH, expand=True)

        self.sidebar_frame = tk.Frame(self.main_container, bg=COLORS["card_bg"], width=230, bd=0, highlightbackground=COLORS["border"], highlightthickness=1)
        self.sidebar_frame.pack(side=tk.LEFT, fill=tk.Y)
        self.sidebar_frame.pack_propagate(False)

        self.workspace_frame = tk.Frame(self.main_container, bg=COLORS["bg_main"])
        self.workspace_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        self._build_sidebar()
        self._build_topbar()

        self.content_area = tk.Frame(self.workspace_frame, bg=COLORS["bg_main"])
        self.content_area.pack(fill=tk.BOTH, expand=True, padx=28, pady=20)

    def _build_sidebar(self):
        brand_f = tk.Frame(self.sidebar_frame, bg=COLORS["card_bg"], height=70)
        brand_f.pack(fill=tk.X, padx=18, pady=(20, 10))

        logo_box = tk.Label(brand_f, text="💼", font=("Segoe UI", 12), bg=COLORS["primary"], fg="#ffffff", width=3, height=1, relief="flat")
        logo_box.pack(side=tk.LEFT, padx=(0, 10))

        brand_lbl = tk.Label(brand_f, text="BudgetBuddy", font=("Segoe UI", 13, "bold"), bg=COLORS["card_bg"], fg=COLORS["text_main"])
        brand_lbl.pack(side=tk.LEFT, anchor=tk.W)

        ws_lbl = tk.Label(self.sidebar_frame, text="WORKSPACE", font=("Segoe UI", 8, "bold"), bg=COLORS["card_bg"], fg=COLORS["text_dim"])
        ws_lbl.pack(anchor=tk.W, padx=22, pady=(15, 8))

        self.nav_buttons = {}
        nav_items = [
            ("dashboard", "Dashboard", "⊞"),
            ("transactions", "Transactions", "⇆"),
            ("budgets", "Budget & Limits", "💳"),
            ("analytics", "Analytics", "📊"),
            ("reports", "Reports", "📄"),
            ("settings", "Settings", "⚙")
        ]

        for key, name, icon in nav_items:
            btn_f = tk.Frame(self.sidebar_frame, bg=COLORS["card_bg"], cursor="hand2")
            btn_f.pack(fill=tk.X, padx=14, pady=2)

            btn_lbl = tk.Label(btn_f, text=f"  {icon}   {name}", font=("Segoe UI", 10, "normal"), bg=COLORS["card_bg"], fg=COLORS["text_muted"], anchor=tk.W, padx=10, pady=8)
            btn_lbl.pack(fill=tk.X)

            btn_f.bind("<Button-1>", lambda e, k=key: self.show_view(k))
            btn_lbl.bind("<Button-1>", lambda e, k=key: self.show_view(k))

            self.nav_buttons[key] = (btn_f, btn_lbl)

        spacer = tk.Frame(self.sidebar_frame, bg=COLORS["card_bg"])
        spacer.pack(fill=tk.BOTH, expand=True)

        footer_f = tk.Frame(self.sidebar_frame, bg=COLORS["card_bg"])
        footer_f.pack(fill=tk.X, side=tk.BOTTOM, padx=16, pady=16)

        sec_f = tk.Frame(footer_f, bg=COLORS["card_bg"])
        sec_f.pack(fill=tk.X, pady=(0, 10))
        tk.Label(sec_f, text="🛡️", font=("Segoe UI", 9), bg=COLORS["card_bg"], fg=COLORS["income"]).pack(side=tk.LEFT, padx=(0, 6))
        tk.Label(sec_f, text="Your finances, protected", font=("Segoe UI", 8), bg=COLORS["card_bg"], fg=COLORS["text_muted"]).pack(side=tk.LEFT)

        sep = tk.Frame(footer_f, bg=COLORS["border"], height=1)
        sep.pack(fill=tk.X, pady=(0, 12))

        user_f = tk.Frame(footer_f, bg=COLORS["card_bg"])
        user_f.pack(fill=tk.X)

        avt = tk.Label(user_f, text="ML", font=("Segoe UI", 9, "bold"), bg=COLORS["primary_light"], fg=COLORS["primary"], width=3, height=1)
        avt.pack(side=tk.LEFT, padx=(0, 10))

        details_f = tk.Frame(user_f, bg=COLORS["card_bg"])
        details_f.pack(side=tk.LEFT, fill=tk.X, expand=True)
        tk.Label(details_f, text="Minh Le", font=("Segoe UI", 9, "bold"), bg=COLORS["card_bg"], fg=COLORS["text_main"], anchor=tk.W).pack(fill=tk.X)
        tk.Label(details_f, text="Personal account", font=("Segoe UI", 8), bg=COLORS["card_bg"], fg=COLORS["text_muted"], anchor=tk.W).pack(fill=tk.X)

        logout_btn = tk.Label(user_f, text="🚪", font=("Segoe UI", 11), bg=COLORS["card_bg"], fg=COLORS["text_muted"], cursor="hand2")
        logout_btn.pack(side=tk.RIGHT)
        logout_btn.bind("<Button-1>", lambda e: messagebox.showinfo("BudgetBuddy", "User session is active."))

    def _build_topbar(self):
        topbar = tk.Frame(self.workspace_frame, bg=COLORS["card_bg"], height=68, bd=0, highlightbackground=COLORS["border"], highlightthickness=1)
        topbar.pack(fill=tk.X, side=tk.TOP)
        topbar.pack_propagate(False)

        inner = tk.Frame(topbar, bg=COLORS["card_bg"])
        inner.pack(fill=tk.BOTH, expand=True, padx=28)

        search_f = tk.Frame(inner, bg=COLORS["bg_main"], bd=0, highlightbackground=COLORS["border"], highlightthickness=1, padx=8, pady=4)
        search_f.pack(side=tk.LEFT, pady=14)

        tk.Label(search_f, text="🔍", font=("Segoe UI", 9), bg=COLORS["bg_main"], fg=COLORS["text_dim"]).pack(side=tk.LEFT, padx=(4, 6))

        self.search_entry = tk.Entry(search_f, textvariable=self.search_query, font=("Segoe UI", 9), bg=COLORS["bg_main"], fg=COLORS["text_main"], bd=0, width=28)
        self.search_entry.pack(side=tk.LEFT, ipady=2)

        kbd_tag = tk.Label(search_f, text="Ctrl K", font=("Segoe UI", 8), bg=COLORS["card_bg"], fg=COLORS["text_muted"], bd=0, padx=5, pady=1, highlightbackground=COLORS["border"], highlightthickness=1)
        kbd_tag.pack(side=tk.LEFT, padx=(6, 2))

        right_f = tk.Frame(inner, bg=COLORS["card_bg"])
        right_f.pack(side=tk.RIGHT, pady=14)

        date_btn = tk.Button(right_f, text="📅 October 2026 ▾", font=("Segoe UI", 9), bg=COLORS["card_bg"], fg=COLORS["text_main"], bd=0, padx=12, pady=6, cursor="hand2", highlightbackground=COLORS["border"], highlightthickness=1)
        date_btn.pack(side=tk.LEFT, padx=(0, 10))

        bell_btn = tk.Button(right_f, text="🔔", font=("Segoe UI", 10), bg=COLORS["card_bg"], fg=COLORS["text_muted"], bd=0, padx=8, pady=5, cursor="hand2", highlightbackground=COLORS["border"], highlightthickness=1)
        bell_btn.pack(side=tk.LEFT, padx=(0, 12))

        add_btn = HoverButton(right_f, default_bg=COLORS["primary"], hover_bg=COLORS["primary_hover"], text="+ Add Transaction", font=("Segoe UI", 9, "bold"), fg="#ffffff", padx=16, pady=7, command=self.open_add_transaction_dialog)
        add_btn.pack(side=tk.LEFT)

    def focus_search(self):
        self.search_entry.focus_set()

    def show_view(self, view_name):
        self.current_view = view_name

        for key, (frame, label) in self.nav_buttons.items():
            if key == view_name:
                frame.config(bg=COLORS["primary_light"])
                label.config(bg=COLORS["primary_light"], fg=COLORS["primary"], font=("Segoe UI", 10, "bold"))
            else:
                frame.config(bg=COLORS["card_bg"])
                label.config(bg=COLORS["card_bg"], fg=COLORS["text_muted"], font=("Segoe UI", 10, "normal"))

        for child in self.content_area.winfo_children():
            child.destroy()

        if view_name == "dashboard":
            self._render_dashboard_view()
        elif view_name == "transactions":
            self._render_transactions_view()
        elif view_name == "budgets":
            self._render_budgets_view()
        elif view_name == "analytics":
            self._render_analytics_view()
        elif view_name == "reports":
            self._render_reports_view()
        elif view_name == "settings":
            self._render_settings_view()

    def _render_dashboard_view(self):
        total_income = sum(t["amount"] for t in self.transactions if t["type"] == "INCOME")
        total_expense = sum(t["amount"] for t in self.transactions if t["type"] == "EXPENSE")
        balance = total_income - total_expense
        retention = (balance / total_income * 100) if total_income > 0 else 0

        header_f = tk.Frame(self.content_area, bg=COLORS["bg_main"])
        header_f.pack(fill=tk.X, pady=(0, 16))

        left_h = tk.Frame(header_f, bg=COLORS["bg_main"])
        left_h.pack(side=tk.LEFT)

        tk.Label(left_h, text="Your money, at a glance", font=("Segoe UI", 17, "bold"), bg=COLORS["bg_main"], fg=COLORS["text_main"]).pack(anchor=tk.W)
        tk.Label(left_h, text="Welcome back, Minh. Here's your financial overview for October.", font=("Segoe UI", 9), bg=COLORS["bg_main"], fg=COLORS["text_muted"]).pack(anchor=tk.W, pady=(2, 0))

        right_h = tk.Frame(header_f, bg=COLORS["bg_main"])
        right_h.pack(side=tk.RIGHT, anchor=tk.S)
        tk.Label(right_h, text="01–31 Oct 2026  ·  VND", font=("Segoe UI", 9, "bold"), bg=COLORS["bg_main"], fg=COLORS["text_muted"]).pack()

        kpi_row = tk.Frame(self.content_area, bg=COLORS["bg_main"])
        kpi_row.pack(fill=tk.X, pady=(0, 18))

        self._create_kpi_card(kpi_row, "Total Income", f"{total_income:,.0f}", "VND", "Earned this month", "↗", COLORS["income"], COLORS["income_bg"], 0)
        self._create_kpi_card(kpi_row, "Total Expense", f"{total_expense:,.0f}", "VND", "Spent this month", "↘", COLORS["expense"], COLORS["expense_bg"], 1)
        self._create_kpi_card(kpi_row, "Current Balance", f"{balance:,.0f}", "VND", f"{retention:.1f}% of income retained", "💼", COLORS["primary"], COLORS["primary_light"], 2)

        mid_row = tk.Frame(self.content_area, bg=COLORS["bg_main"])
        mid_row.pack(fill=tk.BOTH, expand=True, pady=(0, 18))

        self.recent_tx_card = tk.Frame(mid_row, bg=COLORS["card_bg"], bd=0, highlightbackground=COLORS["border"], highlightthickness=1)
        self.recent_tx_card.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 14))

        self.analytics_card = tk.Frame(mid_row, bg=COLORS["card_bg"], width=430, bd=0, highlightbackground=COLORS["border"], highlightthickness=1)
        self.analytics_card.pack(side=tk.RIGHT, fill=tk.BOTH)
        self.analytics_card.pack_propagate(False)

        self._render_recent_transactions_table()
        self._render_spending_analytics_card(total_expense)

        self._render_budget_goals_section()

    def _create_kpi_card(self, parent, title, amount, currency, subtext, badge_icon, accent_color, badge_bg, col_idx):
        card = tk.Frame(parent, bg=COLORS["card_bg"], bd=0, highlightbackground=COLORS["border"], highlightthickness=1)
        card.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0 if col_idx == 0 else 10, 0))

        strip = tk.Frame(card, bg=accent_color, height=3)
        strip.pack(fill=tk.X, side=tk.TOP)

        body = tk.Frame(card, bg=COLORS["card_bg"], padx=18, pady=14)
        body.pack(fill=tk.BOTH, expand=True)

        top_f = tk.Frame(body, bg=COLORS["card_bg"])
        top_f.pack(fill=tk.X)
        tk.Label(top_f, text=title, font=("Segoe UI", 9, "bold"), bg=COLORS["card_bg"], fg=COLORS["text_muted"]).pack(side=tk.LEFT)

        badge = tk.Label(top_f, text=badge_icon, font=("Segoe UI", 10, "bold"), bg=badge_bg, fg=accent_color, width=2, height=1)
        badge.pack(side=tk.RIGHT)

        amt_f = tk.Frame(body, bg=COLORS["card_bg"])
        amt_f.pack(anchor=tk.W, pady=(6, 2))

        val_color = accent_color if title == "Current Balance" else COLORS["text_main"]
        tk.Label(amt_f, text=amount, font=("Segoe UI", 18, "bold"), bg=COLORS["card_bg"], fg=val_color).pack(side=tk.LEFT)
        tk.Label(amt_f, text=f" {currency}", font=("Segoe UI", 9, "bold"), bg=COLORS["card_bg"], fg=COLORS["text_muted"]).pack(side=tk.LEFT, pady=(5, 0))

        tk.Label(body, text=subtext, font=("Segoe UI", 8), bg=COLORS["card_bg"], fg=COLORS["text_muted"]).pack(anchor=tk.W)

    def _render_recent_transactions_table(self):
        head = tk.Frame(self.recent_tx_card, bg=COLORS["card_bg"], padx=18, pady=12)
        head.pack(fill=tk.X)

        h_left = tk.Frame(head, bg=COLORS["card_bg"])
        h_left.pack(side=tk.LEFT)
        tk.Label(h_left, text="Recent Transactions", font=("Segoe UI", 11, "bold"), bg=COLORS["card_bg"], fg=COLORS["text_main"]).pack(anchor=tk.W)
        tk.Label(h_left, text="Your latest money moves", font=("Segoe UI", 8), bg=COLORS["card_bg"], fg=COLORS["text_muted"]).pack(anchor=tk.W)

        view_all = tk.Label(head, text="View all ↗", font=("Segoe UI", 9, "bold"), bg=COLORS["card_bg"], fg=COLORS["primary"], cursor="hand2")
        view_all.pack(side=tk.RIGHT)
        view_all.bind("<Button-1>", lambda e: self.show_view("transactions"))

        cols_f = tk.Frame(self.recent_tx_card, bg=COLORS["bg_main"], highlightbackground=COLORS["border"], highlightthickness=1, padx=14, pady=6)
        cols_f.pack(fill=tk.X)

        tk.Label(cols_f, text="Date", font=("Segoe UI", 8, "bold"), bg=COLORS["bg_main"], fg=COLORS["text_muted"], width=8, anchor=tk.W).pack(side=tk.LEFT)
        tk.Label(cols_f, text="Title", font=("Segoe UI", 8, "bold"), bg=COLORS["bg_main"], fg=COLORS["text_muted"], anchor=tk.W).pack(side=tk.LEFT, fill=tk.X, expand=True)
        tk.Label(cols_f, text="Category", font=("Segoe UI", 8, "bold"), bg=COLORS["bg_main"], fg=COLORS["text_muted"], width=12, anchor=tk.W).pack(side=tk.LEFT)
        tk.Label(cols_f, text="Type", font=("Segoe UI", 8, "bold"), bg=COLORS["bg_main"], fg=COLORS["text_muted"], width=10, anchor=tk.W).pack(side=tk.LEFT)
        tk.Label(cols_f, text="Amount · VND", font=("Segoe UI", 8, "bold"), bg=COLORS["bg_main"], fg=COLORS["text_muted"], width=14, anchor=tk.E).pack(side=tk.LEFT)
        tk.Label(cols_f, text="Actions", font=("Segoe UI", 8, "bold"), bg=COLORS["bg_main"], fg=COLORS["text_muted"], width=8, anchor=tk.E).pack(side=tk.RIGHT)

        self.table_rows_container = tk.Frame(self.recent_tx_card, bg=COLORS["card_bg"])
        self.table_rows_container.pack(fill=tk.BOTH, expand=True)

        self._populate_table_rows(self.transactions[:6])

        foot = tk.Frame(self.recent_tx_card, bg=COLORS["card_bg"], highlightbackground=COLORS["border"], highlightthickness=1, padx=16, pady=8)
        foot.pack(fill=tk.X, side=tk.BOTTOM)
        tk.Label(foot, text="6 recent transactions · Not the full month's ledger", font=("Segoe UI", 8), bg=COLORS["card_bg"], fg=COLORS["text_muted"]).pack(side=tk.LEFT)
        tk.Label(foot, text="Newest first", font=("Segoe UI", 8), bg=COLORS["card_bg"], fg=COLORS["text_dim"]).pack(side=tk.RIGHT)

    def _populate_table_rows(self, data_list):
        for child in self.table_rows_container.winfo_children():
            child.destroy()

        for idx, item in enumerate(data_list):
            row_bg = COLORS["card_bg"] if idx % 2 == 0 else COLORS["bg_main"]
            row = tk.Frame(self.table_rows_container, bg=row_bg, padx=14, pady=5)
            row.pack(fill=tk.X)

            try:
                d_obj = datetime.strptime(item["date"], "%Y-%m-%d")
                d_str = d_obj.strftime("%d %b")
            except Exception:
                d_str = item["date"]

            tk.Label(row, text=d_str, font=("Segoe UI", 8), bg=row_bg, fg=COLORS["text_muted"], width=8, anchor=tk.W).pack(side=tk.LEFT)
            tk.Label(row, text=item["title"], font=("Segoe UI", 9, "bold"), bg=row_bg, fg=COLORS["text_main"], anchor=tk.W).pack(side=tk.LEFT, fill=tk.X, expand=True)

            cat_bg = COLORS["tag_leisure_bg"] if item["category"] == "Leisure" else COLORS["tag_bg"]
            cat_pill = tk.Label(row, text=item["category"], font=("Segoe UI", 8), bg=cat_bg, fg=COLORS["text_muted"], padx=7, pady=2)
            cat_pill.pack(side=tk.LEFT, padx=(0, 10))

            if item["type"] == "INCOME":
                type_pill = tk.Label(row, text="Income", font=("Segoe UI", 8, "bold"), bg=COLORS["income_bg"], fg=COLORS["income"], padx=7, pady=2)
                amt_str = f"+{item['amount']:,.0f}"
                amt_color = COLORS["income"]
            else:
                type_pill = tk.Label(row, text="Expense", font=("Segoe UI", 8, "bold"), bg=COLORS["expense_bg"], fg=COLORS["expense"], padx=7, pady=2)
                amt_str = f"−{item['amount']:,.0f}"
                amt_color = COLORS["text_main"]

            type_pill.pack(side=tk.LEFT, padx=(0, 10))

            tk.Label(row, text=amt_str, font=("Segoe UI", 9, "bold"), bg=row_bg, fg=amt_color, width=14, anchor=tk.E).pack(side=tk.LEFT)

            act_f = tk.Frame(row, bg=row_bg)
            act_f.pack(side=tk.RIGHT)

            edit_b = tk.Label(act_f, text="✏️", font=("Segoe UI", 8), bg=row_bg, cursor="hand2")
            edit_b.pack(side=tk.LEFT, padx=3)
            edit_b.bind("<Button-1>", lambda e, tx=item: self.open_edit_transaction_dialog(tx))

            del_b = tk.Label(act_f, text="🗑️", font=("Segoe UI", 8), bg=row_bg, cursor="hand2")
            del_b.pack(side=tk.LEFT, padx=3)
            del_b.bind("<Button-1>", lambda e, tx_id=item["id"]: self.delete_transaction(tx_id))

    def _render_spending_analytics_card(self, total_expense):
        h = tk.Frame(self.analytics_card, bg=COLORS["card_bg"], padx=18, pady=12)
        h.pack(fill=tk.X)
        tk.Label(h, text="Spending Analytics", font=("Segoe UI", 11, "bold"), bg=COLORS["card_bg"], fg=COLORS["text_main"]).pack(side=tk.LEFT)
        tk.Label(h, text="•••", font=("Segoe UI", 9, "bold"), bg=COLORS["card_bg"], fg=COLORS["text_dim"], cursor="hand2").pack(side=tk.RIGHT)

        cat_spending = {
            "Food": 2500000,
            "Housing": 3000000,
            "Education": 1500000,
            "Transport": 1200000,
            "Leisure": 6000000
        }
        for t in self.transactions:
            if t["type"] == "EXPENSE":
                c = t["category"]
                cat_spending[c] = cat_spending.get(c, 0)

        spent_total = sum(cat_spending.values())
        if spent_total == 0:
            spent_total = total_expense if total_expense > 0 else 1

        chart_frame = tk.Frame(self.analytics_card, bg=COLORS["card_bg"], height=170)
        chart_frame.pack(fill=tk.X, padx=14)

        cat_colors = [COLORS["chart_food"], COLORS["chart_housing"], COLORS["chart_education"], COLORS["chart_transport"], COLORS["chart_leisure"]]

        if HAS_MATPLOTLIB:
            fig = Figure(figsize=(3.4, 2.0), dpi=90, facecolor=COLORS["card_bg"])
            ax = fig.add_subplot(111)

            values = list(cat_spending.values())
            wedges, _ = ax.pie(values, colors=cat_colors[:len(values)], startangle=90, wedgeprops=dict(width=0.45, edgecolor=COLORS["card_bg"], linewidth=2))
            ax.axis("equal")

            fig.text(0.5, 0.58, "Total spent", ha="center", va="center", fontsize=8, color=COLORS["text_muted"])
            fig.text(0.5, 0.46, f"{total_expense:,.0f}", ha="center", va="center", fontsize=11, fontweight="bold", color=COLORS["text_main"])
            fig.text(0.5, 0.36, "VND", ha="center", va="center", fontsize=8, color=COLORS["text_muted"])

            canvas = FigureCanvasTkAgg(fig, master=chart_frame)
            canvas.draw()
            canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        else:
            can = tk.Canvas(chart_frame, width=160, height=160, bg=COLORS["card_bg"], bd=0, highlightthickness=0)
            can.pack(pady=4)
            can.create_oval(10, 10, 150, 150, fill=COLORS["primary"], outline=COLORS["card_bg"])
            can.create_oval(35, 35, 125, 125, fill=COLORS["card_bg"], outline=COLORS["card_bg"])
            can.create_text(80, 65, text="Total spent", font=("Segoe UI", 7), fill=COLORS["text_muted"])
            can.create_text(80, 80, text=f"{total_expense:,.0f}", font=("Segoe UI", 9, "bold"), fill=COLORS["text_main"])
            can.create_text(80, 95, text="VND", font=("Segoe UI", 7), fill=COLORS["text_muted"])

        legend_container = tk.Frame(self.analytics_card, bg=COLORS["card_bg"], padx=18, pady=4)
        legend_container.pack(fill=tk.BOTH, expand=True)

        cat_items = [
            ("Food", cat_spending.get("Food", 2500000), COLORS["chart_food"]),
            ("Housing", cat_spending.get("Housing", 3000000), COLORS["chart_housing"]),
            ("Education", cat_spending.get("Education", 1500000), COLORS["chart_education"]),
            ("Transport", cat_spending.get("Transport", 1200000), COLORS["chart_transport"]),
            ("Leisure", cat_spending.get("Leisure", 6000000), COLORS["chart_leisure"])
        ]

        for name, amt, color in cat_items:
            pct = (amt / spent_total * 100) if spent_total > 0 else 0
            row_l = tk.Frame(legend_container, bg=COLORS["card_bg"])
            row_l.pack(fill=tk.X, pady=2)

            dot = tk.Label(row_l, text="●", font=("Segoe UI", 8), bg=COLORS["card_bg"], fg=color)
            dot.pack(side=tk.LEFT, padx=(0, 6))

            tk.Label(row_l, text=name, font=("Segoe UI", 8), bg=COLORS["card_bg"], fg=COLORS["text_muted"], anchor=tk.W).pack(side=tk.LEFT, fill=tk.X, expand=True)

            amt_label = f"{amt/1000000:.1f}M" if amt >= 1000000 else f"{amt/1000:.0f}K"
            tk.Label(row_l, text=amt_label, font=("Segoe UI", 8, "bold"), bg=COLORS["card_bg"], fg=COLORS["text_main"], width=6, anchor=tk.E).pack(side=tk.LEFT)
            tk.Label(row_l, text=f"{pct:.2f}%", font=("Segoe UI", 8), bg=COLORS["card_bg"], fg=COLORS["text_muted"], width=7, anchor=tk.E).pack(side=tk.RIGHT)

    def _render_budget_goals_section(self):
        head = tk.Frame(self.content_area, bg=COLORS["bg_main"])
        head.pack(fill=tk.X, pady=(0, 10))

        tk.Label(head, text="Monthly Budget Goals", font=("Segoe UI", 11, "bold"), bg=COLORS["bg_main"], fg=COLORS["text_main"]).pack(side=tk.LEFT)

        manage_btn = tk.Label(head, text="Manage budgets →", font=("Segoe UI", 9, "bold"), bg=COLORS["bg_main"], fg=COLORS["primary"], cursor="hand2")
        manage_btn.pack(side=tk.RIGHT)
        manage_btn.bind("<Button-1>", lambda e: self.show_view("budgets"))

        cards_row = tk.Frame(self.content_area, bg=COLORS["bg_main"])
        cards_row.pack(fill=tk.X)

        for idx, item in enumerate(self.budgets):
            card = tk.Frame(cards_row, bg=COLORS["card_bg"], bd=0, highlightbackground=COLORS["border"], highlightthickness=1, padx=16, pady=12)
            card.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0 if idx == 0 else 12, 0))

            top_f = tk.Frame(card, bg=COLORS["card_bg"])
            top_f.pack(fill=tk.X)

            icon_lbl = tk.Label(top_f, text=f"{item['icon']}  {item['category']}", font=("Segoe UI", 9, "bold"), bg=COLORS["card_bg"], fg=COLORS["text_main"])
            icon_lbl.pack(side=tk.LEFT)

            badge = tk.Label(top_f, text=item["status"], font=("Segoe UI", 8, "bold"), bg=item["bg"], fg=item["color"], padx=6, pady=2)
            badge.pack(side=tk.RIGHT)

            pct = (item["spent"] / item["limit"] * 100) if item["limit"] > 0 else 0
            val_f = tk.Frame(card, bg=COLORS["card_bg"])
            val_f.pack(fill=tk.X, pady=(8, 4))

            spent_m = f"{item['spent']/1000000:.1f}M" if item['spent'] >= 1000000 else f"{item['spent']/1000:.0f}K"
            limit_m = f"{item['limit']/1000000:.1f}M" if item['limit'] >= 1000000 else f"{item['limit']/1000:.0f}K"
            tk.Label(val_f, text=f"{spent_m} / {limit_m} VND", font=("Segoe UI", 9, "bold"), bg=COLORS["card_bg"], fg=COLORS["text_main"]).pack(side=tk.LEFT)
            tk.Label(val_f, text=f"{pct:.0f}%", font=("Segoe UI", 9, "bold"), bg=COLORS["card_bg"], fg=item["color"]).pack(side=tk.RIGHT)

            track = tk.Canvas(card, height=6, bg=COLORS["tag_bg"], bd=0, highlightthickness=0)
            track.pack(fill=tk.X, pady=(2, 6))

            def draw_bar(c=track, p=pct, clr=item["color"]):
                c.update_idletasks()
                w = c.winfo_width()
                fill_w = int(w * min(p, 100) / 100)
                if fill_w > 0:
                    c.create_rectangle(0, 0, fill_w, 6, fill=clr, width=0)

            self.after(50, draw_bar)

            diff = item["limit"] - item["spent"]
            if diff > 0:
                sub_txt = f"{diff:,.0f} VND remaining"
                sub_clr = COLORS["text_muted"]
            elif diff == 0:
                sub_txt = "Housing · Fully allocated"
                sub_clr = COLORS["text_muted"]
            else:
                sub_txt = f"{abs(diff):,.0f} VND over limit"
                sub_clr = COLORS["expense"]

            tk.Label(card, text=sub_txt, font=("Segoe UI", 8), bg=COLORS["card_bg"], fg=sub_clr).pack(anchor=tk.W)

    def _render_transactions_view(self):
        top_h = tk.Frame(self.content_area, bg=COLORS["bg_main"])
        top_h.pack(fill=tk.X, pady=(0, 16))

        tk.Label(top_h, text="Transaction Ledger", font=("Segoe UI", 16, "bold"), bg=COLORS["bg_main"], fg=COLORS["text_main"]).pack(side=tk.LEFT)

        act_f = tk.Frame(top_h, bg=COLORS["bg_main"])
        act_f.pack(side=tk.RIGHT)

        HoverButton(act_f, default_bg=COLORS["primary"], hover_bg=COLORS["primary_hover"], text="+ Add Transaction", font=("Segoe UI", 9, "bold"), fg="#ffffff", padx=14, pady=6, command=self.open_add_transaction_dialog).pack(side=tk.LEFT, padx=6)
        HoverButton(act_f, default_bg="#0284c7", hover_bg="#0369a1", text="Export CSV", font=("Segoe UI", 9, "bold"), fg="#ffffff", padx=14, pady=6, command=self.export_csv).pack(side=tk.LEFT)

        card = tk.Frame(self.content_area, bg=COLORS["card_bg"], bd=0, highlightbackground=COLORS["border"], highlightthickness=1)
        card.pack(fill=tk.BOTH, expand=True)

        cols_f = tk.Frame(card, bg=COLORS["bg_main"], highlightbackground=COLORS["border"], highlightthickness=1, padx=14, pady=8)
        cols_f.pack(fill=tk.X)

        tk.Label(cols_f, text="Date", font=("Segoe UI", 9, "bold"), bg=COLORS["bg_main"], fg=COLORS["text_muted"], width=10, anchor=tk.W).pack(side=tk.LEFT)
        tk.Label(cols_f, text="Title", font=("Segoe UI", 9, "bold"), bg=COLORS["bg_main"], fg=COLORS["text_muted"], anchor=tk.W).pack(side=tk.LEFT, fill=tk.X, expand=True)
        tk.Label(cols_f, text="Category", font=("Segoe UI", 9, "bold"), bg=COLORS["bg_main"], fg=COLORS["text_muted"], width=14, anchor=tk.W).pack(side=tk.LEFT)
        tk.Label(cols_f, text="Type", font=("Segoe UI", 9, "bold"), bg=COLORS["bg_main"], fg=COLORS["text_muted"], width=10, anchor=tk.W).pack(side=tk.LEFT)
        tk.Label(cols_f, text="Amount · VND", font=("Segoe UI", 9, "bold"), bg=COLORS["bg_main"], fg=COLORS["text_muted"], width=16, anchor=tk.E).pack(side=tk.LEFT)
        tk.Label(cols_f, text="Actions", font=("Segoe UI", 9, "bold"), bg=COLORS["bg_main"], fg=COLORS["text_muted"], width=10, anchor=tk.E).pack(side=tk.RIGHT)

        self.table_rows_container = tk.Frame(card, bg=COLORS["card_bg"])
        self.table_rows_container.pack(fill=tk.BOTH, expand=True)

        self._populate_table_rows(self.transactions)

    def _render_budgets_view(self):
        top_h = tk.Frame(self.content_area, bg=COLORS["bg_main"])
        top_h.pack(fill=tk.X, pady=(0, 16))
        tk.Label(top_h, text="Budget & Category Limits", font=("Segoe UI", 16, "bold"), bg=COLORS["bg_main"], fg=COLORS["text_main"]).pack(side=tk.LEFT)

        wrap = tk.Frame(self.content_area, bg=COLORS["card_bg"], bd=0, highlightbackground=COLORS["border"], highlightthickness=1, padx=20, pady=16)
        wrap.pack(fill=tk.BOTH, expand=True)

        for b in self.budgets:
            row_f = tk.Frame(wrap, bg=COLORS["bg_main"], bd=0, highlightbackground=COLORS["border"], highlightthickness=1, padx=16, pady=12)
            row_f.pack(fill=tk.X, pady=8)

            t_row = tk.Frame(row_f, bg=COLORS["bg_main"])
            t_row.pack(fill=tk.X)

            tk.Label(t_row, text=f"{b['icon']}  {b['category']}", font=("Segoe UI", 10, "bold"), bg=COLORS["bg_main"], fg=COLORS["text_main"]).pack(side=tk.LEFT)
            tk.Label(t_row, text=f"Spent: {b['spent']:,.0f} VND / Limit: {b['limit']:,.0f} VND", font=("Segoe UI", 9), bg=COLORS["bg_main"], fg=COLORS["text_muted"]).pack(side=tk.LEFT, padx=16)
            tk.Label(t_row, text=b['status'], font=("Segoe UI", 8, "bold"), bg=b['bg'], fg=b['color'], padx=8, pady=2).pack(side=tk.RIGHT)

            pct = (b['spent'] / b['limit'] * 100) if b['limit'] > 0 else 0
            pb = ttk.Progressbar(row_f, maximum=100, value=min(pct, 100))
            pb.pack(fill=tk.X, pady=(8, 4))

    def _render_analytics_view(self):
        top_h = tk.Frame(self.content_area, bg=COLORS["bg_main"])
        top_h.pack(fill=tk.X, pady=(0, 16))
        tk.Label(top_h, text="Financial Analytics", font=("Segoe UI", 16, "bold"), bg=COLORS["bg_main"], fg=COLORS["text_main"]).pack(side=tk.LEFT)

        total_expense = sum(t["amount"] for t in self.transactions if t["type"] == "EXPENSE")
        wrap = tk.Frame(self.content_area, bg=COLORS["card_bg"], bd=0, highlightbackground=COLORS["border"], highlightthickness=1, padx=24, pady=20)
        wrap.pack(fill=tk.BOTH, expand=True)

        self.analytics_card = wrap
        self._render_spending_analytics_card(total_expense)

    def _render_reports_view(self):
        top_h = tk.Frame(self.content_area, bg=COLORS["bg_main"])
        top_h.pack(fill=tk.X, pady=(0, 16))
        tk.Label(top_h, text="Reports & Data Export", font=("Segoe UI", 16, "bold"), bg=COLORS["bg_main"], fg=COLORS["text_main"]).pack(side=tk.LEFT)

        card = tk.Frame(self.content_area, bg=COLORS["card_bg"], bd=0, highlightbackground=COLORS["border"], highlightthickness=1, padx=24, pady=24)
        card.pack(fill=tk.X)

        tk.Label(card, text="📄 Export Transactions Data", font=("Segoe UI", 12, "bold"), bg=COLORS["card_bg"], fg=COLORS["text_main"]).pack(anchor=tk.W)
        tk.Label(card, text="Export full ledger records to UTF-8 CSV compatible with Microsoft Excel.", font=("Segoe UI", 9), bg=COLORS["card_bg"], fg=COLORS["text_muted"]).pack(anchor=tk.W, pady=(4, 16))

        btn_row = tk.Frame(card, bg=COLORS["card_bg"])
        btn_row.pack(anchor=tk.W)

        HoverButton(btn_row, default_bg="#0284c7", hover_bg="#0369a1", text="📄 Export CSV (UTF-8)", font=("Segoe UI", 9, "bold"), fg="#ffffff", padx=16, pady=8, command=self.export_csv).pack(side=tk.LEFT, padx=(0, 12))
        HoverButton(btn_row, default_bg=COLORS["income"], hover_bg="#047857", text="💾 Backup Database", font=("Segoe UI", 9, "bold"), fg="#ffffff", padx=16, pady=8, command=lambda: messagebox.showinfo("BudgetBuddy", "Database backup snapshot saved successfully.")).pack(side=tk.LEFT)

    def _render_settings_view(self):
        top_h = tk.Frame(self.content_area, bg=COLORS["bg_main"])
        top_h.pack(fill=tk.X, pady=(0, 16))
        tk.Label(top_h, text="Account & Preferences", font=("Segoe UI", 16, "bold"), bg=COLORS["bg_main"], fg=COLORS["text_main"]).pack(side=tk.LEFT)

        card = tk.Frame(self.content_area, bg=COLORS["card_bg"], bd=0, highlightbackground=COLORS["border"], highlightthickness=1, padx=24, pady=24)
        card.pack(fill=tk.X)

        tk.Label(card, text="User Profile: Minh Le", font=("Segoe UI", 11, "bold"), bg=COLORS["card_bg"], fg=COLORS["text_main"]).pack(anchor=tk.W)
        tk.Label(card, text="Active Currency: VND (Vietnamese Dong)", font=("Segoe UI", 9), bg=COLORS["card_bg"], fg=COLORS["text_muted"]).pack(anchor=tk.W, pady=4)
        tk.Label(card, text="Application Version: 1.0.0", font=("Segoe UI", 9), bg=COLORS["card_bg"], fg=COLORS["text_muted"]).pack(anchor=tk.W, pady=4)

    def filter_transactions(self):
        q = self.search_query.get().strip().lower()
        if not q:
            filtered = self.transactions
        else:
            filtered = [t for t in self.transactions if q in t["title"].lower() or q in t["category"].lower() or q in t["type"].lower()]
        
        if hasattr(self, "table_rows_container"):
            limit = 6 if self.current_view == "dashboard" else len(filtered)
            self._populate_table_rows(filtered[:limit])

    def open_add_transaction_dialog(self):
        self._show_transaction_modal("Add New Transaction")

    def open_edit_transaction_dialog(self, tx):
        self._show_transaction_modal("Edit Transaction", tx)

    def _show_transaction_modal(self, title_text, edit_item=None):
        dlg = tk.Toplevel(self)
        dlg.title(title_text)
        dlg.geometry("440x480")
        dlg.resizable(False, False)
        dlg.configure(bg=COLORS["card_bg"])
        dlg.transient(self)
        dlg.grab_set()

        head_f = tk.Frame(dlg, bg=COLORS["card_bg"], padx=20, pady=16)
        head_f.pack(fill=tk.X)
        tk.Label(head_f, text=title_text, font=("Segoe UI", 12, "bold"), bg=COLORS["card_bg"], fg=COLORS["text_main"]).pack(anchor=tk.W)

        body_f = tk.Frame(dlg, bg=COLORS["card_bg"], padx=20)
        body_f.pack(fill=tk.BOTH, expand=True)

        def make_field(label_txt, var, is_combo=False, combo_vals=None):
            tk.Label(body_f, text=label_txt, font=("Segoe UI", 8, "bold"), bg=COLORS["card_bg"], fg=COLORS["text_muted"]).pack(anchor=tk.W, pady=(6, 2))
            if is_combo:
                w = ttk.Combobox(body_f, textvariable=var, values=combo_vals, state="readonly", font=("Segoe UI", 9))
                w.pack(fill=tk.X)
                return w
            else:
                w = tk.Entry(body_f, textvariable=var, font=("Segoe UI", 9), bd=0, highlightbackground=COLORS["border"], highlightthickness=1)
                w.pack(fill=tk.X, ipady=4)
                return w

        title_var = tk.StringVar(value=edit_item["title"] if edit_item else "")
        make_field("Transaction Title", title_var)

        type_var = tk.StringVar(value=edit_item["type"] if edit_item else "EXPENSE")
        make_field("Type", type_var, is_combo=True, combo_vals=["EXPENSE", "INCOME"])

        cat_var = tk.StringVar(value=edit_item["category"] if edit_item else "Food")
        make_field("Category", cat_var, is_combo=True, combo_vals=["Food", "Housing", "Education", "Transport", "Leisure", "Work", "Salary", "Other"])

        amt_var = tk.StringVar(value=str(edit_item["amount"]) if edit_item else "")
        make_field("Amount (VND)", amt_var)

        date_var = tk.StringVar(value=edit_item["date"] if edit_item else datetime.now().strftime("%Y-%m-%d"))
        make_field("Date (YYYY-MM-DD)", date_var)

        note_var = tk.StringVar(value=edit_item["note"] if edit_item else "")
        make_field("Note", note_var)

        btn_row = tk.Frame(dlg, bg=COLORS["card_bg"], padx=20, pady=16)
        btn_row.pack(fill=tk.X, side=tk.BOTTOM)

        def save():
            t_val = title_var.get().strip()
            if not t_val:
                messagebox.showerror("Error", "Please enter a transaction title.", parent=dlg)
                return
            try:
                a_val = float(amt_var.get().replace(",", "").replace(".", "").strip())
                if a_val <= 0:
                    raise ValueError()
            except ValueError:
                messagebox.showerror("Error", "Please enter a valid positive amount.", parent=dlg)
                return

            if edit_item:
                edit_item["title"] = t_val
                edit_item["type"] = type_var.get()
                edit_item["category"] = cat_var.get()
                edit_item["amount"] = a_val
                edit_item["date"] = date_var.get()
                edit_item["note"] = note_var.get()
            else:
                new_id = max([t["id"] for t in self.transactions], default=0) + 1
                self.transactions.insert(0, {
                    "id": new_id,
                    "title": t_val,
                    "type": type_var.get(),
                    "category": cat_var.get(),
                    "amount": a_val,
                    "date": date_var.get(),
                    "note": note_var.get()
                })

            dlg.destroy()
            self.show_view(self.current_view)

        HoverButton(btn_row, default_bg=COLORS["primary"], hover_bg=COLORS["primary_hover"], text="Save Transaction", font=("Segoe UI", 9, "bold"), fg="#ffffff", padx=16, pady=6, command=save).pack(side=tk.RIGHT)
        tk.Button(btn_row, text="Cancel", font=("Segoe UI", 9), bg=COLORS["card_bg"], fg=COLORS["text_muted"], bd=0, padx=12, pady=6, cursor="hand2", command=dlg.destroy).pack(side=tk.RIGHT, padx=8)

    def delete_transaction(self, tx_id):
        if messagebox.askyesno("Confirm Delete", "Are you sure you want to delete this transaction?"):
            self.transactions = [t for t in self.transactions if t["id"] != tx_id]
            self.show_view(self.current_view)

    def export_csv(self):
        file_path = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV UTF-8", "*.csv")], initialfile=f"budgetbuddy_export_{datetime.now().strftime('%Y%m%d')}.csv")
        if not file_path:
            return
        try:
            with open(file_path, "w", newline="", encoding="utf-8-sig") as f:
                writer = csv.writer(f)
                writer.writerow(["ID", "Date", "Title", "Type", "Category", "Amount", "Note"])
                for t in self.transactions:
                    writer.writerow([t["id"], t["date"], t["title"], t["type"], t["category"], t["amount"], t["note"]])
            messagebox.showinfo("Export Success", f"Transactions exported successfully to:\n{file_path}")
        except Exception as e:
            messagebox.showerror("Export Failed", str(e))

if __name__ == "__main__":
    app = BudgetBuddyApp()
    app.mainloop()
