import streamlit as st
import pandas as pd
from calculator import calculate_investment

# 設定頁面資訊
st.set_page_config(page_title="買房 vs 租屋投資決策計算機", layout="wide")

st.title("🏡 住宅決策分析儀：買房勝？還是租屋投資勝？")
st.markdown("這是一個幫助您評估「買房」與「租屋並將資金投入股市」長期淨資產變化的分析工具。此APP已優化支援手機版面瀏覽。")

# 側邊欄輸入參數
st.sidebar.header("⚙️ 設定參數")

st.sidebar.subheader("房貸相關")
loan_amount = st.sidebar.number_input("貸款金額 (元)", value=12000000, step=100000)
st.sidebar.caption(f"= {loan_amount:,.0f} 元")
down_payment = st.sidebar.number_input("頭期款金額 (元)", value=3000000, step=100000)
st.sidebar.caption(f"= {down_payment:,.0f} 元")
mortgage_years = st.sidebar.number_input("貸款年限 (年)", value=30, step=1)
grace_period_years = st.sidebar.number_input("寬限期 (年)", value=0, step=1)
mortgage_rate = st.sidebar.number_input("年化房貸利率 (%)", value=2.5, step=0.1) / 100
house_growth_rate = st.sidebar.number_input("房價預估年化成長率 (%)", value=5.0, step=0.5) / 100

st.sidebar.subheader("租屋及投資相關")
rent_initial = st.sidebar.number_input("初始每月租金 (元)", value=27000, step=1000)
st.sidebar.caption(f"= {rent_initial:,.0f} 元")
rent_growth_rate = st.sidebar.number_input("租金預估年成長率 (%)", value=2.0, step=0.5) / 100
stock_return_rate = st.sidebar.number_input("股市預估年化報酬率 (%)", value=10.0, step=0.5) / 100
invest_difference = st.sidebar.checkbox("將買房與租屋的差額投入股市", value=True, help="如果勾選，代表每個月買房要繳的錢扣掉租金後，剩下的錢都會拿去買股票。")

# 執行計算
try:
    res = calculate_investment(
        loan_amount=loan_amount,
        down_payment=down_payment,
        mortgage_rate=mortgage_rate,
        rent_initial=rent_initial,
        rent_growth_rate=rent_growth_rate,
        house_growth_rate=house_growth_rate,
        stock_return_rate=stock_return_rate,
        grace_period_years=grace_period_years,
        invest_difference=invest_difference,
        mortgage_years=mortgage_years
    )
    
    # 顯示核心對決結果
    st.header("📊 最終分析結果")
    diff = res['buy_net_worth'] - res['rent_net_worth']
    
    if diff > 0:
        st.success(f"### 🚀 **【買房勝出】** 買房經過 {mortgage_years} 年後，淨資產多出 **{diff:,.0f}** 元")
    else:
        st.info(f"### 📈 **【租房投資勝出】** 租房並投資經過 {mortgage_years} 年後，淨資產多出 **{-diff:,.0f}** 元")

    # 左右對比數據
    col1, col2 = st.columns(2)
    with col1:
        st.markdown(f"#### 🏠 買房情境")
        st.metric("期末預估房屋價值 (淨資產)", f"{res['buy_net_worth']:,.0f} 元")
        st.metric("累積總支出 (含頭期+房貸)", f"{res['buy_total_spent']:,.0f} 元")
    
    with col2:
        st.markdown(f"#### 🛌 租屋投資情境")
        st.metric("期末股市投資總市值 (淨資產)", f"{res['rent_net_worth']:,.0f} 元")
        st.metric("累積總支出 (租金)", f"{res['total_rent_paid']:,.0f} 元")

    # 顯示圖表
    st.subheader("📈 逐月淨資產變化趨勢")
    
    # 將數據轉為 DataFrame
    df = pd.DataFrame({
        "月份": range(1, res['total_months'] + 1),
        "買房端淨資產 (房屋價值)": res['monthly_buy_net_worths'],
        "租屋端淨資產 (股票+現金)": res['monthly_rent_net_worths']
    }).set_index("月份")
    
    # 使用 streamlit 內建的 line_chart
    st.line_chart(df)

except AssertionError as e:
    st.error(f"⚠️ 參數設定錯誤: {e}")
    st.stop()
