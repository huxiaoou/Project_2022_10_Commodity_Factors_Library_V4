from setup import *
from configure import md_bgn_date
from configure import test_window_list, RETURN_SCALE
from lib_data_structure import database_structure
from custom.XFuns import cal_period_return
from skyrim.falkreath import CManagerLibWriterByDate

# load
raw_return_file = "instruments.return.csv.gz"
raw_return_path = os.path.join(instruments_return_dir, raw_return_file)
raw_return_df = pd.read_csv(raw_return_path, dtype={"trade_date": str}).set_index("trade_date")
print(raw_return_df)

for test_window in test_window_list:
    # --- initialize lib
    test_return_lib_id = "test_return_{:03d}".format(test_window)
    test_return_lib_structure = database_structure[test_return_lib_id]
    test_return_lib = CManagerLibWriterByDate(t_db_name=test_return_lib_structure.m_lib_name, t_db_save_dir=test_return_dir)
    test_return_lib.add_table(t_table=test_return_lib_structure.m_tab)

    rolling_return_df = raw_return_df.rolling(window=test_window).apply(cal_period_return, args=(RETURN_SCALE,))
    test_rolling_return_df = rolling_return_df
    test_rolling_return_df = test_rolling_return_df.loc[test_rolling_return_df.index >= md_bgn_date]
    for trade_date, trade_date_df in test_rolling_return_df.groupby(by="trade_date"):
        save_df = trade_date_df.T.dropna(axis=0)
        if len(save_df) > 0:
            test_return_lib.update_by_date(
                t_table_name=test_return_lib_structure.m_tab.m_table_name,
                t_date=trade_date,
                t_update_df=save_df,
                t_using_index=True,
            )

    test_return_lib.close()
    print("... @ {}, test return for TW = {:>3d} are calculated\n".format(dt.datetime.now(), test_window))
