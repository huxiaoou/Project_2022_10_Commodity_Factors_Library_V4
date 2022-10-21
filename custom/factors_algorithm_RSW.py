from skyrim.falkreath import os, pd, dt, List, Dict
from skyrim.falkreath import CManagerLibWriterByDate, CLib1Tab1
from custom.XFuns import cal_wgt_ary, cal_registered_stock_change_ratio


def factors_algorithm_RSW(
        rs_window: int, half_life: int,
        concerned_instruments_universe: List[str],
        database_structure: Dict[str, CLib1Tab1],
        factors_exposure_dir: str,
        md_bgn_date: str,
        md_stp_date: str,
        extra_data_dir: str,
        major_minor_dir: str,
        RETURN_SCALE: int = 100,
):
    factor_lbl = "RSW{:03d}HL{:03d}".format(rs_window, half_life)
    lag_label = "registered_stock_L{}_HL{}".format(rs_window, half_life)
    rsw_lower_lim = 10
    wgt_ary = cal_wgt_ary(t_half_life=half_life, t_size=rs_window, t_ascending=False)

    # --- calculate factors by instrument
    all_factor_data = {}
    for instrument in concerned_instruments_universe:
        instrument_file = "{}.registered_stock.csv.gz".format(instrument)
        instrument_path = os.path.join(extra_data_dir, instrument_file)
        instrument_df = pd.read_csv(instrument_path, dtype={"trade_date": str}).set_index("trade_date")

        major_minor_file = "major.minor.{}.csv.gz".format(instrument)
        major_minor_path = os.path.join(major_minor_dir, major_minor_file)
        major_minor_df = pd.read_csv(major_minor_path, dtype={"trade_date": str}).set_index("trade_date")

        instrument_df: pd.DataFrame = pd.merge(left=major_minor_df, right=instrument_df, how="left", left_index=True, right_index=True)

        instrument_df = instrument_df.fillna(method="ffill").fillna(0)
        instrument_df[lag_label] = instrument_df["registered_stock"].rolling(window=rs_window).apply(lambda z: z @ wgt_ary)
        instrument_df[factor_lbl] = instrument_df[["registered_stock", lag_label]].apply(
            cal_registered_stock_change_ratio, args=("registered_stock", lag_label, rsw_lower_lim, RETURN_SCALE), axis=1)
        all_factor_data[instrument] = instrument_df[factor_lbl]

    # --- reorganize
    all_factor_df = pd.DataFrame(all_factor_data)

    # --- save
    factor_lib_structure = database_structure[factor_lbl]
    factor_lib = CManagerLibWriterByDate(
        t_db_name=factor_lib_structure.m_lib_name,
        t_db_save_dir=factors_exposure_dir
    )
    factor_lib.add_table(t_table=factor_lib_structure.m_tab)
    factor_lib.save_factor_by_date(
        t_table_name=factor_lib_structure.m_tab.m_table_name,
        t_all_factor_df=all_factor_df,
        t_bgn_date=md_bgn_date, t_stp_date=md_stp_date,
    )
    factor_lib.close()

    print("... @ {} factor = {:>12s} calculated".format(dt.datetime.now(), factor_lbl))
    return 0
