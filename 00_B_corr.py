from setup import *
from configure import concerned_instruments_universe

return_type = "raw"
return_file = "instruments.return.csv.gz"
return_path = os.path.join(instruments_return_dir, return_file)

# load
return_df = pd.read_csv(return_path, dtype={"trade_date": str}).set_index("trade_date")

# plot corr
return_df["trade_year"] = return_df.index.map(lambda z: z[0:4])
for trade_year, trade_year_df in return_df.groupby(by="trade_year"):
    corr_df = trade_year_df.rename(axis=1, mapper={z: z.split(".")[0] for z in concerned_instruments_universe}).corr()
    corr_file = "corr.{}.{}.csv".format(return_type, trade_year)
    corr_path = os.path.join(instruments_corr_dir, corr_file)
    corr_df.to_csv(corr_path, index_label="instrument", float_format="%.3f")
    plot_corr(t_corr_df=corr_df, t_fig_name="corr.{}.{}".format(return_type, trade_year), t_save_dir=instruments_corr_dir, t_annot_size=6)
    print("...", trade_year, "corr", "calculated and plot")

tot_corr_df = return_df.rename(axis=1, mapper={z: z.split(".")[0] for z in concerned_instruments_universe}).corr()
tot_corr_file = "corr.{}.tot.csv".format(return_type)
tot_corr_path = os.path.join(instruments_corr_dir, tot_corr_file)
tot_corr_df.to_csv(tot_corr_path, index_label="instrument", float_format="%.2f")
plot_corr(t_corr_df=tot_corr_df, t_fig_name="corr.{}.tot".format(return_type), t_save_dir=instruments_corr_dir, t_annot_size=6)
