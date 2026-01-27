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
    }
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
