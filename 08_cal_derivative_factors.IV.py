from setup import *
from configure import factors_pool_bgn_date, factors_pool_stp_date
from lib_data_structure import database_structure
from skyrim.falkreath import CManagerLibReader, CManagerLibWriterByDate

pid = sys.argv[1].upper()  # ["P3"]
neutral_method = sys.argv[2].upper()  # ["WE", "WS", "WV"]
test_window = int(sys.argv[3])
factors_return_lag = int(sys.argv[4])
k_iv = 4

factor_lbl = "IV{}{}TW{:03d}T{}".format(pid, neutral_method, test_window, factors_return_lag)

# --- initialize factor lib
factor_lib = CManagerLibWriterByDate(t_db_save_dir=factors_exposure_dir, t_db_name=database_structure[factor_lbl].m_lib_name)
factor_lib.add_table(t_table=database_structure[factor_lbl].m_tab)

# --- load lib: instruments_residual
instruments_residual_lib_id = "instruments_residual.{}.{}.TW{:03d}.T{}".format(pid, neutral_method, test_window, factors_return_lag)
instruments_residual_lib = CManagerLibReader(t_db_save_dir=instruments_residual_dir, t_db_name=database_structure[instruments_residual_lib_id].m_lib_name)

instruments_residual_df = instruments_residual_lib.read(
    t_table_name=database_structure[instruments_residual_lib_id].m_tab.m_table_name,
    t_value_columns=["trade_date", "instrument", "value"]
)
instruments_residual_agg_df = pd.pivot_table(data=instruments_residual_df, index="trade_date", columns="instrument", values="value", aggfunc=sum)
all_factor_df = instruments_residual_agg_df.rolling(window=test_window * k_iv).std()

factor_lib.save_factor_by_date(
    t_table_name=database_structure[factor_lbl].m_tab.m_table_name,
    t_all_factor_df=all_factor_df,
    t_bgn_date=factors_pool_bgn_date, t_stp_date=factors_pool_stp_date
)

instruments_residual_lib.close()
factor_lib.close()

print("... {} factor = {:>12s} calculated\n".format(dt.datetime.now(), factor_lbl))
