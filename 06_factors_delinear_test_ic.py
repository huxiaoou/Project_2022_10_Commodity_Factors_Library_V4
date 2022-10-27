from setup import *
from configure import factors_pool_bgn_date, factors_pool_stp_date
from configure import test_lag, factors_pool_options
from lib_data_structure import database_structure
from skyrim.falkreath import CManagerLibReader, CManagerLibWriterByDate

pid = sys.argv[1].upper()  # ["P3"]
neutral_method = sys.argv[2].upper()  # ["WE", "WS", "WV"]
test_window = int(sys.argv[3])
factors_return_lag = int(sys.argv[4])  # fixed to be 1

# --- initialize output lib: factors_return/instruments_residual/factors_portfolio
factors_delinear_test_ic_lib_id = "factors_delinear_test_ic.{}.{}.TW{:03d}.T{}".format(pid, neutral_method, test_window, factors_return_lag)
factors_delinear_test_ic_lib = CManagerLibWriterByDate(t_db_save_dir=factors_delinear_test_ic_dir, t_db_name=database_structure[factors_delinear_test_ic_lib_id].m_lib_name)
factors_delinear_test_ic_lib.add_table(t_table=database_structure[factors_delinear_test_ic_lib_id].m_tab)

# --- load delinearized factors
delinear_lib_id = "{}.{}.DELINEAR".format(pid, neutral_method)
delinear_lib = CManagerLibReader(t_db_save_dir=factors_exposure_delinear_dir, t_db_name=database_structure[delinear_lib_id].m_lib_name)

# --- load test return
test_return_lib_id = "test_return_{:03d}".format(test_window)
test_return_lib_structure = database_structure[test_return_lib_id]
test_return_lib = CManagerLibReader(t_db_name=test_return_lib_structure.m_lib_name, t_db_save_dir=test_return_dir)

# --- load selected factors
selected_factors_pool = factors_pool_options[pid]

# --- load calendar
trade_calendar = CCalendar(t_path=SKYRIM_CONST_CALENDAR_PATH)

# --- core loop
reg_square_data = []
for trade_date in trade_calendar.get_iter_list(t_bgn_date=factors_pool_bgn_date, t_stp_date=factors_pool_stp_date, t_ascending=True):
    # load test return
    test_return_date = trade_calendar.get_next_date(t_this_date=trade_date, t_shift=(test_lag + test_window) * factors_return_lag)
    test_return_df = test_return_lib.read_by_date(
        t_table_name=database_structure[test_return_lib_id].m_tab.m_table_name,
        t_trade_date=test_return_date,
        t_value_columns=["instrument", "value"]
    ).set_index("instrument")
    if len(test_return_df) == 0:
        continue

    # load delinear factors
    delinearized_df = delinear_lib.read_by_date(
        t_table_name=database_structure[delinear_lib_id].m_tab.m_table_name,
        t_trade_date=trade_date,
        t_value_columns=["instrument"] + selected_factors_pool
    ).set_index("instrument")
    if len(delinearized_df) == 0:
        continue

    # corr between exposure and
    exposure_and_return_df: pd.DataFrame = pd.merge(
        left=test_return_df, right=delinearized_df,
        left_index=True, right_index=True,
        how="right"
    )
    test_ic_srs = exposure_and_return_df[selected_factors_pool].corrwith(
        exposure_and_return_df["value"], axis=0, method="spearman")

    # save factor return
    factors_delinear_test_ic_df = pd.DataFrame(data={"ic": test_ic_srs})
    factors_delinear_test_ic_lib.update_by_date(
        t_table_name=database_structure[factors_delinear_test_ic_lib_id].m_tab.m_table_name,
        t_date=trade_date,
        t_update_df=factors_delinear_test_ic_df,
        t_using_index=True,
    )

# close all libs
delinear_lib.close()
test_return_lib.close()

# plot cumsum
all_ic_df = factors_delinear_test_ic_lib.read(
    t_table_name=database_structure[factors_delinear_test_ic_lib_id].m_tab.m_table_name,
    t_value_columns=["trade_date", "factor", "value"]
)
pivot_ic_df = pd.pivot_table(data=all_ic_df, index="trade_date", columns="factor", values="value", aggfunc=sum)
pivot_ic_cumsum_df = pivot_ic_df[selected_factors_pool].cumsum()
plot_lines(
    t_plot_df=pivot_ic_cumsum_df,
    t_save_dir=factors_delinear_test_ic_dir,
    t_fig_name=factors_delinear_test_ic_lib_id,
    t_colormap="jet"
)
factors_delinear_test_ic_lib.close()

print("... {} factor return for pid = {}, neutral_method = {}, test_window = {:>2d}, factor_return_lag = {} are calculated\n".format(
    dt.datetime.now(), pid, neutral_method, test_window, factors_return_lag))
