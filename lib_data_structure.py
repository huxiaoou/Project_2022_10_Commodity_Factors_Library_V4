import itertools as ittl
from skyrim.falkreath import CLib1Tab1, CTable, Dict
from configure import factors_pool_options, instruments_universe_options, universe_id, sector_classification
from configure import test_window_list, factors_return_lag_list, factors_list, sectors_list, neutral_method_list

# --- DATABASE STRUCTURE
# available universe structure
database_structure: Dict[str, CLib1Tab1] = {
    "available_universe": CLib1Tab1(
        t_lib_name="available_universe.db",
        t_tab=CTable(
            t_table_name="available_universe",
            t_primary_keys={"trade_date": "TEXT", "instrument": "TEXT"},
            t_value_columns={**{"return": "REAL", "amt": "REAL"}, **{"WGT{:02d}".format(z): "REAL" for z in test_window_list}}
        ))
}

# test return structure
test_return_lbl_list = ["test_return_{:03d}".format(w) for w in test_window_list]
database_structure.update({
    z: CLib1Tab1(
        t_lib_name=z + ".db",
        t_tab=CTable(
            t_table_name=z,
            t_primary_keys={"trade_date": "TEXT", "instrument": "TEXT"},
            t_value_columns={"value": "REAL"},
        )) for z in test_return_lbl_list
})

# test return neutral structure
test_return_neutral_lbl_list = ["test_return_{:03d}.{}".format(w, nm)
                                for w, nm in ittl.product(test_window_list, neutral_method_list)]
database_structure.update({
    z: CLib1Tab1(
        t_lib_name=z + ".db",
        t_tab=CTable(
            t_table_name=z.split(".")[0],
            t_primary_keys={"trade_date": "TEXT", "instrument": "TEXT"},
            t_value_columns={"value": "REAL"},
        )) for z in test_return_neutral_lbl_list
})

# factor structure
database_structure.update({
    z: CLib1Tab1(
        t_lib_name=z + ".db",
        t_tab=CTable(
            t_table_name=z,
            t_primary_keys={"trade_date": "TEXT", "instrument": "TEXT"},
            t_value_columns={"value": "REAL"},
        )) for z in factors_list
})

# factors neutral structure
factors_neutral_list = ["{}.{}".format(f, nm)
                        for f, nm in ittl.product(factors_list, neutral_method_list)]
database_structure.update({
    z: CLib1Tab1(
        t_lib_name=z + ".db",
        t_tab=CTable(
            t_table_name=z.split(".")[0],
            t_primary_keys={"trade_date": "TEXT", "instrument": "TEXT"},
            t_value_columns={"value": "REAL"},
        )) for z in factors_neutral_list
})

# norm factors pool
norm_factors_pool_list = ["{}.{}.NORM".format(p, nm)
                          for p, nm in ittl.product(factors_pool_options.keys(), neutral_method_list)]
database_structure.update({
    z: CLib1Tab1(
        t_lib_name=z + ".db",
        t_tab=CTable(
            t_table_name=z.split(".")[0],
            t_primary_keys={"trade_date": "TEXT", "instrument": "TEXT"},
            t_value_columns={f: "REAL" for f in factors_pool_options[z.split(".")[0]]},
        )) for z in norm_factors_pool_list
})

# delinear factors pool
delinear_factors_pool_list = ["{}.{}.DELINEAR".format(p, nm)
                              for p, nm in ittl.product(factors_pool_options.keys(), neutral_method_list)]
database_structure.update({
    z: CLib1Tab1(
        t_lib_name=z + ".db",
        t_tab=CTable(
            t_table_name=z.split(".")[0],
            t_primary_keys={"trade_date": "TEXT", "instrument": "TEXT"},
            t_value_columns={f: "REAL" for f in factors_pool_options[z.split(".")[0]]},
        )) for z in delinear_factors_pool_list
})

# factors return lib
factors_return_list = ["factors_return.{}.{}.TW{:03d}.T{}".format(p, nm, tw, l)
                       for p, nm, tw, l in ittl.product(factors_pool_options.keys(), neutral_method_list, test_window_list, factors_return_lag_list)]
database_structure.update({
    z: CLib1Tab1(
        t_lib_name=z + ".db",
        t_tab=CTable(
            t_table_name=z.split(".")[0],
            t_primary_keys={"trade_date": "TEXT", "factor": "TEXT"},
            t_value_columns={"value": "REAL"},
        )) for z in factors_return_list
})

# factors delinear test ic lib
factors_delinear_test_ic_list = ["factors_delinear_test_ic.{}.{}.TW{:03d}.T{}".format(p, nm, tw, l)
                                 for p, nm, tw, l in ittl.product(factors_pool_options.keys(), neutral_method_list, test_window_list, factors_return_lag_list)]
database_structure.update({
    z: CLib1Tab1(
        t_lib_name=z + ".db",
        t_tab=CTable(
            t_table_name=z.split(".")[0],
            t_primary_keys={"trade_date": "TEXT", "factor": "TEXT"},
            t_value_columns={"value": "REAL"},
        )) for z in factors_delinear_test_ic_list
})

# instrument residual lib
instrument_residual_list = ["instruments_residual.{}.{}.TW{:03d}.T{}".format(p, nm, tw, l)
                            for p, nm, tw, l in ittl.product(factors_pool_options.keys(), neutral_method_list, test_window_list, factors_return_lag_list)]
database_structure.update({
    z: CLib1Tab1(
        t_lib_name=z + ".db",
        t_tab=CTable(
            t_table_name=z.split(".")[0],
            t_primary_keys={"trade_date": "TEXT", "instrument": "TEXT"},
            t_value_columns={"value": "REAL"},
        )) for z in instrument_residual_list
})

# factors portfolio lib
factors_portfolio_list = ["factors_portfolio.{}.{}.TW{:03d}.T{}".format(p, nm, tw, l)
                          for p, nm, tw, l in ittl.product(factors_pool_options.keys(), neutral_method_list, test_window_list, factors_return_lag_list)]
for z in factors_portfolio_list:
    # selected sectors list
    mother_universe = instruments_universe_options[universe_id]
    sector_set = {sector_classification[u] for u in mother_universe}  # this set may be a subset of sectors_list and in random order
    selected_sectors_list = [z for z in sectors_list if z in sector_set]  # sort sector set by sectors list order

    # selected factors pool
    selected_factors_pool = factors_pool_options[z.split(".")[1]]

    database_structure.update({
        z: CLib1Tab1(
            t_lib_name=z + ".db",
            t_tab=CTable(
                t_table_name=z.split(".")[0],
                t_primary_keys={"trade_date": "TEXT", "instrument": "TEXT"},
                t_value_columns={f: "REAL" for f in ["MARKET"] + selected_sectors_list + selected_factors_pool}
            ))
    })

# IV lib
iv_list = ["IV{}{}TW{:03d}T{}".format(p, nm, tw, l)
           for p, nm, tw, l in ittl.product(factors_pool_options.keys(), neutral_method_list, test_window_list, factors_return_lag_list)]
database_structure.update({
    z: CLib1Tab1(
        t_lib_name=z + ".db",
        t_tab=CTable(
            t_table_name=z,
            t_primary_keys={"trade_date": "TEXT", "instrument": "TEXT"},
            t_value_columns={"value": "REAL"},
        )) for z in iv_list
})

if __name__ == "__main__":
    print(norm_factors_pool_list)
    print(database_structure["P3.WS.NORM"].m_tab.m_value_columns)
