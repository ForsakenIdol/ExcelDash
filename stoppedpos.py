import pandas as pd
import plotly.express as px

def stoppedpos(groupby_num=1):
    bar_filters = ["HOLEID", "REGION", "REGIONPIT", "SUBREGIONPIT", "SURVEY_STATUS"]
    groupby = bar_filters[groupby_num]

    dframe = pd.read_excel("LAS file.xlsx", engine="openpyxl")
    positions = dframe[dframe["LAS_READING_DEPTH"].notna()].filter(items=bar_filters).sort_values([groupby, bar_filters[len(bar_filters) - 1]])

    counts = []
    count = 0
    current_region = ""
    current_position = ""
    for headers, data in positions.iterrows():
        if (data[bar_filters[len(bar_filters) - 1]] != current_position and current_position != ""): # Change in current_position value
            if (current_region != ""): counts.append({
                groupby: current_region,
                bar_filters[len(bar_filters) - 1]: current_position,
                "COUNT": count
            })
            count = 0
        current_region = data[groupby]
        current_position = data[bar_filters[len(bar_filters) - 1]]
        count += 1

    # Append the final row
    counts.append({ groupby: current_region, bar_filters[len(bar_filters) - 1]: current_position, "COUNT": count })

    df_counts = pd.DataFrame(data=counts)
    return px.bar(df_counts, x=groupby, y="COUNT", color=bar_filters[len(bar_filters) - 1], title="{} VALUES BY {}".format(bar_filters[len(bar_filters) - 1], groupby))