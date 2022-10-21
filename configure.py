"""
created @ 2022-10-17
0.  move SP.SHF from sector "MISC" to sector "CHEM"
1.  the weight for components of market return is proportional to sqrt(amt),
    which is amt in old version.
"""

# md_bgn_date, md_stp_date = "20140101", (dt.datetime.now() + dt.timedelta(days=1)).strftime("%Y%m%d")
md_bgn_date, md_stp_date = "20140101", "20221017"
factors_bgn_date, factors_stp_date = "20150401", md_stp_date
factors_pool_bgn_date, factors_pool_stp_date = "20150801", md_stp_date

# universe
concerned_instruments_universe = [
    "AU.SHF",  # "20080109"
    "AG.SHF",  # "20120510"
    "CU.SHF",  # "19950417"
    "AL.SHF",  # "19950417"
    "PB.SHF",  # "20140801"
    "ZN.SHF",  # "20070326"
    "SN.SHF",  # "20151102"
    "NI.SHF",  # "20150327"
    "SS.SHF",  # "20190925"
    "RB.SHF",  # "20090327"
    "HC.SHF",  # "20140321"
    "J.DCE",  # "20110415"
    "JM.DCE",  # "20130322"
    "I.DCE",  # "20131018"
    "FG.CZC",  # "20121203"
    "SA.CZC",  # "20191206"
    "UR.CZC",  # "20190809"
    "ZC.CZC",  # "20151201"
    "SF.CZC",  # "20140808"
    "SM.CZC",  # "20140808"
    "Y.DCE",  # "20060109"
    "P.DCE",  # "20071029"
    "OI.CZC",  # "20130423"
    "M.DCE",  # "20000717"
    "RM.CZC",  # "20121228"
    "A.DCE",  # "19990104"
    "RU.SHF",  # "19950516"
    "BU.SHF",  # "20131009"
    "FU.SHF",  # "20040825"  # re-active since 20180801
    "L.DCE",  # "20070731"
    "V.DCE",  # "20090525"
    "PP.DCE",  # "20140228"
    "EG.DCE",  # "20181210"
    "EB.DCE",  # "20191206"
    "PG.DCE",  # "20200330"
    "TA.CZC",  # "20061218"
    "MA.CZC",  # "20141224"
    "SP.SHF",  # "20181127"
    "CF.CZC",  # "20040601"
    "CY.CZC",  # "20170808"
    "SR.CZC",  # "20060106"
    "C.DCE",  # "20040922"
    "CS.DCE",  # "20141219"
    "JD.DCE",  # "20131108"
    "AP.CZC",  # "20171222"
    "CJ.CZC",  # "20190430"
]
ciu_size = len(concerned_instruments_universe)  # should be 46

# available universe
available_universe_rolling_window = 20
available_universe_amt_threshold = 5

# sector
sectors_list = ["AUAG", "METAL", "BLACK", "OIL", "CHEM", "MISC"]  # 6
sector_classification = {
    "AU.SHF": "AUAG",
    "AG.SHF": "AUAG",
    "CU.SHF": "METAL",
    "AL.SHF": "METAL",
    "PB.SHF": "METAL",
    "ZN.SHF": "METAL",
    "SN.SHF": "METAL",
    "NI.SHF": "METAL",
    "SS.SHF": "METAL",
    "RB.SHF": "BLACK",
    "HC.SHF": "BLACK",
    "J.DCE": "BLACK",
    "JM.DCE": "BLACK",
    "I.DCE": "BLACK",
    "FG.CZC": "BLACK",
    "SA.CZC": "BLACK",
    "UR.CZC": "BLACK",
    "ZC.CZC": "BLACK",
    "SF.CZC": "BLACK",
    "SM.CZC": "BLACK",
    "Y.DCE": "OIL",
    "P.DCE": "OIL",
    "OI.CZC": "OIL",
    "M.DCE": "OIL",
    "RM.CZC": "OIL",
    "A.DCE": "OIL",
    "RU.SHF": "CHEM",
    "BU.SHF": "CHEM",
    "FU.SHF": "CHEM",
    "L.DCE": "CHEM",
    "V.DCE": "CHEM",
    "PP.DCE": "CHEM",
    "EG.DCE": "CHEM",
    "EB.DCE": "CHEM",
    "PG.DCE": "CHEM",
    "TA.CZC": "CHEM",
    "MA.CZC": "CHEM",
    "SP.SHF": "CHEM",
    "CF.CZC": "MISC",
    "CY.CZC": "MISC",
    "SR.CZC": "MISC",
    "C.DCE": "MISC",
    "CS.DCE": "MISC",
    "JD.DCE": "MISC",
    "AP.CZC": "MISC",
    "CJ.CZC": "MISC",
}

# --- factor settings ---
factors_args_dict = {
    "BASIS": [105, 126, 147],
    "BETA": [10, 21, 63, 126, 189, 252],
    "CSP": [10, 21, 63, 126, 189, 252],
    "CSR": [10, 21, 63, 126, 189, 252],
    "CTP": [10, 21, 63, 126, 189, 252],
    "CTR": [10, 21, 63, 126, 189, 252],
    "CV": [10, 21, 63, 126, 189, 252],
    "CVP": [10, 21, 63, 126, 189, 252],
    "CVR": [10, 21, 63, 126, 189, 252],
    "HP": [10, 21, 63, 126, 189, 252],
    "MTM": [10, 21, 63, 126, 189, 231, 252],
    "RSW252HL": [21, 63, 126],
    "SGM": [10, 21, 63, 126, 189, 252],
    "SIZE": [10, 21, 63, 126, 189, 252],
    "SKEW": [10, 21, 63, 126, 189, 252],
    "TO": [10, 21, 63, 126, 189, 252],
    "TS": [1, 5, 10, 21, 63, 126],
    "VOL": [10, 21, 63, 126, 189, 252],
}
factors_list = []
for factor_class, arg_lst in factors_args_dict.items():
    factors_list += ["{}{:03d}".format(factor_class, z) for z in arg_lst]
factors_list_size = len(factors_list)

# --- test return ---
test_window_list = [3, 5, 10, 15, 20]  # 5
test_lag = 1
factors_return_lag_list = (0, 1)

# --- instrument universe ---
instruments_universe_options = {
    "U46": concerned_instruments_universe,  # size = 46
    "U29": [
        "CU.SHF",  # "19950417"
        "AL.SHF",  # "19950417"
        "PB.SHF",  # "20140801"
        "ZN.SHF",  # "20070326"
        "SN.SHF",  # "20151102"
        "NI.SHF",  # "20150327"
        "RB.SHF",  # "20090327"
        "HC.SHF",  # "20140321"
        "J.DCE",  # "20110415"
        "JM.DCE",  # "20130322"
        "I.DCE",  # "20131018"
        "FG.CZC",  # "20121203"
        "Y.DCE",  # "20060109"
        "P.DCE",  # "20071029"
        "OI.CZC",  # "20130423"
        "M.DCE",  # "20000717"
        "RM.CZC",  # "20121228"
        "A.DCE",  # "19990104"
        "RU.SHF",  # "19950516"
        "BU.SHF",  # "20131009"
        "L.DCE",  # "20070731"
        "V.DCE",  # "20090525"
        "PP.DCE",  # "20140228"
        "TA.CZC",  # "20061218"
        "MA.CZC",  # "20141224"
        "CF.CZC",  # "20040601"
        "SR.CZC",  # "20060106"
        "C.DCE",  # "20040922"
        "CS.DCE",  # "20141219"
    ],  # size = 29
    "U23": [
        "RB.SHF",  # "20090327"
        "HC.SHF",  # "20140321"
        "J.DCE",  # "20110415"
        "JM.DCE",  # "20130322"
        "I.DCE",  # "20131018"
        "FG.CZC",  # "20121203"
        "Y.DCE",  # "20060109"
        "P.DCE",  # "20071029"
        "OI.CZC",  # "20130423"
        "M.DCE",  # "20000717"
        "RM.CZC",  # "20121228"
        "A.DCE",  # "19990104"
        "RU.SHF",  # "19950516"
        "BU.SHF",  # "20131009"
        "L.DCE",  # "20070731"
        "V.DCE",  # "20090525"
        "PP.DCE",  # "20140228"
        "TA.CZC",  # "20061218"
        "MA.CZC",  # "20141224"
        "CF.CZC",  # "20040601"
        "SR.CZC",  # "20060106"
        "C.DCE",  # "20040922"
        "CS.DCE",  # "20141219"
    ],  # size = 23
}
universe_id = "U46"

# --- factors pool ---
factors_pool_options = {
    "P3": ["BASIS147", "RSW252HL063", "CTP063", "CSP189", "CVP063", "MTM231", "SKEW010", "TS126", "BETA063", "SIZE126", "TO126"],
}

# neutral methods
neutral_method_list = ["WE", "WS", "WV"]

# secondary parameters
RETURN_SCALE = 100
YIYUAN = 1e8
days_per_year = 252
price_type = "close"

if __name__ == "__main__":
    print("Total number of factors = {}".format(len(factors_list)))  # 103
    print("\n".join(factors_list))
