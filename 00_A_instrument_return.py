from setup import *
from configure import concerned_instruments_universe, md_bgn_date

major_return_data = {}
for instrument in concerned_instruments_universe:
    major_return_file = "major_return.{}.close.csv.gz".format(instrument)
    major_return_path = os.path.join(major_return_dir, major_return_file)
    major_return_df = pd.read_csv(major_return_path, dtype={"trade_date": str}).set_index("trade_date")
    major_return_data[instrument] = major_return_df["major_return"]

return_df = pd.DataFrame(major_return_data)
return_df = return_df.loc[return_df.index >= md_bgn_date]
return_file = "instruments.return.csv.gz"
return_path = os.path.join(instruments_return_dir, return_file)
return_df.to_csv(return_path, float_format="%.8f")

print(return_df)

print("... {} instruments major return calculated".format(dt.datetime.now()))
