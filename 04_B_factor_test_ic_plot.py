from setup import *
from configure import test_window_list

factor_lbl = sys.argv[1].upper()

print("... {} begin to plot cum ic for {}".format(dt.datetime.now(), factor_lbl))

ic_cumsum_data = {}
statistics_data = []
for test_window in test_window_list:
    test_id = "{}.TW{:03d}".format(factor_lbl, test_window)
    ic_file = "ic.{}.csv.gz".format(test_id)
    ic_path = os.path.join(test_ic_dir, factor_lbl, ic_file)
    ic_df = pd.read_csv(ic_path, dtype={"trade_date": str}).set_index("trade_date")
    ic_cumsum_data[test_id] = ic_df["cum_ic"]

    # get statistic summary
    obs = len(ic_df)
    mu = ic_df["ic"].mean()
    sd = ic_df["ic"].std()
    icir = mu / sd
    ic_q000 = np.percentile(ic_df["ic"], q=0)
    ic_q025 = np.percentile(ic_df["ic"], q=25)
    ic_q050 = np.percentile(ic_df["ic"], q=50)
    ic_q075 = np.percentile(ic_df["ic"], q=75)
    ic_q100 = np.percentile(ic_df["ic"], q=100)
    statistics_data.append({
        "因子": factor_lbl,
        "预测窗口": test_window,
        "样本量": obs,
        "IC均值": mu,
        "IC标准差": sd,
        "ICIR": icir,
        "q000": ic_q000,
        "q025": ic_q025,
        "q050": ic_q050,
        "q075": ic_q075,
        "q100": ic_q100,
    })

if len(ic_cumsum_data) > 0:
    ic_cumsum_df = pd.DataFrame(ic_cumsum_data)
    # print(ic_cumsum_df)
    plot_lines(
        t_plot_df=ic_cumsum_df,
        t_fig_name="ic_cumsum.{}".format(factor_lbl),
        t_save_dir=os.path.join(test_ic_dir, factor_lbl),
        t_colormap="jet"
    )

statistics_df = pd.DataFrame(statistics_data)
statistics_file = "statistics.{}.csv".format(factor_lbl)
statistics_path = os.path.join(test_ic_dir, factor_lbl, statistics_file)
statistics_df.to_csv(statistics_path, index=False, float_format="%.4f")

print(statistics_df)
