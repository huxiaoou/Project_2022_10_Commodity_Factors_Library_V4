from skyrim.falkreath import os, np, pd, dt, List, Dict
from skyrim.falkreath import CManagerLibWriterByDate, CLib1Tab1


def factors_algorithm_HP(
        hp_window: int,
        concerned_instruments_universe: List[str],
        database_structure: Dict[str, CLib1Tab1],
        factors_exposure_dir: str,
        md_bgn_date: str,
        md_stp_date: str,
        major_return_dir: str,
        price_type: str = "close",
        hp_adj_scale: int = 1000,

):
    factor_lbl = "HP{:03d}".format(hp_window)

    # --- load all register data
    all_factor_data = {}
    for instrument in concerned_instruments_universe:
        major_return_file = "major_return.{}.{}.csv.gz".format(instrument, price_type)
        major_return_path = os.path.join(major_return_dir, major_return_file)
        major_return_df = pd.read_csv(major_return_path, dtype={"trade_date": str}).set_index("trade_date")
        major_return_df["abs_dlt_oi"] = np.abs(major_return_df["oi"] - major_return_df["oi"].shift(hp_window))
        major_return_df["volume_rolling_sum"] = major_return_df["volume"].rolling(window=hp_window).sum()
        major_return_df[factor_lbl] = -major_return_df["abs_dlt_oi"] / major_return_df["volume_rolling_sum"] * hp_adj_scale
        all_factor_data[instrument] = major_return_df[factor_lbl]

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
