import streamlit as st
import pandas as pd
import folium

from streamlit_folium import st_folium

from sheets import (
    load_sheet,
    get_towns
)


# =====================================
# PAGE CONFIG
# =====================================

st.set_page_config(
    page_title="Product Availability Intelligence",
    layout="wide"
)


st.title(
    "Product Availability Intelligence"
)


st.write(
    "Analyze pharmacy product availability by territory"
)


# =====================================
# INPUT
# =====================================


sheet_url = st.text_input(
    "Google Sheet URL"
)


if sheet_url:


    try:


        df = load_sheet(
            sheet_url
        )


        # =============================
        # FILTER SECTION
        # =============================


        towns = get_towns(
            df
        )


        selected_towns = st.multiselect(

            "Select Towns",

            towns

        )



        selected_status = st.multiselect(

            "Availability Status",

            [
                "YES",
                "NO"
            ],

            default=[
                "YES",
                "NO"
            ]

        )



        filtered_df = df.copy()



        # town filter


        if selected_towns:


            filtered_df = filtered_df[

                filtered_df["Town"]
                .isin(
                    selected_towns
                )

            ]



        # availability filter


        filtered_df = filtered_df[

            filtered_df["Availability"]
            .isin(
                selected_status
            )

        ]



        # =============================
        # KPI SECTION
        # =============================


        st.divider()


        st.header(
            "Availability Summary"
        )



        total_store = len(
            filtered_df
        )



        available = len(

            filtered_df[

                filtered_df["Availability"]

                ==

                "YES"

            ]

        )



        unavailable = len(

            filtered_df[

                filtered_df["Availability"]

                ==

                "NO"

            ]

        )



        coverage = (

            round(
                available /
                total_store *
                100,
                1
            )

            if total_store > 0

            else 0

        )



        c1,c2,c3,c4 = st.columns(
            4
        )


        c1.metric(

            "Total Stores",

            total_store

        )


        c2.metric(

            "Available",

            available

        )


        c3.metric(

            "Not Available",

            unavailable

        )


        c4.metric(

            "Coverage %",

            f"{coverage}%"

        )



        # =============================
        # STORE TABLE
        # =============================


        st.divider()


        st.header(
            "Store List"
        )



        show_columns = [

            "Customer name",

            "Town",

            "Location",

            "Availability",

            "Latitude",

            "Longitude"

        ]



        available_cols = [

            col

            for col in show_columns

            if col in filtered_df.columns

        ]



        st.dataframe(

            filtered_df[
                available_cols
            ],

            use_container_width=True

        )



        # =============================
        # MAP VIEW
        # =============================


        st.divider()


        st.header(
            "Availability Map"
        )



        if len(filtered_df) > 0:



            center_lat = (

                filtered_df["Latitude"]

                .mean()

            )



            center_lon = (

                filtered_df["Longitude"]

                .mean()

            )



            m = folium.Map(

                location=[

                    center_lat,

                    center_lon

                ],

                zoom_start=10

            )



            for _, row in filtered_df.iterrows():



                if row["Availability"] == "YES":


                    color = "green"


                else:


                    color = "red"




                popup = f"""

                <b>{row['Customer name']}</b>

                <br>

                Town:

                {row['Town']}

                <br>

                Product:

                {row['Availability']}

                """



                folium.Marker(

                    location=[

                        row["Latitude"],

                        row["Longitude"]

                    ],

                    popup=popup,

                    tooltip=row[
                        "Customer name"
                    ],

                    icon=folium.Icon(

                        color=color

                    )

                ).add_to(
                    m
                )



            st_folium(

                m,

                width=1400,

                height=700

            )


        else:


            st.warning(

                "No stores found for selected filters"

            )



    except Exception as e:


        import traceback


        st.error(
            str(e)
        )


        st.code(
            traceback.format_exc()
        )