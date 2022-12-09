import numpy as np
import pandas as pd
import scipy.stats as sps
from itertools import product
import subprocess


# -------------------------------------------
# --- Part I: factor exposure calculation ---
def cal_period_return(t_z: pd.Series, t_ret_scale: int) -> float:
    return (np.prod(t_z / t_ret_scale + 1) - 1) * t_ret_scale


def find_price(t_x: pd.Series, t_md_df: pd.DataFrame):
    _trade_date = t_x.name
    return t_md_df.at[_trade_date, t_x["n_contract"]], t_md_df.at[_trade_date, t_x["d_contract"]]


def cal_roll_return(t_x: pd.Series, t_n_prc_lbl: str, t_d_prc_lbl: str, t_ret_scale: int):
    _dlt_month = int(t_x["d_contract"].split(".")[0][-2:]) - int(t_x["n_contract"].split(".")[0][-2:])
    _dlt_month = _dlt_month + (12 if _dlt_month <= 0 else 0)
    return (t_x[t_n_prc_lbl] / t_x[t_d_prc_lbl] - 1) / _dlt_month * 12 * t_ret_scale


def cal_registered_stock_change_ratio(t_x: pd.Series, t_this_lbl: str, t_prev_lbl: str, t_lower_lim: float, t_ret_scale: int):
    if t_x[t_prev_lbl] >= t_lower_lim:
        return -(t_x[t_this_lbl] / t_x[t_prev_lbl] - 1) * t_ret_scale
    else:
        return np.nan


def cal_rolling_corr(t_major_return_df: pd.DataFrame, t_x: str, t_y: str, t_rolling_window: int, t_corr_lbl: str):
    t_major_return_df["xy"] = (t_major_return_df[t_x] * t_major_return_df[t_y]).rolling(window=t_rolling_window).mean()
    t_major_return_df["xx"] = (t_major_return_df[t_x] * t_major_return_df[t_x]).rolling(window=t_rolling_window).mean()
    t_major_return_df["yy"] = (t_major_return_df[t_y] * t_major_return_df[t_y]).rolling(window=t_rolling_window).mean()
    t_major_return_df["x"] = t_major_return_df[t_x].rolling(window=t_rolling_window).mean()
    t_major_return_df["y"] = t_major_return_df[t_y].rolling(window=t_rolling_window).mean()

    t_major_return_df["cov_xy"] = t_major_return_df["xy"] - t_major_return_df["x"] * t_major_return_df["y"]
    t_major_return_df["cov_xx"] = t_major_return_df["xx"] - t_major_return_df["x"] * t_major_return_df["x"]
    t_major_return_df["cov_yy"] = t_major_return_df["yy"] - t_major_return_df["y"] * t_major_return_df["y"]

    t_major_return_df.loc[np.abs(t_major_return_df["cov_xx"]) <= 1e-8, "cov_xx"] = 0
    t_major_return_df.loc[np.abs(t_major_return_df["cov_yy"]) <= 1e-8, "cov_yy"] = 0

    t_major_return_df["sqrt_cov_xx_yy"] = np.sqrt(t_major_return_df["cov_xx"] * t_major_return_df["cov_yy"]).fillna(0)
    t_major_return_df[t_corr_lbl] = t_major_return_df[["cov_xy", "sqrt_cov_xx_yy"]].apply(
        lambda z: 0 if z["sqrt_cov_xx_yy"] == 0 else -z["cov_xy"] / z["sqrt_cov_xx_yy"], axis=1)
    return 0


def cal_wgt_ary(t_half_life: int, t_size: int, t_ascending: bool):
    """

    :param t_half_life:
    :param t_size:
    :param t_ascending: if true, the near days would have more weight, otherwise less weight.
    :return:
    """
    _rou = np.power(0.5, 1 / t_half_life)
    if t_ascending:
        _w = np.power(_rou, np.arange(t_size, 0, -1))
    else:
        _w = np.power(_rou, np.arange(0, t_size, 1))
    _w = _w / _w.sum()
    return _w


def neutralize_by_sector(t_raw_data: pd.Series, t_sector_df: pd.DataFrame, t_weight=None):
    """

    :param t_raw_data: A pd.Series with length = N. Its value could be exposure or return.
    :param t_sector_df: A 0-1 matrix with size = (M, K). And M >=N, make sure that index of
                        t_raw_data is a subset of the index of t_sector_df before call this
                        function.
                        Element[m, k] = 1 if Instruments[m] is in Sector[k] else 0.
    :param t_weight: A pd.Series with length = N1 >= N, make sure that index of t_raw_data
                     is a subset of the index of t_weight. Each element means relative weight
                     of corresponding instrument when regression.
    :return:
    """
    n = len(t_raw_data)
    idx = t_raw_data.index
    if t_weight is None:
        _w: np.ndarray = np.ones(n) / n
    else:
        _w: np.ndarray = t_weight[idx].values

    _w = np.diag(_w)  # It is allowed that sum of _w may not equal 1
    _x: np.ndarray = t_sector_df.loc[idx].values
    _y: np.ndarray = t_raw_data.values

    xw = _x.T.dot(_w)
    xwx_inv = np.linalg.inv(xw.dot(_x))
    xwy = xw.dot(_y)
    b = xwx_inv.dot(xwy)  # b = [XWX]^{-1}[XWY]
    _r = _y - _x.dot(b)  # r = Y - bX
    return pd.Series(data=_r, index=idx)


# -------------------------------------
# --- Part II: factor exposure ic test ---
def fun_for_test_ic(t_group_id: int, t_gn: int,
                    t_factor_list: list, t_test_window_list: list):
    iter_list = product(t_factor_list, t_test_window_list)
    for it, (factor_lbl, test_window) in enumerate(iter_list):
        if it % t_gn == t_group_id:
            subprocess.run(["python", "04_A_factor_test_ic.py", factor_lbl, str(test_window)])
    return 0


def fun_for_test_neutral_ic(t_group_id: int, t_gn: int,
                            t_factor_list: list, t_neutral_method_list: list, t_test_window_list: list):
    iter_list = product(t_factor_list, t_neutral_method_list, t_test_window_list)
    for it, (factor_lbl, neutral_method, test_window) in enumerate(iter_list):
        if it % t_gn == t_group_id:
            subprocess.run(["python", "04_A_factor_test_neutral_ic.py", factor_lbl, neutral_method, str(test_window)])
    return 0


# -----------------------------------------
# --- Part III: factor exposure process ---
def drop_df_rows_by_nan_prop(t_df: pd.DataFrame, t_factors_list: list, t_nan_prop_threshold: float = 1 - 0.618):
    """

    :param t_df:
    :param t_factors_list:
    :param t_nan_prop_threshold: must be [0, 1]
    :return:
    """

    nan_prop = (t_df[t_factors_list].isnull().sum(axis=1) / len(t_factors_list))
    f = nan_prop <= t_nan_prop_threshold
    selected_df: pd.DataFrame = t_df.loc[f]
    m = selected_df.median()
    selected_df_fillna = selected_df.fillna(m)
    return selected_df_fillna


def transform_dist(t_exposure_srs: pd.Series):
    """

    :param t_exposure_srs:
    :return: remap an array of any distribution to norm distribution
    """

    return sps.norm.ppf(t_exposure_srs.rank() / (len(t_exposure_srs) + 1))


def adjust_weight(t_input_df: pd.DataFrame, t_weight_id: str, t_neutral_method: str):
    # update weight_id according to neutral method
    if t_neutral_method == "WE":
        t_input_df["rel_w"] = 1
    elif t_neutral_method == "WS":
        t_input_df["rel_w"] = np.sqrt(t_input_df[t_weight_id])
    else:
        t_input_df["rel_w"] = t_input_df[t_weight_id]
    t_input_df["w"] = t_input_df["rel_w"] / t_input_df["rel_w"].sum()
    return 0


def sector_neutralize_factors_pool(t_input_df: pd.DataFrame, t_sectors_list: list, t_factors_list: list, t_weight_id: str = "w"):
    sector_neutralized_data = {}
    for factor in t_factors_list:
        sector_neutralized_data[factor] = neutralize_by_sector(
            t_raw_data=t_input_df[factor],
            t_sector_df=t_input_df[t_sectors_list],
            t_weight=t_input_df[t_weight_id]
        )
    return pd.DataFrame(sector_neutralized_data)


def normalize(t_sector_neutralized_df: pd.DataFrame, w: pd.Series):
    m = t_sector_neutralized_df.T @ w
    s = np.sqrt(((t_sector_neutralized_df - m) ** 2).T @ w)
    return (t_sector_neutralized_df - m) / s


def delinear(t_exposure_df: pd.DataFrame, t_selected_factors_pool: list, w: pd.Series) -> pd.DataFrame:
    delinear_exposure_data = {}
    f_h_square_sum = {}
    for i, fi_lbl in enumerate(t_selected_factors_pool):
        if i == 0:
            delinear_exposure_data[fi_lbl] = t_exposure_df[fi_lbl]
        else:  # i > 0, since the second component
            fi = t_exposure_df[fi_lbl]
            projection = 0
            for j, fj_lbl in zip(range(i), t_selected_factors_pool[0:i]):
                fj_h = delinear_exposure_data[fj_lbl]
                projection += fi.dot(w * fj_h) / f_h_square_sum[fj_lbl] * fj_h
            delinear_exposure_data[fi_lbl] = fi - projection
        f_h_square_sum[fi_lbl] = delinear_exposure_data[fi_lbl].dot(w * delinear_exposure_data[fi_lbl])
    delinear_exposure_df = pd.DataFrame(delinear_exposure_data)
    res_df = normalize(delinear_exposure_df, w)
    return res_df


def cal_risk_factor_return_colinear(t_r: np.ndarray, t_x: np.ndarray, t_instru_wgt: np.ndarray, t_sector_wgt: np.ndarray):
    """

    :param t_r: n x 1, n: number of instruments
    :param t_x: n x K, K = 1 + k, k = p + q; p = number of sectors; q = number of style factors; 1 = market; K: number of all risk factors
    :param t_instru_wgt: n x 1, weight (market value) for each instrument
    :param t_sector_wgt: p x 1, weight (market value) of each sector
    :return:
    """
    _n, _K = t_x.shape
    _p = len(t_sector_wgt)
    _q = _K - 1 - _p
    _R11_up_ = np.diag(np.ones(_p))  # p x p
    _R11_dn_ = np.concatenate(([0], -t_sector_wgt[:-1] / t_sector_wgt[-1]))  # 1 x p, linear constrain: \sum_{i=1}^kw_iR_i = 0, R_i: sector return, output of this function
    _R11 = np.vstack((_R11_up_, _R11_dn_))  # (p + 1) x p
    _R12 = np.zeros(shape=(_p + 1, _q))
    _R21 = np.zeros(shape=(_q, _p))
    _R22 = np.diag(np.ones(_q))
    _R = np.vstack((np.hstack((_R11, _R12)), np.hstack((_R21, _R22))))  # (p + q + 1) x (p + q) = K x (K - 1)
    _v_raw = np.sqrt(t_instru_wgt)
    _v = np.diag(_v_raw / np.sum(_v_raw))  # n x n

    #
    # Omega = R((XR)'VXR)^{-1} (XR)'V # size = K x n
    # f = Omega * r
    # Omega * X = E_{kk} # size = K x K
    # Omega *XR = R

    _XR = t_x.dot(_R)  # n x (K-1)
    _P = _XR.T.dot(_v).dot(_XR)  # (K-1) x (K-1)
    _Omega = _R.dot(np.linalg.inv(_P).dot(_XR.T.dot(_v)))  # K x n
    _f = _Omega.dot(t_r)  # K x 1
    return _f, _Omega


def check_for_factor_return_colinear(t_r: np.ndarray, t_x: np.ndarray, t_instru_wgt: np.ndarray, t_factor_ret: np.ndarray):
    """

    :param t_r: same as the t_r in cal_risk_factor_return_colinear
    :param t_x: same as the t_x in cal_risk_factor_return_colinear
    :param t_instru_wgt: same as the t_instru_wgt in cal_risk_factor_return_colinear
    :param t_factor_ret: _f in cal_risk_factor_return_colinear
    :return:
    """
    _rh = t_x @ t_factor_ret
    _residual = t_r - _rh
    _w = np.sqrt(t_instru_wgt)
    _r_wgt_mean = t_r.dot(_w)
    _sst = np.sum((t_r - _r_wgt_mean) ** 2 * _w)
    _ssr = np.sum((_rh - _r_wgt_mean) ** 2 * _w)
    _sse = np.sum(_residual ** 2 * _w)
    _rsq = _ssr / _sst
    _err = np.abs(_sst - _ssr - _sse)
    return _residual, _sst, _ssr, _sse, _rsq, _err


# -----------------------------------------
# --- Part IV: Regression ---
def fun_for_normalize_delinear(t_pid_list: list, t_neutral_method_list: list):
    for pid, neutral_method in product(t_pid_list, t_neutral_method_list):
        subprocess.run(["python", "05_factors_normalize_delinear.py", pid, neutral_method])
    return 0


def fun_for_factors_delinear_test_ic(t_pid_list: list, t_neutral_method_list: list, t_test_window_list: list, t_factors_return_lag_list: list):
    for pid, neutral_method, test_window, factors_return_lag in product(t_pid_list, t_neutral_method_list, t_test_window_list, t_factors_return_lag_list):
        subprocess.run(["python", "06_factors_delinear_test_ic.py", pid, neutral_method, str(test_window), str(factors_return_lag)])
    return 0


def fun_for_factors_return(t_pid_list: list, t_neutral_method_list: list, t_test_window_list: list, t_factors_return_lag_list: list):
    for pid, neutral_method, test_window, factors_return_lag in product(t_pid_list, t_neutral_method_list, t_test_window_list, t_factors_return_lag_list):
        subprocess.run(["python", "07_factors_return.py", pid, neutral_method, str(test_window), str(factors_return_lag)])
    return 0


def fun_for_factors_return_agg(t_pid_list: list, t_neutral_method_list: list, t_test_window_list: list, t_factors_return_lag_list: list):
    for pid, neutral_method, test_window, factors_return_lag in product(t_pid_list, t_neutral_method_list, t_test_window_list, t_factors_return_lag_list):
        subprocess.run(["python", "07_factors_return_agg.py", pid, neutral_method, str(test_window), str(factors_return_lag)])
    return 0


def fun_for_derivative_factors_IV(t_pid_list: list, t_neutral_method_list: list, t_test_window_list: list, t_factors_return_lag_list: list):
    for pid, neutral_method, test_window, factors_return_lag in product(t_pid_list, t_neutral_method_list, t_test_window_list, t_factors_return_lag_list):
        subprocess.run(["python", "08_cal_derivative_factors.IV.py", pid, neutral_method, str(test_window), str(factors_return_lag)])
    return 0


if __name__ == "__main__":
    # ---- TEST EXAMPLE 0
    print("---- TEST EXAMPLE 0")
    sector_classification = {
        "CU.SHF": "METAL",
        "AL.SHF": "METAL",
        "ZN.SHF": "METAL",
        "A.DCE": "OIL",
        "M.DCE": "OIL",
        "Y.DCE": "OIL",
        "P.DCE": "OIL",
        "MA.CZC": "CHEM",
        "TA.CZC": "CHEM",
        "PP.DCE": "CHEM",
    }

    sector_df = pd.DataFrame.from_dict({z: {sector_classification[z]: 1} for z in sector_classification}, orient="index").fillna(0)
    print(sector_df)

    raw_factor = pd.Series({
        "CU.SHF": 10,
        "ZN.SHF": 8,
        "Y.DCE": 3,
        "P.DCE": 0,
        "MA.CZC": -2,
        "TA.CZC": -4,
    })

    weight = pd.Series({
        "Y.DCE": 2,
        "P.DCE": 1,
        "MA.CZC": 1,
        "TA.CZC": 1,
        "CU.SHF": 1,
        "ZN.SHF": 2,
    })

    new_factor = neutralize_by_sector(
        t_raw_data=raw_factor,
        t_sector_df=sector_df,
        t_weight=weight,
    )

    df = pd.DataFrame({
        "OLD": raw_factor,
        "WGT": weight,
        "NEW": new_factor,
    }).loc[raw_factor.index]

    print(df)

    # ---- TEST EXAMPLE 1
    print("---- TEST EXAMPLE 1")
    df = pd.DataFrame({
        "sector": ["I1", "I1", "I2", "I2"],
        "I1": [1, 1, 0, 0],
        "I2": [0, 0, 1, 1],
        "raw_factor": [100, 80, 32, 8],
        "raw_return": [24, 6, 45, 15],
        "ave_factor_by_sec": [90, 90, 20, 20],
        "ave_return_by_sec": [15, 15, 30, 30],
    }, index=["S1", "S2", "S3", "S4"])
    df.index.name = "资产"
    df["neu_factor"] = neutralize_by_sector(t_raw_data=df["raw_factor"], t_sector_df=df[["I1", "I2"]], t_weight=None)
    df["neu_return"] = neutralize_by_sector(t_raw_data=df["raw_return"], t_sector_df=df[["I1", "I2"]], t_weight=None)

    # wgt_srs = pd.Series({"S1": 1, "S2": 1, "S3": 2, "S4": 3})
    # df["neu_factor"] = neutralize_by_sector(t_raw_data=df["raw_factor"], t_sector_df=df[["I1", "I2"]], t_weight=wgt_srs)
    # df["neu_return"] = neutralize_by_sector(t_raw_data=df["raw_return"], t_sector_df=df[["I1", "I2"]], t_weight=wgt_srs)

    pd.set_option("display.width", 0)
    print(df)

    for x, y in product(["raw_factor", "neu_factor", "I1", "I2"], ["raw_return", "neu_return"]):
        r = df[[x, y]].corr().loc[x, y]
        # print("Corr({:4s},{:4s}) = {:>9.4f}".format(x, y, r))
        print("{} & {} & {:>.3f}\\\\".format(x, y, r))
