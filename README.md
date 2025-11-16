# 💰 Financial Simulation Interactive App

An interactive Streamlit application for comparing investment portfolio strategies over 15 years using historical market data (1926-2024).

## Features

- **Compare up to 4 portfolios** simultaneously with different asset allocations
- **Customizable parameters**: Initial investments, contribution schedules, timelines, and market volatility
- **Historical market data**: Uses real S&P 500, NASDAQ 100, and T-Bill returns
- **Monte Carlo simulation**: Generates thousands of possible outcomes per portfolio
- **Interactive visualizations**: Plotly charts for exploring results
- **Detailed statistics**: IRR calculations, percentile ranges, and milestone comparisons

## 📁 Files

- `app.py` - Main Streamlit application
- `financial_simulation_lib.py` - Core simulation functions and historical data
- `requirements.txt` - Python dependencies
- `colab_notebook_cell.py` - Quick setup for Google Colab
- `README.md` - This file

## 🚀 Running in Google Colab

### Option 1: Quick Start (Recommended)

1. Open a new Google Colab notebook
2. Upload all files from this repository to Colab
3. Create a new code cell and paste the contents of `colab_notebook_cell.py`
4. Run the cell and click the ngrok URL that appears
5. The app will open in a new tab!

### Option 2: Manual Setup

```python
# Install dependencies
!pip install -q streamlit numpy pandas matplotlib seaborn scipy plotly pyngrok

# Start the app with ngrok tunnel
from pyngrok import ngrok
import subprocess

# Start Streamlit
proc = subprocess.Popen(["streamlit", "run", "app.py", "--server.port", "8501"])

# Create public URL
public_url = ngrok.connect(8501)
print(f"Access your app at: {public_url}")
```

## 🌐 Running Locally

### Prerequisites

- Python 3.8 or higher
- pip package manager

### Installation

```bash
# Clone the repository
git clone <your-repo-url>
cd financial-simulation-app

# Install dependencies
pip install -r requirements.txt

# Run the app
streamlit run app.py
```

The app will open automatically in your browser at `http://localhost:8501`

## ☁️ Deploying to Streamlit Cloud

1. Push your code to a GitHub repository
2. Go to [share.streamlit.io](https://share.streamlit.io)
3. Sign in with GitHub
4. Click "New app"
5. Select your repository, branch, and `app.py` as the main file
6. Click "Deploy"

Your app will be live at `https://<your-username>-<repo-name>.streamlit.app`

## 📊 How to Use

### 1. Configure Parameters (Sidebar)

- **Initial Amounts**: Set starting investment and emergency fund
- **Monthly Contributions**: Define contribution amounts for different life stages
- **Timeline**: Set when major life events occur (new job, kid arrival)
- **Market Volatility**: Adjust standard deviations for each asset class
- **Iterations**: Choose simulation intensity (more = more accurate but slower)

### 2. Set Up Portfolios

Configure up to 4 portfolios with different allocations:
- **S&P 500**: Large-cap US stocks
- **NASDAQ 100**: Tech-heavy growth stocks
- **T-Bills**: Low-risk government bonds
- **HYSA**: High-yield savings account

Each portfolio allocation must sum to 100%.

### 3. Run Simulation

Click "Run Simulation" to:
- Generate thousands of possible outcomes
- Compare portfolios across historical periods
- Calculate returns, risks, and probabilities

### 4. Analyze Results

Review:
- **Summary metrics**: Median values and baseline comparison
- **Growth trajectories**: Portfolio values over time
- **Distribution charts**: Range of possible outcomes
- **Detailed statistics**: IRR, percentiles, and fund-specific returns

## 📈 Understanding the Results

### Key Metrics

- **Median Value**: The middle outcome (50th percentile)
- **Beat Baseline %**: Probability of outperforming HYSA-only strategy
- **IRR**: Internal Rate of Return (annualized, accounts for contribution timing)
- **Percentiles**: 10th/25th/75th/90th show the range of outcomes

### What the Charts Show

1. **Growth Over Time**: Median portfolio value at 3, 5, 7, 10, and 15 years
2. **Distribution**: Histogram showing all possible final values
3. **Percentile Ranges**: Best/worst case scenarios for each portfolio

## ⚠️ Important Notes

- **Past performance ≠ future results**: This tool is for educational purposes only
- **Simplified model**: Doesn't account for taxes, fees, inflation, or rebalancing
- **Monte Carlo limitations**: Assumes returns follow historical patterns
- **Volatility**: Adjustable standard deviations add randomness to monthly returns

## 🛠️ Customization

### Adding New Asset Classes

Edit `financial_simulation_lib.py`:

1. Add historical returns to `market_returns` dictionary
2. Update allocation parameters in `app.py`
3. Modify `run_investment_simulation()` to include new asset

### Changing the Time Horizon

Currently set to 15 years. To change:

1. Update `get_15_year_sequences()` in `financial_simulation_lib.py`
2. Adjust milestone years in `app.py`
3. Update IRR calculations to use new time period

### Customizing Visualizations

All charts use Plotly. Modify the figure configurations in `app.py`:
- Colors: Change the `colors` list
- Layout: Adjust `fig.update_layout()`
- Data: Modify the data extraction and processing

## 🐛 Troubleshooting

### Google Colab Issues

**Problem**: "Module not found" error
- **Solution**: Make sure all files are uploaded to Colab
- Run the pip install cell again

**Problem**: Ngrok tunnel expires
- **Solution**: Free ngrok tunnels expire after 2 hours. Restart the cell.

**Problem**: App loads slowly
- **Solution**: Reduce the number of iterations in the sidebar (try 100 or 500)

### Local/Deployment Issues

**Problem**: Port already in use
- **Solution**: Run `streamlit run app.py --server.port 8502` (different port)

**Problem**: Out of memory
- **Solution**: Reduce iterations or number of enabled portfolios

**Problem**: Slow performance
- **Solution**: 
  - Reduce iterations (100-500 for testing)
  - Enable fewer portfolios
  - Use a more powerful machine

## 📚 Additional Resources

- [Streamlit Documentation](https://docs.streamlit.io)
- [Monte Carlo Simulation Explained](https://www.investopedia.com/terms/m/montecarlosimulation.asp)
- [Historical Market Returns](https://pages.stern.nyu.edu/~adamodar/New_Home_Page/datafile/histretSP.html)

## 🤝 Contributing

Contributions welcome! Ideas for improvements:
- Add inflation adjustment
- Include tax calculations
- Add more asset classes (crypto, real estate, international stocks)
- Implement portfolio rebalancing
- Add scenario analysis (recession, bull market, etc.)

## 📄 License

This project is provided as-is for educational purposes. Use at your own risk.

## 🙏 Acknowledgments

- Historical market data from various public sources
- Built with Streamlit, Plotly, and NumPy
- Inspired by personal finance simulation needs

---

**Disclaimer**: This tool provides educational simulations only. It is not financial advice. Consult with a qualified financial advisor before making investment decisions.
