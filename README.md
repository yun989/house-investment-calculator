# 🏡 住宅決策分析儀：買房勝？還是租屋投資勝？ (House Investment Calculator)

這是一個幫助使用者評估「買房」與「租屋並將多餘資金投入股市」長期淨資產累積差異的決策分析工具。
本專案提供**網頁版 (Streamlit)** 與 **桌面端 GUI** 兩種介面，讓使用者可以輕鬆輸入各種參數進行試算，並且視覺化逐月的淨資產變化趨勢。

## ✨ 核心特色 (Features)

- **精確的淨資產計算 (Home Equity)**：買房端的資產並非單純計算房屋總價，而是採取標準的「房屋現值 - 尚未償還的銀行本金」來衡量真實淨資產，初期起步計算更加公平合理。
- **支援台灣銀行實務**：房貸計算支援「寬限期 (只繳息不繳本)」與「本息平均攤還」邏輯。
- **租屋投資對比**：完整模擬「將買房頭期款」以及「每月（房貸-租金）的差額」投入股市，搭配複利效益，與買房的長期效益進行 PK。
- **多平台支援**：提供可部署於雲端的 Web APP，手機、平板、電腦皆可無需環境直接使用。

## 🚀 線上體驗 (Live Demo)

歡迎直接透過 Streamlit 部署的 Web App 來體驗：
👉 **[點此前往決策分析儀網頁版](https://house-investment-calculator.streamlit.app/)** 
*(請注意：如果尚未部署完成，連結可能無法使用)*

## 🛠️ 系統需求 (Requirements)

- Python 3.7+
- Streamlit
- Pandas
- Matplotlib

## 💻 本機執行與開發 (Running Locally)

### 1. 安裝依賴套件
```bash
pip install -r requirements.txt
```

### 2. 啟動網頁版 (Streamlit Web App)
網頁版支援響應式設計 (Responsive Design)，適合手機與電腦瀏覽。
```bash
python -m streamlit run app.py
```
啟動後會自動在瀏覽器打開 `http://localhost:8501`。

### 3. 啟動桌面版 GUI
如果您偏好使用傳統桌面應用程式：
```bash
python calculator_gui.py
```

### 4. 使用純文字終端機介面
也可直接執行核心腳本獲得命令列輸出：
```bash
python calculator.py
```

## 📂 檔案結構 (Repository Structure)

- `calculator.py`：核心財務計算邏輯，包含房貸公式、投資複利運算與資料統整。
- `app.py`：使用 Streamlit 撰寫的網頁版互動介面。
- `calculator_gui.py`：使用 Python GUI 套件撰寫的桌面版介面。
- `requirements.txt`：Python 套件依賴清單。

## ⚖️ 財務模型說明與免責聲明

1. **房屋淨值 (Home Equity)**：本系統於計算「買房淨資產」時，遵循實務邏輯，以「當下房屋估值」扣除「剩餘未償還貸款本金」。
2. **變動因素保留**：此模型為協助長期決策的簡化模擬，實際生活中的「房屋稅、地價稅、裝潢費、折舊」或是「股票交易手續費、稅金」並未深入細計。
3. **免責聲明**：本工具計算結果僅供參考，不構成任何實質投資建議。房地產與股票市場皆具備風險，請使用者依據自身財務狀況謹慎評估。
