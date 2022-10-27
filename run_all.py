from configure import factors_list, test_window_list, neutral_method_list, factors_pool_options, factors_return_lag_list
from threading import Thread
import subprocess
from custom.XFuns import product, fun_for_test_ic, fun_for_test_neutral_ic, fun_for_normalize_delinear, fun_for_factors_delinear_test_ic
from custom.XFuns import fun_for_factors_return, fun_for_factors_return_agg
from custom.XFuns import fun_for_derivative_factors_IV

switch = {
    "factor": False,
    "factor_neutral": False,

    "test_ic": False,
    "test_ic_neutral": False,

    "factors_delinear": False,
    "factors_delinear_test_ic": False,

    "factors_return": False,

    "derivative_factors": True,

}

if switch["factor"]:
    subprocess.run(["python", "03_cal_factors.py"])

if switch["factor_neutral"]:
    subprocess.run(["python", "03_cal_factors_neutral.py", "WV"])
    subprocess.run(["python", "03_cal_factors_neutral.py", "WS"])
    subprocess.run(["python", "03_cal_factors_neutral.py", "WE"])

if switch["test_ic"]:
    target_factor_list = factors_list
    gn = 3
    join_list = []
    for group_id in range(gn):
        t = Thread(target=fun_for_test_ic, args=(group_id, gn, target_factor_list, test_window_list))
        t.start()
        join_list.append(t)
    for t in join_list:
        t.join()

    for factor in target_factor_list:
        subprocess.run(["python", "04_B_factor_test_ic_plot.py", factor])

if switch["test_ic_neutral"]:
    target_factor_list = factors_list
    target_neutral_method_list = neutral_method_list
    gn = 3
    join_list = []
    for group_id in range(gn):
        t = Thread(target=fun_for_test_neutral_ic, args=(group_id, gn, target_factor_list, target_neutral_method_list, test_window_list))
        t.start()
        join_list.append(t)
    for t in join_list:
        t.join()

    for factor, uid in product(target_factor_list, target_neutral_method_list):
        subprocess.run(["python", "04_B_factor_test_neutral_ic_plot.py", factor, uid])

if switch["factors_delinear"]:
    fun_for_normalize_delinear(
        t_pid_list=list(factors_pool_options.keys()),
        t_neutral_method_list=neutral_method_list,
    )

if switch["factors_delinear_test_ic"]:
    fun_for_factors_delinear_test_ic(
        t_pid_list=list(factors_pool_options.keys()),
        t_neutral_method_list=neutral_method_list,
        t_test_window_list=test_window_list,
        t_factors_return_lag_list=factors_return_lag_list,
    )

if switch["factors_return"]:
    fun_for_factors_return(
        t_pid_list=list(factors_pool_options.keys()),
        t_neutral_method_list=neutral_method_list,
        t_test_window_list=test_window_list,
        t_factors_return_lag_list=factors_return_lag_list,
    )

    fun_for_factors_return_agg(
        t_pid_list=list(factors_pool_options.keys()),
        t_neutral_method_list=neutral_method_list,
        t_test_window_list=test_window_list,
        t_factors_return_lag_list=factors_return_lag_list,
    )

if switch["derivative_factors"]:
    fun_for_derivative_factors_IV(
        t_pid_list=list(factors_pool_options.keys()),
        t_neutral_method_list=neutral_method_list,
        t_test_window_list=test_window_list,
        t_factors_return_lag_list=factors_return_lag_list,
    )
