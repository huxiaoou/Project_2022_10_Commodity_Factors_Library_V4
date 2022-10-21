from setup import *
from configure import factors_list, neutral_method_list

exception_list = ["RSW252HL021", "RSW252HL126", "BASIS105", "BASIS126"]

for neutral_method in neutral_method_list:
    summary_dfs_list = []
    for factor_lbl in factors_list:
        if factor_lbl in exception_list:
            continue

        statistics_file = "statistics.{}.csv".format(factor_lbl)
        statistics_path = os.path.join(test_ic_dir, factor_lbl, statistics_file)
        statistics_df = pd.read_csv(statistics_path)
        statistics_df = statistics_df[["因子", "预测窗口", "IC均值", "IC标准差", "ICIR"]]

        statistics_neutral_file = "statistics.{}.{}.csv".format(factor_lbl, neutral_method)
        statistics_neutral_path = os.path.join(test_ic_dir, factor_lbl, statistics_neutral_file)
        statistics_neutral_df = pd.read_csv(statistics_neutral_path)
        statistics_neutral_df = statistics_neutral_df[["因子", "预测窗口", "IC均值", "IC标准差", "ICIR"]]

        summary_df = pd.merge(
            left=statistics_df, right=statistics_neutral_df,
            on=["因子", "预测窗口"],
            how="outer", suffixes=("", "(行业中性化)")
        )

        summary_dfs_list.append(summary_df)

    tot_summary_df = pd.concat(summary_dfs_list, ignore_index=True, axis=0)
    print(tot_summary_df)

    pd.set_option("display.float_format", "{:.3f}".format)
    for test_window, test_window_df in tot_summary_df.groupby(by="预测窗口"):
        ic_order_df = test_window_df.sort_values(by="IC均值", ascending=False).head(12)
        ic_order_neutral_df = test_window_df.sort_values(by="IC均值(行业中性化)", ascending=False).head(12)
        print("=" * 120)
        print("test window = {}".format(test_window))
        print("-" * 120)
        print(ic_order_df)
        print("-" * 120)
        print(ic_order_neutral_df)

        ic_order_file = "ic_order.{}.TW{:03d}.csv".format(neutral_method, test_window)
        ic_order_path = os.path.join(test_ic_dir, ic_order_file)
        ic_order_df.to_csv(ic_order_path, index=False, float_format="%.3f")

        ic_order_neutral_file = "ic_order_neutral.{}.TW{:03d}.csv".format(neutral_method, test_window)
        ic_order_neutral_path = os.path.join(test_ic_dir, ic_order_neutral_file)
        ic_order_neutral_df.to_csv(ic_order_neutral_path, index=False, float_format="%.3f")
