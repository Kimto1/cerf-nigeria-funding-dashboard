# CERF Nigeria Funding Analysis Dashboard

An end-to-end data analytics capstone project examining approved Central Emergency Response Fund (CERF) allocations represented in a supplied Nigeria project-level dataset.

The project combines data cleaning, validation, exploratory analysis, interactive visualisation and dashboard development using Python, Pandas, Plotly and Streamlit.

## Project Objectives

This project aims to:

- Clean and standardise the supplied CERF Nigeria dataset.
- Validate the accuracy and integrity of the cleaned data.
- Analyse funding by agency, year, emergency type, funding window, sector combination and crisis grouping.
- Identify leading agencies, sectors, years and projects.
- Examine important source-data quality limitations.
- Build an interactive dashboard for exploring and downloading filtered project records.

## Executive Findings

The supplied dataset contains 125 projects and approximately $207.84 million in approved funding.

Key findings include:

- UNICEF received the highest total funding at approximately $73.20 million and implemented the largest number of projects, with 39 projects.
- WFP had the highest average funding per project at approximately $4.05 million.
- The two largest agencies accounted for 64.5% of total approved funding.
- Displacement-related projects received approximately $109.40 million.
- Rapid Response accounted for 70.6% of funding, compared with 29.4% for Underfunded Emergencies.
- Food Assistance was the leading recorded sector combination, receiving approximately $46.82 million.
- Funding peaked in 2021 at approximately $33.50 million.
- The largest project was `20-RR-WFP-056`, valued at approximately $15 million.
- Project-grouping information was absent from 51.2% of source records.
- CAP-code information was absent from 69.6% of source records.

These findings describe allocation patterns within the supplied dataset. They do not measure humanitarian need, programme effectiveness, expenditure or outcomes.

## Dashboard Features

The Streamlit dashboard provides:

- Interactive year filters
- Implementing-agency filters
- Emergency-type filters
- CERF funding-window filters
- Dynamic funding and project KPIs
- Funding analysis by agency
- Annual funding trends
- Emergency-type analysis
- Funding-window distribution
- Sector-combination analysis
- Crisis-grouping analysis
- Ten-largest-project analysis
- Filtered project-level records
- Downloadable filtered CSV data
- Dynamic executive findings
- Source-data quality visualisation
- Methodological and analytical limitations

## Project Structure

```text
cerf-nigeria-capstone/
├── app.py
├── data/
│   ├── raw/
│   └── processed/
│       └── cerf_nigeria_cleaned.csv
├── notebooks/
│   └── CERF_Nigeria_Analysis.ipynb
├── outputs/
│   ├── charts/
│   └── tables/
├── .gitignore
├── README.md
└── requirements.txt

## Data Preparation

The cleaning process included:

- Standardising column names
- Converting funding values to numeric format
- Converting signature dates to datetime format
- Checking project identifiers for uniqueness
- Reconciling raw and cleaned funding totals
- Checking consistency between recorded years and signature dates
- Categorising project funding values
- Replacing missing project-grouping and CAP-code values with `Not Specified`
- Exporting the cleaned dataset without an unnecessary index column

`Not Specified` is a transparent missing-data label. It is not an invented value or statistical imputation.

## Validation

The following checks were performed:

- Row count preserved
- Project IDs remain unique
- Project codes remain unique
- No missing funding values
- All dates converted successfully
- No year mismatches
- Missing grouping values resolved
- Missing CAP-code values resolved
- Funding categories complete
- Raw and cleaned funding totals reconcile

All validation checks passed.

## Sector Methodology

Some projects contain multiple sectors in one field. Funding was analysed using the original sector combinations exactly as recorded.

The full project amount was not assigned separately to every individual sector because doing so would double-count funding.

## Annual Trend Methodology

Years without supplied project records are displayed as gaps rather than automatically treated as zero-funding years.

The 2026 values represent a partial year because the latest project signature date in the supplied dataset is 3 June 2026.

## Installation

Clone or download the project and open the main project folder in a terminal.

Create and activate a virtual environment:

```bash
python3 -m venv myenv
source myenv/bin/activate
```

Install the required packages:

```bash
pip install -r requirements.txt
```

## Run the Dashboard

From the main `cerf-nigeria-capstone` project folder, run:

```bash
streamlit run app.py
```

Then open the local address displayed in the terminal, normally:

```text
http://localhost:8501
```

## Run the Notebook

Open:

```text
notebooks/CERF_Nigeria_Analysis.ipynb
```

Select the project’s `myenv` Python kernel and run all cells from beginning to end.

## Tools and Technologies

- Python
- Pandas
- NumPy
- Plotly
- Streamlit
- Jupyter Notebook
- Visual Studio Code

## Limitations

- The analysis is limited to records contained in the supplied dataset.
- Approved funding does not necessarily equal actual expenditure.
- Funding amounts do not measure beneficiaries reached, programme quality or impact.
- Missing crisis-grouping and CAP-code information limits some interpretations.
- Multi-sector combinations cannot be interpreted as separate sector allocations.
- Years without records cannot automatically be interpreted as years with zero CERF funding.
- The 2026 data represents a partial year.
- Observed patterns are descriptive and do not establish causality.

## Author

Kimto Oche Emmanuel
