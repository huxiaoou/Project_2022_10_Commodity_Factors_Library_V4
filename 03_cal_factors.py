from setup import *
from custom.factors_algorithm_BASIS import factors_algorithm_BASIS
from custom.factors_algorithm_BETA import factors_algorithm_BETA
from custom.factors_algorithm_CSP import factors_algorithm_CSP
from custom.factors_algorithm_CSR import factors_algorithm_CSR
from custom.factors_algorithm_CTP import factors_algorithm_CTP
from custom.factors_algorithm_CTR import factors_algorithm_CTR
from custom.factors_algorithm_CV import factors_algorithm_CV
from custom.factors_algorithm_CVP import factors_algorithm_CVP
from custom.factors_algorithm_CVR import factors_algorithm_CVR
from custom.factors_algorithm_HP import factors_algorithm_HP
from custom.factors_algorithm_MTM import factors_algorithm_MTM
from custom.factors_algorithm_RSW import factors_algorithm_RSW
from custom.factors_algorithm_SGM import factors_algorithm_SGM
from custom.factors_algorithm_SIZE import factors_algorithm_SIZE
from custom.factors_algorithm_SKEW import factors_algorithm_SKEW
from custom.factors_algorithm_TO import factors_algorithm_TO
from custom.factors_algorithm_TS import factors_algorithm_TS
from custom.factors_algorithm_VOL import factors_algorithm_VOL
from configure import concerned_instruments_universe, md_bgn_date, md_stp_date
from configure import factors_args_dict
from lib_data_structure import database_structure

switch = {
    "BASIS": True,
    "BETA": True,
    "CSP": True,
    "CSR": True,
    "CTP": True,
    "CTR": True,
    "CV": True,
    "CVP": True,
    "CVR": True,
    "HP": True,
    "MTM": True,
    "RSW": True,
    "SGM": True,
    "SIZE": True,
    "SKEW": True,
    "TO": True,
    "TS": True,
    "VOL": True,
}

instrument_info_table = CInstrumentInfoTable(t_path=SKYRIM_CONST_INSTRUMENT_INFO_PATH, t_index_label="windCode")

if switch["BASIS"]:
    for basis_window in factors_args_dict["BASIS"]:
        factors_algorithm_BASIS(
            basis_window=basis_window,
            concerned_instruments_universe=concerned_instruments_universe,
            database_structure=database_structure,
            factors_exposure_dir=factors_exposure_dir,
            md_bgn_date=md_bgn_date,
            md_stp_date=md_stp_date,
            extra_data_dir=extra_data_dir,
            major_minor_dir=major_minor_dir
        )

if switch["BETA"]:
    for beta_window in factors_args_dict["BETA"]:
        factors_algorithm_BETA(
            beta_window=beta_window,
            concerned_instruments_universe=concerned_instruments_universe,
            database_structure=database_structure,
            factors_exposure_dir=factors_exposure_dir,
            md_bgn_date=md_bgn_date,
            md_stp_date=md_stp_date,
            instruments_return_dir=instruments_return_dir,
            major_return_dir=major_return_dir,
        )

if switch["CSP"]:
    for csp_window in factors_args_dict["CSP"]:
        factors_algorithm_CSP(
            csp_window=csp_window,
            concerned_instruments_universe=concerned_instruments_universe,
            database_structure=database_structure,
            factors_exposure_dir=factors_exposure_dir,
            md_bgn_date=md_bgn_date,
            md_stp_date=md_stp_date,
            major_return_dir=major_return_dir
        )

if switch["CSR"]:
    for csr_window in factors_args_dict["CSR"]:
        factors_algorithm_CSR(
            csr_window=csr_window,
            concerned_instruments_universe=concerned_instruments_universe,
            database_structure=database_structure,
            factors_exposure_dir=factors_exposure_dir,
            md_bgn_date=md_bgn_date,
            md_stp_date=md_stp_date,
            major_return_dir=major_return_dir
        )

if switch["CTP"]:
    for ctp_window in factors_args_dict["CTP"]:
        factors_algorithm_CTP(
            ctp_window=ctp_window,
            concerned_instruments_universe=concerned_instruments_universe,
            database_structure=database_structure,
            factors_exposure_dir=factors_exposure_dir,
            md_bgn_date=md_bgn_date,
            md_stp_date=md_stp_date,
            major_return_dir=major_return_dir
        )

if switch["CTR"]:
    for ctr_window in factors_args_dict["CTR"]:
        factors_algorithm_CTR(
            ctr_window=ctr_window,
            concerned_instruments_universe=concerned_instruments_universe,
            database_structure=database_structure,
            factors_exposure_dir=factors_exposure_dir,
            md_bgn_date=md_bgn_date,
            md_stp_date=md_stp_date,
            major_return_dir=major_return_dir
        )

if switch["CV"]:
    for cv_window in factors_args_dict["CV"]:
        factors_algorithm_CV(
            cv_window=cv_window,
            concerned_instruments_universe=concerned_instruments_universe,
            database_structure=database_structure,
            factors_exposure_dir=factors_exposure_dir,
            md_bgn_date=md_bgn_date,
            md_stp_date=md_stp_date,
            major_return_dir=major_return_dir
        )

if switch["CVP"]:
    for cvp_window in factors_args_dict["CVP"]:
        factors_algorithm_CVP(
            cvp_window=cvp_window,
            concerned_instruments_universe=concerned_instruments_universe,
            database_structure=database_structure,
            factors_exposure_dir=factors_exposure_dir,
            md_bgn_date=md_bgn_date,
            md_stp_date=md_stp_date,
            major_return_dir=major_return_dir,
        )

if switch["CVR"]:
    for cvr_window in factors_args_dict["CVR"]:
        factors_algorithm_CVR(
            cvr_window=cvr_window,
            concerned_instruments_universe=concerned_instruments_universe,
            database_structure=database_structure,
            factors_exposure_dir=factors_exposure_dir,
            md_bgn_date=md_bgn_date,
            md_stp_date=md_stp_date,
            major_return_dir=major_return_dir,
        )

if switch["HP"]:
    for hp_window in factors_args_dict["HP"]:
        factors_algorithm_HP(
            hp_window=hp_window,
            concerned_instruments_universe=concerned_instruments_universe,
            database_structure=database_structure,
            factors_exposure_dir=factors_exposure_dir,
            md_bgn_date=md_bgn_date,
            md_stp_date=md_stp_date,
            major_return_dir=major_return_dir
        )

if switch["MTM"]:
    for mtm_window in factors_args_dict["MTM"]:
        factors_algorithm_MTM(
            mtm_window=mtm_window,
            concerned_instruments_universe=concerned_instruments_universe,
            database_structure=database_structure,
            factors_exposure_dir=factors_exposure_dir,
            md_bgn_date=md_bgn_date,
            md_stp_date=md_stp_date,
            index_dir=index_dir,
        )

if switch["RSW"]:
    for half_life in factors_args_dict["RSW252HL"]:
        factors_algorithm_RSW(
            rs_window=252, half_life=half_life,
            concerned_instruments_universe=concerned_instruments_universe,
            database_structure=database_structure,
            factors_exposure_dir=factors_exposure_dir,
            md_bgn_date=md_bgn_date,
            md_stp_date=md_stp_date,
            extra_data_dir=extra_data_dir,
            major_minor_dir=major_minor_dir,
        )

if switch["SGM"]:
    for sgm_window in factors_args_dict["SGM"]:
        factors_algorithm_SGM(
            sgm_window=sgm_window,
            concerned_instruments_universe=concerned_instruments_universe,
            database_structure=database_structure,
            factors_exposure_dir=factors_exposure_dir,
            md_bgn_date=md_bgn_date,
            md_stp_date=md_stp_date,
            major_return_dir=major_return_dir,
        )

if switch["SIZE"]:
    for size_window in factors_args_dict["SIZE"]:
        factors_algorithm_SIZE(
            size_window=size_window,
            concerned_instruments_universe=concerned_instruments_universe,
            database_structure=database_structure,
            factors_exposure_dir=factors_exposure_dir,
            md_bgn_date=md_bgn_date,
            md_stp_date=md_stp_date,
            major_return_dir=major_return_dir,
            instrument_info_table=instrument_info_table
        )

if switch["SKEW"]:
    for skew_window in factors_args_dict["SKEW"]:
        factors_algorithm_SKEW(
            skew_window=skew_window,
            concerned_instruments_universe=concerned_instruments_universe,
            database_structure=database_structure,
            factors_exposure_dir=factors_exposure_dir,
            md_bgn_date=md_bgn_date,
            md_stp_date=md_stp_date,
            major_return_dir=major_return_dir,
        )

if switch["TO"]:
    for to_window in factors_args_dict["TO"]:
        factors_algorithm_TO(
            to_window=to_window,
            concerned_instruments_universe=concerned_instruments_universe,
            database_structure=database_structure,
            factors_exposure_dir=factors_exposure_dir,
            md_bgn_date=md_bgn_date,
            md_stp_date=md_stp_date,
            major_return_dir=major_return_dir,
        )

if switch["TS"]:
    for ts_window in factors_args_dict["TS"]:
        factors_algorithm_TS(
            ts_window=ts_window,
            concerned_instruments_universe=concerned_instruments_universe,
            database_structure=database_structure,
            factors_exposure_dir=factors_exposure_dir,
            md_bgn_date=md_bgn_date,
            md_stp_date=md_stp_date,
            major_minor_dir=major_minor_dir,
            md_dir=md_dir,
        )

if switch["VOL"]:
    for vol_window in factors_args_dict["VOL"]:
        factors_algorithm_VOL(
            vol_window=vol_window,
            concerned_instruments_universe=concerned_instruments_universe,
            database_structure=database_structure,
            factors_exposure_dir=factors_exposure_dir,
            md_bgn_date=md_bgn_date,
            md_stp_date=md_stp_date,
            major_return_dir=major_return_dir,
        )
