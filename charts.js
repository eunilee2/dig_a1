
const fig_1 = {
  "data": {"url": "data/fatal_overdoses_2007_2025.csv"},
  "title": "Number of Fatal Overdose Cases by Year",
  "width": 400,
  "height": 350,
  "mark": "bar",
  "encoding": {
    "x": {"field": "case_year", "type": "ordinal", "title": "Year"},
    "y": {"aggregate": "count", "title": "Number of Cases"}
  }
};

// Aggregate by Month
const fig_2 = {
  "data": {"url": "data/fatal_overdoses_2007_2025.csv"},
  "title": "Number of Fatal Overdose Cases by Month (Colored by Season)",
  "transform": [
    {
      "calculate": "['Winter','Winter','Spring','Spring','Spring','Summer','Summer','Summer','Fall','Fall','Fall','Winter'][month(datum.death_date_and_time)]",
      "as": "season"
    }
  ],
  "width": 400,
  "height": 350,
  "layer": [
    {
      "mark": "bar",
      "encoding": {
        "y": {
          "field": "death_date_and_time",
          "type": "ordinal",
          "timeUnit": "month",
          "title": "Month",
          "axis": {"format": "%b"}
        },
        "x": {"aggregate": "count", "title": "Number of Cases"},
        "color": {
          "field": "season",
          "type": "nominal",
          "title": "Season",
          "scale": {
            "domain": ["Winter", "Spring", "Summer", "Fall"],
            "range": ["#7fa7d6", "#a7d67f", "#ffd966", "#ffb366"]
          }
        }
      }
    },
    {
      "mark": {"type": "text", "align": "left", "baseline": "middle", "dx": 3},
      "encoding": {
        "y": {
          "field": "death_date_and_time",
          "type": "ordinal",
          "timeUnit": "month"
        },
        "x": {"aggregate": "count", "type": "quantitative"},
        "text": {"aggregate": "count", "type": "quantitative"},
        "color": {"value": "black"}
      }
    }
  ]
};

const fig_3 = {
  "data": {"url": "data/fatal_overdoses_2007_2025.csv"},
  "title": "Number of Fatal Overdose Cases by Day of Week",
  "transform": [
    {
      "calculate": "['Sunday','Monday','Tuesday','Wednesday','Thursday','Friday','Saturday'][day(datum.death_date_and_time)]",
      "as": "day_of_week"
    }
  ],
  "width": 400,
  "height": 350,
  "layer": [
    {
      "mark": "bar",
      "encoding": {
        "x": {"field": "day_of_week", "type": "ordinal", "title": "Day of Week", "sort": ["Sunday", "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"]},
        "y": {"aggregate": "count", "title": "Number of Cases", "type": "quantitative"},
        "color": {"field": "day_of_week", "type": "nominal", "legend": null}
      }
    },
    {
      "mark": {"type": "text", "dy": -8, "fontWeight": "bold"},
      "encoding": {
        "x": {"field": "day_of_week", "type": "ordinal", "sort": ["Sunday", "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"]},
        "y": {"aggregate": "count", "type": "quantitative"},
        "text": {"aggregate": "count", "type": "quantitative"},
        "color": {"value": "black"}
      }
    }
  ]
};

const fig_4 = {
  "data": {"url": "data/fatal_overdoses_2007_2025.csv"},
  "title": "Top Ten Zips: Number of Fatal Overdose Cases by Zip (Aggregate 2007-2024)",
  "transform": [
    {"calculate": "datum.incident_zip === null || datum.incident_zip === '' ? 'Unknown Zip' : datum.incident_zip", "as": "incident_zip"},
    {"filter": "datum.case_year >= 2007 && datum.case_year <= 2024"},
    {"aggregate": [{"op": "count", "as": "count"}], "groupby": ["incident_zip"]},
    {"window": [{"op": "rank", "field": "count", "as": "rank"}], "sort": [{"field": "count", "order": "descending"}]},
    {"filter": "datum.rank <= 10"}
  ],
  "mark": "bar",
  "encoding": {
    "y": {"field": "incident_zip", "type": "ordinal", "title": "ZIP Code", "sort": "-x"},
    "x": {"field": "count", "type": "quantitative", "title": "Number of Cases"}
  }
};


const fig_7 = {
  "$schema": "https://vega.github.io/schema/vega-lite/v5.json",
  "hconcat": [
    {
      // Race donut + minority table underneath
      "vconcat": [
        {
          "title": "Fatal Overdose Cases by Race",
    // ...existing code...
          "transform": [
            {
              "calculate": "datum.race == 'W' ? 'White' : datum.race == 'B' ? 'Black' : datum.race == 'H' ? 'Hispanic' : datum.race == 'A' ? 'Asian' : datum.race == 'I' ? 'American Indian/Alaska Native' : datum.race == 'M' ? 'Mixed' : datum.race == 'O' ? 'Other' : 'Unknown'",
              "as": "race_label"
            },
            {"aggregate": [{"op": "count", "as": "cases"}], "groupby": ["race_label"]},
            {"joinaggregate": [{"op": "sum", "field": "cases", "as": "total_cases"}]},
            {"calculate": "datum.cases / datum.total_cases", "as": "pct"}
          ],
          "mark": {"type": "arc", "innerRadius": 60},
          "encoding": {
            "theta": {"field": "cases", "type": "quantitative"},
            "color": {
              "field": "race_label",
              "type": "nominal",
              "title": "Race",
              "legend": {"orient": "bottom"}
            },
            "tooltip": [
              {"field": "race_label", "type": "nominal", "title": "Race"},
              {"field": "cases", "type": "quantitative", "title": "Cases"},
              {"field": "pct", "type": "quantitative", "title": "Share", "format": ".1%"}
            ]
          },
          "view": {"stroke": null}
        },
        {
        "title": {"text": "Minority Race Breakdown (Counts, % of all, % of minority)", "anchor": "start", "fontSize": 12},
        "data": {"url": "/data/fatal_overdoses_allegheny_only.csv"},
          // ...existing code...
        "transform": [
            {
            "calculate": "datum.race == 'W' ? 'White' : datum.race == 'B' ? 'Black' : datum.race == 'H' ? 'Hispanic' : datum.race == 'A' ? 'Asian' : datum.race == 'I' ? 'American Indian/Alaska Native' : datum.race == 'M' ? 'Mixed' : datum.race == 'O' ? 'Other' : 'Unknown'",
            "as": "race_label"
            },
            {"aggregate": [{"op": "count", "as": "cases"}], "groupby": ["race_label"]},

            /* compute overall total BEFORE filtering to minority */
            {"joinaggregate": [{"op": "sum", "field": "cases", "as": "total_all"}]},
            {"calculate": "datum.cases / datum.total_all", "as": "pct_all"},

            /* now filter to minority races only */
            {"filter": "datum.race_label != 'White' && datum.race_label != 'Black'"},

            /* compute minority-only total AFTER the filter */
            {"joinaggregate": [{"op": "sum", "field": "cases", "as": "total_minority"}]},
            {"calculate": "datum.cases / datum.total_minority", "as": "pct_minority"},

            {
            "calculate": "datum.race_label + ': ' + datum.cases + ' (' + format(datum.pct_all, '.1%') + ' of all; ' + format(datum.pct_minority, '.1%') + ' of minority)'",
            "as": "row_text"
            },
            {"sort": [{"field": "cases", "order": "descending"}]}
        ],
        "mark": {"type": "text", "align": "left"},
        "encoding": {
            "y": {"field": "race_label", "type": "nominal", "axis": null, "sort": {"field": "cases", "order": "descending"}},
            "text": {"field": "row_text", "type": "nominal"},
            "size": {"value": 11}
        },
        "height": 110
        }

      ],
      "spacing": 8
    },

    {
      "title": "Fatal Overdose Cases by Gender",
      "data": {"url": "/data/fatal_overdoses_allegheny_only.csv"},
      "transform": [
        {"calculate": "datum.sex == 'M' ? 'Male' : datum.sex == 'F' ? 'Female' : 'Unknown'", "as": "sex_label"},
        {"aggregate": [{"op": "count", "as": "cases"}], "groupby": ["sex_label"]},
        {"joinaggregate": [{"op": "sum", "field": "cases", "as": "total_cases"}]},
        {"calculate": "datum.cases / datum.total_cases", "as": "pct"}
      ],
      "mark": {"type": "arc", "innerRadius": 60},
      "encoding": {
        "theta": {"field": "cases", "type": "quantitative"},
        "color": {
          "field": "sex_label",
          "type": "nominal",
          "title": "Gender",
          "legend": {"orient": "bottom"}
        },
        "tooltip": [
          {"field": "sex_label", "type": "nominal", "title": "Gender"},
            "data": {"url": "data/fatal_overdoses_allegheny_only.csv"},
          {"field": "pct", "type": "quantitative", "title": "Share", "format": ".1%"}
        ]
      },
      "view": {"stroke": null}
    },

    {
      "title": "Fatal Overdose Cases by Age Group",
      "data": {"url": "/data/fatal_overdoses_allegheny_only.csv"},
      "transform": [
        {"calculate": "toNumber(datum.age)", "as": "age_num"},
        {
          "calculate": "isValid(datum.age_num) && datum.age_num >= 0 && datum.age_num < 25 ? '0–24' : isValid(datum.age_num) && datum.age_num < 35 ? '25–34' : isValid(datum.age_num) && datum.age_num < 45 ? '35–44' : isValid(datum.age_num) && datum.age_num < 55 ? '45–54' : isValid(datum.age_num) && datum.age_num < 65 ? '55–64' : isValid(datum.age_num) && datum.age_num >= 65 ? '65+' : 'Unknown'",
          "as": "age_group_6"
        },
        {"aggregate": [{"op": "count", "as": "cases"}], "groupby": ["age_group_6"]},
        {"joinaggregate": [{"op": "sum", "field": "cases", "as": "total_cases"}]},
        {"calculate": "datum.cases / datum.total_cases", "as": "pct"}
      ],
      "mark": {"type": "arc", "innerRadius": 60},
      "encoding": {
        "theta": {"field": "cases", "type": "quantitative"},
        "color": {
          "field": "age_group_6",
          "type": "ordinal",
          "title": "Age Group",
          "sort": ["0–24", "25–34", "35–44", "45–54", "55–64", "65+", "Unknown"],
          "legend": {"orient": "bottom"}
        },
        "tooltip": [
          {"field": "age_group_6", "type": "nominal", "title": "Age Group"},
          {"field": "cases", "type": "quantitative", "title": "Cases"},
          {"field": "pct", "type": "quantitative", "title": "Share", "format": ".1%"}
        ]
      },
      "view": {"stroke": null}
    }
  ],
  "config": {
          "data": {"url": "data/fatal_overdoses_allegheny_only.csv"},
  }
};


const fig_8A = {
  "data": {"url": "data/fatal_overdoses_2007_2025.csv"},
  "title": "Overdose Cases by Race (Black/White) and Year",
  "transform": [
    {"filter": "datum.race === 'B' || datum.race === 'W'"},
    {"filter": "datum.case_year == 2007 || datum.case_year == 2016 || datum.case_year == 2017 || datum.case_year == 2023"}
  ],
  "mark": "bar",
  "width": 350,
  "height": 300,
  "encoding": {
    "x": {"field": "case_year", "type": "ordinal", "title": "Year"},
    "y": {"aggregate": "count", "title": "Number of Cases"},
    "color": {"field": "race", "type": "nominal", "title": "Race", "scale": {"domain": ["B", "W"], "range": ["#444", "#ccc"]}},
    "column": {"field": "race", "type": "nominal", "title": "Race", "spacing": 10}
  }
};

const fig_8B = {
  "data": {"url": "data/fatal_overdoses_2007_2025.csv"},
  "title": "Overdose Cases by Sex and Year",
  "transform": [
          "data": {"url": "data/fatal_overdoses_allegheny_only.csv"},
    {"filter": "datum.case_year == 2007 || datum.case_year == 2016 || datum.case_year == 2017 || datum.case_year == 2023"}
  ],
  "mark": "bar",
  "width": 350,
  "height": 300,
  "encoding": {
    "x": {"field": "case_year", "type": "ordinal", "title": "Year"},
    "y": {"aggregate": "count", "title": "Number of Cases"},
    "color": {"field": "sex", "type": "nominal", "title": "Sex", "scale": {"domain": ["M", "F"], "range": ["#4e79a7", "#f28e2b"]}},
    "column": {"field": "sex", "type": "nominal", "title": "Sex", "spacing": 10}
  }
};

const fig_8C = {
  "data": {"url": "data/fatal_overdoses_2007_2025.csv"},
  "title": "Overdose Cases by Age Group and Year",
  "transform": [
    {"filter": "datum.case_year == 2007 || datum.case_year == 2016 || datum.case_year == 2017 || datum.case_year == 2023"},
    {"calculate": "toNumber(datum.age)", "as": "age_num"},
    {
      "calculate": "isValid(datum.age_num) && datum.age_num >= 0 && datum.age_num < 25 ? '0–24' : isValid(datum.age_num) && datum.age_num < 35 ? '25–34' : isValid(datum.age_num) && datum.age_num < 45 ? '35–44' : isValid(datum.age_num) && datum.age_num < 55 ? '45–54' : isValid(datum.age_num) && datum.age_num < 65 ? '55–64' : isValid(datum.age_num) && datum.age_num >= 65 ? '65+' : 'Unknown'",
      "as": "age_group"
    }
  ],
  "mark": "bar",
  "width": 350,
  "height": 60,
  "encoding": {
    "y": {"field": "case_year", "type": "ordinal", "title": "Year"},
    "x": {"aggregate": "count", "title": "Number of Cases"},
    "color": {"field": "age_group", "type": "ordinal", "title": "Age Group", "sort": ["0–24", "25–34", "35–44", "45–54", "55–64", "65+", "Unknown"]},
    "row": {"field": "age_group", "type": "ordinal", "title": "Age Group", "sort": ["0–24", "25–34", "35–44", "45–54", "55–64", "65+", "Unknown"], "spacing": 8}
  }
};


const fig_9 = {
  "data": {"url": "data/fatal_overdoses_allegheny_only_long.csv"},
  "title": "Most Common Drugs in Fatal Overdose Cases (Any Involvement)",
  "transform": [
    {"aggregate": [{"op": "count", "as": "case_count"}], "groupby": ["drug"]},
    {"window": [{"op": "rank", "field": "case_count", "as": "rank"}], "sort": [{"field": "case_count", "order": "descending"}]},
    {"filter": "datum.rank <= 10"}
  ],
  "width": 400,
  "height": 350,
  "layer": [
    {
      "mark": "bar",
      "encoding": {
        "y": {"field": "drug", "type": "ordinal", "title": "Drug", "sort": "-x"},
        "x": {"field": "case_count", "type": "quantitative", "title": "Number of Cases"},
        "color": {"field": "drug", "type": "nominal", "legend": null}
      }
    },
    {
      "mark": {"type": "text", "align": "left", "baseline": "middle", "dx": 3},
      "encoding": {
        "y": {"field": "drug", "type": "ordinal", "sort": "-x"},
        "x": {"field": "case_count", "type": "quantitative"},
        "text": {"field": "case_count", "type": "quantitative"},
        "color": {"value": "black"}
      }
    }
  ]
};

const fig_10 = {
  "data": {"url": "data/fatal_overdoses_allegheny_only_drugtype.csv"},
  "title": "Single Drug vs. Polysubstance Overdose Cases",
  "transform": [
    {"filter": "datum.drug_case_type === 'Single' || datum.drug_case_type === 'Poly'"},
    {"aggregate": [{"op": "count", "as": "case_count"}], "groupby": ["drug_case_type"]}
  ],
  "width": 300,
  "height": 300,
  "layer": [
    {
      "mark": "bar",
      "encoding": {
        "y": {"field": "drug_case_type", "type": "nominal", "title": "Case Type", "sort": ["Single", "Poly"]},
        "x": {"field": "case_count", "type": "quantitative", "title": "Number of Cases"},
        "color": {"field": "drug_case_type", "type": "nominal", "legend": null}
      }
    },
    {
      "mark": {"type": "text", "align": "left", "baseline": "middle", "dx": 3},
      "encoding": {
        "y": {"field": "drug_case_type", "type": "nominal", "sort": ["Single", "Poly"]},
        "x": {"field": "case_count", "type": "quantitative"},
        "text": {"field": "case_count", "type": "quantitative"},
        "color": {"value": "black"}
      }
    }
  ]
};

vegaEmbed("#fig_1", fig_1)
  .then(console.log)
  .catch(console.error);

vegaEmbed("#fig_2", fig_2)
  .then(console.log)
  .catch(console.error);

vegaEmbed("#fig_3", fig_3)
  .then(console.log)
  .catch(console.error);

vegaEmbed("#fig_4", fig_4)
  .then(console.log)
  .catch(console.error);

vegaEmbed("#fig_7", fig_7)
  .then(console.log)
  .catch(console.error);

vegaEmbed("#fig_8A", fig_8A)
  .then(console.log)
  .catch(console.error);
vegaEmbed("#fig_8B", fig_8B)
  .then(console.log)
  .catch(console.error);
vegaEmbed("#fig_8C", fig_8C)
  .then(console.log)
  .catch(console.error);

vegaEmbed("#fig_9", fig_9)
  .then(console.log)
  .catch(console.error);

vegaEmbed("#fig_10", fig_10)
  .then(console.log)
  .catch(console.error);
