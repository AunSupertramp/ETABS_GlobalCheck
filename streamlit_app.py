# etabs_global_check_with_defaults.py

import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import base64

# Set the title of the app
st.title('ETABS Global Check Application')

# Sidebar for unit selection
st.sidebar.header('Unit System')
unit = st.sidebar.selectbox('Select Unit System', ['Metric (kN, m)', 'Imperial (kip, ft)'])

# Conversion factors
if unit == 'Imperial (kip, ft)':
    load_conversion = 0.224809  # 1 kN = 0.224809 kip
    area_conversion = 10.7639   # 1 m² = 10.7639 ft²
    length_conversion = 3.28084  # 1 m = 3.28084 ft
    load_unit = 'kip'
    area_unit = 'ft²'
    length_unit = 'ft'
    load_format = "%.2f"
else:
    load_conversion = 1
    area_conversion = 1
    length_conversion = 1
    load_unit = 'kN'
    area_unit = 'm²'
    length_unit = 'm'
    load_format = "%.2f"

# Default values based on example data
DL_default = 5000.0      # kN
LL_default = 2000.0      # kN
SDL_default = 1500.0     # kN
Floor_Area_default = 1000.0   # m²
SideX_Area_default = 500.0    # m²
H_default = 30.0         # m
top_displacement_default = 0.15  # m
Wx_default = 800.0       # kN
Wy_default = 750.0       # kN
EQx_default = 1200.0     # kN
EQy_default = 1100.0     # kN
SideY_Area_default = 450.0  # m²
T_model_default = 2.5    # seconds

# Function to validate inputs
def validate_input(value, input_name):
    if value < 0:
        st.error(f'{input_name} must be non-negative.')
        return False
    return True

# Input fields
st.header('Input Parameters')

# Create two columns for inputs
col1, col2 = st.columns(2)

with col1:
    DL = st.number_input(f'Dead Load (DL) of the whole building ({load_unit})',
                         value=DL_default / load_conversion, format=load_format)
    LL = st.number_input(f'Live Load (LL) of the whole building ({load_unit})',
                         value=LL_default / load_conversion, format=load_format)
    SDL = st.number_input(f'Superimposed Dead Load (SDL) of the whole building ({load_unit})',
                          value=SDL_default / load_conversion, format=load_format)
    Floor_Area = st.number_input(f'Total Floor Area ({area_unit})',
                                 value=Floor_Area_default / area_conversion, format="%.2f")
    SideX_Area = st.number_input(f'Side X Building Surface Area ({area_unit})',
                                 value=SideX_Area_default / area_conversion, format="%.2f")
    H = st.number_input(f'Building Height (H) ({length_unit})',
                        value=H_default / length_conversion, format="%.2f")
    top_displacement = st.number_input(f'Top Displacement (Δ) ({length_unit})',
                                       value=top_displacement_default / length_conversion, format="%.4f")

with col2:
    Wx = st.number_input(f'Wind Load in X direction (Wx) ({load_unit})',
                         value=Wx_default / load_conversion, format=load_format)
    Wy = st.number_input(f'Wind Load in Y direction (Wy) ({load_unit})',
                         value=Wy_default / load_conversion, format=load_format)
    EQx = st.number_input(f'Earthquake Load in X direction (EQx) ({load_unit})',
                          value=EQx_default / load_conversion, format=load_format)
    EQy = st.number_input(f'Earthquake Load in Y direction (EQy) ({load_unit})',
                          value=EQy_default / load_conversion, format=load_format)
    SideY_Area = st.number_input(f'Side Y Building Surface Area ({area_unit})',
                                 value=SideY_Area_default / area_conversion, format="%.2f")
    T_model = st.number_input('Time Period from ETABS Model (T_model) (seconds)',
                              value=T_model_default, format="%.3f")

# Apply unit conversions if necessary
DL *= load_conversion
LL *= load_conversion
SDL *= load_conversion
Wx *= load_conversion
Wy *= load_conversion
EQx *= load_conversion
EQy *= load_conversion
Floor_Area *= area_conversion
SideX_Area *= area_conversion
SideY_Area *= area_conversion
H *= length_conversion
top_displacement *= length_conversion

# Validate inputs
inputs_valid = True
inputs_valid &= validate_input(DL, 'Dead Load')
inputs_valid &= validate_input(LL, 'Live Load')
inputs_valid &= validate_input(SDL, 'Superimposed Dead Load')
inputs_valid &= validate_input(Floor_Area, 'Total Floor Area')
inputs_valid &= validate_input(SideX_Area, 'Side X Building Surface Area')
inputs_valid &= validate_input(SideY_Area, 'Side Y Building Surface Area')
inputs_valid &= validate_input(H, 'Building Height')
inputs_valid &= validate_input(top_displacement, 'Top Displacement')
inputs_valid &= validate_input(T_model, 'Time Period from ETABS Model')

if inputs_valid:
    # Calculations
    st.header('Calculations')

    # Create two columns for calculations and results
    calc_col1, calc_col2 = st.columns(2)

    # Load Per Area Calculations
    DL_per_area = DL / Floor_Area if Floor_Area > 0 else None
    LL_per_area = LL / Floor_Area if Floor_Area > 0 else None
    SDL_per_area = SDL / Floor_Area if Floor_Area > 0 else None

    # Display Load Per Area
    with calc_col1:
        st.subheader(f'Load Per Area ({load_unit}/{area_unit})')

        def display_load_check(load_per_area, typical_range, load_type):
            if load_per_area is not None:
                st.write(f'{load_type} per area: **{load_per_area:.2f}** {load_unit}/{area_unit}')
                if typical_range[0] <= load_per_area <= typical_range[1]:
                    st.success(f'{load_type} per area is **Reasonable**.')
                else:
                    st.warning(f'{load_type} per area is outside the typical range. **PLS Check**.')
            else:
                st.error(f'Floor Area must be greater than zero for {load_type} calculation.')

        # Typical ranges (adjust these based on standards)
        DL_range = (3, 10)
        LL_range = (2, 5)
        SDL_range = (1, 5)

        display_load_check(DL_per_area, DL_range, 'DL')
        display_load_check(LL_per_area, LL_range, 'LL')
        display_load_check(SDL_per_area, SDL_range, 'SDL')

    # Wind Load per Side Area
    with calc_col2:
        st.subheader(f'Wind Load Per Side Area ({load_unit}/{area_unit})')

        Wx_per_area = Wx / SideX_Area if SideX_Area > 0 else None
        Wy_per_area = Wy / SideY_Area if SideY_Area > 0 else None

        def display_wind_check(wind_per_area, side_area, direction):
            if wind_per_area is not None:
                st.write(f'W{direction} per area: **{wind_per_area:.2f}** {load_unit}/{area_unit}')
                # You can add checks for wind load per area if you have typical ranges
            else:
                st.error(f'Side {direction} Building Surface Area must be greater than zero for W{direction} calculation.')

        display_wind_check(Wx_per_area, SideX_Area, 'x')
        display_wind_check(Wy_per_area, SideY_Area, 'y')

    # Earthquake Load Comparison
    st.subheader('Earthquake Load Comparison')

    EQ_col1, EQ_col2 = st.columns(2)

    with EQ_col1:
        if EQy != 0:
            EQ_ratio = EQx / EQy
            st.write(f'EQx/EQy Ratio: **{EQ_ratio:.2f}**')

            if 0.8 <= EQ_ratio <= 1.2:
                st.success('EQx and EQy loads are **balanced**.')
            else:
                st.warning('Significant difference between EQx and EQy. **PLS Check**.')
        else:
            st.error('EQy must not be zero for EQx/EQy ratio calculation.')

    # Load Percentages
    with EQ_col2:
        st.subheader('Load Percentages of Total Vertical Load')

        total_vertical_load = DL + LL + SDL

        if total_vertical_load > 0:
            DL_percentage = (DL / total_vertical_load) * 100
            LL_percentage = (LL / total_vertical_load) * 100
            SDL_percentage = (SDL / total_vertical_load) * 100

            st.write(f'DL: **{DL_percentage:.2f}%**')
            st.write(f'LL: **{LL_percentage:.2f}%**')
            st.write(f'SDL: **{SDL_percentage:.2f}%**')

            # Check for reasonable percentages
            def check_percentage(value, typical_range, load_type):
                if typical_range[0] <= value <= typical_range[1]:
                    st.success(f'{load_type} percentage is **Reasonable**.')
                else:
                    st.warning(f'{load_type} percentage is outside the typical range. **PLS Check**.')

            check_percentage(DL_percentage, (40, 60), 'DL')
            check_percentage(LL_percentage, (20, 40), 'LL')
            check_percentage(SDL_percentage, (10, 30), 'SDL')
        else:
            st.error('Total vertical load must be greater than zero.')

    # Drift Ratio and Time Period Checks
    st.header('Drift Ratio and Time Period Checks')
    drift_col1, drift_col2 = st.columns(2)

    with drift_col1:
        if H > 0:
            drift_ratio = top_displacement / H
            st.subheader('Drift Ratio Calculation')
            st.write(f'Drift Ratio (Δ/H): **{drift_ratio:.5f}**')

            # Allowable Drift Ratio (θ_allowable)
            theta_allowable = 0.02  # Adjust based on code and building type
            st.write(f'Allowable Drift Ratio: **{theta_allowable:.5f}**')
            if drift_ratio <= theta_allowable:
                st.success('Drift ratio is within the allowable limit.')
            else:
                st.warning('Drift ratio exceeds the allowable limit. **PLS Check**.')
        else:
            st.error('Building Height must be greater than zero.')

    # Time Period Check
    with drift_col2:
        if H > 0:
            # Constants (Example values, adjust based on code and structural system)
            C_t = 0.016  # For concrete moment-resisting frames per ASCE 7-16 Table 12.8-2
            x = 0.9
            T_approx = C_t * H ** x
            st.subheader('Time Period Check')
            st.write(f'Approximate Fundamental Period (T_approx): **{T_approx:.3f}** seconds')
            st.write(f'Model Time Period (T_model): **{T_model:.3f}** seconds')

            # Allowable maximum period (e.g., T_max = 1.4 * T_approx)
            T_max = 1.4 * T_approx
            st.write(f'Allowable Maximum Period (T_max): **{T_max:.3f}** seconds')
            if T_model <= T_max:
                st.success('Model time period is within allowable limits.')
            else:
                st.warning('Model time period exceeds allowable limits. **PLS Check**.')
        else:
            st.error('Building Height must be greater than zero.')

    # Visualization
    st.header('Visualization')

    # Create two columns for visualizations
    vis_col1, vis_col2 = st.columns(2)

    # Pie Chart for Vertical Loads
    vertical_loads = {
        'DL': DL,
        'LL': LL,
        'SDL': SDL
    }

    load_values = list(vertical_loads.values())
    load_labels = list(vertical_loads.keys())

    if total_vertical_load > 0:
        with vis_col1:
            st.subheader('Vertical Loads Distribution')
            fig1, ax1 = plt.subplots()
            ax1.pie(load_values, labels=load_labels, autopct='%1.1f%%', startangle=90)
            ax1.axis('equal')  # Equal aspect ratio ensures that pie is drawn as a circle.
            st.pyplot(fig1)

    # You can add another visualization in vis_col2 if needed

    # Download Results as CSV
    st.header('Download Results')

    results_df = pd.DataFrame({
        'Load Type': ['DL', 'LL', 'SDL'],
        f'Load ({load_unit})': [DL, LL, SDL],
        f'Load per Area ({load_unit}/{area_unit})': [DL_per_area, LL_per_area, SDL_per_area],
        'Percentage (%)': [DL_percentage, LL_percentage, SDL_percentage]
    })

    def get_table_download_link(df, filename, text):
        csv = df.to_csv(index=False)
        b64 = base64.b64encode(csv.encode()).decode()  # B64 encoding
        href = f'<a href="data:file/csv;base64,{b64}" download="{filename}">{text}</a>'
        return href

    st.markdown(get_table_download_link(results_df, 'global_check_results.csv', 'Download Results as CSV'), unsafe_allow_html=True)

    # Documentation and Interpretation Guide
    with st.expander("Click here for instructions and interpretation guide"):
        st.write("""
        **Instructions:**
        - Enter all the required input parameters in the fields provided.
        - The default values are based on typical data but can be modified.
        - Ensure that all loads, areas, heights, displacements, and periods are non-negative.
        - Select the appropriate unit system from the sidebar.

        **Interpretation Guide:**
        - **Load Per Area**: This helps in understanding the distribution of loads over the floor area.
        - **Drift Ratio (Δ/H)**: Indicates the lateral displacement relative to the building height. It should be within allowable limits as per code.
        - **Time Period Check**: Ensures that the model's fundamental period is within acceptable limits compared to code-based approximations.
        - **Typical Ranges** (These are general guidelines and may vary based on specific codes or standards):
            - **DL per area**: 3 to 10 kN/m²
            - **LL per area**: 2 to 5 kN/m²
            - **SDL per area**: 1 to 5 kN/m²
            - **Allowable Drift Ratio**: Typically 0.005 to 0.020 (0.5% to 2%)
        - **Messages**:
            - **Reasonable**: The calculated value is within the typical range.
            - **PLS Check**: The calculated value is outside the typical range and should be reviewed.

        **Notes:**
        - Adjust constants and limits based on the specific building code and structural system you are using.
        - The EQx/EQy ratio helps in understanding the balance of earthquake loads in both directions.
        - Load percentages indicate the proportion of each load type in the total vertical load.
        """)
else:
    st.error('Please correct the input errors and try again.')
