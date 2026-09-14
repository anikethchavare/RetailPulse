# RetailPulse (Enterprise Sales Data Analyzer) - analytics_engine.py

# Imports
import re
import csv
import math
import hashlib
from datetime import datetime
from typing import List, Dict, Tuple, Set, Any

# Class 1: AuditBlock
class AuditBlock:
    """ Represents an immutable, cryptographically chained audit record. """
    
    # Constructor: __init__
    def __init__(self, index: int, user: str, action: str, details: str, prev_hash: str) -> None:
        self.index: int = index
        self.timestamp: str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.user: str = user
        self.action: str = action
        self.details: str = details
        self.prev_hash: str = prev_hash
        self.block_hash: str = self.compute_hash()
    
    # Method 1: compute_hash
    def compute_hash(self) -> str:
        payload = f"{self.index}|{self.timestamp}|{self.user}|{self.action}|{self.details}|{self.prev_hash}"
        
        return hashlib.sha256(payload.encode("utf-8")).hexdigest()
    
    # Method 2: to_dict
    def to_dict(self) -> Dict[str, Any]:
        return {
            "index": self.index,
            "timestamp": self.timestamp,
            "user": self.user,
            "action": self.action,
            "details": self.details,
            "block_hash": self.block_hash,
            "prev_hash": self.prev_hash
        }

# Class 2: AnalyticsEngine
class AnalyticsEngine:
    """ In-memory data processing, sanitization, and mathematical modeling engine. """
    
    # Constructor: __init__
    def __init__(self, csv_filepath: str = "amazon.csv") -> None:
        self.csv_filepath = csv_filepath
        self.raw_records: List[Dict[str, Any]] = []
        self.current_dataset: List[Dict[str, Any]] = []

        # Stacks for Analytical Filter Rollback (Undo / Redo)
        self.undo_stack: List[List[Dict[str, Any]]] = []
        self.redo_stack: List[List[Dict[str, Any]]] = []

        # Tamper-Evident Cryptographic Audit Ledger
        self.audit_chain: List[AuditBlock] = []
        self._initialize_audit_ledger()

        # Load and Clean Dataset
        self.load_and_clean_data()

    # Method 1: _initialize_audit_ledger (Internal)
    def _initialize_audit_ledger(self) -> None:
        """ Seed the audit ledger with a genesis block. """
        
        genesis = AuditBlock(
            index=0,
            user="SYSTEM",
            action="GENESIS",
            details="Audit ledger initialized",
            prev_hash="0" * 64
        )
        
        self.audit_chain.append(genesis)
    
    # Method 2: append_audit_entry
    def append_audit_entry(self, user: str, action: str, details: str) -> None:
        """ Appends a new verified transaction block to the audit ledger. """
        
        prev_hash = self.audit_chain[-1].block_hash
        
        new_block = AuditBlock(
            index=len(self.audit_chain),
            user=user,
            action=action,
            details=details,
            prev_hash=prev_hash
        )
        
        self.audit_chain.append(new_block)
    
    # Method 3: verify_audit_ledger
    def verify_audit_ledger(self) -> Tuple[bool, str]:
        """ Cryptographically verifies that no block in the ledger has been tampered with. """
        
        for i in range(1, len(self.audit_chain)):
            current = self.audit_chain[i]
            previous = self.audit_chain[i - 1]

            if current.prev_hash != previous.block_hash:
                return False, f"Broken chain link detected at block #{current.index}"

            if current.block_hash != current.compute_hash():
                return False, f"Data tampering detected inside block #{current.index}"

        return True, "Audit ledger integrity verified. All cryptographic hashes match."
    
    # Method 4: _clean_price (Static & Internal)
    @staticmethod
    def _clean_price(val: str) -> float:
        """ Clean currency strings (e.g., '₹1,099') to floats. """
        
        if not val:
            return 0.0
        
        cleaned = re.sub(r"[^\d.]", "", str(val))
        
        try:
            return float(cleaned) if cleaned else 0.0
        except ValueError:
            return 0.0
    
    # Method 5: _clean_percentage (Static & Internal)
    @staticmethod
    def _clean_percentage(val: str) -> float:
        """ Clean discount percentage strings (e.g., '64%') to float numbers. """
        
        if not val:
            return 0.0
        
        cleaned = str(val).replace("%", "").strip()
        
        try:
            return float(cleaned) if cleaned else 0.0
        except ValueError:
            return 0.0

    # Method 6: _clean_rating (Static & Internal)
    @staticmethod
    def _clean_rating(val: str) -> float:
        """ Clean rating field handling missing or malformed inputs. """
        
        if not val:
            return 0.0
        
        try:
            return float(str(val).strip())
        except ValueError:
            return 0.0

    # Method 7: _mask_pii (Static & Internal)
    @staticmethod
    def _mask_pii(text: str) -> str:
        """ Sanitize sensitive PII names using salt and masked characters. """
        
        if not text:
            return "Anonymous"
        
        parts = [p.strip() for p in text.split(",") if p.strip()]
        masked = []
        
        for name in parts:
            if len(name) <= 2:
                masked.append(name[0] + "*")
            else:
                masked.append(name[:2] + "*" * (len(name) - 2))
                
        return ", ".join(masked)
    
    # Method 8: load_and_clean_data
    def load_and_clean_data(self) -> None:
        """ Load and normalize CSV data into native Python dictionaries. """
        
        self.raw_records.clear()
        
        try:
            with open(self.csv_filepath, mode="r", encoding="utf-8", errors="replace") as f:
                reader = csv.DictReader(f)
                
                for row in reader:
                    disc_price = self._clean_price(row.get("discounted_price", "0"))
                    act_price = self._clean_price(row.get("actual_price", "0"))
                    disc_pct = self._clean_percentage(row.get("discount_percentage", "0"))
                    rating_val = self._clean_rating(row.get("rating", "0"))

                    # Split Category Path Into Primary and Sub-Category
                    raw_cat = row.get("category", "General")
                    cat_parts = [c.strip() for c in raw_cat.split("|") if c.strip()]
                    primary_cat = cat_parts[0] if cat_parts else "General"
                    sub_cat = cat_parts[1] if len(cat_parts) > 1 else primary_cat

                    # Parse User IDs Into Sets for Basket Analysis
                    raw_users = row.get("user_id", "")
                    user_set = tuple(u.strip() for u in raw_users.split(",") if u.strip())

                    record = {
                        "product_id": row.get("product_id", "").strip(),
                        "product_name": row.get("product_name", "").strip(),
                        "category": primary_cat,
                        "sub_category": sub_cat,
                        "discounted_price": disc_price,
                        "actual_price": act_price,
                        "discount_percentage": disc_pct,
                        "rating": rating_val,
                        "rating_count": row.get("rating_count", "0").replace(
                            ",", "").strip(),
                        "masked_users": self._mask_pii(
                            row.get("user_name", "")),
                        "user_ids": user_set
                    }
                    
                    self.raw_records.append(record)

            self.current_dataset = list(self.raw_records)
            self.undo_stack = [list(self.raw_records)]
            self.redo_stack.clear()
            self.append_audit_entry("SYSTEM", "LOAD_DATA", f"Loaded {len(self.raw_records)} records from {self.csv_filepath}")
        except Exception as e:
            self.append_audit_entry("SYSTEM", "LOAD_ERROR", f"Failed reading dataset: {str(e)}")
    
    # Method 9: push_state
    def push_state(self, new_dataset: List[Dict[str, Any]]) -> None:
        """ Pushes a new analytical view state onto the undo stack. """
        
        self.undo_stack.append(list(self.current_dataset))
        self.current_dataset = list(new_dataset)
        self.redo_stack.clear()
    
    # Method 10: undo
    def undo(self, user: str) -> bool:
        """ Rolls back the dataset to the previous analytical state. """
        
        if len(self.undo_stack) > 1:
            prev_state = self.undo_stack.pop()
            self.redo_stack.append(list(self.current_dataset))
            self.current_dataset = prev_state
            self.append_audit_entry(user, "UNDO_STATE", f"Reverted filter step. Active records: {len(self.current_dataset)}")
            
            return True
        
        return False
    
    # Method 11: redo
    def redo(self, user: str) -> bool:
        """ Steps forward into the previously undone analytical state. """
        
        if self.redo_stack:
            next_state = self.redo_stack.pop()
            self.undo_stack.append(list(self.current_dataset))
            self.current_dataset = next_state
            self.append_audit_entry(user, "REDO_STATE", f"Restored filter step. Active records: {len(self.current_dataset)}")
            
            return True
        
        return False
    
    # Method 12: reset_filters
    def reset_filters(self, user: str) -> None:
        """ Resets the dataset to its base untouched state. """
        
        self.push_state(self.raw_records)
        self.append_audit_entry(user, "RESET_DATASET", f"Restored base dataset of {len(self.raw_records)} records")
    
    # Method 13: execute_sql_query
    def execute_sql_query(self, query_str: str, user: str) -> Tuple[List[Dict[str, Any]], str]:
        """ Pure-Python SQL-Like In-Memory Query Tokenizer """
        
        clean_q = query_str.strip()
        
        if not clean_q:
            return self.current_dataset, "Empty query provided."

        if not clean_q.upper().startswith("FILTER"):
            return self.current_dataset, "Syntax Error: Queries must begin with 'FILTER'."

        condition_str = clean_q[6:].strip()
        
        # Split Conditions Joined by AND
        raw_conditions = condition_str.split(" AND ")
        filtered = list(self.current_dataset)

        for cond in raw_conditions:
            cond = cond.strip()
            
            # Match Operator: ==, !=, >=, <=, >, <, CONTAINS
            match = re.search(r"(==|!=|>=|<=|>|<|CONTAINS)", cond, re.IGNORECASE)
            
            if not match:
                return self.current_dataset, f"Syntax Error: No valid operator found in '{cond}'."

            op = match.group(1).upper()
            field_name, target_val = cond.split(match.group(1), 1)
            field_name = field_name.strip().lower()
            target_val = target_val.strip().strip('"').strip("'")
            
            # Nested Function 1 - evaluate_record
            def evaluate_record(rec: Dict[str, Any]) -> bool:
                if field_name not in rec:
                    return False
                
                actual_val = rec[field_name]

                # String Checks
                if isinstance(actual_val, str):
                    t_str = str(target_val).lower()
                    a_str = actual_val.lower()
                    
                    if op == "==":
                        return a_str == t_str
                    elif op == "!=":
                        return a_str != t_str
                    elif op == "CONTAINS":
                        return t_str in a_str
                    
                    return False

                # Numeric Checks
                try:
                    num_target = float(target_val)
                    num_actual = float(actual_val)
                    
                    if op == "==":
                        return num_actual == num_target
                    elif op == "!=":
                        return num_actual != num_target
                    elif op == ">":
                        return num_actual > num_target
                    elif op == "<":
                        return num_actual < num_target
                    elif op == ">=":
                        return num_actual >= num_target
                    elif op == "<=":
                        return num_actual <= num_target
                except ValueError:
                    return False
                
                return False

            filtered = [r for r in filtered if evaluate_record(r)]

        self.push_state(filtered)
        self.append_audit_entry(user, "EXECUTE_QUERY", f"Executed: '{query_str}' -> {len(filtered)} matches")
        
        return filtered, f"Success: Query yielded {len(filtered)} matching records."
    
    # Method 14: calculate_category_summary
    def calculate_category_summary(self) -> Dict[str, Dict[str, Any]]:
        """ Calculates revenue, product counts, and average discounts grouped by category. """
        
        summary: Dict[str, Dict[str, Any]] = {}
        
        for r in self.current_dataset:
            cat = r["category"]
            
            if cat not in summary:
                summary[cat] = {
                    "count": 0,
                    "total_revenue": 0.0,
                    "total_discount": 0.0,
                    "ratings": []
                }
                
            summary[cat]["count"] += 1
            summary[cat]["total_revenue"] += r["discounted_price"]
            summary[cat]["total_discount"] += r["discount_percentage"]
            
            if r["rating"] > 0:
                summary[cat]["ratings"].append(r["rating"])

        # Use Dictionary Comprehension to Compute Aggregates
        return {
            cat: {
                "count": data["count"],
                "total_revenue": round(data["total_revenue"], 2),
                "avg_price": round(data["total_revenue"] / data["count"], 2),
                "avg_discount": round(data["total_discount"] / data["count"], 1),
                "avg_rating": round(sum(data["ratings"]) / len(data["ratings"]), 2) if data["ratings"] else 0.0
            }
            
            for cat, data in summary.items()
        }
    
    # Method 15: detect_pricing_anomalies
    def detect_pricing_anomalies(self, threshold: float = 2.5) -> List[Dict[str, Any]]:
        """
        Pure-Python Statistical Anomaly Detector via Z-Score calculation.
        Computes mean and standard deviation without external libraries.
        """
        
        prices = [r["discounted_price"] for r in self.current_dataset if r["discounted_price"] > 0]
        
        if len(prices) < 5:
            return []

        mean_price = sum(prices) / len(prices)
        variance = sum([(p - mean_price) ** 2 for p in prices]) / len(prices)
        std_dev = math.sqrt(variance)

        if std_dev == 0:
            return []

        anomalies = []
        
        for r in self.current_dataset:
            p = r["discounted_price"]
            z_score = abs(p - mean_price) / std_dev
            
            if z_score >= threshold:
                item = dict(r)
                item["z_score"] = round(z_score, 2)
                item["expected_mean"] = round(mean_price, 2)
                anomalies.append(item)

        return anomalies
    
    # Method 16: calculate_market_basket_affinity
    def calculate_market_basket_affinity(self, min_support: int = 2) -> List[Dict[str, Any]]:
        """
        Market Basket Affinity Engine using native set operations.
        Computes product pairs purchased/reviewed together by user cohorts.
        """
        
        user_baskets: Dict[str, Set[str]] = {}
        
        for r in self.current_dataset:
            p_id = r["product_name"][:30] + "..."
            
            for uid in r["user_ids"]:
                if uid not in user_baskets:
                    user_baskets[uid] = set()
                    
                user_baskets[uid].add(p_id)

        pair_counts: Dict[Tuple[str, str], int] = {}
        
        # Count Co-Occurrences Using Set Combinations
        for basket in user_baskets.values():
            if len(basket) > 1:
                basket_list = sorted(list(basket))
                
                for i in range(len(basket_list)):
                    for j in range(i + 1, len(basket_list)):
                        pair = (basket_list[i], basket_list[j])
                        pair_counts[pair] = pair_counts.get(pair, 0) + 1

        # Filter by Minimum Support and Sort
        affinity_results = [
            {
                "product_a": pair[0],
                "product_b": pair[1],
                "co_occurrence_count": count
            }
            
            for pair, count in pair_counts.items()
            if count >= min_support
        ]
        
        affinity_results.sort(key=lambda x: x["co_occurrence_count"], reverse=True)
        
        return affinity_results[:25]
    
    # Method 17: compute_rfm_segmentation
    def compute_rfm_segmentation(self) -> Dict[str, Dict[str, Any]]:
        """
        RFM Customer Segmentation Engine.
        Classifies buyer cohorts into Champions, Loyalists, At-Risk based on transaction counts & revenue.
        """
        
        user_metrics: Dict[str, Dict[str, Any]] = {}
        
        for r in self.current_dataset:
            price = r["discounted_price"]
            
            for uid in r["user_ids"]:
                if uid not in user_metrics:
                    user_metrics[uid] = {"frequency": 0, "monetary": 0.0}
                    
                user_metrics[uid]["frequency"] += 1
                user_metrics[uid]["monetary"] += price

        segments: Dict[str, Dict[str, Any]] = {
            "Champions": {"count": 0, "total_spend": 0.0},
            "Loyal Customers": {"count": 0, "total_spend": 0.0},
            "Promising": {"count": 0, "total_spend": 0.0},
            "At-Risk / Casual": {"count": 0, "total_spend": 0.0}
        }

        for uid, metrics in user_metrics.items():
            freq = metrics["frequency"]
            mon = metrics["monetary"]

            if freq >= 4 and mon >= 5000:
                seg = "Champions"
            elif freq >= 2:
                seg = "Loyal Customers"
            elif mon >= 2000:
                seg = "Promising"
            else:
                seg = "At-Risk / Casual"

            segments[seg]["count"] += 1
            segments[seg]["total_spend"] += mon

        return {
            k: {
                "count": v["count"],
                "total_spend": round(v["total_spend"], 2),
                "avg_spend": round(v["total_spend"] / v["count"], 2) if v["count"] > 0 else 0.0
            }
            
            for k, v in segments.items()
        }
    
    # Method 18: export_markdown_report
    def export_markdown_report(self, filepath: str, user: str) -> None:
        """ Generates an executive analytical summary in Markdown format. """
        
        summary = self.calculate_category_summary()
        rfm = self.compute_rfm_segmentation()
        total_rev = sum(d["total_revenue"] for d in summary.values())
        total_items = len(self.current_dataset)

        md_content = f"""# RetailPulse Executive Sales Summary
*Generated on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} by user: `{user}`*

## Key Performance Overview
- **Active Filtered Inventory:** {total_items:,} items
- **Aggregated Revenue:** ₹{total_rev:,.2f}
- **Active Categories Analyzed:** {len(summary)}

## Category Breakdown
| Category | Item Count | Total Sales (₹) | Avg Discount (%) | Avg Rating |
| :--- | :--- | :--- | :--- | :--- |
"""
        
        for cat, data in summary.items():
            md_content += f"| {cat} | {data['count']} | ₹{data['total_revenue']:,.2f} | {data['avg_discount']}% | {data['avg_rating']}★ |\n"

        md_content += "\n## Customer RFM Behavioral Cohorts\n"
        md_content += "| Segment | Unique Customers | Total Spend (₹) | Avg Spend / User (₹) |\n| :--- | :--- | :--- | :--- |\n"
        
        for seg, data in rfm.items():
            md_content += f"| {seg} | {data['count']} | ₹{data['total_spend']:,.2f} | ₹{data['avg_spend']:,.2f} |\n"

        with open(filepath, "w", encoding="utf-8") as f:
            f.write(md_content)

        self.append_audit_entry(user, "EXPORT_MARKDOWN", f"Exported analytical report to {filepath}")
    
    # Method 19: export_html_dashboard
    def export_html_dashboard(self, filepath: str, user: str) -> None:
        """ Generates an executive dashboard in standalone HTML/CSS format. """
        
        summary = self.calculate_category_summary()
        rfm = self.compute_rfm_segmentation()
        total_rev = sum(d["total_revenue"] for d in summary.values())

        html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>RetailPulse Executive Dashboard</title>
    <style>
        body {{ font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif; margin: 30px; background: #0f172a; color: #f8fafc; }}
        h1, h2 {{ color: #38bdf8; }}
        .metric-cards {{ display: flex; gap: 20px; margin-bottom: 25px; }}
        .card {{ background: #1e293b; padding: 20px; border-radius: 8px; border: 1px solid #334155; flex: 1; }}
        .card h3 {{ margin: 0 0 10px 0; color: #94a3b8; font-size: 14px; text-transform: uppercase; }}
        .card p {{ margin: 0; font-size: 24px; font-weight: bold; color: #f1f5f9; }}
        table {{ width: 100%; border-collapse: collapse; margin-top: 15px; background: #1e293b; border-radius: 8px; overflow: hidden; }}
        th, td {{ padding: 12px 16px; text-align: left; border-bottom: 1px solid #334155; }}
        th {{ background: #0284c7; color: #ffffff; font-weight: 600; }}
        tr:hover {{ background: #334155; }}
        .badge {{ padding: 4px 8px; border-radius: 4px; background: #0369a1; font-size: 12px; }}
    </style>
</head>
<body>
    <h1>RetailPulse Executive Analytics Dashboard</h1>
    <p>Report dispatched on <strong>{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</strong> | Generated by: <span class="badge">{user}</span></p>

    <div class="metric-cards">
        <div class="card"><h3>Total Revenue</h3><p>₹{total_rev:,.2f}</p></div>
        <div class="card"><h3>Filtered Records</h3><p>{len(self.current_dataset):,}</p></div>
        <div class="card"><h3>Tracked Categories</h3><p>{len(summary)}</p></div>
    </div>

    <h2>Category Performance Breakdown</h2>
    <table>
        <thead><tr><th>Category</th><th>Products</th><th>Revenue (₹)</th><th>Avg Discount</th><th>Avg Rating</th></tr></thead>
        <tbody>
"""
        
        for cat, data in summary.items():
            html += f"<tr><td>{cat}</td><td>{data['count']}</td><td>₹{data['total_revenue']:,.2f}</td><td>{data['avg_discount']}%</td><td>{data['avg_rating']} ★</td></tr>\n"

        html += """</tbody>
    </table>

    <h2>Customer RFM Segments</h2>
    <table>
        <thead><tr><th>Segment Cohort</th><th>Customer Count</th><th>Total Spend (₹)</th><th>Avg Spend / Customer (₹)</th></tr></thead>
        <tbody>
"""
        
        for seg, data in rfm.items():
            html += f"<tr><td>{seg}</td><td>{data['count']}</td><td>₹{data['total_spend']:,.2f}</td><td>₹{data['avg_spend']:,.2f}</td></tr>\n"

        html += """</tbody>
    </table>
</body>
</html>
"""
        
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(html)

        self.append_audit_entry(user, "EXPORT_HTML", f"Exported HTML dashboard to {filepath}")