import os
import sys
import datetime as dt
import numpy as np
import pandas as pd
import itertools as ittl
from skyrim.winterhold import check_and_mkdir, plot_corr, plot_lines, plot_bar
from skyrim.whiterun import CCalendar, CInstrumentInfoTable
from skyrim.configurationOffice import SKYRIM_CONST_CALENDAR_PATH, SKYRIM_CONST_INSTRUMENT_INFO_PATH

"""
Project: Project_2022_10_Commodity_Factors_Library_V4
Author : HUXO
Created: 13:59, 周一, 2022/10/17
"""

pd.set_option("display.width", 0)
pd.set_option("display.float_format", "{:.2f}".format)

# --- project data settings
data_root_dir = os.path.join("/Data")
project_name = os.getcwd().split("\\")[-1]
project_data_dir = os.path.join(data_root_dir, project_name)
instruments_return_dir = os.path.join(project_data_dir, "instruments_return")
instruments_corr_dir = os.path.join(project_data_dir, "instruments_corr")
available_universe_dir = os.path.join(project_data_dir, "available_universe")
test_return_dir = os.path.join(project_data_dir, "test_return")
test_return_neutral_dir = os.path.join(project_data_dir, "test_return_neutral")
factors_exposure_dir = os.path.join(project_data_dir, "factors_exposure")
factors_exposure_neutral_dir = os.path.join(project_data_dir, "factors_exposure_neutral")
factors_exposure_corr_dir = os.path.join(project_data_dir, "factors_exposure_corr")
test_ic_dir = os.path.join(project_data_dir, "test_ic")
factors_exposure_norm_dir = os.path.join(project_data_dir, "factors_exposure_norm")
factors_exposure_delinear_dir = os.path.join(project_data_dir, "factors_exposure_delinear")
factors_portfolio_dir = os.path.join(project_data_dir, "factors_portfolio")
factors_return_dir = os.path.join(project_data_dir, "factors_return")
factors_return_agg_dir = os.path.join(project_data_dir, "factors_return_agg")
instruments_residual_dir = os.path.join(project_data_dir, "instruments_residual")
instruments_residual_agg_dir = os.path.join(project_data_dir, "instruments_residual_agg")
factors_delinear_test_ic_dir = os.path.join(project_data_dir, "factors_delinear_test_ic")

if __name__ == "__main__":
    check_and_mkdir(project_data_dir)
    check_and_mkdir(instruments_return_dir)
    check_and_mkdir(instruments_corr_dir)
    check_and_mkdir(available_universe_dir)
    check_and_mkdir(test_return_dir)
    check_and_mkdir(test_return_neutral_dir)
    check_and_mkdir(factors_exposure_dir)
    check_and_mkdir(factors_exposure_neutral_dir)
    check_and_mkdir(factors_exposure_corr_dir)
    check_and_mkdir(test_ic_dir)
    check_and_mkdir(factors_exposure_norm_dir)
    check_and_mkdir(factors_exposure_delinear_dir)
    check_and_mkdir(factors_portfolio_dir)
    check_and_mkdir(factors_return_dir)
    check_and_mkdir(factors_return_agg_dir)
    check_and_mkdir(instruments_residual_dir)
    check_and_mkdir(instruments_residual_agg_dir)
    check_and_mkdir(factors_delinear_test_ic_dir)

# --- database settings
DATABASE = os.path.join("/Database")
futures_dir = os.path.join(DATABASE, "Futures")
futures_instrument_mkt_data_dir = os.path.join(futures_dir, "instrument_mkt_data")
major_minor_dir = os.path.join(futures_dir, "by_instrument", "major_minor")
major_return_dir = os.path.join(futures_dir, "by_instrument", "major_return")
md_dir = os.path.join(futures_dir, "by_instrument", "md")
index_dir = os.path.join(futures_dir, "by_instrument", "index", "CUSTOM")
extra_data_dir = os.path.join(futures_dir, "by_instrument", "extra_data")
