# 🏡 House Investment Calculator: Rent vs. Buy

This tool helps you decide whether it's better to **buy a house** or **rent while investing** the extra money into the stock market. 
It calculates your long-term net worth and visualizes wealth growth over the years.

## ✨ Features

- **Accurate Net Worth:** Home wealth is calculated as "House Value - Remaining Mortgage," showing a fair comparison.
- **Mortgage Options:** Supports grace periods (interest-only payments) and standard principal + interest payments.
- **Rent vs. Invest:** Simulates investing the down payment and any monthly savings (mortgage minus rent) into the stock market.
- **Multiple Interfaces:** Available as a web app, a desktop app, or a command-line script.

## 🚀 Live Demo

Try the web version directly from your browser: 
👉 **[Open House Investment Calculator](https://house-investment-calculator.streamlit.app/)** 
*(Note: Link may be unavailable if not deployed yet)*

## 🛠️ Requirements

- Python 3.7+
- Streamlit
- Pandas
- Matplotlib

## 💻 Running Locally

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Run Web App (Streamlit)
Works on both desktop and mobile devices.
```bash
python -m streamlit run app.py
```
It will open `http://localhost:8501` automatically.

### 3. Run Desktop App
If you prefer a classic desktop window:
```bash
python calculator_gui.py
```

### 4. Run Command-Line Tool
For a simple text output:
```bash
python calculator.py
```

## 📂 Project Structure

- `calculator.py`: Core logic for mortgage, investment compound interest, and data generation.
- `app.py`: Web interface built with Streamlit.
- `calculator_gui.py`: Desktop interface built with Python GUI.
- `requirements.txt`: List of Python packages needed.

## ⚖️ Disclaimer & Notes

1. **Home Equity**: The net worth of buying is "Current Home Value - Unpaid Loan."
2. **Simplified Model**: This is for long-term planning. Real-life costs like property taxes, home repairs, or stock trading fees are not included.
3. **Disclaimer**: Results are for reference only. Both real estate and the stock market involve risks. Please make your own financial decisions carefully.
