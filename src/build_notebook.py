from pathlib import Path
import nbformat as nbf

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "notebooks" / "unemployment_analysis.ipynb"

nb = nbf.v4.new_notebook()
nb["metadata"] = {
    "kernelspec": {"display_name": "Python 3", "language": "python", "name": "python3"},
    "language_info": {"name": "python", "version": "3.12"},
}
nb["cells"] = [
    nbf.v4.new_markdown_cell(
        "# Unemployment Analysis in India — CodeAlpha Task 2\n\n"
        "Professional exploratory analysis of monthly unemployment, labour participation, regional variation, and the March–June 2020 COVID shock.\n\n"
        "**Important:** the uploaded file is CSV data with an `.xls` filename. The notebook reads it as UTF-8 CSV."
    ),
    nbf.v4.new_code_cell(
        """from pathlib import Path\nimport glob\nimport pandas as pd\nimport matplotlib.pyplot as plt\n\nplt.style.use('seaborn-v0_8-whitegrid')\nplt.rcParams.update({'figure.dpi': 120, 'axes.titlesize': 14, 'axes.titleweight': 'bold'})\n\n# Works locally and on Kaggle after attaching the dataset.\ncandidates = [\n    Path('/kaggle/input/UnemploymentinIndia.xls'),\n    Path('/kaggle/input/unemployment-in-india/Unemployment in India.csv'),\n    Path('../data_raw/UnemploymentinIndia.csv'),\n    Path('data_raw/UnemploymentinIndia.csv'),\n]\nfiles = [p for p in candidates if p.exists()]\nif not files:\n    files = [Path(p) for p in glob.glob('/kaggle/input/**/*', recursive=True) if Path(p).is_file() and Path(p).suffix.lower() in {'.csv', '.xls'}]\nif not files:\n    raise FileNotFoundError('Attach the unemployment dataset or place it in data_raw/.')\nDATA_PATH = files[0]\nprint('Using:', DATA_PATH)\ndf = pd.read_csv(DATA_PATH, encoding='utf-8-sig')\ndf.columns = df.columns.str.strip()\ndf = df.dropna(how='all').copy()\nprint('Raw rows after removing blank rows:', len(df))\n"""
    ),
    nbf.v4.new_code_cell(
        """RATE = 'Estimated Unemployment Rate (%)'\nEMPLOYED = 'Estimated Employed'\nLPR = 'Estimated Labour Participation Rate (%)'\n\ndf['Date'] = pd.to_datetime(df['Date'], dayfirst=True, errors='coerce')\nfor col in [RATE, EMPLOYED, LPR]:\n    df[col] = pd.to_numeric(df[col], errors='coerce')\ndf['Region'] = df['Region'].astype('string').str.strip()\ndf['Area'] = df['Area'].astype('string').str.strip()\ndf = df.dropna(subset=['Date', RATE, 'Region', 'Area']).sort_values('Date')\ndf['Period'] = df['Date'].map(lambda x: 'Pre-COVID' if x < pd.Timestamp('2020-03-01') else 'COVID shock')\ndf['Month'] = df['Date'].dt.to_period('M').dt.to_timestamp()\n\nperiod_summary = df.groupby('Period', observed=True)[RATE].agg(['count','mean','median','min','max']).round(2)\narea_summary = df.groupby(['Period','Area'], observed=True)[RATE].mean().round(2).unstack()\nregion_summary = df.groupby('Region')[RATE].mean().sort_values(ascending=False).round(2)\nprint('Clean shape:', df.shape)\nprint('Date range:', df['Date'].min().date(), 'to', df['Date'].max().date())\nprint('Regions:', df['Region'].nunique())\ndisplay(period_summary)\nprint('Top five regions by average unemployment rate:')\ndisplay(region_summary.head())\n"""
    ),
    nbf.v4.new_markdown_cell(
        """## COVID-19 impact\n\nThe dataset covers May 2019–June 2020. I use May 2019–February 2020 as the pre-COVID baseline and March–June 2020 as the COVID shock window. This is a descriptive before/after comparison, not a causal estimate.\n"""
    ),
    nbf.v4.new_code_cell(
        """monthly = df.groupby('Month', as_index=False)[RATE].mean()\nmonthly_area = df.groupby(['Month','Area'], as_index=False)[RATE].mean()\npre = df.loc[df['Period'].eq('Pre-COVID'), RATE].mean()\nshock = df.loc[df['Period'].eq('COVID shock'), RATE].mean()\nprint(f'Pre-COVID mean: {pre:.2f}%')\nprint(f'COVID shock mean: {shock:.2f}%')\nprint(f'Increase: {(shock/pre-1)*100:.1f}%')\n\nfig, axes = plt.subplots(2, 2, figsize=(15, 10))\nax = axes[0,0]\nax.plot(monthly['Month'], monthly[RATE], color='#0F766E', marker='o', linewidth=3, label='All areas')\nfor area, color in [('Urban','#F97316'),('Rural','#2563EB')]:\n    temp = monthly_area[monthly_area['Area'].eq(area)]\n    ax.plot(temp['Month'], temp[RATE], color=color, marker='o', label=area)\nax.axvspan(pd.Timestamp('2020-03-01'), pd.Timestamp('2020-06-30'), color='#FDE68A', alpha=.45, label='COVID shock')\nax.set_title('Monthly unemployment trend')\nax.set_ylabel('Rate (%)'); ax.legend(frameon=False)\n\nax = axes[0,1]\nvalues = [pre, shock]\nbars = ax.bar(['Pre-COVID','COVID shock'], values, color=['#94A3B8','#DC2626'])\nax.bar_label(bars, labels=[f'{v:.1f}%' for v in values], padding=3, fontweight='bold')\nax.set_title('Average rate comparison'); ax.set_ylabel('Rate (%)')\n\nax = axes[1,0]\nrank = region_summary.sort_values()\nax.barh(rank.index, rank.values, color='#0F766E')\nax.set_title('Regional average unemployment'); ax.set_xlabel('Rate (%)')\n\nax = axes[1,1]\nfor period, color in [('Pre-COVID','#64748B'),('COVID shock','#DC2626')]:\n    temp = df[df['Period'].eq(period)]\n    ax.scatter(temp[LPR], temp[RATE], s=20, alpha=.4, color=color, label=period)\nax.set_title('Participation vs unemployment')\nax.set_xlabel('Labour participation rate (%)'); ax.set_ylabel('Unemployment rate (%)'); ax.legend(frameon=False)\nplt.tight_layout()\nplt.show()\n"""
    ),
    nbf.v4.new_markdown_cell(
        """## Key findings and policy implications\n\n- The national average unemployment rate rises sharply during March–June 2020, with the monthly peak in May 2020.\n- Regional averages differ materially, so national targeting alone would miss local labour-market stress.\n- Urban and rural unemployment both rise; the two segments should be monitored separately.\n- Labour participation should be interpreted alongside unemployment to distinguish job loss from labour-force exit.\n- The evidence supports geographically targeted employment support, high-frequency monitoring, and post-shock evaluation using longer time series.\n\n**Limitation:** the supplied data ends in June 2020, so this notebook identifies the initial COVID shock but cannot evaluate the full recovery.\n"""
    ),
]
OUT.parent.mkdir(exist_ok=True)
nbf.write(nb, OUT)
print(f'Wrote {OUT}')
