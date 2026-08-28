from pathlib import Path

import pandas as pd
import plotly.express as px
import streamlit as st


# Configure the dashboard before displaying other elements
st.set_page_config(
    page_title="CERF Nigeria Funding Dashboard",
    page_icon="🌍",
    layout="wide",
    initial_sidebar_state="expanded"
)


# Identify the project folder
project_root = Path(__file__).resolve().parent

data_path = (
    project_root
    / "data"
    / "processed"
    / "cerf_nigeria_cleaned.csv"
)


@st.cache_data
def load_data(file_path):
    """Load and prepare the cleaned CERF dataset."""
    data = pd.read_csv(
        file_path,
        parse_dates=["date_usg_signature"]
    )

    data["year"] = data["year"].astype(int)

    return data


# Stop the application gracefully if the dataset is unavailable
if not data_path.exists():
    st.error(
        "The cleaned dataset could not be found at "
        f"{data_path}"
    )
    st.stop()


df = load_data(data_path)

st.title("CERF Nigeria Funding Dashboard")

st.markdown(
    """
    Explore approved Central Emergency Response Fund projects
    represented in the supplied Nigeria dataset. Use the sidebar
    filters to examine funding patterns across years, agencies,
    emergencies and CERF funding windows.
    """
)

st.caption(
    "Funding values represent approved project allocations. "
    "The dataset does not measure humanitarian outcomes, "
    "programme effectiveness or unmet need."
)

st.sidebar.header("Dashboard Filters")

available_years = sorted(df["year"].dropna().unique())

selected_years = st.sidebar.multiselect(
    "Select signature year(s)",
    options=available_years,
    default=available_years
)

available_agencies = sorted(
    df["agency_name"].dropna().unique()
)

selected_agencies = st.sidebar.multiselect(
    "Select implementing agency",
    options=available_agencies,
    default=available_agencies
)

available_emergencies = sorted(
    df["emergency_type_name"].dropna().unique()
)

selected_emergencies = st.sidebar.multiselect(
    "Select emergency type",
    options=available_emergencies,
    default=available_emergencies
)

available_windows = sorted(
    df["window_full_name"].dropna().unique()
)

selected_windows = st.sidebar.multiselect(
    "Select CERF funding window",
    options=available_windows,
    default=available_windows
)

filtered_df = df[
    df["year"].isin(selected_years)
    & df["agency_name"].isin(selected_agencies)
    & df["emergency_type_name"].isin(
        selected_emergencies
    )
    & df["window_full_name"].isin(
        selected_windows
    )
].copy()


if filtered_df.empty:
    st.warning(
        "No projects match the selected filters. "
        "Please broaden your selection."
    )
    st.stop()


st.sidebar.markdown("---")

st.sidebar.caption(
    f"{len(filtered_df):,} of {len(df):,} projects displayed"
)

total_funding = filtered_df[
    "total_amount_approved"
].sum()

project_count = filtered_df["project_id"].nunique()

agency_count = filtered_df["agency_name"].nunique()

average_project_funding = filtered_df[
    "total_amount_approved"
].mean()


st.subheader("Portfolio Overview")

kpi_1, kpi_2, kpi_3, kpi_4 = st.columns(4)

kpi_1.metric(
    "Approved Funding",
    f"${total_funding / 1_000_000:,.1f}M"
)

kpi_2.metric(
    "Projects",
    f"{project_count:,}"
)

kpi_3.metric(
    "Implementing Agencies",
    f"{agency_count:,}"
)

kpi_4.metric(
    "Average Project Funding",
    f"${average_project_funding / 1_000_000:,.2f}M"
)

st.markdown("---")
st.subheader("Funding Distribution and Trends")

agency_summary = (
    filtered_df
    .groupby("agency_name", as_index=False)
    .agg(
        total_funding=(
            "total_amount_approved",
            "sum"
        ),
        project_count=(
            "project_id",
            "nunique"
        )
    )
    .sort_values(
        "total_funding",
        ascending=True
    )
)


agency_abbreviations = {
    "United Nations Children’s Fund": "UNICEF",
    "World Health Organization": "WHO",
    "World Food Programme": "WFP",
    "United Nations Population Fund": "UNFPA",
    "International Organization for Migration": "IOM",
    "United Nations High Commissioner for Refugees": "UNHCR",
    "Food and Agriculture Organization": "FAO",
    "United Nations Development Programme": "UNDP"
}


agency_summary["agency_short"] = (
    agency_summary["agency_name"]
    .map(agency_abbreviations)
    .fillna(agency_summary["agency_name"])
)

agency_summary["funding_label"] = (
    agency_summary["total_funding"]
    .map(lambda value: f"${value / 1_000_000:.1f}M")
)


fig_agency = px.bar(
    agency_summary,
    x="total_funding",
    y="agency_short",
    orientation="h",
    text="funding_label",
    title="Funding by Implementing Agency",
    labels={
        "total_funding": "Approved funding (US$)",
        "agency_short": ""
    },
    hover_data={
        "agency_name": True,
        "project_count": True,
        "funding_label": False
    },
    color_discrete_sequence=["#185A8D"]
)

fig_agency.update_traces(
    textposition="outside",
    cliponaxis=False
)

fig_agency.update_layout(
    height=500,
    showlegend=False,
    margin=dict(l=40, r=70, t=70, b=50),
    xaxis=dict(
        tickprefix="$",
        tickformat=".2s"
    ),
    yaxis=dict(
        title="",
        automargin=True
    )
)

fig_agency.update_xaxes(
    range=[
        0,
        agency_summary["total_funding"].max() * 1.20
    ]
)

annual_summary = (
    filtered_df
    .groupby("year", as_index=False)
    .agg(
        total_funding=(
            "total_amount_approved",
            "sum"
        ),
        project_count=(
            "project_id",
            "nunique"
        )
    )
    .sort_values("year")
)


complete_years = pd.DataFrame({
    "year": range(
        int(filtered_df["year"].min()),
        int(filtered_df["year"].max()) + 1
    )
})

annual_chart_data = complete_years.merge(
    annual_summary,
    on="year",
    how="left"
)


fig_annual = px.line(
    annual_chart_data,
    x="year",
    y="total_funding",
    markers=True,
    title="Annual Approved Funding",
    labels={
        "year": "Signature year",
        "total_funding": "Approved funding (US$)"
    },
    hover_data={
        "project_count": True,
        "total_funding": ":$,.2f"
    }
)

fig_annual.update_traces(
    line=dict(
        color="#185A8D",
        width=3
    ),
    marker=dict(
        color="#E9A23B",
        size=8
    ),
    connectgaps=False
)

fig_annual.update_layout(
    height=500,
    showlegend=False,
    margin=dict(l=50, r=30, t=70, b=70),
    xaxis=dict(
        dtick=1,
        tickangle=-45
    ),
    yaxis=dict(
        tickprefix="$",
        tickformat=".2s"
    )
)

chart_col_1, chart_col_2 = st.columns(2)

with chart_col_1:
    st.plotly_chart(
        fig_agency,
        use_container_width=True
    )

with chart_col_2:
    st.plotly_chart(
        fig_annual,
        use_container_width=True
    )


st.caption(
    "Gaps in the annual chart indicate years for which the "
    "supplied dataset contains no matching records. "
    "The 2026 figures represent a partial year."
)

st.markdown("---")
st.subheader("Emergency and Funding-Window Analysis")

emergency_summary = (
    filtered_df
    .groupby("emergency_type_name", as_index=False)
    .agg(
        total_funding=(
            "total_amount_approved",
            "sum"
        ),
        project_count=(
            "project_id",
            "nunique"
        )
    )
    .sort_values(
        "total_funding",
        ascending=True
    )
)

emergency_summary["funding_label"] = (
    emergency_summary["total_funding"]
    .map(lambda value: f"${value / 1_000_000:.1f}M")
)


fig_emergency = px.bar(
    emergency_summary,
    x="total_funding",
    y="emergency_type_name",
    orientation="h",
    text="funding_label",
    title="Funding by Emergency Type",
    labels={
        "total_funding": "Approved funding (US$)",
        "emergency_type_name": ""
    },
    hover_data={
        "project_count": True,
        "funding_label": False
    },
    color_discrete_sequence=["#287D8E"]
)

fig_emergency.update_traces(
    textposition="outside",
    cliponaxis=False
)

fig_emergency.update_layout(
    height=500,
    showlegend=False,
    margin=dict(l=40, r=70, t=70, b=50),
    xaxis=dict(
        tickprefix="$",
        tickformat=".2s"
    ),
    yaxis=dict(
        title="",
        automargin=True
    )
)

fig_emergency.update_xaxes(
    range=[
        0,
        emergency_summary["total_funding"].max() * 1.20
    ]
)

window_summary = (
    filtered_df
    .groupby("window_full_name", as_index=False)
    .agg(
        total_funding=(
            "total_amount_approved",
            "sum"
        ),
        project_count=(
            "project_id",
            "nunique"
        )
    )
    .sort_values(
        "total_funding",
        ascending=False
    )
)


window_colours = {
    "Rapid Response": "#185A8D",
    "Underfunded Emergencies": "#E9A23B"
}


fig_window = px.pie(
    window_summary,
    values="total_funding",
    names="window_full_name",
    hole=0.55,
    title="Funding Distribution by CERF Window",
    color_discrete_sequence=[
        "#185A8D",
        "#E9A23B"
    ],
    hover_data={
        "project_count": True
    }
)

fig_window.update_traces(
    textposition="inside",
    textinfo="percent"
)

fig_window.update_layout(
    height=500,
    margin=dict(l=30, r=30, t=70, b=50),
    legend=dict(
        orientation="h",
        title_text="",
        yanchor="top",
        y=-0.05,
        xanchor="center",
        x=0.5
    )
)

emergency_col, window_col = st.columns(2)

with emergency_col:
    st.plotly_chart(
        fig_emergency,
        use_container_width=True
    )

with window_col:
    st.plotly_chart(
        fig_window,
        use_container_width=True
    )


st.caption(
    "These charts show approved funding allocation patterns. "
    "They do not establish relative humanitarian need or "
    "programme effectiveness."
)

st.markdown("---")
st.subheader("Sector and Crisis Analysis")

sector_summary = (
    filtered_df
    .groupby("project_sectors", as_index=False)
    .agg(
        total_funding=(
            "total_amount_approved",
            "sum"
        ),
        project_count=(
            "project_id",
            "nunique"
        )
    )
    .sort_values(
        "total_funding",
        ascending=False
    )
    .head(10)
    .sort_values(
        "total_funding",
        ascending=True
    )
)


sector_summary["sector_short"] = (
    sector_summary["project_sectors"]
    .map(
        lambda text:
        text if len(text) <= 35
        else text[:32] + "..."
    )
)

sector_summary["funding_label"] = (
    sector_summary["total_funding"]
    .map(lambda value: f"${value / 1_000_000:.1f}M")
)


fig_sector = px.bar(
    sector_summary,
    x="total_funding",
    y="sector_short",
    orientation="h",
    text="funding_label",
    title="Top Sector Combinations by Funding",
    labels={
        "total_funding": "Approved funding (US$)",
        "sector_short": ""
    },
    hover_data={
        "project_sectors": True,
        "project_count": True,
        "funding_label": False
    },
    color_discrete_sequence=["#287D8E"]
)

fig_sector.update_traces(
    textposition="outside",
    cliponaxis=False
)

fig_sector.update_layout(
    height=590,
    showlegend=False,
    margin=dict(l=40, r=70, t=70, b=50),
    xaxis=dict(
        tickprefix="$",
        tickformat=".2s"
    ),
    yaxis=dict(
        title="",
        automargin=True
    )
)

fig_sector.update_xaxes(
    range=[
        0,
        sector_summary["total_funding"].max() * 1.20
    ]
)

crisis_summary = (
    filtered_df
    .groupby("project_groupings", as_index=False)
    .agg(
        total_funding=(
            "total_amount_approved",
            "sum"
        ),
        project_count=(
            "project_id",
            "nunique"
        )
    )
    .sort_values(
        "total_funding",
        ascending=True
    )
)


crisis_summary["funding_label"] = (
    crisis_summary["total_funding"]
    .map(lambda value: f"${value / 1_000_000:.1f}M")
)

crisis_summary["grouping_status"] = (
    crisis_summary["project_groupings"]
    .map(
        lambda value:
        "Not Specified"
        if value == "Not Specified"
        else "Named crisis"
    )
)


fig_crisis = px.bar(
    crisis_summary,
    x="total_funding",
    y="project_groupings",
    orientation="h",
    text="funding_label",
    color="grouping_status",
    title="Funding by Recorded Crisis Grouping",
    labels={
        "total_funding": "Approved funding (US$)",
        "project_groupings": "",
        "grouping_status": "Grouping status"
    },
    color_discrete_map={
        "Not Specified": "#E9A23B",
        "Named crisis": "#185A8D"
    },
    hover_data={
        "project_count": True,
        "funding_label": False
    }
)

fig_crisis.update_traces(
    textposition="outside",
    cliponaxis=False
)

fig_crisis.update_layout(
    height=590,
    showlegend=False,
    margin=dict(l=40, r=70, t=70, b=50),
    xaxis=dict(
        tickprefix="$",
        tickformat=".2s"
    ),
    yaxis=dict(
        title="",
        automargin=True
    )
)

fig_crisis.update_xaxes(
    range=[
        0,
        crisis_summary["total_funding"].max() * 1.20
    ]
)

sector_col, crisis_col = st.columns(2)

with sector_col:
    st.plotly_chart(
        fig_sector,
        use_container_width=True
    )

with crisis_col:
    st.plotly_chart(
        fig_crisis,
        use_container_width=True
    )


st.caption(
    "Multi-sector projects are analysed using their original "
    "sector combinations to avoid counting the full project "
    "funding repeatedly. 'Not Specified' identifies missing "
    "source information and is not an estimated crisis category."
)

st.markdown("---")
st.subheader("Largest Funded Projects")

top_projects = (
    filtered_df
    .nlargest(
        10,
        "total_amount_approved"
    )[
        [
            "project_code",
            "project_title",
            "agency_name",
            "year",
            "emergency_type_name",
            "window_full_name",
            "total_amount_approved"
        ]
    ]
    .sort_values(
        "total_amount_approved",
        ascending=True
    )
    .copy()
)


top_projects["funding_label"] = (
    top_projects["total_amount_approved"]
    .map(lambda value: f"${value / 1_000_000:.1f}M")
)


fig_projects = px.bar(
    top_projects,
    x="total_amount_approved",
    y="project_code",
    orientation="h",
    text="funding_label",
    title="Ten Largest Projects in the Current Selection",
    labels={
        "total_amount_approved": "Approved funding (US$)",
        "project_code": "Project code"
    },
    hover_data={
        "project_title": True,
        "agency_name": True,
        "year": True,
        "emergency_type_name": True,
        "window_full_name": True,
        "funding_label": False
    },
    color_discrete_sequence=["#185A8D"]
)

fig_projects.update_traces(
    textposition="outside",
    cliponaxis=False
)

fig_projects.update_layout(
    height=600,
    showlegend=False,
    margin=dict(l=100, r=80, t=70, b=60),
    xaxis=dict(
        tickprefix="$",
        tickformat=".2s"
    ),
    yaxis=dict(
        title="Project code",
        automargin=True
    )
)

fig_projects.update_xaxes(
    range=[
        0,
        top_projects["total_amount_approved"].max() * 1.20
    ]
)


st.plotly_chart(
    fig_projects,
    use_container_width=True
)

st.subheader("Filtered Project Records")

project_records = (
    filtered_df[
        [
            "project_code",
            "project_title",
            "agency_name",
            "year",
            "emergency_type_name",
            "window_full_name",
            "project_sectors",
            "total_amount_approved"
        ]
    ]
    .sort_values(
        "total_amount_approved",
        ascending=False
    )
    .rename(
        columns={
            "project_code": "Project Code",
            "project_title": "Project Title",
            "agency_name": "Agency",
            "year": "Year",
            "emergency_type_name": "Emergency Type",
            "window_full_name": "Funding Window",
            "project_sectors": "Sector Combination",
            "total_amount_approved": "Approved Funding"
        }
    )
)


st.dataframe(
    project_records,
    use_container_width=True,
    hide_index=True,
    column_config={
        "Approved Funding": st.column_config.NumberColumn(
            "Approved Funding",
            format="$%.2f"
        )
    }
)

download_data = project_records.to_csv(
    index=False
).encode("utf-8")


st.download_button(
    label="Download Filtered Project Records",
    data=download_data,
    file_name="cerf_nigeria_filtered_projects.csv",
    mime="text/csv"
)


st.caption(
    "The table and downloaded CSV reflect the current "
    "dashboard filter selections."
)

st.markdown("---")
st.subheader("Executive Insights")

leading_agency = (
    filtered_df
    .groupby("agency_name")["total_amount_approved"]
    .sum()
    .sort_values(ascending=False)
)

leading_emergency = (
    filtered_df
    .groupby("emergency_type_name")[
        "total_amount_approved"
    ]
    .sum()
    .sort_values(ascending=False)
)

leading_sector = (
    filtered_df
    .groupby("project_sectors")[
        "total_amount_approved"
    ]
    .sum()
    .sort_values(ascending=False)
)

leading_year = (
    filtered_df
    .groupby("year")["total_amount_approved"]
    .sum()
    .sort_values(ascending=False)
)

largest_project_row = filtered_df.loc[
    filtered_df["total_amount_approved"].idxmax()
]


st.info(
    f"""
    **Current-selection findings**

    - **Leading agency:** {leading_agency.index[0]}  
      (${leading_agency.iloc[0]:,.2f})

    - **Leading emergency type:** {leading_emergency.index[0]}  
      (${leading_emergency.iloc[0]:,.2f})

    - **Leading sector combination:** {leading_sector.index[0]}  
      (${leading_sector.iloc[0]:,.2f})

    - **Peak funding year:** {int(leading_year.index[0])}  
      (${leading_year.iloc[0]:,.2f})

    - **Largest project:** {largest_project_row['project_code']}  
      (${largest_project_row['total_amount_approved']:,.2f})
    """
)

st.subheader("Data Quality")

data_quality_summary = pd.DataFrame({
    "Field": [
        "Project grouping",
        "Project CAP code"
    ],
    "Not Specified Count": [
        (
            df["project_groupings"]
            == "Not Specified"
        ).sum(),
        (
            df["project_cap_codes"]
            == "Not Specified"
        ).sum()
    ]
})


data_quality_summary["Missing Percentage"] = (
    data_quality_summary["Not Specified Count"]
    / len(df)
    * 100
)

data_quality_summary["Percentage Label"] = (
    data_quality_summary["Missing Percentage"]
    .map(lambda value: f"{value:.1f}%")
)


fig_quality = px.bar(
    data_quality_summary,
    x="Missing Percentage",
    y="Field",
    orientation="h",
    text="Percentage Label",
    title="Missingness in Key Source Fields",
    labels={
        "Missing Percentage": "Records with missing source values (%)",
        "Field": ""
    },
    color_discrete_sequence=["#E9A23B"]
)

fig_quality.update_traces(
    textposition="outside",
    cliponaxis=False
)

fig_quality.update_layout(
    height=350,
    showlegend=False,
    margin=dict(l=40, r=70, t=70, b=50),
    xaxis=dict(
        range=[0, 100],
        ticksuffix="%"
    ),
    yaxis=dict(
        title="",
        automargin=True
    )
)


st.plotly_chart(
    fig_quality,
    use_container_width=True
)

with st.expander("Methodology and limitations"):
    st.markdown(
        """
        - Funding values represent approved project allocations,
          not expenditure, beneficiaries reached or programme impact.
        - Missing project-grouping and CAP-code values were labelled
          **Not Specified** rather than guessed or statistically
          imputed.
        - Multi-sector projects were analysed using the complete
          sector combinations recorded in the source data. This
          prevents the full project amount from being repeatedly
          assigned to individual sectors.
        - Years without supplied project records are displayed as
          gaps rather than interpreted automatically as zero funding.
        - The 2026 figures are partial because the latest signature
          date represented in the dataset is 3 June 2026.
        - Dashboard filters describe allocation patterns within the
          supplied dataset and do not establish humanitarian need,
          causality or programme effectiveness.
        """
    )


st.markdown("---")

st.caption(
    "CERF Nigeria Funding Analysis Dashboard | "
    "Prepared from the supplied project-level dataset"
)
