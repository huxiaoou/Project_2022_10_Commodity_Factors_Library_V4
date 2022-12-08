from setup import *
from configure import sector_classification
from configure import factors_pool_bgn_date, factors_pool_stp_date, universe_id
from configure import instruments_universe_options, factors_pool_options
from lib_data_structure import database_structure
from custom.XFuns import drop_df_rows_by_nan_prop, transform_dist, adjust_weight, sector_neutralize_factors_pool, normalize, delinear
from skyrim.falkreath import CManagerLibReader, CManagerLibWriterByDate, Dict

pid = sys.argv[1].upper()  # ["P3"]
neutral_method = sys.argv[2].upper()  # ["WE", "WS", "WV"]
weight_id = "amt"

# --- initialize output factor lib
norm_lib_id = "{}.{}.NORM".format(pid, neutral_method)
norm_lib = CManagerLibWriterByDate(t_db_save_dir=factors_exposure_norm_dir, t_db_name=database_structure[norm_lib_id].m_lib_name)
norm_lib.add_table(t_table=database_structure[norm_lib_id].m_tab)
delinear_lib_id = "{}.{}.DELINEAR".format(pid, neutral_method)
delinear_lib = CManagerLibWriterByDate(t_db_save_dir=factors_exposure_delinear_dir, t_db_name=database_structure[delinear_lib_id].m_lib_name)
delinear_lib.add_table(t_table=database_structure[delinear_lib_id].m_tab)

# --- load selected factors
selected_factors_pool = factors_pool_options[pid]

# --- load  universe
mother_universe = instruments_universe_options[universe_id]
mother_universe_df = pd.DataFrame({"instrument": mother_universe})

# --- load sector df
sector_df = pd.DataFrame.from_dict({z: {sector_classification[z]: 1} for z in mother_universe}, orient="index").fillna(0)
selected_sectors_list = sector_df.columns.to_list()

# --- load raw factor libs
raw_factor_libs_manager: Dict[str, dict] = {}
for factor_lbl in selected_factors_pool:
    raw_factor_libs_manager[factor_lbl] = {
        "structure": database_structure[factor_lbl],
        "reader": CManagerLibReader(
            t_db_name=database_structure[factor_lbl].m_lib_name,
            t_db_save_dir=factors_exposure_dir
        )
    }

# --- load available universe
available_universe_lib_structure = database_structure["available_universe"]
available_universe_lib = CManagerLibReader(t_db_name=available_universe_lib_structure.m_lib_name, t_db_save_dir=available_universe_dir)

# --- load calendar
trade_calendar = CCalendar(t_path=SKYRIM_CONST_CALENDAR_PATH)

# --- core loop
for trade_date in trade_calendar.get_iter_list(t_bgn_date=factors_pool_bgn_date, t_stp_date=factors_pool_stp_date, t_ascending=True):
    # Load available universe
    available_universe_df = available_universe_lib.read_by_date(
        t_table_name=available_universe_lib_structure.m_tab.m_table_name,
        t_trade_date=trade_date,
        t_value_columns=["instrument", weight_id]
    )
    if len(available_universe_df) == 0:
        continue

    # Header
    header_df = pd.merge(
        left=sector_df, right=available_universe_df[["instrument", weight_id]],
        left_index=True, right_on="instrument", how="inner"
    ).set_index("instrument")

    # Load raw factor exposures
    raw_factors_data = {}
    for factor_lbl in selected_factors_pool:
        factor_df = raw_factor_libs_manager[factor_lbl]["reader"].read_by_date(
            t_table_name=raw_factor_libs_manager[factor_lbl]["structure"].m_tab.m_table_name,
            t_trade_date=trade_date,
            t_value_columns=["instrument", "value"]
        ).set_index("instrument")
        raw_factors_data[factor_lbl] = factor_df["value"]
    raw_factors_df = pd.merge(
        left=header_df, right=pd.DataFrame(raw_factors_data),
        left_index=True, right_index=True,
        how="left"
    )

    # Drop rows with too many nan
    # After this state, no rows are dropped.
    raw_input_df = drop_df_rows_by_nan_prop(t_df=raw_factors_df, t_factors_list=selected_factors_pool)

    # Transform general factors distribution
    raw_input_df[selected_factors_pool] = raw_input_df[selected_factors_pool].apply(transform_dist)

    # Set weight
    adjust_weight(t_input_df=raw_input_df, t_weight_id=weight_id, t_neutral_method=neutral_method)

    # Get sector neutralized exposure
    sector_neutralized_df = sector_neutralize_factors_pool(
        t_input_df=raw_input_df,
        t_factors_list=selected_factors_pool, t_sectors_list=selected_sectors_list)

    # Normalize and Delinear
    norm_factors_df = normalize(t_sector_neutralized_df=sector_neutralized_df, w=raw_input_df["w"])
    delinearized_df = delinear(t_exposure_df=norm_factors_df, t_selected_factors_pool=selected_factors_pool, w=raw_input_df["w"])

    # xdf = pd.merge(
    #     left=raw_input_df[selected_sectors_list],
    #     right=delinearized_df,
    #     left_index=True, right_index=True,
    #     how="outer")
    # ws = raw_input_df["w"]
    # wdf = pd.DataFrame(data=np.diag(ws), index=ws.index, columns=ws.index)
    # m = xdf.T @ raw_input_df["w"]
    # v = np.round(xdf.T @ wdf @ xdf, 8)

    # Save to lib
    norm_lib.update_by_date(
        t_table_name=database_structure[norm_lib_id].m_tab.m_table_name,
        t_date=trade_date,
        t_update_df=norm_factors_df,
        t_using_index=True
    )
    delinear_lib.update_by_date(
        t_table_name=database_structure[delinear_lib_id].m_tab.m_table_name,
        t_date=trade_date,
        t_update_df=delinearized_df,
        t_using_index=True
    )

# --- close libs
available_universe_lib.close()
norm_lib.close()
delinear_lib.close()
for raw_factor_lib in raw_factor_libs_manager.values():
    raw_factor_lib["reader"].close()

print("... {} factors_pool = {} neutral method = {} normalized factors are calculated\n".format(dt.datetime.now(), pid, neutral_method))
