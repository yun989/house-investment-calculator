import argparse
import sys
import math

# Ensure UTF-8 output for Windows console to support Chinese characters
if sys.stdout.encoding != 'utf-8':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except AttributeError:
        # Fallback for Python versions < 3.7
        import codecs
        sys.stdout = codecs.getwriter("utf-8")(sys.stdout.detach())

def calculate_investment(
    loan_amount,
    down_payment,
    mortgage_rate,
    rent_initial,
    rent_growth_rate,
    house_growth_rate,
    stock_return_rate,
    grace_period_years,
    invest_difference,
    mortgage_years
):
    """
    Core calculation logic for Mortgage vs Renting & Investing.
    Includes Taiwan Bank (Bank of Taiwan) style grace period and amortization.
    """
    house_price_initial = loan_amount + down_payment
    monthly_mortgage_rate = mortgage_rate / 12
    total_months = int(mortgage_years * 12)
    grace_months = int(grace_period_years * 12)
    
    # 房貸計算 (台灣銀行常見 本息平均攤還)
    # 寬限期內：每月繳利息 = 貸款餘額 * 月利率
    # 寬限期後：將剩餘本金在剩餘期限內「本息平均攤還」
    remaining_months = total_months - grace_months
    if remaining_months > 0:
        if monthly_mortgage_rate > 0:
            # Standard Amortization Formula: P * [i(1+i)^n] / [(1+i)^n - 1]
            p = loan_amount
            i = monthly_mortgage_rate
            n = remaining_months
            post_grace_payment = p * (i * (1 + i)**n) / ((1 + i)**n - 1)
        else:
            post_grace_payment = loan_amount / remaining_months
    else:
        post_grace_payment = 0

    # 投資計算
    # 股市年化報酬率 10% -> 月化報酬率 (幾何平均)
    # (1 + r_monthly)^12 = 1 + r_annual => r_monthly = (1 + r_annual)^(1/12) - 1
    monthly_stock_return = (1 + stock_return_rate) ** (1/12) - 1
    
    # 初始化追蹤變數
    stock_portfolio = down_payment
    total_mortgage_paid = 0
    total_rent_paid = 0
    current_rent = rent_initial
    cash_savings = 0 # 用於存放未投入股市的差額
    
    # 逐月演進
    for month in range(1, total_months + 1):
        # 1. 房貸支出
        if month <= grace_months:
            mortgage_pay = loan_amount * monthly_mortgage_rate
        else:
            mortgage_pay = post_grace_payment
        total_mortgage_paid += mortgage_pay
        
        # 2. 租屋支出 (每年調整一次)
        if month > 1 and (month - 1) % 12 == 0:
            current_rent *= (1 + rent_growth_rate)
        total_rent_paid += current_rent
        
        # 3. 租房端投資成長
        stock_portfolio *= (1 + monthly_stock_return)
        
        # 4. 投入差額 (買房月供 - 當月租金)
        # 如果月供 > 租金, Renter 把多出的錢投進股市
        # 如果月供 < 租金, Renter 必須從股市/現金中支付超出的租金
        diff = mortgage_pay - current_rent
        if invest_difference:
            stock_portfolio += diff
        else:
            cash_savings += diff

    # 期末房屋價值
    final_house_value = house_price_initial * ((1 + house_growth_rate) ** mortgage_years)
    
    # 最終清算
    buy_net_worth = final_house_value
    buy_total_spent = down_payment + total_mortgage_paid
    
    rent_net_worth = stock_portfolio + cash_savings
    
    return {
        "house_price_initial": house_price_initial,
        "loan_amount": loan_amount,
        "down_payment": down_payment,
        "mortgage_years": mortgage_years,
        "grace_period_years": grace_period_years,
        "mortgage_rate": mortgage_rate,
        "house_growth_rate": house_growth_rate,
        "rent_initial": rent_initial,
        "rent_growth_rate": rent_growth_rate,
        "stock_return_rate": stock_return_rate,
        "buy_net_worth": buy_net_worth,
        "buy_total_spent": buy_total_spent,
        "total_mortgage_paid": total_mortgage_paid,
        "rent_net_worth": rent_net_worth,
        "total_rent_paid": total_rent_paid,
        "final_stock_portfolio": stock_portfolio,
        "cash_savings": cash_savings,
        "grace_monthly_pay": loan_amount * monthly_mortgage_rate if grace_months > 0 else 0,
        "post_grace_monthly_pay": post_grace_payment
    }

def fmt(num):
    return f"{num:,.0f}"

def print_dashboard(res):
    print("\n" + "="*60)
    print("        住宅決策分析儀：買房勝？還是租屋投資勝？        ")
    print("="*60)
    
    # 輸入參數區
    print(f"| 【基本條件】")
    print(f"|  房屋總價：{fmt(res['house_price_initial']):>12} 元 │ 貸款年限：{res['mortgage_years']:>2} 年")
    print(f"|  自備頭期：{fmt(res['down_payment']):>12} 元 │ 寬限期  ：{res['grace_period_years']:>2} 年")
    print(f"|  房貸利率：{res['mortgage_rate']*100:>12.2f} %  │ 房價成長：{res['house_growth_rate']*100:>2.1f} %/y")
    print(f"|  初始月租：{fmt(res['rent_initial']):>12} 元 │ 租金成長：{res['rent_growth_rate']*100:>2.1f} %/y")
    print(f"|  股市回報：{res['stock_return_rate']*100:>12.2f} %/y │ 投資差額：{'是' if res['cash_savings']==0 else '否'}")
    print("-" * 60)
    
    # 月供資訊
    if res['grace_period_years'] > 0:
        print(f"|  寬限期月付 (利息)： {fmt(res['grace_monthly_pay'])} 元")
        print(f"|  寬限期後月付 (本息)： {fmt(res['post_grace_monthly_pay'])} 元")
    else:
        print(f"|  每月還款額 (本息平均)： {fmt(res['post_grace_monthly_pay'])} 元")
    print("-" * 60)

    # 買房結果
    print(f"| 【買房情境 - {res['mortgage_years']} 年後】")
    print(f"|  累積總支出(含頭期)： {fmt(res['buy_total_spent']):>15} 元")
    print(f"|  期末預估房屋價值  ： {fmt(res['buy_net_worth']):>15} 元")
    print(f"|  ● 買房端最終淨資產： {fmt(res['buy_net_worth']):>15} 元")
    print("-" * 60)

    # 租屋結果
    print(f"| 【租屋投資情境 - {res['mortgage_years']} 年後】")
    print(f"|  累積總支出(租金)  ： {fmt(res['total_rent_paid']):>15} 元")
    print(f"|  期末股市投資總市值： {fmt(res['final_stock_portfolio']):>15} 元")
    if res['cash_savings'] != 0:
        print(f"|  未投資現金餘額    ： {fmt(res['cash_savings']):>15} 元")
    print(f"|  ● 租房端最終淨資產： {fmt(res['rent_net_worth']):>15} 元")

    # 最終對決
    print("=" * 60)
    diff = res['buy_net_worth'] - res['rent_net_worth']
    if diff > 0:
        print(f" RESULT: 🚀 【買房勝出】 期末淨資產多出 {fmt(diff)} 元")
        winner_comment = "長期來看，房屋增值與財務槓桿帶來的效益超過了股市投資。"
    else:
        print(f" RESULT: 📈 【租房投資勝出】 期末淨資產多出 {fmt(-diff)} 元")
        winner_comment = "股市的高年化報酬率結合複利效應，抵銷了租金成本並超越房產增值。"
    
    print(f" 註解: {winner_comment}")
    print("=" * 60)
    print(" *註1: 台灣銀行算法通常採用『每月本息平均攤還』。")
    print(" *註2: 寬限期內僅繳納利息，本金延後至剩餘年度攤還，會增加總支出。")
    print(" *註3: 本計算未考量房屋稅、地價稅、維護成本及房屋折舊。")
    print("=" * 60 + "\n")

def str2bool(v):
    if v is None: return False
    if isinstance(v, bool): return v
    return str(v).lower() in ('yes', 'true', 't', 'y', '1')

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='買房 vs 租房投資股市 決策計算機 (台灣銀行算法預設)')
    parser.add_argument('--mortgage_rate', type=float, default=0.025, help='年化房貸利率 (例: 0.025)')
    parser.add_argument('--loan_amount', type=float, default=12000000, help='貸款金額')
    parser.add_argument('--down_payment', type=float, default=3000000, help='頭期款金額')
    parser.add_argument('--loan_years', type=int, default=30, help='貸款年限')
    parser.add_argument('--house_growth', type=float, default=0.05, help='房價年化成長率')
    parser.add_argument('--rent', type=float, default=27000, help='初始每月租金')
    parser.add_argument('--rent_growth', type=float, default=0.02, help='租金年成長率')
    parser.add_argument('--grace_period', type=float, default=0, help='寬限期年數')
    parser.add_argument('--stock_return', type=float, default=0.10, help='股市年化報酬率')
    parser.add_argument('--invest_diff', type=str2bool, default=True, help='是否將差額投入股市')
    
    args = parser.parse_args()
    
    result = calculate_investment(
        loan_amount=args.loan_amount,
        down_payment=args.down_payment,
        mortgage_rate=args.mortgage_rate,
        rent_initial=args.rent,
        rent_growth_rate=args.rent_growth,
        house_growth_rate=args.house_growth,
        stock_return_rate=args.stock_return,
        grace_period_years=args.grace_period,
        invest_difference=args.invest_diff,
        mortgage_years=args.loan_years
    )
    
    print_dashboard(result)
