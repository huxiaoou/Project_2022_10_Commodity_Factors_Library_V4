from setup import *
from configure import concerned_instruments_universe, available_universe_rolling_window, available_universe_amt_threshold
from configure import price_type, YIYUAN, test_window_list
from lib_data_structure import database_structure
from skyrim.falkreath import CManagerLibWriterByDate

"""
0.  No bgn_date and stp_date are needed
"""

print("... {} available universe calculating".format(dt.datetime.now()))

cne_calendar = CCalendar(t_path=SKYRIM_CONST_CALENDAR_PATH)

# --- initialize lib
available_universe_lib_structure = database_structure["available_universe"]
available_universe_lib = CManagerLibWriterByDate(t_db_name=available_universe_lib_structure.m_lib_name, t_db_save_dir=available_universe_dir)
available_universe_lib.add_table(t_table=available_universe_lib_structure.m_tab)

# --- load all amount and return data
amt_ma_data_for_available = {}
amt_ma_data_for_test = {test_window: {} for test_window in test_window_list}
amt_data = {}
return_data = {}
for instrument in concerned_instruments_universe:
    major_return_file = "major_return.{}.{}.csv.gz".format(instrument, price_type)
    major_return_path = os.path.join(major_return_dir, major_return_file)
    major_return_df = pd.read_csv(major_return_path, dtype={"trade_date": str}).set_index("trade_date")
    amt_ma_data_for_available[instrument] = major_return_df["amt"].rolling(window=available_universe_rolling_window).mean() / YIYUAN
    for test_window in test_window_list:
        amt_ma_data_for_test[test_window][instrument] = major_return_df["amt"].rolling(window=test_window).mean() / YIYUAN
    amt_data[instrument] = major_return_df["amt"] / YIYUAN
    return_data[instrument] = major_return_df["major_return"]

# --- reorganize and save
amt_ma_df_for_available = pd.DataFrame(amt_ma_data_for_available)
amt_ma_df_for_test = {k: pd.DataFrame(v) for k, v in amt_ma_data_for_test.items()}
amt_df = pd.DataFrame(amt_data)
return_df = pd.DataFrame(return_data)
filter_df = amt_ma_df_for_available >= available_universe_amt_threshold
for trade_date, trade_date_filter_df in filter_df.groupby(by="trade_date"):
    trade_date_filter = trade_date_filter_df.loc[trade_date]  # use this as index to get available instruments
    available_universe_df = pd.DataFrame({
        "return": return_df.loc[trade_date, trade_date_filter],
        "amt": amt_df.loc[trade_date, trade_date_filter],
    })
    for k, v in amt_ma_df_for_test.items():
        available_universe_df["WGT{:02d}".format(k)] = v.loc[trade_date, trade_date_filter]

    # save to database
    available_universe_lib.update_by_date(
        t_table_name=available_universe_lib_structure.m_tab.m_table_name,
        t_date=trade_date,
        t_update_df=available_universe_df,
        t_using_index=True
    )

available_universe_lib.close()
print("... {} available universe calculated".format(dt.datetime.now()))
