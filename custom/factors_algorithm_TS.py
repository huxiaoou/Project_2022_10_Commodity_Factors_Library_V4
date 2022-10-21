from skyrim.falkreath import os, pd, dt, List, Dict
from skyrim.falkreath import CManagerLibWriterByDate, CLib1Tab1
from custom.XFuns import cal_roll_return, find_price


def factors_algorithm_TS(
        ts_window: int,
        concerned_instruments_universe: List[str],
        database_structure: Dict[str, CLib1Tab1],
        factors_exposure_dir: str,
        md_bgn_date: str,
        md_stp_date: str,
        major_minor_dir: str,
        md_dir: str,
        price_type: str = "close",
        RETURN_SCALE: int = 100,
):
    factor_lbl = "TS{:03d}".format(ts_window)

    # --- calculate factors by instrument
    all_factor_data = {}
    for instrument in concerned_instruments_universe:
        major_minor_file = "major.minor.{}.csv.gz".format(instrument)
        major_minor_path = os.path.join(major_minor_dir, major_minor_file)
        major_minor_df = pd.read_csv(major_minor_path, dtype={"trade_date": str}).set_index("trade_date")
        md_file = "{}.md.{}.csv.gz".format(instrument, price_type)
        md_path = os.path.join(md_dir, md_file)
        md_df = pd.read_csv(md_path, dtype={"trade_date": str}).set_index("trade_date")
        shared_bgn_date = max(md_bgn_date, major_minor_df.index[0], md_df.index[0])
        major_minor_df = major_minor_df[major_minor_df.index >= shared_bgn_date]
        major_minor_df["n_" + price_type], major_minor_df["d_" + price_type] = zip(*major_minor_df.apply(find_price, args=(md_df,), axis=1))
        major_minor_df["roll_return"] = major_minor_df.apply(cal_roll_return, args=("n_" + price_type, "d_" + price_type, RETURN_SCALE), axis=1)
        major_minor_df["roll_return"] = major_minor_df["roll_return"].fillna(method="ffill").rolling(window=ts_window).mean()
        all_factor_data[instrument] = major_minor_df["roll_return"]

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
