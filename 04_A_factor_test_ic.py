from setup import *
from configure import test_lag
from configure import factors_bgn_date, factors_stp_date
from lib_data_structure import database_structure
from skyrim.falkreath import CManagerLibReader

factor_lbl = sys.argv[1].upper()
test_window = int(sys.argv[2])

# --- directory check
check_and_mkdir(os.path.join(test_ic_dir, factor_lbl))

# --- test id
test_id = "{}.TW{:03d}".format(factor_lbl, test_window)

# --- check existence
ic_file = "ic.{}.csv.gz".format(test_id)
ic_path = os.path.join(test_ic_dir, factor_lbl, ic_file)
if os.path.exists(ic_path):
    sys.exit()

print("... {} begin to calculate ic for {}".format(dt.datetime.now(), test_id))

# --- load calendar
trade_calendar = CCalendar(t_path=SKYRIM_CONST_CALENDAR_PATH)

# --- available universe
available_universe_lib_structure = database_structure["available_universe"]
available_universe_lib = CManagerLibReader(t_db_name=available_universe_lib_structure.m_lib_name, t_db_save_dir=available_universe_dir)

# --- factor library
factor_lib_structure = database_structure[factor_lbl]
factor_lib = CManagerLibReader(t_db_name=factor_lib_structure.m_lib_name, t_db_save_dir=factors_exposure_dir)

# --- test return library
test_return_lib_id = "test_return_{:03d}".format(test_window)
test_return_lib_structure = database_structure[test_return_lib_id]
test_return_lib = CManagerLibReader(t_db_name=test_return_lib_structure.m_lib_name, t_db_save_dir=test_return_dir)

# --- core loop
ic_data = []
for trade_date in trade_calendar.get_iter_list(t_bgn_date=factors_bgn_date, t_stp_date=factors_stp_date, t_ascending=True):
    # load available universe
    available_universe_df = available_universe_lib.read_by_date(
        t_table_name=available_universe_lib_structure.m_tab.m_table_name,
        t_trade_date=trade_date,
        t_value_columns=["instrument"]
    )
    if len(available_universe_df) == 0:
        continue

    # load factor
    factor_df = factor_lib.read_by_date(
        t_table_name=factor_lib_structure.m_tab.m_table_name,
        t_trade_date=trade_date,
        t_value_columns=["instrument", "value"]
    ).rename(mapper={"value": factor_lbl}, axis=1)
    if len(factor_df) == 0:
        continue

    # load test return
    test_return_date = trade_calendar.get_next_date(t_this_date=trade_date, t_shift=test_lag + test_window)
    test_return_df = test_return_lib.read_by_date(
        t_table_name=test_return_lib_structure.m_tab.m_table_name,
        t_trade_date=test_return_date,
        t_value_columns=["instrument", "value"]
    ).rename(mapper={"value": "test_return"}, axis=1)
    if len(test_return_df) == 0:
        continue

    # merge
    factor_and_test_return_df: pd.DataFrame = pd.merge(
        left=factor_df, right=test_return_df,
        how="left", on=["instrument"]
    )
    factor_and_test_return_df = pd.merge(
        left=available_universe_df, right=factor_and_test_return_df,
        how="left", on=["instrument"]
    )
    factor_and_test_return_df = factor_and_test_return_df.dropna(axis=0)
    if len(factor_and_test_return_df) > 2:
        ic = factor_and_test_return_df[[factor_lbl, "test_return"]].corr(method="spearman").at[factor_lbl, "test_return"]
        ic_data.append({"trade_date": trade_date, "ic": 0 if np.isnan(ic) else ic})
    else:
        print(trade_date, "|->", test_return_date, factor_lbl, test_window, "Not enough instruments")

# all ic df
ic_df = pd.DataFrame(ic_data).set_index("trade_date")
ic_df["cum_ic"] = ic_df["ic"].cumsum()
ic_df.to_csv(ic_path, float_format="%.6f", compression="gzip")

# close lib
available_universe_lib.close()
factor_lib.close()
test_return_lib.close()
