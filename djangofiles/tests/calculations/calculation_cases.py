BASIC_TAX_CALCULATION_INPUTS = {
    "qualified_income_edge_cases": {
        "dataset": {"name": "Tax Calc 2024-2021 Edge Cases", "max_elected_farm_income": 12000, "qualified_farm_income": 0, "election_year": "2024"},
        "inputs": [
            { # Edge case: negative ordinary income 15%
                "year": 2024,
                "filing_status": "single",
                "taxable_income": 100000,
                "qualified_income": 140000,
                "is_electing": True,
                "elected_farm_income": 12000,
                "qualified_farm_income": 3000,
            },
            { # cap gains in 0%, 15%, 20%
                "year": 2023,
                "filing_status": "single",
                "taxable_income": 640000,
                "qualified_income": 600000,
                "is_electing": False,
                "elected_farm_income": 0,
                "qualified_farm_income": 0,
            },
            { # Cap gains in 15%, 20%
                "year": 2022,
                "filing_status": "single",
                "taxable_income": 640000,
                "qualified_income": 540000,
                "is_electing": False,
                "elected_farm_income": 0,
                "qualified_farm_income": 0,
            },
            { # Edge case: negative ordinary income in 0%, 15%, 20%
                "year": 2021,
                "filing_status": "single",
                "taxable_income": 600000,
                "qualified_income": 640000,
                "is_electing": True,
                "elected_farm_income": 15000,
                "qualified_farm_income": 0,
            },
        ],
    },

    "basic_scenario": {
        "dataset": {"name": "Basic scenario 2021-2024", "max_elected_farm_income": 60000, "qualified_farm_income": 0, "election_year": "2024"},
        "inputs": [
            {
                "year": 2024,
                "filing_status": "MFJ",
                "taxable_income": 120000,
                "qualified_income": 105000,
                "is_electing": True,
                "elected_farm_income": 60000,
                "qualified_farm_income": 0,
            },
            {
                "year": 2023,
                "filing_status": "MFJ",
                "taxable_income": 85000,
                "qualified_income": 70000,
                "is_electing": True,
                "elected_farm_income": 30000,
                "qualified_farm_income": 0,
            },
            {
                "year": 2022,
                "filing_status": "single",
                "taxable_income": 55000,
                "qualified_income": 40000,
                "is_electing": False,
                "elected_farm_income": 0,
                "qualified_farm_income": 0,
            },
            {
                "year": 2021,
                "filing_status": "MFJ",
                "taxable_income": 96000,
                "qualified_income": 45000,
                "is_electing": False,
                "elected_farm_income": 0,
                "qualified_farm_income": 0,
            },
        ],
    },

    "basic_scenario_high_income": {
        "dataset": {"name": "Basic scenario high income 2021-2024", "max_elected_farm_income": 60000, "qualified_farm_income": 0, "election_year": "2024"},
        "inputs": [
            {
                "year": 2024,
                "filing_status": "single",
                "taxable_income": 230000,
                "qualified_income": 200000,
                "is_electing": True,
                "elected_farm_income": 60000,
                "qualified_farm_income": 0,
            },
            {
                "year": 2023,
                "filing_status": "single",
                "taxable_income": 340000,
                "qualified_income": 40000,
                "is_electing": True,
                "elected_farm_income": 30000,
                "qualified_farm_income": 0,
            },
            {
                "year": 2022,
                "filing_status": "MFJ",
                "taxable_income": 460000,
                "qualified_income": 280000,
                "is_electing": True,
                "elected_farm_income": 15000,
                "qualified_farm_income": 0,
            },
            {
                "year": 2021,
                "filing_status": "MFJ",
                "taxable_income": 315000,
                "qualified_income": 2000,
                "is_electing": True,
                "elected_farm_income": 90000,
                "qualified_farm_income": 0,
            },
        ],
    },

    "basic_scenario_older_years": {
        "inputs": [
            {
                "year": 2021,
                "filing_status": "MFJ",
                "taxable_income": 100000,
                "qualified_income": 40000,
                "is_electing": False,
                "elected_farm_income": 0,
                "qualified_farm_income": 0,
            },
            {
                "year": 2020,
                "filing_status": "MFJ",
                "taxable_income": 100000,
                "qualified_income": 40000,
                "is_electing": False,
                "elected_farm_income": 0,
                "qualified_farm_income": 0,
            },
            {
                "year": 2019,
                "filing_status": "MFJ",
                "taxable_income": 100000,
                "qualified_income": 40000,
                "is_electing": False,
                "elected_farm_income": 0,
                "qualified_farm_income": 0,
            },
            {
                "year": 2018,
                "filing_status": "MFJ",
                "taxable_income": 100000,
                "qualified_income": 40000,
                "is_electing": False,
                "elected_farm_income": 0,
                "qualified_farm_income": 0,
            },
        ],
    },

    "unsorted_older_years": {
        "dataset": {"name": "Unsorted years 2021-2018", "max_elected_farm_income": 0, "qualified_farm_income": 0, "election_year": "2021"},
        "inputs": [
            {
                "year": 2018,
                "filing_status": "MFJ",
                "taxable_income": 100000,
                "qualified_income": 40000,
                "is_electing": False,
                "elected_farm_income": 0,
                "qualified_farm_income": 0,
            },
            {
                "year": 2020,
                "filing_status": "MFJ",
                "taxable_income": 100000,
                "qualified_income": 40000,
                "is_electing": False,
                "elected_farm_income": 0,
                "qualified_farm_income": 0,
            },
            {
                "year": 2021,
                "filing_status": "MFJ",
                "taxable_income": 100000,
                "qualified_income": 40000,
                "is_electing": False,
                "elected_farm_income": 0,
                "qualified_farm_income": 0,
            },
            {
                "year": 2019,
                "filing_status": "MFJ",
                "taxable_income": 100000,
                "qualified_income": 40000,
                "is_electing": False,
                "elected_farm_income": 0,
                "qualified_farm_income": 0,
            },
        ],
    },

    "none_elected": {
        "dataset": {"name": "No elected income 2021-2024", "max_elected_farm_income": 0, "qualified_farm_income": 0, "election_year": "2024"},
        "inputs": [
            {
                "year": 2024,
                "filing_status": "single",
                "taxable_income": 100000,
                "qualified_income": 0,
                "is_electing": False,
                "elected_farm_income": 0,
                "qualified_farm_income": 0,
            },
            {
                "year": 2023,
                "filing_status": "single",
                "taxable_income": 200000,
                "qualified_income": 0,
                "is_electing": False,
                "elected_farm_income": 0,
                "qualified_farm_income": 0,
            },
            {
                "year": 2022,
                "filing_status": "single",
                "taxable_income": 300000,
                "qualified_income": 0,
                "is_electing": False,
                "elected_farm_income": 0,
                "qualified_farm_income": 0,
            },
            {
                "year": 2021,
                "filing_status": "single",
                "taxable_income": 400000,
                "qualified_income": 0,
                "is_electing": False,
                "elected_farm_income": 0,
                "qualified_farm_income": 0,
            },
        ],
    },

    "basic_scenario_electing": {
        "dataset": {"name": "2022-2024 electing, no 2021 election", "max_elected_farm_income": 10000, "qualified_farm_income": 0, "election_year": "2024"},
        "inputs": [
            {
                "year": 2024,
                "filing_status": "MFJ",
                "taxable_income": 120000,
                "qualified_income": 105000,
                "is_electing": True,
                "elected_farm_income": 10000,
                "qualified_farm_income": 0,
            },
            {
                "year": 2023,
                "filing_status": "MFJ",
                "taxable_income": 85000,
                "qualified_income": 70000,
                "is_electing": True,
                "elected_farm_income": 20000,
                "qualified_farm_income": 1000,
            },
            {
                "year": 2022,
                "filing_status": "single",
                "taxable_income": 55000,
                "qualified_income": 40000,
                "is_electing": True,
                "elected_farm_income": 5000,
                "qualified_farm_income": 0,
            },
            {
                "year": 2021,
                "filing_status": "MFJ",
                "taxable_income": 96000,
                "qualified_income": 45000,
                "is_electing": False,
                "elected_farm_income": 0,
                "qualified_farm_income": 0,
            },
        ],
    },

    "basic_scenario_electing_2023": {
        "dataset": {"name": "2021-2023 electing, no 2020 election", "max_elected_farm_income": 10000, "qualified_farm_income": 0, "election_year": "2023"},
        "inputs": [
            {
                "year": 2023,
                "filing_status": "MFJ",
                "taxable_income": 120000,
                "qualified_income": 105000,
                "is_electing": True,
                "elected_farm_income": 10000,
                "qualified_farm_income": 0,
            },
            {
                "year": 2022,
                "filing_status": "MFJ",
                "taxable_income": 85000,
                "qualified_income": 70000,
                "is_electing": True,
                "elected_farm_income": 20000,
                "qualified_farm_income": 1000,
            },
            {
                "year": 2021,
                "filing_status": "single",
                "taxable_income": 55000,
                "qualified_income": 40000,
                "is_electing": True,
                "elected_farm_income": 5000,
                "qualified_farm_income": 0,
            },
            {
                "year": 2020,
                "filing_status": "MFJ",
                "taxable_income": 96000,
                "qualified_income": 45000,
                "is_electing": False,
                "elected_farm_income": 0,
                "qualified_farm_income": 0,
            },
        ],
    },

    "optimization": {
        "dataset": {"name": "optimization test", "max_elected_farm_income": 50000, "qualified_farm_income": 0, "election_year": "2024"},
        "inputs": [
            {
                "year": 2024,
                "filing_status": "MFJ",
                "taxable_income": 110000,
                "qualified_income": 0,
                "is_electing": True,
                "elected_farm_income": 50000,
                "qualified_farm_income": 0,
            },
            {
                "year": 2023,
                "filing_status": "MFJ",
                "taxable_income": 70000,
                "qualified_income": 0,
                "is_electing": True,
                "elected_farm_income": 5000,
                "qualified_farm_income": 0,
            },
            {
                "year": 2022,
                "filing_status": "MFJ",
                "taxable_income": 65000,
                "qualified_income": 0,
                "is_electing": True,
                "elected_farm_income": 5000,
                "qualified_farm_income": 0,
            },
            {
                "year": 2021,
                "filing_status": "MFJ",
                "taxable_income": 72000,
                "qualified_income": 0,
                "is_electing": True,
                "elected_farm_income": 5000,
                "qualified_farm_income": 0,
            },
        ],
    },


    "optimization_older_years": {
        "dataset": {"name": "optimization test older years", "max_elected_farm_income": 50000, "qualified_farm_income": 25000, "election_year": "2022"},
        "inputs": [
            {
                "year": 2022,
                "filing_status": "MFJ",
                "taxable_income": 110000,
                "qualified_income": 0,
                "is_electing": True,
                "elected_farm_income": 50000,
                "qualified_farm_income": 25000,
            },
            {
                "year": 2021,
                "filing_status": "MFJ",
                "taxable_income": 70000,
                "qualified_income": 0,
                "is_electing": True,
                "elected_farm_income": 5000,
                "qualified_farm_income": 0,
            },
            {
                "year": 2020,
                "filing_status": "MFJ",
                "taxable_income": 65000,
                "qualified_income": 0,
                "is_electing": True,
                "elected_farm_income": 5000,
                "qualified_farm_income": 0,
            },
            {
                "year": 2019,
                "filing_status": "MFJ",
                "taxable_income": 72000,
                "qualified_income": 0,
                "is_electing": True,
                "elected_farm_income": 5000,
                "qualified_farm_income": 0,
            },
        ],
    },

    "varied_income": {
        "dataset": {"name": "varied income for bracket thresholds", "max_elected_farm_income": 50000, "qualified_farm_income": 25000, "election_year": "2022"},
        "inputs": [
            {
                "year": 2024,
                "filing_status": "MFJ",
                "taxable_income": 120000,
                "qualified_income": 15000,
                "is_electing": True,
                "elected_farm_income": 10000,
                "qualified_farm_income": 0,
            },
            {
                "year": 2023,
                "filing_status": "MFJ",
                "taxable_income": 85000,
                "qualified_income": 10000,
                "is_electing": True,
                "elected_farm_income": 20000,
                "qualified_farm_income": 1000,
            },
            {
                "year": 2022,
                "filing_status": "single",
                "taxable_income": 55000,
                "qualified_income": 4000,
                "is_electing": True,
                "elected_farm_income": 5000,
                "qualified_farm_income": 0,
            },
            {
                "year": 2021,
                "filing_status": "MFJ",
                "taxable_income": 496000,
                "qualified_income": 45000,
                "is_electing": False,
                "elected_farm_income": 0,
                "qualified_farm_income": 0,
            },
        ],
    },

    "varied_income_older_years": {
        "dataset": {"name": "varied income for bracket thresholds", "max_elected_farm_income": 10000, "qualified_farm_income": 0, "election_year": "2023"},
        "inputs": [
            {
                "year": 2021,
                "filing_status": "MFJ",
                "taxable_income": 120000,
                "qualified_income": 1000,
                "is_electing": True,
                "elected_farm_income": 10000,
                "qualified_farm_income": 0,
            },
            {
                "year": 2020,
                "filing_status": "MFJ",
                "taxable_income": 185000,
                "qualified_income": 5000,
                "is_electing": True,
                "elected_farm_income": 20000,
                "qualified_farm_income": 1000,
            },
            {
                "year": 2019,
                "filing_status": "single",
                "taxable_income": 335000,
                "qualified_income": 4000,
                "is_electing": True,
                "elected_farm_income": 5000,
                "qualified_farm_income": 0,
            },
            {
                "year": 2018,
                "filing_status": "MFJ",
                "taxable_income": 96000,
                "qualified_income": 5000,
                "is_electing": False,
                "elected_farm_income": 0,
                "qualified_farm_income": 0,
            },
        ],
    },
}

EXPECTED_OUTPUTS_BASIC_TAX_CALC = {
    "tax_calculation": {
        "qualified_income_edge_cases": {
            "total_tax": [7946, 101271, 107848, 91647],
        },
        "basic_scenario": {
            "total_tax": [5392, 1500, 3593, 8002],
        },
        "basic_scenario_high_income": {
            "total_tax": [30814, 82894, 72871, 63462],
        },
        "basic_scenario_older_years": {
            "total_tax": [9682, 9805, 9999, 10239],
        },
    },
}

EXPECTED_OUTPUTS_SORTED_YEARS = {
    "sort_years": {
        "unsorted_older_years": {
            "years": ["2021", "2020", "2019", "2018"],
        },
    },
}

EXPECTED_OUTPUT_SCHEDULE_J = {
    "allocate_income": {
        "qualified_income_edge_cases": {
            "allocated_taxable_income": [88000, 644000, 644000, 589000],
            "allocated_qualified_income": [137000, 601000, 541000, 641000],
        },
        "basic_scenario": {
            "allocated_taxable_income": [60000, 75000, 85000, 126000],
            "allocated_qualified_income": [105000, 70000, 40000, 45000],
        },
        "basic_scenario_high_income": {
            "allocated_taxable_income": [170000, 330000, 475000, 260000],
            "allocated_qualified_income": [200000, 40000, 280000, 2000],
        },
    },
    "create_map": {
        "basic_scenario": {
            "years": [2024, 2023, 2022, 2021],
        },
    },
    "tax_assignment": {
        "none_elected": {
            "line_11": 300000,
            "line_12": 78753,
            "line_15": 200000,
            "line_16": 42832,
            "line_3": 100000,
            "line_4": 17053,
            "line_7": 400000,
            "line_8": 114544,
        },
    },
    "adj_tax_assignment": {
        "none_elected": {
            "line_1": 100000,
            "line_5": 400000,
            "line_9": 300000,
            "line_13": 200000,
            "line_19": 114544,
            "line_20": 78753,
            "line_21": 42832,
            "election_year_base_tax": 17053,
        },
    },
}

EXPECTED_OUTPUTS_FULL_SCH_J_CALC = {
    "full_sch_j_calc": {
        "basic_scenario_electing": {
            "line_1": 120000,
            "line_2a": 10000,
            "line_2b": 0.00,
            "line_3": 110000,
            "line_4": 2892,
            "line_5": 104333,
            "line_6": 3333,
            "line_7": 107667,
            "line_8": 11112,
            "line_9": 56667,
            "line_10": 3333,
            "line_11": 60000,
            "line_12": 4903,
            "line_13": 65000,
            "line_14": 3333,
            "line_15": 68333,
            "line_16": 0,
            "line_17": 18908,
            "line_18": 18908,
            "line_19": 10212,
            "line_20": 4003,
            "line_21": 0,
            "line_22": 14215,
            "line_23": 4692,
            "election_year_base_tax": 5392,
            "tax_delta": 700,
        },
        "basic_scenario_electing_2023": {
                "line_1": 120000,
                "line_2a": 10000,
                "line_2b": 0.00,
                "line_3": 110000,
                "line_4": 3612,
                "line_5": 104333,
                "line_6": 3333,
                "line_7": 107667,
                "line_8": 11235,
                "line_9": 56667,
                "line_10": 3333,
                "line_11": 60000,
                "line_12": 5101,
                "line_13": 65000,
                "line_14": 3333,
                "line_15": 68333,
                "line_16": 0.00,
                "line_17": 19948,
                "line_18": 19948,
                "line_19": 10335,
                "line_20": 4201,
                "line_21": 0,
                "line_22": 14536,
                "line_23": 5412,
                "election_year_base_tax": 6112,
                "tax_delta": 700,
            },
    },
}

EXPECTED_OUTPUTS_OPTIMIZATION = {
    "income_proportion": {
        "optimization": {
            "ordinary_percentage": 1,
            "qualified_percentage": 0,
        },
        "optimization_older_years": {
            "ordinary_percentage": .5,
            "qualified_percentage": .5,
        },
    },

    "first_and_last_instances": {
        "optimization": {
            "first_instance": {
                "line_23": 13331,
            },
            "last_instance": {
                "line_23": 6813,
            },
        },
        "optimization_older_years": {
            "first_instance": {
                "line_23": 14301,
            },
            "last_instance": {
                "line_23": 10014,
            },
        },
    },

    "complete_optimization": {
        "optimization" : {
            "results": None,
        },
        "optimization_older_years" : {
            "results": None,
        },
    },
}

EXPECTED_OUTPUTS_BRACKET_THRESHOLDS = {
    "bracket_thresholds": {
        "varied_income": {
            "brackets": {
                2024: {"0.12": 23201, "0.22": 94301, "0.24": 201051},
                2023: {"0.10": 0, "0.12": 22001, "0.22": 89451},
                2022: {"0.12": 10276, "0.22": 41776, "0.24": 89076},
                2021: {"0.32": 329851, "0.35": 418851, "0.37": 628301}},
        },
        "varied_income_older_years": {
            "brackets": {
                2021: {"0.12": 19901, "0.22": 81051, "0.24": 172751},
                2020: {"0.12": 19751, "0.22": 80251, "0.24": 171051},
                2019: {"0.32": 160726, "0.35": 204101, "0.37": 510301},
                2018: {"0.12": 19051, "0.22": 77401, "0.24": 165001}},
        },
    },
}
