"""
住宅決策分析儀 GUI
買房 vs 租屋投資 — 圖形化介面
使用 tkinter 搭配現代化深色主題設計 + matplotlib 折線圖
"""

import tkinter as tk
from tkinter import ttk, messagebox
import math
import sys
import os

# matplotlib for embedding charts in tkinter
import matplotlib
matplotlib.use('TkAgg')
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.ticker import FuncFormatter
import matplotlib.font_manager as fm
import numpy as np

# Import the core calculation engine
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from calculator import calculate_investment


# ─────────────────────────────────────────────
# Design Tokens / Theme
# ─────────────────────────────────────────────
COLORS = {
    "bg_primary":       "#0f1117",
    "bg_secondary":     "#1a1c25",
    "bg_card":          "#21232d",
    "bg_input":         "#2a2d3a",
    "bg_input_focus":   "#333750",
    "border":           "#3a3d4e",
    "border_accent":    "#5b5fef",
    "text_primary":     "#e8e9f0",
    "text_secondary":   "#9598a8",
    "text_muted":       "#6b6e80",
    "accent_blue":      "#6366f1",
    "accent_blue_hover":"#818cf8",
    "accent_green":     "#22c55e",
    "accent_green_bg":  "#0a3622",
    "accent_red":       "#ef4444",
    "accent_red_bg":    "#3b1111",
    "accent_amber":     "#f59e0b",
    "accent_amber_bg":  "#3b2a06",
    "accent_cyan":      "#06b6d4",
    "gradient_start":   "#6366f1",
    "gradient_end":     "#8b5cf6",
    "buy_color":        "#f59e0b",     # amber for buy
    "rent_color":       "#06b6d4",     # cyan for rent
    "win_color":        "#22c55e",
    "separator":        "#2e3040",
    "chart_bg":         "#181a24",
    "chart_grid":       "#2e3040",
    "mortgage_line":    "#f59e0b",
    "rent_line":        "#06b6d4",
    "buy_area":         "#f59e0b",
    "rent_area":        "#06b6d4",
}

FONT_FAMILY = "Microsoft JhengHei UI"  # 微軟正黑體（Windows 中文）
FONT_FAMILY_MONO = "Consolas"
FALLBACK_FONT = "Arial"

# ─── Matplotlib font config for Chinese ───
plt.rcParams['font.sans-serif'] = ['Microsoft JhengHei', 'Microsoft JhengHei UI', 'SimHei', 'Arial']
plt.rcParams['axes.unicode_minus'] = False


# ─────────────────────────────────────────────
# Helper: Format Numbers
# ─────────────────────────────────────────────
def fmt(num):
    """Format number with comma separator."""
    return f"{num:,.0f}"

def fmt_pct(num):
    """Format as percentage."""
    return f"{num * 100:.2f}%"

def fmt_wan(x, pos):
    """Format axis ticks in 萬 (10k) units."""
    return f'{x/10000:.0f}萬'

def fmt_yi(x, pos):
    """Format axis ticks: use 億 if >= 1億, else 萬."""
    if abs(x) >= 1e8:
        return f'{x/1e8:.1f}億'
    else:
        return f'{x/10000:.0f}萬'


# ─────────────────────────────────────────────
# Custom Widgets
# ─────────────────────────────────────────────
class GradientFrame(tk.Canvas):
    """A frame-like canvas widget that draws a horizontal gradient background."""

    def __init__(self, parent, color1, color2, height=4, **kwargs):
        super().__init__(parent, height=height, highlightthickness=0, **kwargs)
        self.color1 = color1
        self.color2 = color2
        self.bind("<Configure>", self._draw_gradient)

    def _draw_gradient(self, event=None):
        self.delete("gradient")
        width = self.winfo_width()
        height = self.winfo_height()
        limit = width
        r1, g1, b1 = self.winfo_rgb(self.color1)
        r2, g2, b2 = self.winfo_rgb(self.color2)
        r_ratio = (r2 - r1) / max(limit, 1)
        g_ratio = (g2 - g1) / max(limit, 1)
        b_ratio = (b2 - b1) / max(limit, 1)

        for i in range(limit):
            nr = int(r1 + (r_ratio * i))
            ng = int(g1 + (g_ratio * i))
            nb = int(b1 + (b_ratio * i))
            color = f"#{nr >> 8:02x}{ng >> 8:02x}{nb >> 8:02x}"
            self.create_line(i, 0, i, height, tags=("gradient",), fill=color)


class HoverButton(tk.Canvas):
    """A custom button with hover animation and rounded corners."""

    def __init__(self, parent, text, command=None, width=200, height=44,
                 bg=COLORS["accent_blue"], hover_bg=COLORS["accent_blue_hover"],
                 fg="#ffffff", font_size=12, corner_radius=10, **kwargs):
        super().__init__(parent, width=width, height=height,
                         bg=parent["bg"] if isinstance(parent, (tk.Frame, tk.Canvas)) else COLORS["bg_primary"],
                         highlightthickness=0, **kwargs)
        self.command = command
        self.bg_color = bg
        self.hover_color = hover_bg
        self.fg_color = fg
        self.corner_radius = corner_radius
        self.btn_width = width
        self.btn_height = height
        self.text = text
        self.font_size = font_size
        self._current_bg = bg
        self._draw()

        self.bind("<Enter>", self._on_enter)
        self.bind("<Leave>", self._on_leave)
        self.bind("<ButtonPress-1>", self._on_press)
        self.bind("<ButtonRelease-1>", self._on_release)

    def _draw(self):
        self.delete("all")
        r = self.corner_radius
        w, h = self.btn_width, self.btn_height
        # Rounded rectangle
        self.create_arc(0, 0, 2*r, 2*r, start=90, extent=90, fill=self._current_bg, outline="")
        self.create_arc(w-2*r, 0, w, 2*r, start=0, extent=90, fill=self._current_bg, outline="")
        self.create_arc(0, h-2*r, 2*r, h, start=180, extent=90, fill=self._current_bg, outline="")
        self.create_arc(w-2*r, h-2*r, w, h, start=270, extent=90, fill=self._current_bg, outline="")
        self.create_rectangle(r, 0, w-r, h, fill=self._current_bg, outline="")
        self.create_rectangle(0, r, w, h-r, fill=self._current_bg, outline="")
        # Text
        self.create_text(w//2, h//2, text=self.text, fill=self.fg_color,
                         font=(FONT_FAMILY, self.font_size, "bold"))

    def _on_enter(self, e):
        self._current_bg = self.hover_color
        self._draw()
        self.config(cursor="hand2")

    def _on_leave(self, e):
        self._current_bg = self.bg_color
        self._draw()
        self.config(cursor="")

    def _on_press(self, e):
        self._current_bg = self.bg_color
        self._draw()

    def _on_release(self, e):
        self._current_bg = self.hover_color
        self._draw()
        if self.command:
            self.command()


class ModernEntry(tk.Frame):
    """A styled entry widget with label and optional suffix."""

    def __init__(self, parent, label, default_value="", suffix="",
                 tooltip="", width=18, **kwargs):
        super().__init__(parent, bg=COLORS["bg_card"], **kwargs)
        self.label_text = label
        self.suffix_text = suffix

        # Label
        lbl = tk.Label(self, text=label, fg=COLORS["text_secondary"],
                        bg=COLORS["bg_card"],
                        font=(FONT_FAMILY, 10), anchor="w")
        lbl.pack(anchor="w", padx=2, pady=(0, 3))

        # Entry row
        entry_frame = tk.Frame(self, bg=COLORS["bg_input"],
                                highlightbackground=COLORS["border"],
                                highlightthickness=1, highlightcolor=COLORS["border_accent"])
        entry_frame.pack(fill="x", padx=2)

        self.entry = tk.Entry(entry_frame, bg=COLORS["bg_input"],
                               fg=COLORS["text_primary"], insertbackground=COLORS["text_primary"],
                               font=(FONT_FAMILY_MONO, 11), border=0, width=width,
                               relief="flat")
        # Initial format and event binding
        self.set(default_value)
        self.entry.pack(side="left", padx=8, pady=6, fill="x", expand=True)
        self.entry.bind("<FocusOut>", self._format_with_commas)

        if suffix:
            sfx = tk.Label(entry_frame, text=suffix, fg=COLORS["text_muted"],
                            bg=COLORS["bg_input"], font=(FONT_FAMILY, 9))
            sfx.pack(side="right", padx=8)

        # Tooltip
        if tooltip:
            tip = tk.Label(self, text=tooltip, fg=COLORS["text_muted"],
                            bg=COLORS["bg_card"], font=(FONT_FAMILY, 8),
                            anchor="w")
            tip.pack(anchor="w", padx=2, pady=(2, 0))

    def _format_with_commas(self, event=None):
        """Format the entry text with commas when focus is lost."""
        val = self.entry.get().replace(",", "")
        try:
            if val:
                float_val = float(val)
                if float_val == int(float_val):
                    formatted = f"{int(float_val):,}"
                else:
                    formatted = f"{float_val:,}"
                self.entry.delete(0, tk.END)
                self.entry.insert(0, formatted)
        except ValueError:
            pass

    def get(self):
        """Return value as a raw string without commas."""
        return self.entry.get().replace(",", "")

    def set(self, value):
        """Set value and format it with commas."""
        self.entry.delete(0, tk.END)
        try:
            num = float(str(value).replace(",", ""))
            if num == int(num):
                formatted = f"{int(num):,}"
            else:
                formatted = f"{num:,}"
            self.entry.insert(0, formatted)
        except ValueError:
            self.entry.insert(0, str(value))


class ModernCheckbox(tk.Frame):
    """A styled checkbox widget."""

    def __init__(self, parent, label, default=True, **kwargs):
        super().__init__(parent, bg=COLORS["bg_card"], **kwargs)
        self.var = tk.BooleanVar(value=default)

        self.cb = tk.Checkbutton(
            self, text=label, variable=self.var,
            bg=COLORS["bg_card"], fg=COLORS["text_secondary"],
            selectcolor=COLORS["bg_input"],
            activebackground=COLORS["bg_card"],
            activeforeground=COLORS["text_primary"],
            font=(FONT_FAMILY, 10),
            anchor="w"
        )
        self.cb.pack(anchor="w", padx=2, pady=4)

    def get(self):
        return self.var.get()


# ─────────────────────────────────────────────
# Result Card Widget
# ─────────────────────────────────────────────
class ResultCard(tk.Frame):
    """A card widget for displaying grouped results."""

    def __init__(self, parent, title, icon, accent_color, **kwargs):
        super().__init__(parent, bg=COLORS["bg_card"],
                         highlightbackground=COLORS["border"],
                         highlightthickness=1, highlightcolor=accent_color,
                         **kwargs)
        self.accent_color = accent_color
        self.rows = []

        # Header
        header = tk.Frame(self, bg=COLORS["bg_card"])
        header.pack(fill="x", padx=16, pady=(14, 8))

        tk.Label(header, text=icon, font=(FONT_FAMILY, 16),
                 bg=COLORS["bg_card"], fg=accent_color).pack(side="left")
        tk.Label(header, text=f"  {title}", font=(FONT_FAMILY, 13, "bold"),
                 bg=COLORS["bg_card"], fg=COLORS["text_primary"]).pack(side="left")

        # Separator
        sep = tk.Frame(self, bg=COLORS["separator"], height=1)
        sep.pack(fill="x", padx=16, pady=(0, 8))

        # Content area
        self.content = tk.Frame(self, bg=COLORS["bg_card"])
        self.content.pack(fill="x", padx=16, pady=(0, 14))

    def add_row(self, label, value, highlight=False, large=False):
        row = tk.Frame(self.content, bg=COLORS["bg_card"])
        row.pack(fill="x", pady=3)

        fg_label = COLORS["text_secondary"]
        fg_value = COLORS["text_primary"]
        font_size_label = 10
        font_size_value = 11

        if highlight:
            fg_label = self.accent_color
            fg_value = self.accent_color
            font_size_label = 11
            font_size_value = 13

        if large:
            font_size_value = 16

        tk.Label(row, text=label, fg=fg_label, bg=COLORS["bg_card"],
                 font=(FONT_FAMILY, font_size_label), anchor="w").pack(side="left")
        tk.Label(row, text=value, fg=fg_value, bg=COLORS["bg_card"],
                 font=(FONT_FAMILY_MONO, font_size_value, "bold" if highlight else ""),
                 anchor="e").pack(side="right")

    def clear(self):
        for child in self.content.winfo_children():
            child.destroy()


# ─────────────────────────────────────────────
# Bar Chart Widget (Pure tkinter Canvas)
# ─────────────────────────────────────────────
class ComparisonBar(tk.Canvas):
    """Visual bar chart comparing buy vs rent."""

    def __init__(self, parent, width=400, height=120, **kwargs):
        super().__init__(parent, width=width, height=height,
                         bg=COLORS["bg_card"], highlightthickness=0, **kwargs)
        self.chart_width = width
        self.chart_height = height

    def update_chart(self, buy_value, rent_value):
        self.delete("all")
        max_val = max(abs(buy_value), abs(rent_value), 1)
        bar_max_width = self.chart_width - 160
        padding_left = 100
        bar_height = 28
        gap = 16

        # Buy bar
        buy_w = int((buy_value / max_val) * bar_max_width)
        buy_y = 20
        self.create_text(padding_left - 10, buy_y + bar_height // 2,
                         text="買房", anchor="e",
                         fill=COLORS["buy_color"],
                         font=(FONT_FAMILY, 11, "bold"))
        self._draw_rounded_bar(padding_left, buy_y, buy_w, bar_height,
                                COLORS["buy_color"], "#fbbf24")
        self.create_text(padding_left + buy_w + 10, buy_y + bar_height // 2,
                         text=f"{fmt(buy_value)} 元", anchor="w",
                         fill=COLORS["text_secondary"],
                         font=(FONT_FAMILY_MONO, 10))

        # Rent bar
        rent_w = int((rent_value / max_val) * bar_max_width)
        rent_y = buy_y + bar_height + gap
        self.create_text(padding_left - 10, rent_y + bar_height // 2,
                         text="租屋投資", anchor="e",
                         fill=COLORS["rent_color"],
                         font=(FONT_FAMILY, 11, "bold"))
        self._draw_rounded_bar(padding_left, rent_y, rent_w, bar_height,
                                COLORS["rent_color"], "#22d3ee")
        self.create_text(padding_left + rent_w + 10, rent_y + bar_height // 2,
                         text=f"{fmt(rent_value)} 元", anchor="w",
                         fill=COLORS["text_secondary"],
                         font=(FONT_FAMILY_MONO, 10))

    def _draw_rounded_bar(self, x, y, w, h, color1, color2):
        if w < 1:
            w = 1
        r = min(h // 2, 8)
        self.create_arc(x, y, x + 2*r, y + 2*r, start=90, extent=90,
                        fill=color1, outline="")
        self.create_arc(x, y + h - 2*r, x + 2*r, y + h, start=180, extent=90,
                        fill=color1, outline="")
        self.create_rectangle(x + r, y, x + w, y + h, fill=color1, outline="")
        self.create_rectangle(x, y + r, x + r, y + h - r, fill=color1, outline="")
        if w > 2*r:
            self.create_arc(x + w - 2*r, y, x + w, y + 2*r, start=0, extent=90,
                            fill=color2, outline="")
            self.create_arc(x + w - 2*r, y + h - 2*r, x + w, y + h, start=270, extent=90,
                            fill=color2, outline="")
            grad_start = max(x + r, x + w - 60)
            self.create_rectangle(grad_start, y, x + w - r, y + h, fill=color2, outline="")
            self.create_rectangle(x + w - r, y + r, x + w, y + h - r, fill=color2, outline="")


# ─────────────────────────────────────────────
# Main Application Window
# ─────────────────────────────────────────────
class CalculatorApp(tk.Tk):
    """Main application window."""

    def __init__(self):
        super().__init__()
        self.title("住宅決策分析儀 — 買房 vs 租屋投資")
        self.configure(bg=COLORS["bg_primary"])
        self.geometry("1060x900")
        self.minsize(1000, 800)

        # Track embedded matplotlib figures for cleanup
        self._chart_canvases = []

        try:
            self.iconbitmap(default="")
        except Exception:
            pass

        self._build_ui()
        self._center_window()

    def _center_window(self):
        self.update_idletasks()
        w = self.winfo_width()
        h = self.winfo_height()
        x = (self.winfo_screenwidth() // 2) - (w // 2)
        y = (self.winfo_screenheight() // 2) - (h // 2)
        self.geometry(f"+{x}+{y}")

    def _build_ui(self):
        # ── Main Scrollable Container ──
        outer = tk.Frame(self, bg=COLORS["bg_primary"])
        outer.pack(fill="both", expand=True)

        self.main_canvas = tk.Canvas(outer, bg=COLORS["bg_primary"], highlightthickness=0)
        scrollbar = ttk.Scrollbar(outer, orient="vertical", command=self.main_canvas.yview)

        self.scroll_frame = tk.Frame(self.main_canvas, bg=COLORS["bg_primary"])
        self.scroll_frame.bind(
            "<Configure>",
            lambda e: self.main_canvas.configure(scrollregion=self.main_canvas.bbox("all"))
        )

        self.main_canvas.create_window((0, 0), window=self.scroll_frame, anchor="nw")
        self.main_canvas.configure(yscrollcommand=scrollbar.set)

        scrollbar.pack(side="right", fill="y")
        self.main_canvas.pack(side="left", fill="both", expand=True)

        # Mouse wheel scroll
        def _on_mousewheel(event):
            self.main_canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

        self.main_canvas.bind_all("<MouseWheel>", _on_mousewheel)

        # ── Content Container (centered) ──
        container = tk.Frame(self.scroll_frame, bg=COLORS["bg_primary"])
        container.pack(fill="x", expand=True, padx=30, pady=10)

        # ── Title Bar ──
        title_frame = tk.Frame(container, bg=COLORS["bg_primary"])
        title_frame.pack(fill="x", pady=(10, 0))

        tk.Label(title_frame, text="🏠",
                 font=(FONT_FAMILY, 28),
                 bg=COLORS["bg_primary"], fg=COLORS["accent_blue"]).pack(side="left")

        title_text_frame = tk.Frame(title_frame, bg=COLORS["bg_primary"])
        title_text_frame.pack(side="left", padx=(12, 0))

        tk.Label(title_text_frame, text="住宅決策分析儀",
                 font=(FONT_FAMILY, 22, "bold"),
                 bg=COLORS["bg_primary"], fg=COLORS["text_primary"]).pack(anchor="w")
        tk.Label(title_text_frame, text="買房 vs 租屋投資 ─ 智慧決策試算",
                 font=(FONT_FAMILY, 10),
                 bg=COLORS["bg_primary"], fg=COLORS["text_secondary"]).pack(anchor="w")

        # ── Gradient Separator ──
        gradient = GradientFrame(container, COLORS["gradient_start"],
                                  COLORS["gradient_end"], height=3)
        gradient.pack(fill="x", pady=(12, 16))

        # ── Input Section ──
        input_section = tk.Frame(container, bg=COLORS["bg_card"],
                                  highlightbackground=COLORS["border"],
                                  highlightthickness=1)
        input_section.pack(fill="x", pady=(0, 12))

        # Section Header
        input_header = tk.Frame(input_section, bg=COLORS["bg_card"])
        input_header.pack(fill="x", padx=20, pady=(14, 8))
        tk.Label(input_header, text="⚙️  參數設定",
                 font=(FONT_FAMILY, 14, "bold"),
                 bg=COLORS["bg_card"], fg=COLORS["text_primary"]).pack(side="left")

        sep = tk.Frame(input_section, bg=COLORS["separator"], height=1)
        sep.pack(fill="x", padx=20)

        # ── Input Grid ──
        grid_frame = tk.Frame(input_section, bg=COLORS["bg_card"])
        grid_frame.pack(fill="x", padx=20, pady=(10, 0))

        # Row 1: Loan & Down Payment
        row1 = tk.Frame(grid_frame, bg=COLORS["bg_card"])
        row1.pack(fill="x", pady=4)

        self.inp_loan = ModernEntry(row1, "房貸金額", "6000000", "元",
                                     tooltip="向銀行貸款的總金額")
        self.inp_loan.pack(side="left", fill="x", expand=True, padx=(0, 8))

        self.inp_down = ModernEntry(row1, "頭期款", "6000000", "元",
                                     tooltip="自備款 (需大於或等於貸款金額)")
        self.inp_down.pack(side="left", fill="x", expand=True, padx=(0, 8))

        self.inp_years = ModernEntry(row1, "貸款年限", "30", "年")
        self.inp_years.pack(side="left", fill="x", expand=True)

        # Row 2: Rates
        row2 = tk.Frame(grid_frame, bg=COLORS["bg_card"])
        row2.pack(fill="x", pady=4)

        self.inp_rate = ModernEntry(row2, "房貸年利率", "2.5", "%",
                                     tooltip="例如：2.5 代表 2.5%")
        self.inp_rate.pack(side="left", fill="x", expand=True, padx=(0, 8))

        self.inp_house_growth = ModernEntry(row2, "房價年成長率", "5.0", "%",
                                             tooltip="房屋每年預期漲幅")
        self.inp_house_growth.pack(side="left", fill="x", expand=True, padx=(0, 8))

        self.inp_grace = ModernEntry(row2, "寬限期", "0", "年",
                                      tooltip="寬限期內僅繳利息，不還本金")
        self.inp_grace.pack(side="left", fill="x", expand=True)

        # Row 3: Rent & Stock
        row3 = tk.Frame(grid_frame, bg=COLORS["bg_card"])
        row3.pack(fill="x", pady=4)

        self.inp_rent = ModernEntry(row3, "初始月租金", "27000", "元/月")
        self.inp_rent.pack(side="left", fill="x", expand=True, padx=(0, 8))

        self.inp_rent_growth = ModernEntry(row3, "租金年成長率", "2.0", "%",
                                            tooltip="租金每年調漲幅度")
        self.inp_rent_growth.pack(side="left", fill="x", expand=True, padx=(0, 8))

        self.inp_stock = ModernEntry(row3, "股市年化報酬率", "10.0", "%",
                                      tooltip="長期年化報酬率 (含息 S&P 500 ≈ 10%)")
        self.inp_stock.pack(side="left", fill="x", expand=True)

        # Row 4: Checkbox
        row4 = tk.Frame(grid_frame, bg=COLORS["bg_card"])
        row4.pack(fill="x", pady=(4, 8))

        self.inp_invest_diff = ModernCheckbox(row4, "將 (月供 - 月租) 差額投入股市",
                                               default=True)
        self.inp_invest_diff.pack(side="left")

        # ── Action Button ──
        btn_frame = tk.Frame(input_section, bg=COLORS["bg_card"])
        btn_frame.pack(fill="x", padx=20, pady=(4, 18))

        self.calc_btn = HoverButton(btn_frame, text="▶  開始分析", command=self._run_calc,
                                     width=220, height=46, font_size=13,
                                     bg=COLORS["accent_blue"],
                                     hover_bg=COLORS["accent_blue_hover"])
        self.calc_btn.pack(side="left")

        # Reset button
        self.reset_btn = HoverButton(btn_frame, text="↻  重設預設",
                                      command=self._reset_defaults,
                                      width=140, height=46, font_size=11,
                                      bg=COLORS["bg_input"],
                                      hover_bg=COLORS["border"])
        self.reset_btn.pack(side="left", padx=(12, 0))

        # ── Results Section (hidden until calculated) ──
        self.results_frame = tk.Frame(container, bg=COLORS["bg_primary"])
        self.results_frame.pack(fill="x")

    def _reset_defaults(self):
        """Reset all inputs to default values."""
        defaults = {
            self.inp_loan: "6,000,000",
            self.inp_down: "6,000,000",
            self.inp_years: "30",
            self.inp_rate: "2.5",
            self.inp_house_growth: "5.0",
            self.inp_grace: "0",
            self.inp_rent: "27,000",
            self.inp_rent_growth: "2.0",
            self.inp_stock: "10.0",
        }
        for widget, val in defaults.items():
            widget.set(val)
        self.inp_invest_diff.var.set(True)

    def _run_calc(self):
        """Parse inputs and run the calculation."""
        try:
            loan_amount = float(self.inp_loan.get().replace(",", ""))
            down_payment = float(self.inp_down.get().replace(",", ""))
            mortgage_years = int(float(self.inp_years.get()))
            mortgage_rate = float(self.inp_rate.get()) / 100.0
            house_growth = float(self.inp_house_growth.get()) / 100.0
            grace_period = float(self.inp_grace.get())
            rent_initial = float(self.inp_rent.get().replace(",", ""))
            rent_growth = float(self.inp_rent_growth.get()) / 100.0
            stock_return = float(self.inp_stock.get()) / 100.0
            invest_diff = self.inp_invest_diff.get()
        except ValueError as e:
            messagebox.showerror("輸入錯誤", f"請確認所有欄位都填入有效的數字。\n\n{e}")
            return

        try:
            result = calculate_investment(
                loan_amount=loan_amount,
                down_payment=down_payment,
                mortgage_rate=mortgage_rate,
                rent_initial=rent_initial,
                rent_growth_rate=rent_growth,
                house_growth_rate=house_growth,
                stock_return_rate=stock_return,
                grace_period_years=grace_period,
                invest_difference=invest_diff,
                mortgage_years=mortgage_years
            )
        except AssertionError as e:
            messagebox.showerror("參數驗證失敗", str(e))
            return
        except Exception as e:
            messagebox.showerror("計算錯誤", f"計算過程中發生錯誤：\n\n{e}")
            return

        self._display_results(result)

    def _cleanup_charts(self):
        """Close all previous matplotlib figures to prevent memory leaks."""
        for canvas_widget in self._chart_canvases:
            try:
                fig = canvas_widget.figure
                plt.close(fig)
            except Exception:
                pass
        self._chart_canvases.clear()

    def _create_dark_chart(self, figsize=(9.5, 3.5)):
        """Create a matplotlib figure with dark theme styling."""
        fig, ax = plt.subplots(figsize=figsize, facecolor=COLORS["chart_bg"])
        ax.set_facecolor(COLORS["chart_bg"])
        ax.tick_params(colors=COLORS["text_secondary"], labelsize=9)
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        ax.spines['bottom'].set_color(COLORS["chart_grid"])
        ax.spines['left'].set_color(COLORS["chart_grid"])
        ax.grid(True, alpha=0.15, color=COLORS["text_muted"], linestyle='--')
        ax.xaxis.label.set_color(COLORS["text_secondary"])
        ax.yaxis.label.set_color(COLORS["text_secondary"])
        ax.title.set_color(COLORS["text_primary"])
        return fig, ax

    def _embed_chart(self, fig, parent_frame):
        """Embed a matplotlib figure into a tkinter frame."""
        canvas_widget = FigureCanvasTkAgg(fig, master=parent_frame)
        canvas_widget.draw()
        widget = canvas_widget.get_tk_widget()
        widget.configure(highlightthickness=0, borderwidth=0)
        widget.pack(fill="x", padx=16, pady=(8, 14))
        self._chart_canvases.append(canvas_widget)
        return canvas_widget

    def _display_results(self, res):
        """Build and display the results dashboard."""
        # Cleanup previous charts
        self._cleanup_charts()

        # Clear previous results
        for child in self.results_frame.winfo_children():
            child.destroy()

        # ── Gradient Separator ──
        gradient2 = GradientFrame(self.results_frame, COLORS["gradient_end"],
                                   COLORS["gradient_start"], height=3)
        gradient2.pack(fill="x", pady=(8, 16))

        # ── Monthly Payment Info ──
        monthly_card = tk.Frame(self.results_frame, bg=COLORS["bg_card"],
                                 highlightbackground=COLORS["border"],
                                 highlightthickness=1)
        monthly_card.pack(fill="x", pady=(0, 12))

        monthly_header = tk.Frame(monthly_card, bg=COLORS["bg_card"])
        monthly_header.pack(fill="x", padx=16, pady=(12, 6))
        tk.Label(monthly_header, text="💳  每月還款資訊",
                 font=(FONT_FAMILY, 13, "bold"),
                 bg=COLORS["bg_card"], fg=COLORS["text_primary"]).pack(side="left")

        monthly_sep = tk.Frame(monthly_card, bg=COLORS["separator"], height=1)
        monthly_sep.pack(fill="x", padx=16)

        monthly_content = tk.Frame(monthly_card, bg=COLORS["bg_card"])
        monthly_content.pack(fill="x", padx=20, pady=(8, 14))

        if res["grace_period_years"] > 0:
            pay_row1 = tk.Frame(monthly_content, bg=COLORS["bg_card"])
            pay_row1.pack(fill="x", pady=2)
            tk.Label(pay_row1, text=f"寬限期月付 (僅利息) — 第 1~{res['grace_months']} 月",
                     fg=COLORS["text_secondary"], bg=COLORS["bg_card"],
                     font=(FONT_FAMILY, 10)).pack(side="left")
            tk.Label(pay_row1, text=f"{fmt(res['grace_monthly_pay'])} 元",
                     fg=COLORS["accent_amber"], bg=COLORS["bg_card"],
                     font=(FONT_FAMILY_MONO, 13, "bold")).pack(side="right")

            pay_row2 = tk.Frame(monthly_content, bg=COLORS["bg_card"])
            pay_row2.pack(fill="x", pady=2)
            tk.Label(pay_row2, text=f"寬限期後月付 (本息均攤) — 第 {res['grace_months']+1}~{res['total_months']} 月",
                     fg=COLORS["text_secondary"], bg=COLORS["bg_card"],
                     font=(FONT_FAMILY, 10)).pack(side="left")
            tk.Label(pay_row2, text=f"{fmt(res['post_grace_monthly_pay'])} 元",
                     fg=COLORS["accent_amber"], bg=COLORS["bg_card"],
                     font=(FONT_FAMILY_MONO, 13, "bold")).pack(side="right")
        else:
            pay_row = tk.Frame(monthly_content, bg=COLORS["bg_card"])
            pay_row.pack(fill="x", pady=2)
            tk.Label(pay_row, text="每月還款額 (本息均攤)",
                     fg=COLORS["text_secondary"], bg=COLORS["bg_card"],
                     font=(FONT_FAMILY, 10)).pack(side="left")
            tk.Label(pay_row, text=f"{fmt(res['post_grace_monthly_pay'])} 元",
                     fg=COLORS["accent_amber"], bg=COLORS["bg_card"],
                     font=(FONT_FAMILY_MONO, 13, "bold")).pack(side="right")

        # ===================================================================
        # CHART 1: 每月房貸還款金額折線圖
        # ===================================================================
        chart1_card = tk.Frame(self.results_frame, bg=COLORS["bg_card"],
                               highlightbackground=COLORS["border"],
                               highlightthickness=1)
        chart1_card.pack(fill="x", pady=(0, 12))

        chart1_header = tk.Frame(chart1_card, bg=COLORS["bg_card"])
        chart1_header.pack(fill="x", padx=16, pady=(12, 6))
        tk.Label(chart1_header, text="📊  每月房貸還款金額",
                 font=(FONT_FAMILY, 13, "bold"),
                 bg=COLORS["bg_card"], fg=COLORS["text_primary"]).pack(side="left")

        chart1_sep = tk.Frame(chart1_card, bg=COLORS["separator"], height=1)
        chart1_sep.pack(fill="x", padx=16)

        months = list(range(1, res["total_months"] + 1))
        mortgage_payments = res["monthly_mortgage_payments"]

        fig1, ax1 = self._create_dark_chart()
        ax1.plot(months, mortgage_payments, color=COLORS["mortgage_line"],
                 linewidth=2, label='每月房貸')
        ax1.fill_between(months, mortgage_payments, alpha=0.15,
                         color=COLORS["mortgage_line"])

        # Mark grace period boundary
        if res["grace_months"] > 0:
            ax1.axvline(x=res["grace_months"], color=COLORS["accent_red"],
                        linestyle='--', alpha=0.7, linewidth=1.2)
            ax1.text(res["grace_months"] + 2, max(mortgage_payments) * 0.95,
                     f'← 寬限期結束 (第{res["grace_months"]}月)',
                     color=COLORS["accent_red"], fontsize=9, va='top')

        ax1.set_xlabel('月數', fontsize=10)
        ax1.set_ylabel('金額 (元)', fontsize=10)
        ax1.set_title('每月房貸還款金額', fontsize=13, fontweight='bold', pad=12)
        ax1.yaxis.set_major_formatter(FuncFormatter(fmt_wan))
        ax1.legend(loc='upper right', fontsize=9, facecolor=COLORS["chart_bg"],
                   edgecolor=COLORS["chart_grid"], labelcolor=COLORS["text_secondary"])
        fig1.tight_layout()
        self._embed_chart(fig1, chart1_card)

        # ===================================================================
        # CHART 2: 每月投入股市金額折線圖
        # ===================================================================
        chart2_card = tk.Frame(self.results_frame, bg=COLORS["bg_card"],
                               highlightbackground=COLORS["border"],
                               highlightthickness=1)
        chart2_card.pack(fill="x", pady=(0, 12))

        chart2_header = tk.Frame(chart2_card, bg=COLORS["bg_card"])
        chart2_header.pack(fill="x", padx=16, pady=(12, 6))
        tk.Label(chart2_header, text="📊  每月投入股市金額",
                 font=(FONT_FAMILY, 13, "bold"),
                 bg=COLORS["bg_card"], fg=COLORS["text_primary"]).pack(side="left")

        chart2_sep = tk.Frame(chart2_card, bg=COLORS["separator"], height=1)
        chart2_sep.pack(fill="x", padx=16)

        stock_investments = res["monthly_stock_investments"]

        fig2, ax2 = self._create_dark_chart()
        
        # Color positive investments differently from negative if desired, or just use rent_line
        ax2.plot(months, stock_investments, color=COLORS["rent_line"],
                 linewidth=2, label='每月投入股市金額')
        ax2.fill_between(months, stock_investments, alpha=0.15,
                         color=COLORS["rent_line"])
        
        # Add zero line for reference
        ax2.axhline(0, color=COLORS["text_muted"], linestyle='--', linewidth=1)

        ax2.set_xlabel('月數', fontsize=10)
        ax2.set_ylabel('金額 (元)', fontsize=10)
        ax2.set_title('每月投入股市金額 (房貸月供 - 租金)', fontsize=13, fontweight='bold', pad=12)
        ax2.yaxis.set_major_formatter(FuncFormatter(fmt_wan))
        ax2.legend(loc='upper right', fontsize=9, facecolor=COLORS["chart_bg"],
                   edgecolor=COLORS["chart_grid"], labelcolor=COLORS["text_secondary"])
        fig2.tight_layout()
        self._embed_chart(fig2, chart2_card)

        # ===================================================================
        # CHART 3: 買房 vs 租屋投資 逐月資產變化折線圖
        # ===================================================================
        chart3_card = tk.Frame(self.results_frame, bg=COLORS["bg_card"],
                               highlightbackground=COLORS["border"],
                               highlightthickness=1)
        chart3_card.pack(fill="x", pady=(0, 12))

        chart3_header = tk.Frame(chart3_card, bg=COLORS["bg_card"])
        chart3_header.pack(fill="x", padx=16, pady=(12, 6))
        tk.Label(chart3_header, text="📊  買房 vs 租屋投資 — 逐月資產變化",
                 font=(FONT_FAMILY, 13, "bold"),
                 bg=COLORS["bg_card"], fg=COLORS["text_primary"]).pack(side="left")

        chart3_sep = tk.Frame(chart3_card, bg=COLORS["separator"], height=1)
        chart3_sep.pack(fill="x", padx=16)

        buy_net_worths = res["monthly_buy_net_worths"]
        rent_net_worths = res["monthly_rent_net_worths"]

        fig3, ax3 = self._create_dark_chart(figsize=(9.5, 4.0))
        ax3.plot(months, buy_net_worths, color=COLORS["buy_area"],
                 linewidth=2.5, label='買房淨資產 (房屋估值)')
        ax3.plot(months, rent_net_worths, color=COLORS["rent_area"],
                 linewidth=2.5, label='租屋投資淨資產 (股市組合)')

        # Fill between to highlight which is leading
        buy_arr = np.array(buy_net_worths)
        rent_arr = np.array(rent_net_worths)
        months_arr = np.array(months)

        ax3.fill_between(months_arr, buy_arr, rent_arr,
                         where=(buy_arr >= rent_arr),
                         interpolate=True, alpha=0.12,
                         color=COLORS["buy_area"], label='_nolegend_')
        ax3.fill_between(months_arr, buy_arr, rent_arr,
                         where=(buy_arr < rent_arr),
                         interpolate=True, alpha=0.12,
                         color=COLORS["rent_area"], label='_nolegend_')

        # Mark crossover points
        for i in range(1, len(buy_net_worths)):
            # Check for sign change in (buy - rent)
            prev_diff = buy_net_worths[i-1] - rent_net_worths[i-1]
            curr_diff = buy_net_worths[i] - rent_net_worths[i]
            if prev_diff * curr_diff < 0:  # sign change
                ax3.axvline(x=months[i], color=COLORS["win_color"],
                            linestyle=':', alpha=0.6, linewidth=1)
                ax3.annotate(f'交叉 (第{months[i]}月)',
                             xy=(months[i], buy_net_worths[i]),
                             xytext=(months[i] + len(months)*0.03, 
                                     buy_net_worths[i] * 1.05),
                             color=COLORS["win_color"], fontsize=8,
                             arrowprops=dict(arrowstyle='->', color=COLORS["win_color"],
                                             alpha=0.6))

        ax3.set_xlabel('月數', fontsize=10)
        ax3.set_ylabel('淨資產 (元)', fontsize=10)
        ax3.set_title('買房 vs 租屋投資 — 逐月資產累積曲線', fontsize=13,
                      fontweight='bold', pad=12)
        ax3.yaxis.set_major_formatter(FuncFormatter(fmt_yi))
        ax3.legend(loc='upper left', fontsize=9, facecolor=COLORS["chart_bg"],
                   edgecolor=COLORS["chart_grid"], labelcolor=COLORS["text_secondary"])
        fig3.tight_layout()
        self._embed_chart(fig3, chart3_card)

        # ── Result Cards (side by side) ──
        cards_frame = tk.Frame(self.results_frame, bg=COLORS["bg_primary"])
        cards_frame.pack(fill="x", pady=(0, 12))

        # Buy Card
        buy_card = ResultCard(cards_frame, f"買房情境 — {res['mortgage_years']} 年後",
                               "🏠", COLORS["buy_color"])
        buy_card.pack(side="left", fill="x", expand=True, padx=(0, 6))
        buy_card.add_row("房屋總價（現值）", f"{fmt(res['house_price_initial'])} 元")
        buy_card.add_row("累積總支出（含頭期）", f"{fmt(res['buy_total_spent'])} 元")
        buy_card.add_row("其中房貸利息支出", f"{fmt(res['total_mortgage_paid'] - res['loan_amount'])} 元")
        buy_card.add_row("", "")
        buy_card.add_row("期末房屋估值", f"{fmt(res['buy_net_worth'])} 元",
                          highlight=True, large=True)

        # Rent Card
        rent_card = ResultCard(cards_frame, f"租屋投資情境 — {res['mortgage_years']} 年後",
                                "📈", COLORS["rent_color"])
        rent_card.pack(side="left", fill="x", expand=True, padx=(6, 0))
        rent_card.add_row("累積租金支出", f"{fmt(res['total_rent_paid'])} 元")
        rent_card.add_row("股市投資組合市值", f"{fmt(res['final_stock_portfolio'])} 元")
        if res["cash_savings"] != 0:
            rent_card.add_row("未投資現金餘額", f"{fmt(res['cash_savings'])} 元")
        rent_card.add_row("", "")
        rent_card.add_row("期末淨資產", f"{fmt(res['rent_net_worth'])} 元",
                           highlight=True, large=True)

        # ── Comparison Bar Chart ──
        chart_card = tk.Frame(self.results_frame, bg=COLORS["bg_card"],
                               highlightbackground=COLORS["border"],
                               highlightthickness=1)
        chart_card.pack(fill="x", pady=(0, 12))

        chart_header = tk.Frame(chart_card, bg=COLORS["bg_card"])
        chart_header.pack(fill="x", padx=16, pady=(12, 6))
        tk.Label(chart_header, text="📊  視覺比較",
                 font=(FONT_FAMILY, 13, "bold"),
                 bg=COLORS["bg_card"], fg=COLORS["text_primary"]).pack(side="left")

        chart_sep = tk.Frame(chart_card, bg=COLORS["separator"], height=1)
        chart_sep.pack(fill="x", padx=16)

        bar_chart = ComparisonBar(chart_card, width=980, height=110)
        bar_chart.pack(padx=16, pady=(8, 14))
        bar_chart.update_chart(res["buy_net_worth"], res["rent_net_worth"])

        # ── Verdict Banner ──
        diff = res["buy_net_worth"] - res["rent_net_worth"]
        if diff > 0:
            verdict_bg = COLORS["accent_amber_bg"]
            verdict_border = COLORS["buy_color"]
            verdict_icon = "🚀"
            verdict_text = "買房勝出"
            verdict_detail = f"期末淨資產多出 {fmt(diff)} 元"
            verdict_comment = "長期來看，房屋增值與財務槓桿帶來的效益超過了股市投資。"
        else:
            verdict_bg = "#0a2e3b"
            verdict_border = COLORS["rent_color"]
            verdict_icon = "📈"
            verdict_text = "租屋投資勝出"
            verdict_detail = f"期末淨資產多出 {fmt(-diff)} 元"
            verdict_comment = "股市的高年化報酬率結合複利效應，抵銷了租金成本並超越房產增值。"

        verdict_frame = tk.Frame(self.results_frame, bg=verdict_bg,
                                  highlightbackground=verdict_border,
                                  highlightthickness=2)
        verdict_frame.pack(fill="x", pady=(0, 12))

        verdict_inner = tk.Frame(verdict_frame, bg=verdict_bg)
        verdict_inner.pack(fill="x", padx=20, pady=16)

        # Icon + Title
        verdict_title_frame = tk.Frame(verdict_inner, bg=verdict_bg)
        verdict_title_frame.pack(fill="x")
        tk.Label(verdict_title_frame, text=verdict_icon,
                 font=(FONT_FAMILY, 24),
                 bg=verdict_bg, fg=verdict_border).pack(side="left")
        tk.Label(verdict_title_frame, text=f"  {verdict_text}",
                 font=(FONT_FAMILY, 20, "bold"),
                 bg=verdict_bg, fg=verdict_border).pack(side="left")

        tk.Label(verdict_inner, text=verdict_detail,
                 font=(FONT_FAMILY_MONO, 14, "bold"),
                 bg=verdict_bg, fg=COLORS["text_primary"],
                 anchor="w").pack(fill="x", pady=(8, 2))
        tk.Label(verdict_inner, text=verdict_comment,
                 font=(FONT_FAMILY, 10),
                 bg=verdict_bg, fg=COLORS["text_secondary"],
                 anchor="w", wraplength=900).pack(fill="x")

        # ── Notes / Footnotes ──
        notes_frame = tk.Frame(self.results_frame, bg=COLORS["bg_secondary"])
        notes_frame.pack(fill="x", pady=(0, 20))

        notes_content = tk.Frame(notes_frame, bg=COLORS["bg_secondary"])
        notes_content.pack(fill="x", padx=20, pady=12)

        notes = [
            "📌 台灣銀行算法通常採用「每月本息平均攤還」。",
            "📌 寬限期內僅繳納利息，本金延後至剩餘年度攤還，會增加總利息支出。",
            "📌 本計算未考量房屋稅、地價稅、維護成本、房屋折舊及交易稅費。",
            "📌 股市報酬率假設為歷史長期平均，實際波動可能劇烈。",
        ]
        for note in notes:
            tk.Label(notes_content, text=note, fg=COLORS["text_muted"],
                     bg=COLORS["bg_secondary"], font=(FONT_FAMILY, 9),
                     anchor="w").pack(anchor="w", pady=1)

        # Auto-scroll to results
        self.results_frame.update_idletasks()
        self.update_idletasks()


# ─────────────────────────────────────────────
# Entry Point
# ─────────────────────────────────────────────
if __name__ == "__main__":
    app = CalculatorApp()
    app.mainloop()
