from setup import *
from skyrim.falkreath import CManagerLibReader
from lib_data_structure import database_structure

"""
updated @ 2022-03-01
0.  this market return can not be tradable
"""

print("| ... {} market index return calculating | ".format(dt.datetime.now()))

# --- load
return_file = "instruments.return.csv.gz"
return_path = os.path.join(instruments_return_dir, return_file)
return_df = pd.read_csv(return_path, dtype={"trade_date": str}).set_index("trade_date")

# --- initialize lib
available_universe_lib_structure = database_structure["available_universe"]
available_universe_lib = CManagerLibReader(t_db_name=available_universe_lib_structure.m_lib_name, t_db_save_dir=available_universe_dir)

# --- loop
market_index_return_data = []
for trade_date in return_df.index:
    available_universe_df = available_universe_lib.read_by_date(
        t_table_name=available_universe_lib_structure.m_tab.m_table_name,
        t_value_columns=["instrument", "return", "amt"],
        t_trade_date=trade_date
    )

    available_universe_df["rel_wgt"] = np.sqrt(available_universe_df["amt"])
    # available_universe_df["rel_wgt"] = 1  # weight of instruments are equal

    available_universe_df["wgt"] = available_universe_df["rel_wgt"] / available_universe_df["rel_wgt"].sum()
    mkt_idx_trade_date_ret = available_universe_df["wgt"].dot(available_universe_df["return"])

    market_index_return_data.append({
        "trade_date": trade_date,
        "market": mkt_idx_trade_date_ret
    })

available_universe_lib.close()

market_index_df = pd.DataFrame(market_index_return_data).set_index("trade_date")
market_index_file = "market.return.csv.gz"
market_index_path = os.path.join(instruments_return_dir, market_index_file)
market_index_df.to_csv(market_index_path, float_format="%.8f")

print("| ... {} market index return calculated  | ".format(dt.datetime.now()))
print(market_index_df)

# load
official_mkt_idx_file = "official_mkt_idx.xlsx"
official_mkt_idx_path = os.path.join(instruments_return_dir, official_mkt_idx_file)
official_mkt_idx_df = pd.read_excel(official_mkt_idx_path, sheet_name="daily_return")

official_mkt_idx_df["trade_date"] = official_mkt_idx_df["trade_date"].map(lambda x: x.strftime("%Y%m%d"))
official_mkt_idx_df = official_mkt_idx_df.set_index("trade_date")
official_mkt_idx_df = official_mkt_idx_df[["??????????????????", "Wind????????????"]]

print(official_mkt_idx_df)

merged_return_df = pd.merge(
    left=market_index_df.rename(axis=1, mapper={"market": "CUSTOM"}), right=official_mkt_idx_df,
    left_index=True, right_index=True,
    how="left"
)

print(merged_return_df)

merged_return_cumsum = merged_return_df.cumsum()
plot_lines(
    t_plot_df=merged_return_cumsum,
    t_colormap="jet",
    t_fig_name="mkt_idx.return.comparison",
    t_save_dir=instruments_return_dir,
)

print(merged_return_df.corr())
