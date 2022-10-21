from skyrim.falkreath import os, pd, dt, List, Dict
from skyrim.falkreath import CManagerLibWriterByDate, CLib1Tab1
from custom.XFuns import cal_period_return


def factors_algorithm_MTM(
        mtm_window: int,
        concerned_instruments_universe: List[str],
        database_structure: Dict[str, CLib1Tab1],
        factors_exposure_dir: str,
        md_bgn_date: str,
        md_stp_date: str,
        index_dir: str,
        RETURN_SCALE: int = 100,
):
    factor_lbl = "MTM{:03d}".format(mtm_window)

    all_factor_data = {}
    for instrument in concerned_instruments_universe:
        instrument_file = "{}.index.csv.gz".format(instrument)
        instrument_path = os.path.join(index_dir, instrument_file)
        instrument_df = pd.read_csv(instrument_path, dtype={"trade_date": str}).set_index("trade_date")
        instrument_df["major_return"] = (instrument_df["CLOSE"] / instrument_df["CLOSE"].shift(1).fillna(method="bfill") - 1) * RETURN_SCALE
        instrument_df[factor_lbl] = instrument_df["major_return"].rolling(window=mtm_window).apply(cal_period_return, args=(RETURN_SCALE,), raw=True)
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
