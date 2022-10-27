from setup import *
from configure import factors_pool_bgn_date, factors_pool_stp_date, sector_classification
from configure import test_lag, universe_id, sectors_list
from configure import instruments_universe_options, factors_pool_options
from lib_data_structure import database_structure
from custom.XFuns import cal_risk_factor_return_colinear, check_for_factor_return_colinear
from skyrim.falkreath import CManagerLibReader, CManagerLibWriterByDate

pid = sys.argv[1].upper()  # ["P3"]
neutral_method = sys.argv[2].upper()  # ["WE", "WS", "WV"]
test_window = int(sys.argv[3])
factors_return_lag = int(sys.argv[4])
weight_id = "WGT{:02d}".format(test_window)

# --- initialize output lib: factors_return/instruments_residual/factors_portfolio
factors_return_lib_id = "factors_return.{}.{}.TW{:03d}.T{}".format(pid, neutral_method, test_window, factors_return_lag)
factors_portfolio_lib_id = "factors_portfolio.{}.{}.TW{:03d}.T{}".format(pid, neutral_method, test_window, factors_return_lag)
instruments_residual_lib_id = "instruments_residual.{}.{}.TW{:03d}.T{}".format(pid, neutral_method, test_window, factors_return_lag)

factors_return_lib = CManagerLibWriterByDate(t_db_save_dir=factors_return_dir, t_db_name=database_structure[factors_return_lib_id].m_lib_name)
factors_portfolio_lib = CManagerLibWriterByDate(t_db_save_dir=factors_portfolio_dir, t_db_name=database_structure[factors_portfolio_lib_id].m_lib_name)
instruments_residual_lib = CManagerLibWriterByDate(t_db_save_dir=instruments_residual_dir, t_db_name=database_structure[instruments_residual_lib_id].m_lib_name)

factors_return_lib.add_table(t_table=database_structure[factors_return_lib_id].m_tab)
factors_portfolio_lib.add_table(t_table=database_structure[factors_portfolio_lib_id].m_tab)
instruments_residual_lib.add_table(t_table=database_structure[instruments_residual_lib_id].m_tab)

# --- load delinearized factors
delinear_lib_id = "{}.{}.DELINEAR".format(pid, neutral_method)
delinear_lib = CManagerLibReader(t_db_save_dir=factors_exposure_delinear_dir, t_db_name=database_structure[delinear_lib_id].m_lib_name)

# --- load test return
test_return_lib_id = "test_return_{:03d}".format(test_window)
test_return_lib_structure = database_structure[test_return_lib_id]
test_return_lib = CManagerLibReader(t_db_name=test_return_lib_structure.m_lib_name, t_db_save_dir=test_return_dir)

# --- load selected factors
selected_factors_pool = factors_pool_options[pid]

# --- load  universe
mother_universe = instruments_universe_options[universe_id]
mother_universe_df = pd.DataFrame({"instrument": mother_universe})

# --- load sector df
sector_df = pd.DataFrame.from_dict({z: {sector_classification[z]: 1} for z in mother_universe}, orient="index").fillna(0)
selected_sectors_list = [z for z in sectors_list if z in sector_df.columns.to_list()]  # sector_df.columns may be a subset of sector_list and in random order
sector_df["MARKET"] = 1.00

# --- regression labels
x_lbls = ["MARKET"] + selected_sectors_list + selected_factors_pool
y_lbl = "value"

# --- load available universe
available_universe_lib_structure = database_structure["available_universe"]
available_universe_lib = CManagerLibReader(t_db_name=available_universe_lib_structure.m_lib_name, t_db_save_dir=available_universe_dir)

# --- load calendar
trade_calendar = CCalendar(t_path=SKYRIM_CONST_CALENDAR_PATH)

# --- core loop
reg_square_data = []
for trade_date in trade_calendar.get_iter_list(t_bgn_date=factors_pool_bgn_date, t_stp_date=factors_pool_stp_date, t_ascending=True):
    # load available instrument to get weight
    available_universe_df = available_universe_lib.read_by_date(
        t_table_name=available_universe_lib_structure.m_tab.m_table_name,
        t_trade_date=trade_date,
        t_value_columns=["instrument", weight_id]
    ).set_index("instrument")
    if len(available_universe_df) == 0:
        continue

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

    # factors exposure
    exposure_df: pd.DataFrame = pd.merge(
        left=sector_df, right=delinearized_df,
        left_index=True, right_index=True,
        how="right"
    )

    # regression
    reg_df: pd.DataFrame = pd.merge(
        left=test_return_df, right=exposure_df,
        left_index=True, right_index=True,
        how="right"
    )
    x = reg_df[x_lbls].values
    y = reg_df[y_lbl].values
    n, _ = x.shape
    instru_wgt_rel = available_universe_df.loc[reg_df.index, weight_id]
    instru_wgt = instru_wgt_rel / instru_wgt_rel.sum()
    sector_wgt = exposure_df[selected_sectors_list].T.dot(instru_wgt)
    factor_ret, factor_portfolio = cal_risk_factor_return_colinear(t_r=y, t_x=x, t_instru_wgt=instru_wgt.values, t_sector_wgt=sector_wgt.values)
    residual, sst, ssr, sse, rsq, err = check_for_factor_return_colinear(t_r=y, t_x=x, t_instru_wgt=instru_wgt, t_factor_ret=factor_ret)
    if err > 1e-6:
        print(pid, neutral_method, test_window, factors_return_lag, trade_date, test_return_date, "Regression Error! SST - SSR - SSE != 0")

    reg_square_data.append(
        {
            "trade_date": trade_date,
            "test_return_date": test_return_date,
            "num_instru": n,
            "num_mkt": 1,
            "num_sec": len(selected_sectors_list),
            "num_fac": len(selected_factors_pool),
            "ssr": ssr,
            "sse": sse,
            "sst": sst,
            "rsq": rsq,
        }
    )

    # save factor return
    factor_return_df = pd.DataFrame(data={"return": factor_ret}, index=x_lbls)
    factors_return_lib.update_by_date(
        t_table_name=database_structure[factors_return_lib_id].m_tab.m_table_name,
        t_date=test_return_date,
        t_update_df=factor_return_df,
        t_using_index=True,
    )

    # save error
    instruments_residual_df = pd.DataFrame(data={"residual": residual}, index=reg_df.index)
    instruments_residual_lib.update_by_date(
        t_table_name=database_structure[instruments_residual_lib_id].m_tab.m_table_name,
        t_date=test_return_date,
        t_update_df=instruments_residual_df,
        t_using_index=True,
    )

    # save factor portfolio
    factors_portfolio_df = pd.DataFrame(data=factor_portfolio, index=x_lbls, columns=reg_df.index).T
    factors_portfolio_lib.update_by_date(
        t_table_name=database_structure[factors_portfolio_lib_id].m_tab.m_table_name,
        t_date=test_return_date,
        t_update_df=factors_portfolio_df,
        t_using_index=True,
    )

# close all libs
factors_return_lib.close()
factors_portfolio_lib.close()
instruments_residual_lib.close()
available_universe_lib.close()
delinear_lib.close()
test_return_lib.close()

# save regression
reg_square_df = pd.DataFrame(reg_square_data)
reg_square_file = "reg_square.{}.{}.TW{:03d}.T{}.csv.gz".format(pid, neutral_method, test_window, factors_return_lag)
reg_square_path = os.path.join(factors_return_dir, reg_square_file)
reg_square_df.to_csv(reg_square_path, index=False, float_format="%.6f")
plot_bar(
    t_bar_df=reg_square_df.set_index("trade_date")[["rsq"]],
    t_stacked=False, t_fig_name=reg_square_file.replace(".csv.gz", ""),
    t_xtick_span=63, t_tick_label_rotation=90,
    t_save_dir=factors_return_dir
)

print("... {} factor return for pid = {}, neutral_method = {}, test_window = {:>2d}, factor_return_lag = {} are calculated\n".format(
    dt.datetime.now(), pid, neutral_method, test_window, factors_return_lag))
