from setup import *
from configure import sector_classification, universe_id
from configure import instruments_universe_options, factors_pool_options
from lib_data_structure import database_structure
from skyrim.falkreath import CManagerLibReader

pid = sys.argv[1].upper()  # ["P3"]
neutral_method = sys.argv[2].upper()  # ["WE", "WS", "WV"]
test_window = int(sys.argv[3])
factors_return_lag = int(sys.argv[4])

print(pid, neutral_method, "TW{:03d}".format(test_window), "T{}".format(factors_return_lag))

# --- load lib: factors_return/instruments_residual
factors_return_lib_id = "factors_return.{}.{}.TW{:03d}.T{}".format(pid, neutral_method, test_window, factors_return_lag)
instruments_residual_lib_id = "instruments_residual.{}.{}.TW{:03d}.T{}".format(pid, neutral_method, test_window, factors_return_lag)
factors_return_lib = CManagerLibReader(t_db_save_dir=factors_return_dir, t_db_name=database_structure[factors_return_lib_id].m_lib_name)
instruments_residual_lib = CManagerLibReader(t_db_save_dir=instruments_residual_dir, t_db_name=database_structure[instruments_residual_lib_id].m_lib_name)

# --- load universe and factors
mother_universe = instruments_universe_options[universe_id]
selected_sectors_list = list({sector_classification[z] for z in mother_universe})
selected_factors_pool = factors_pool_options[pid]

# --- load calendar
trade_calendar = CCalendar(t_path=SKYRIM_CONST_CALENDAR_PATH)

# --- sector exposure
sector_exposure_df = pd.DataFrame({z: {sector_classification[z]: 1} for z in mother_universe}).fillna(0).T

# --- core loop
factors_return_df = factors_return_lib.read(
    t_table_name=database_structure[factors_return_lib_id].m_tab.m_table_name,
    t_value_columns=["trade_date", "factor", "value"])

instruments_residual_df = instruments_residual_lib.read(
    t_table_name=database_structure[instruments_residual_lib_id].m_tab.m_table_name,
    t_value_columns=["trade_date", "instrument", "value"]
)

factors_return_agg_df = pd.pivot_table(data=factors_return_df, index="trade_date", columns="factor", values="value", aggfunc=sum)
factors_return_agg_cumsum_df = factors_return_agg_df.cumsum()
factors_return_agg_cumsum_file = "factors_return.cumsum.{}.{}.TW{:03d}.T{}.csv.gz".format(pid, neutral_method, test_window, factors_return_lag)
factors_return_agg_cumsum_path = os.path.join(factors_return_agg_dir, factors_return_agg_cumsum_file)
factors_return_agg_cumsum_df.to_csv(factors_return_agg_cumsum_path, index_label="trade_date", float_format="%.6f")

instruments_residual_agg_df = pd.pivot_table(data=instruments_residual_df, index="trade_date", columns="instrument", values="value", aggfunc=sum)
instruments_residual_agg_cumsum_df = instruments_residual_agg_df.cumsum()
instruments_residual_agg_cumsum_file = "instruments_residual.cumsum.{}.{}.TW{:03d}.T{}.csv.gz".format(pid, neutral_method, test_window, factors_return_lag)
instruments_residual_agg_cumsum_path = os.path.join(instruments_residual_agg_dir, instruments_residual_agg_cumsum_file)
instruments_residual_agg_cumsum_df.to_csv(instruments_residual_agg_cumsum_path, index_label="trade_date", float_format="%.6f")

plot_lines(t_plot_df=factors_return_agg_cumsum_df[["MARKET"] + selected_sectors_list],
           t_fig_name=factors_return_agg_cumsum_file.replace(".csv.gz", ".sector"),
           t_save_dir=factors_return_agg_dir, t_colormap="jet")

plot_lines(t_plot_df=factors_return_agg_cumsum_df[selected_factors_pool],
           t_fig_name=factors_return_agg_cumsum_file.replace(".csv.gz", ".selected"),
           t_save_dir=factors_return_agg_dir, t_colormap="jet")

for sector in sector_exposure_df.columns:
    sector_instru_set = set(sector_exposure_df.loc[sector_exposure_df[sector] > 0, sector].index)
    residual_instru_set = set(instruments_residual_agg_cumsum_df.columns)
    sector_instru_list = list(sector_instru_set.intersection(residual_instru_set))
    plot_lines(t_plot_df=instruments_residual_agg_cumsum_df[sector_instru_list],
               t_fig_name=instruments_residual_agg_cumsum_file.replace(".csv.gz", "." + sector),
               t_save_dir=instruments_residual_agg_dir, t_colormap="jet")

factors_return_lib.close()
instruments_residual_lib.close()
