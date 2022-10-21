from setup import *
from configure import instruments_universe_options, universe_id
from configure import md_bgn_date, md_stp_date
from configure import sector_classification
from lib_data_structure import database_structure
from skyrim.falkreath import CManagerLibReader, CManagerLibWriterByDate
from custom.XFuns import neutralize_by_sector, transform_dist
from configure import factors_list

neutral_method = sys.argv[1].upper()  # ["WE", "WV", "WS"]
weight_id = "amt"

# --- calendar
cne_calendar = CCalendar(t_path=SKYRIM_CONST_CALENDAR_PATH)

# --- available universe
available_universe_lib_structure = database_structure["available_universe"]
available_universe_lib = CManagerLibReader(t_db_name=available_universe_lib_structure.m_lib_name, t_db_save_dir=available_universe_dir)

# --- mother universe
mother_universe = instruments_universe_options[universe_id]
mother_universe_df = pd.DataFrame({"instrument": mother_universe})

# --- sector df
sector_df = pd.DataFrame.from_dict({z: {sector_classification[z]: 1} for z in mother_universe}, orient="index").fillna(0)

for factor_lbl in factors_list:
    # --- factor library
    factor_lib_structure = database_structure[factor_lbl]
    factor_lib = CManagerLibReader(t_db_name=factor_lib_structure.m_lib_name, t_db_save_dir=factors_exposure_dir)

    # --- factor neutral library
    factor_neutral_lib_id = "{}.{}".format(factor_lbl, neutral_method)
    factor_neutral_lib_structure = database_structure[factor_neutral_lib_id]
    factor_neutral_lib = CManagerLibWriterByDate(t_db_name=factor_neutral_lib_structure.m_lib_name, t_db_save_dir=factors_exposure_neutral_dir)
    factor_neutral_lib.add_table(t_table=factor_neutral_lib_structure.m_tab)

    # --- update by date
    for trade_date in cne_calendar.get_iter_list(t_bgn_date=md_bgn_date, t_stp_date=md_stp_date, t_ascending=True):
        factor_df = factor_lib.read_by_date(
            t_table_name=factor_lib_structure.m_tab.m_table_name,
            t_trade_date=trade_date,
            t_value_columns=["instrument", "value"]
        )
        if len(factor_df) == 0:
            continue

        weight_df = available_universe_lib.read_by_date(
            t_table_name=available_universe_lib_structure.m_tab.m_table_name,
            t_trade_date=trade_date,
            t_value_columns=["instrument", weight_id]
        )
        if len(weight_df) == 0:
            continue

        input_df = mother_universe_df.merge(
            right=weight_df, on=["instrument"], how="inner"
        ).merge(
            right=factor_df, on=["instrument"], how="inner"
        ).set_index("instrument")

        # update value: transform its distribution to Normal
        input_df["value_norm"] = transform_dist(t_exposure_srs=input_df["value"])

        # update weight_id according to neutral method
        if neutral_method == "WE":
            input_df[weight_id] = 1
        elif neutral_method == "WS":
            input_df[weight_id] = np.sqrt(input_df[weight_id])

        factor_neutral_srs = neutralize_by_sector(
            t_raw_data=input_df["value_norm"],
            t_sector_df=sector_df,
            t_weight=input_df[weight_id]
        )

        factor_neutral_lib.update_by_date(
            t_table_name=factor_neutral_lib_structure.m_tab.m_table_name,
            t_date=trade_date,
            t_update_df=pd.DataFrame({"value": factor_neutral_srs}),
            t_using_index=True
        )

    factor_lib.close()
    factor_neutral_lib.close()

    print("... @ {} Neutralization for factor {:>12s} of {} calculated\n".format(
        dt.datetime.now(), factor_lbl, neutral_method))

available_universe_lib.close()
