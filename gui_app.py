# RetailPulse (Enterprise Sales Data Analyzer) - gui_app.py

# Imports
import tkinter as tk
from tkinter import ttk, messagebox, filedialog

from auth_manager import AuthManager
from analytics_engine import AnalyticsEngine
from email_dispatcher import EmailDispatcher

# Class 1: RetailPulseGUI
class RetailPulseGUI:
    """ Primary graphical user interface controller for RetailPulse. """
    
    # Constructor: __init__
    def __init__(self, root: tk.Tk, engine: AnalyticsEngine, auth: AuthManager, email_dispatcher: EmailDispatcher) -> None:
        self.root = root
        self.engine = engine
        self.auth = auth
        self.email_dispatcher = email_dispatcher

        self.root.title("RetailPulse - Enterprise Sales Data Analyzer")
        self.root.geometry("1180x760")
        self.root.minsize(980, 640)

        # Style Configuration
        self.style = ttk.Style()
        self.style.theme_use("clam")
        self._configure_styles()

        # Hide Main Window Until Authenticated
        self.root.withdraw()

        # Launch Authentication Modal
        self._show_login_modal()
    
    # Method 1: _configure_styles (Internal)
    def _configure_styles(self) -> None:
        """ Configures clean colors and typography for ttk widgets. """
        
        self.style.configure(".", font=("Segoe UI", 10))
        self.style.configure("Treeview.Heading", font=("Segoe UI", 10, "bold"), background="#e2e8f0")
        self.style.configure("Treeview", rowheight=24)
        self.style.configure("Header.TLabel", font=("Segoe UI", 14, "bold"), foreground="#0f172a")
        self.style.configure("SubHeader.TLabel", font=("Segoe UI", 10, "italic"), foreground="#475569")
        self.style.configure("Accent.TButton", font=("Segoe UI", 10, "bold"))
    
    # Method 2: _show_login_modal (Internal)
    def _show_login_modal(self) -> None:
        """ Displays Harsha's authentication login window. """
        
        self.login_win = tk.Toplevel(self.root)
        self.login_win.title("RetailPulse Login")
        self.login_win.resizable(False, False)
        self.login_win.protocol("WM_DELETE_WINDOW", self.root.destroy)

        # Center Dialog on the Screen
        self.login_win.update_idletasks()
        
        win_w, win_h = 380, 280
        screen_w = self.login_win.winfo_screenwidth()
        screen_h = self.login_win.winfo_screenheight()
        pos_x = (screen_w // 2) - (win_w // 2)
        pos_y = (screen_h // 2) - (win_h // 2)
        
        self.login_win.geometry(f"{win_w}x{win_h}+{pos_x}+{pos_y}")

        frame = ttk.Frame(self.login_win, padding=25)
        frame.pack(fill=tk.BOTH, expand=True)

        ttk.Label(frame, text="RetailPulse Access", font=("Segoe UI", 14, "bold")).pack(pady=(0, 5))
        ttk.Label(frame, text="Role-Based Security Portal", font=("Segoe UI", 9, "italic")).pack(pady=(0, 15))

        ttk.Label(frame, text="Username:").pack(anchor=tk.W)
        self.username_entry = ttk.Entry(frame, width=32)
        self.username_entry.pack(fill=tk.X, pady=(2, 10))
        self.username_entry.focus()

        ttk.Label(frame, text="Password:").pack(anchor=tk.W)
        self.password_entry = ttk.Entry(frame, width=32, show="•")
        self.password_entry.pack(fill=tk.X, pady=(2, 15))
        self.password_entry.bind("<Return>", lambda e: self._attempt_login())

        btn_frame = ttk.Frame(frame)
        btn_frame.pack(fill=tk.X, pady=(5, 0))

        ttk.Button(btn_frame, text="Login", command=self._attempt_login, style="Accent.TButton").pack(side=tk.RIGHT)
        ttk.Button(btn_frame, text="Cancel", command=self.root.destroy).pack(side=tk.RIGHT, padx=5)
    
    # Method 3: _attempt_login (Internal)
    def _attempt_login(self) -> None:
        """ Validates credentials against AuthManager. """
        
        user = self.username_entry.get().strip()
        pwd = self.password_entry.get().strip()

        success, msg, role = self.auth.authenticate(user, pwd)
        
        if success:
            self.login_win.destroy()
            self.engine.append_audit_entry(user, "LOGIN", f"User logged in with role '{role}'")
            self._build_main_ui()
            self.root.deiconify()
        else:
            self.engine.append_audit_entry(user or "UNKNOWN", "LOGIN_FAILED", "Invalid credentials entered")
            messagebox.showerror("Authentication Failed", msg, parent=self.login_win)
    
    # Method 4: _build_main_ui (Internal)
    def _build_main_ui(self) -> None:
        """ Assembles the primary workspace and role-guarded tabbed pages. """
        
        # Top Banner with Session Indicator
        top_bar = ttk.Frame(self.root, padding="12 8", relief=tk.RAISED)
        top_bar.pack(fill=tk.X)

        session = self.auth.get_session_info()
        title_lbl = ttk.Label(top_bar, text="RetailPulse Sales Analyzer", font=("Segoe UI", 12, "bold"))
        title_lbl.pack(side=tk.LEFT)

        user_badge = f"Active User: {session['username']} ({session['role']})"
        ttk.Label(top_bar, text=user_badge, font=("Segoe UI", 10, "italic"), foreground="#0369a1").pack(side=tk.RIGHT, padx=10)
        ttk.Button(top_bar, text="Logout", command=self._logout).pack(side=tk.RIGHT)

        # Tabbed Workspace
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Tab 1: Sales Data Explorer
        self.tab_sales = ttk.Frame(self.notebook)
        self.notebook.add(self.tab_sales, text="Sales Explorer")
        self._build_sales_tab()

        # Tab 2: SQL Query Engine
        if self.auth.has_permission("execute_query"):
            self.tab_query = ttk.Frame(self.notebook)
            self.notebook.add(self.tab_query, text="Query Engine")
            self._build_query_tab()

        # Tab 3: Market Basket & RFM
        if self.auth.has_permission("view_basket"):
            self.tab_analytics = ttk.Frame(self.notebook)
            self.notebook.add(self.tab_analytics, text="Basket & RFM")
            self._build_basket_rfm_tab()

        # Tab 4: Anomaly Detection
        if self.auth.has_permission("view_anomalies"):
            self.tab_anomalies = ttk.Frame(self.notebook)
            self.notebook.add(self.tab_anomalies, text="Pricing Anomalies")
            self._build_anomalies_tab()

        # Tab 5: Tamper-Evident Audit Ledger
        if self.auth.has_permission("view_audit_trail"):
            self.tab_audit = ttk.Frame(self.notebook)
            self.notebook.add(self.tab_audit, text="Audit Ledger")
            self._build_audit_tab()

        # Tab 6: Reports & Email Dispatch
        if self.auth.has_permission("export_reports"):
            self.tab_reports = ttk.Frame(self.notebook)
            self.notebook.add(self.tab_reports, text="Reports & Alerts")
            self._build_reports_tab()
    
    # Method 5: _logout (Internal)
    def _logout(self) -> None:
        """ Logs out the active user and restarts login window. """
        
        session = self.auth.get_session_info()
        self.engine.append_audit_entry(session["username"] or "ANON", "LOGOUT", "User terminated session")
        self.auth.logout()

        for widget in self.root.winfo_children():
            widget.destroy()

        self.root.withdraw()
        self._show_login_modal()
    
    # Method 6: _build_sales_tab (Internal) - Tab 1
    def _build_sales_tab(self) -> None:
        top_controls = ttk.Frame(self.tab_sales, padding=10)
        top_controls.pack(fill=tk.X)

        ttk.Label(top_controls, text="Sales Data Records", style="Header.TLabel").pack(side=tk.LEFT)

        # Undo/Redo Buttons
        self.btn_undo = ttk.Button(top_controls, text="↶ Undo Filter", command=self._handle_undo)
        self.btn_undo.pack(side=tk.RIGHT, padx=4)
        self.btn_redo = ttk.Button(top_controls, text="↷ Redo Filter", command=self._handle_redo)
        self.btn_redo.pack(side=tk.RIGHT, padx=4)
        ttk.Button(top_controls, text="Reset View", command=self._handle_reset).pack(side=tk.RIGHT, padx=4)

        # Record Counter
        self.lbl_record_count = ttk.Label(self.tab_sales, text="", font=("Segoe UI", 9, "italic"))
        self.lbl_record_count.pack(anchor=tk.W, padx=12, pady=(0, 6))

        # Data Table
        table_frame = ttk.Frame(self.tab_sales)
        table_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=(0, 10))

        cols = ("id", "name", "category", "price", "discount", "rating", "users")
        self.sales_tree = ttk.Treeview(table_frame, columns=cols, show="headings", selectmode="browse")

        self.sales_tree.heading("id", text="Product ID")
        self.sales_tree.heading("name", text="Product Name")
        self.sales_tree.heading("category", text="Category")
        self.sales_tree.heading("price", text="Price (₹)")
        self.sales_tree.heading("discount", text="Discount")
        self.sales_tree.heading("rating", text="Rating")
        self.sales_tree.heading("users", text="Sanitized Reviewers (PII)")

        self.sales_tree.column("id", width=95, anchor=tk.CENTER)
        self.sales_tree.column("name", width=340)
        self.sales_tree.column("category", width=160)
        self.sales_tree.column("price", width=90, anchor=tk.E)
        self.sales_tree.column("discount", width=80, anchor=tk.CENTER)
        self.sales_tree.column("rating", width=70, anchor=tk.CENTER)
        self.sales_tree.column("users", width=200)

        scroll_y = ttk.Scrollbar(table_frame, orient=tk.VERTICAL, command=self.sales_tree.yview)
        scroll_x = ttk.Scrollbar(table_frame, orient=tk.HORIZONTAL, command=self.sales_tree.xview)
        self.sales_tree.configure(yscrollcommand=scroll_y.set, xscrollcommand=scroll_x.set)

        self.sales_tree.grid(row=0, column=0, sticky="nsew")
        scroll_y.grid(row=0, column=1, sticky="ns")
        scroll_x.grid(row=1, column=0, sticky="ew")

        table_frame.rowconfigure(0, weight=1)
        table_frame.columnconfigure(0, weight=1)

        self._refresh_sales_table()
    
    # Method 7: _refresh_sales_table (Internal)
    def _refresh_sales_table(self) -> None:
        """ Repopulates the sales explorer table with current analytical state. """
        
        for item in self.sales_tree.get_children():
            self.sales_tree.delete(item)

        for rec in self.engine.current_dataset:
            self.sales_tree.insert("", tk.END, values=(
                rec["product_id"],
                rec["product_name"][:55] + "..." if len(rec["product_name"]) > 55 else rec["product_name"],
                rec["category"],
                f"₹{rec['discounted_price']:,.2f}",
                f"{rec['discount_percentage']}%",
                f"{rec['rating']} ★",
                rec["masked_users"]
            ))

        self.lbl_record_count.config(text=f"Showing {len(self.engine.current_dataset):,} active records (Base: {len(self.engine.raw_records):,})")
    
    # Method 8: _handle_undo (Internal)
    def _handle_undo(self) -> None:
        user = self.auth.get_session_info()["username"] or "ANON"
        
        if self.engine.undo(user):
            self._refresh_sales_table()
        else:
            messagebox.showinfo("Undo", "No previous analytical filter states to revert.")
    
    # Method 9: _handle_redo (Internal)
    def _handle_redo(self) -> None:
        user = self.auth.get_session_info()["username"] or "ANON"
        
        if self.engine.redo(user):
            self._refresh_sales_table()
        else:
            messagebox.showinfo("Redo", "No subsequent states to redo.")
    
    # Method 10: _handle_reset (Internal)
    def _handle_reset(self) -> None:
        user = self.auth.get_session_info()["username"] or "ANON"
        self.engine.reset_filters(user)
        self._refresh_sales_table()
    
    # Method 11: _build_query_tab (Internal) - Tab 2
    def _build_query_tab(self) -> None:
        container = ttk.Frame(self.tab_query, padding=15)
        container.pack(fill=tk.BOTH, expand=True)

        ttk.Label(container, text="In-Memory SQL Query Tokenizer", style="Header.TLabel").pack(anchor=tk.W)
        ttk.Label(
            container,
            text="Query format: FILTER <column> <op> <value> [AND <column> <op> <value>]",
            style="SubHeader.TLabel"
        ).pack(anchor=tk.W, pady=(0, 10))

        q_frame = ttk.Frame(container)
        q_frame.pack(fill=tk.X, pady=5)

        self.query_var = tk.StringVar(value='FILTER category == "Computers&Accessories" AND discounted_price > 500')
        self.query_entry = ttk.Entry(q_frame, textvariable=self.query_var, font=("Consolas", 10))
        self.query_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 10))

        ttk.Button(q_frame, text="Execute Query", command=self._execute_custom_query, style="Accent.TButton").pack(side=tk.RIGHT)

        # Query Suggestions
        sugg_frame = ttk.LabelFrame(container, text="Sample Query Templates", padding=8)
        sugg_frame.pack(fill=tk.X, pady=10)

        templates = [
            'FILTER category == "Electronics" AND rating >= 4.0',
            'FILTER discount_percentage >= 60',
            'FILTER discounted_price > 2000 AND discount_percentage >= 40'
        ]
        
        for t in templates:
            ttk.Button(sugg_frame, text=t, command=lambda val=t: self.query_var.set(val)).pack(anchor=tk.W, pady=2)

        # Output Label
        self.lbl_query_status = ttk.Label(container, text="Awaiting execution...", font=("Segoe UI", 9, "bold"), foreground="#0369a1")
        self.lbl_query_status.pack(anchor=tk.W, pady=8)
    
    # Method 12: _execute_custom_query (Internal)
    def _execute_custom_query(self) -> None:
        user = self.auth.get_session_info()["username"] or "ANON"
        query_text = self.query_var.get()
        _, status_msg = self.engine.execute_sql_query(query_text, user)
        
        self.lbl_query_status.config(text=status_msg)
        self._refresh_sales_table()
        
        messagebox.showinfo("Query Execution", status_msg)
    
    # Method 13: _build_basket_rfm_tab (Internal) - Tab 3
    def _build_basket_rfm_tab(self) -> None:
        container = ttk.Frame(self.tab_analytics, padding=12)
        container.pack(fill=tk.BOTH, expand=True)

        # Left Pane: Market Basket
        left_frame = ttk.LabelFrame(container, text="Market Basket Affinity (Product Cross-Sells)", padding=10)
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 6))

        basket_cols = ("a", "b", "count")
        self.basket_tree = ttk.Treeview(left_frame, columns=basket_cols, show="headings")
        self.basket_tree.heading("a", text="Product A")
        self.basket_tree.heading("b", text="Product B")
        self.basket_tree.heading("count", text="Shared Co-purchases")
        self.basket_tree.column("a", width=180)
        self.basket_tree.column("b", width=180)
        self.basket_tree.column("count", width=130, anchor=tk.CENTER)
        self.basket_tree.pack(fill=tk.BOTH, expand=True)

        # Right Pane: RFM Cohorts
        right_frame = ttk.LabelFrame(container, text="Customer RFM Behavioral Cohorts", padding=10)
        right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=(6, 0))

        rfm_cols = ("segment", "users", "spend", "avg")
        self.rfm_tree = ttk.Treeview(right_frame, columns=rfm_cols, show="headings")
        self.rfm_tree.heading("segment", text="Segment")
        self.rfm_tree.heading("users", text="Unique Users")
        self.rfm_tree.heading("spend", text="Total Revenue (₹)")
        self.rfm_tree.heading("avg", text="Avg Spend (₹)")
        self.rfm_tree.column("segment", width=140)
        self.rfm_tree.column("users", width=90, anchor=tk.CENTER)
        self.rfm_tree.column("spend", width=120, anchor=tk.E)
        self.rfm_tree.column("avg", width=110, anchor=tk.E)
        self.rfm_tree.pack(fill=tk.BOTH, expand=True)

        ttk.Button(container, text="Refresh Analytics", command=self._populate_basket_and_rfm).pack(pady=6)
        self._populate_basket_and_rfm()
    
    # Method 14: _populate_basket_and_rfm (Internal)
    def _populate_basket_and_rfm(self) -> None:
        # Basket Data
        for item in self.basket_tree.get_children():
            self.basket_tree.delete(item)
            
        pairs = self.engine.calculate_market_basket_affinity(min_support=2)
        
        for p in pairs:
            self.basket_tree.insert("", tk.END, values=(p["product_a"], p["product_b"], p["co_occurrence_count"]))

        # RFM Data
        for item in self.rfm_tree.get_children():
            self.rfm_tree.delete(item)
            
        rfm_res = self.engine.compute_rfm_segmentation()

        for seg, data in rfm_res.items():
            self.rfm_tree.insert("", tk.END, values=(
                seg,
                f"{data['count']:,}",
                f"₹{data['total_spend']:,.2f}",
                f"₹{data['avg_spend']:,.2f}"
            ))
    
    # Method 15: _build_anomalies_tab (Internal) - Tab 4
    def _build_anomalies_tab(self) -> None:
        container = ttk.Frame(self.tab_anomalies, padding=12)
        container.pack(fill=tk.BOTH, expand=True)

        ttk.Label(container, text="Pure-Python Z-Score Anomaly Detector", style="Header.TLabel").pack(anchor=tk.W)
        ttk.Label(container, text="Flags pricing anomalies exceeding 2.5 standard deviations from dataset mean.", style="SubHeader.TLabel").pack(anchor=tk.W, pady=(0, 8))

        cols = ("id", "name", "price", "expected", "z_score")
        self.anomaly_tree = ttk.Treeview(container, columns=cols, show="headings")
        self.anomaly_tree.heading("id", text="Product ID")
        self.anomaly_tree.heading("name", text="Product Title")
        self.anomaly_tree.heading("price", text="Actual Price (₹)")
        self.anomaly_tree.heading("expected", text="Mean Baseline (₹)")
        self.anomaly_tree.heading("z_score", text="Z-Score Deviance")

        self.anomaly_tree.column("id", width=100, anchor=tk.CENTER)
        self.anomaly_tree.column("name", width=380)
        self.anomaly_tree.column("price", width=120, anchor=tk.E)
        self.anomaly_tree.column("expected", width=130, anchor=tk.E)
        self.anomaly_tree.column("z_score", width=130, anchor=tk.CENTER)
        self.anomaly_tree.pack(fill=tk.BOTH, expand=True, pady=8)

        btn_bar = ttk.Frame(container)
        btn_bar.pack(fill=tk.X)
        ttk.Button(btn_bar, text="Scan for Anomalies", command=self._scan_anomalies).pack(side=tk.LEFT)
        self.lbl_anomaly_summary = ttk.Label(btn_bar, text="", font=("Segoe UI", 9, "bold"))
        self.lbl_anomaly_summary.pack(side=tk.LEFT, padx=12)

        self._scan_anomalies()
    
    # Method 16: _scan_anomalies (Internal)
    def _scan_anomalies(self) -> None:
        for item in self.anomaly_tree.get_children():
            self.anomaly_tree.delete(item)

        anomalies = self.engine.detect_pricing_anomalies(threshold=2.5)
        
        for a in anomalies:
            self.anomaly_tree.insert("", tk.END, values=(
                a["product_id"],
                a["product_name"][:60] + "...",
                f"₹{a['discounted_price']:,.2f}",
                f"₹{a['expected_mean']:,.2f}",
                f"{a['z_score']} σ"
            ))
            
        self.lbl_anomaly_summary.config(text=f"Detected {len(anomalies)} statistical anomalies.")
    
    # Method 17: _build_audit_tab (Internal) - Tab 5
    def _build_audit_tab(self) -> None:
        container = ttk.Frame(self.tab_audit, padding=12)
        container.pack(fill=tk.BOTH, expand=True)

        top_audit = ttk.Frame(container)
        top_audit.pack(fill=tk.X, pady=(0, 8))

        ttk.Label(top_audit, text="Tamper-Evident SHA-256 Cryptographic Audit Ledger", style="Header.TLabel").pack(side=tk.LEFT)
        ttk.Button(top_audit, text="Verify Chain Integrity", command=self._verify_chain).pack(side=tk.RIGHT)
        ttk.Button(top_audit, text="Refresh Ledger", command=self._refresh_audit_tree).pack(side=tk.RIGHT, padx=5)

        cols = ("idx", "timestamp", "user", "action", "details", "hash")
        self.audit_tree = ttk.Treeview(container, columns=cols, show="headings")
        self.audit_tree.heading("idx", text="#")
        self.audit_tree.heading("timestamp", text="Timestamp")
        self.audit_tree.heading("user", text="Operator")
        self.audit_tree.heading("action", text="Action")
        self.audit_tree.heading("details", text="Operation Details")
        self.audit_tree.heading("hash", text="Cryptographic Block Hash")

        self.audit_tree.column("idx", width=40, anchor=tk.CENTER)
        self.audit_tree.column("timestamp", width=140, anchor=tk.CENTER)
        self.audit_tree.column("user", width=90, anchor=tk.CENTER)
        self.audit_tree.column("action", width=120)
        self.audit_tree.column("details", width=340)
        self.audit_tree.column("hash", width=220)
        self.audit_tree.pack(fill=tk.BOTH, expand=True)

        self._refresh_audit_tree()

    # Method 18: _refresh_audit_tree (Internal)
    def _refresh_audit_tree(self) -> None:
        for item in self.audit_tree.get_children():
            self.audit_tree.delete(item)
            
        for b in self.engine.audit_chain:
            self.audit_tree.insert("", tk.END, values=(
                b.index,
                b.timestamp,
                b.user,
                b.action,
                b.details,
                b.block_hash[:20] + "..." + b.block_hash[-10:]
            ))
    
    # Method 19: _verify_chain (Internal)
    def _verify_chain(self) -> None:
        valid, msg = self.engine.verify_audit_ledger()
        
        if valid:
            messagebox.showinfo("Ledger Integrity", msg)
        else:
            messagebox.showerror("Tamper Alert", msg)
    
    # Method 20: _build_reports_tab (Internal) - Tab 6
    def _build_reports_tab(self) -> None:
        container = ttk.Frame(self.tab_reports, padding=15)
        container.pack(fill=tk.BOTH, expand=True)

        # Export Box
        exp_frame = ttk.LabelFrame(container, text="Generate Executive Exports", padding=12)
        exp_frame.pack(fill=tk.X, pady=(0, 15))

        ttk.Button(exp_frame, text="Export Markdown Report (.md)", command=self._export_markdown).pack(side=tk.LEFT, padx=6)
        ttk.Button(exp_frame, text="Export Standalone HTML Dashboard (.html)", command=self._export_html).pack(side=tk.LEFT, padx=6)

        # Email Dispatch Box
        email_frame = ttk.LabelFrame(container, text="Nikhil's Automated SMTP Report Dispatcher", padding=12)
        email_frame.pack(fill=tk.BOTH, expand=True)

        ttk.Label(email_frame, text="Receiver Email Address:").pack(anchor=tk.W, pady=(4, 2))
        self.email_target_entry = ttk.Entry(email_frame, width=45)
        self.email_target_entry.pack(anchor=tk.W, pady=(0, 10))

        ttk.Button(email_frame, text="Dispatch Executive Summary Email", command=self._dispatch_email, style="Accent.TButton").pack(anchor=tk.W)

        self.lbl_email_status = ttk.Label(email_frame, text="", font=("Segoe UI", 9, "italic"))
        self.lbl_email_status.pack(anchor=tk.W, pady=8)
    
    # Method 21: _export_markdown (Internal)
    def _export_markdown(self) -> None:
        fpath = filedialog.asksaveasfilename(defaultextension=".md", filetypes=[("Markdown files", "*.md")])
        
        if fpath:
            user = self.auth.get_session_info()["username"] or "ANON"
            self.engine.export_markdown_report(fpath, user)
            messagebox.showinfo("Export Successful", f"Markdown summary written to {fpath}")
    
    # Method 22: _export_html (Internal)
    def _export_html(self) -> None:
        fpath = filedialog.asksaveasfilename(defaultextension=".html", filetypes=[("HTML files", "*.html")])
        
        if fpath:
            user = self.auth.get_session_info()["username"] or "ANON"
            self.engine.export_html_dashboard(fpath, user)
            messagebox.showinfo("Export Successful", f"HTML dashboard written to {fpath}")
    
    # Method 23: _dispatch_email (Internal)
    def _dispatch_email(self) -> None:
        target = self.email_target_entry.get().strip()
        
        if not target:
            messagebox.showerror("Error", "Please provide a recipient email address.")
            return

        summary = self.engine.calculate_category_summary()
        total_rev = sum(d["total_revenue"] for d in summary.values())

        subject = "RetailPulse Automated Executive Analytical Briefing"
        text_body = f"""RetailPulse Automated Sales Briefing
=========================================
Active Records Analyzed: {len(self.engine.current_dataset):,}
Aggregated Active Revenue: INR {total_rev:,.2f}
Total Categories Tracked: {len(summary)}

Report dispatched from RetailPulse Sales Data Analyzer.
"""
        
        success, msg = self.email_dispatcher.send_report(target, subject, text_body)
        user = self.auth.get_session_info()["username"] or "ANON"

        if success:
            self.engine.append_audit_entry(user, "EMAIL_DISPATCH", f"Dispatched report to {target}")
            self.lbl_email_status.config(text=msg, foreground="green")
            messagebox.showinfo("Email Dispatched", msg)
        else:
            self.engine.append_audit_entry(user, "EMAIL_FAILED", f"Failed dispatch to {target}: {msg}")
            self.lbl_email_status.config(text=msg, foreground="red")
            messagebox.showerror("Email Error", msg)