import copy
import json
import project.djangofiles.tax.calculations.tax_brackets as tax_brackets

def find_ordinary_bracket(year, tax_info):
    for rate, (lower, upper, prior_tax) in tax_brackets.ORDINARY_TAX_TABLES[year][tax_info['Filing Status']].items():
        #first calculate taxable ordinary
        tax_info['Taxable Ordinary'] = max(tax_info['Taxable Income'] - tax_info['Qualified Income'], 0)

        #find ordinary bracket
        if lower <= tax_info['Taxable Ordinary'] <= upper:             
            tax_info['Ordinary Rate'] = rate 
            tax_info['Lower Ordinary Bound'] = lower 
            tax_info['Upper Ordinary Bound'] = upper
            tax_info['Tax On Prior Brackets'] = prior_tax
            return
        
    #if not in any brackets    
    print("Income too large or negative") 
    return 1

def find_ordinary_tax(tax_info):

    #typical tax calculation
    tax_info['Ordinary Tax'] = ((tax_info['Taxable Ordinary'] - tax_info['Lower Ordinary Bound']) * tax_info['Ordinary Rate']) + tax_info['Tax On Prior Brackets']     
    return

def find_qualified_tax(year, tax_info):

    #intialize some variables for ease of use
    filing_status = tax_info['Filing Status']
    taxable_income = tax_info['Taxable Income']
    taxable_ordinary = tax_info['Taxable Ordinary']
    qualified_income = tax_info['Qualified Income']

    #if qualified less than 0% bracket, all at 0%
    if taxable_income < tax_brackets.QUALIFIED_TAX_TABLES[year][filing_status][0][1]:            
        qualified_tax = qualified_income * 0     

    #see if taxable exceeds 15%                                     
    elif taxable_income < tax_brackets.QUALIFIED_TAX_TABLES[year][filing_status][.15][1]:

        #tax at 0% = 0% bracket - ordinary          
        zero_bracket = max((tax_brackets.QUALIFIED_TAX_TABLES[year][filing_status][0][1] - taxable_ordinary),0)
        #tax at 15% = qualified - 0% tax        
        fifteen_bracket = qualified_income - zero_bracket
        qualified_tax = (zero_bracket * 0) + (fifteen_bracket * .15)

    #above 15% bracket, should be minimum 15%
    else:        
        #0% bracket - ordinary: cases where high taxable and high qualified
        zero_bracket = max(tax_brackets.QUALIFIED_TAX_TABLES[year][filing_status][0][1] - taxable_ordinary, 0)

        #15% bracket - tax at zero (if any) - ordinary  
        fifteen_bracket = max(tax_brackets.QUALIFIED_TAX_TABLES[year][filing_status][.15][1] - zero_bracket - taxable_ordinary, 0)

        #find amount at 20%
        twenty_bracket = qualified_income - fifteen_bracket - zero_bracket                                          
        qualified_tax = (zero_bracket * 0) + (fifteen_bracket * .15) + (twenty_bracket * .20)
    
    tax_info['Qualified Tax'] = max(qualified_tax, 0)

def calculate_total_tax(tax_info):
    # loop through all years
    # results get stored inside function
    for year, tax_results in tax_info.items():
        #get ordinary bracket
        find_ordinary_bracket(year, tax_results)

        #find ordinary tax 
        find_ordinary_tax(tax_results)
        
        #find qualified tax
        find_qualified_tax(year, tax_results)

        #get total tax
        tax_results['Total Tax'] = max(tax_results['Ordinary Tax'] + tax_results['Qualified Tax'], 0)

    return


def schedule_j_calculation(tax_info):
    
    #create placeholder for ease of use
    sch_j_form = tax_info['Schedule J Optimization']['Schedule J calc']
    sch_j_adjusted_info = tax_info['Schedule J Optimization']['Adjusted Tax Info']

    sch_j_form['Line 1'] = tax_info['Standard Tax'][2024]['Taxable Income']
    sch_j_form['Line 2a'] = tax_info['Schedule J Optimization']['Max Elected Farm Income']
    sch_j_form['Line 2b'] = tax_info['Schedule J Optimization']['Max Elected Farm Income Cap Gains'] #think about where to put this variable
    sch_j_form['Line 3'] = sch_j_form['Line 1'] - sch_j_form['Line 2a']

    #intitialize elected farm income amounts and find 1/3 of each
    total_elected =  tax_info['Schedule J Optimization']['Max Elected Farm Income']
    elected_qualified = tax_info['Schedule J Optimization']['Max Elected Farm Income Cap Gains']
    elected_ordinary =  total_elected - elected_qualified
    tax_info['Schedule J Optimization']['Max Elected Farm Income Ordinary'] = elected_ordinary

    # Copy 2024 numbers from baseline and decrease incomes by elected amounts
    sch_j_adjusted_info[2024]['Taxable Income'] = tax_info['Standard Tax'][2024]['Taxable Income']
    sch_j_adjusted_info[2024]['Qualified Income'] = tax_info['Standard Tax'][2024]['Qualified Income']
    sch_j_adjusted_info[2024]['Taxable Ordinary'] = tax_info['Standard Tax'][2024]['Taxable Ordinary']

    sch_j_adjusted_info[2024]['Taxable Income'] -= sch_j_form['Line 2a']
    sch_j_adjusted_info[2024]['Qualified Income'] -= elected_qualified
    sch_j_adjusted_info[2024]['Taxable Ordinary'] -= elected_ordinary

    #find tax on 2024 taxable less elected farm income
    calculate_total_tax({2024: sch_j_adjusted_info[2024]})
    sch_j_form['Line 4'] = sch_j_adjusted_info[2024]['Total Tax']

    distribute_total_elected = total_elected / 3
    #fill in respective 1/3 of farm income lines
    sch_j_form.update(dict.fromkeys(['Line 6', 'Line 10', 'Line 14'], distribute_total_elected))
    distribute_farm_ordinary = elected_ordinary / 3
    distribute_farm_qualified = elected_qualified / 3


    # distribute elected farm income to each year, calculate tax
    update_lines = {
            2021: ['Line 5', 'Line 7', 'Line 8'],
            2022: ['Line 9', 'Line 11', 'Line 12'],
            2023: ['Line 13', 'Line 15', 'Line 16']
        }
    for year, (base_income, adjusted_income, calculate_tax) in update_lines.items():
            
            #pull income from given tax info
            base_ordinary_income = tax_info['Standard Tax'][year]['Taxable Ordinary']
            base_qualified_income = tax_info['Standard Tax'][year]['Qualified Income']
            base_taxable_income = tax_info['Standard Tax'][year]['Taxable Income']

            sch_j_form[base_income] = base_taxable_income

            #increase income by 1/3
            adjusted_ordinary_income = base_ordinary_income + distribute_farm_ordinary
            adjusted_qualified_income = base_qualified_income + distribute_farm_qualified
            adjusted_taxable_income = base_taxable_income + distribute_total_elected

            #place increased income total taxable income into Sch J
            sch_j_form[adjusted_income] = adjusted_taxable_income 

            #increase ordinary, qualified, taxable income with respective elected farm incomes
            sch_j_adjusted_info[year]['Taxable Ordinary'] = adjusted_ordinary_income
            sch_j_adjusted_info[year]['Qualified Income'] = adjusted_qualified_income
            sch_j_adjusted_info[year]['Taxable Income'] = adjusted_taxable_income 

            #calculate tax with new income. Passes in dict so we don't need to restructure tax calc
            calculate_total_tax({year: sch_j_adjusted_info[year]})
            sch_j_form[calculate_tax] = sch_j_adjusted_info[year]['Total Tax']

    sch_j_form['Line 17'] = sch_j_form['Line 4'] + sch_j_form['Line 8'] + sch_j_form['Line 12'] + sch_j_form['Line 16']
    sch_j_form['Line 18'] = sch_j_form['Line 17']

    # get baseline tax from each year
    base_tax = {
            2021: 'Line 19',
            2022: 'Line 20',
            2023: 'Line 21',
        }

    for year, (tax_amount) in base_tax.items():
        sch_j_form[tax_amount] = tax_info['Standard Tax'][year]['Total Tax']

    # Total base tax from prior years
    sch_j_form['Line 22'] = sch_j_form['Line 19'] + sch_j_form['Line 20'] + sch_j_form['Line 21']

    # Schedule J tax for 2024
    sch_j_form['Line 23'] = sch_j_form['Line 18'] - sch_j_form['Line 22']


def schedule_j_optimization(tax_info):
    results = []
    current_total_elected = tax_info['Schedule J Optimization']['Max Elected Farm Income']
    current_ordinary_elected = tax_info['Schedule J Optimization']['Max Elected Farm Income Ordinary']
    current_qualified_elected = tax_info['Schedule J Optimization']['Max Elected Farm Income Cap Gains']

    # find percentage so we can decrease proportionally
    ordinary_percentage = current_ordinary_elected / current_total_elected
    qualified_percentage = current_qualified_elected / current_total_elected
    
    while current_total_elected >= 0:
        # Deep copy so we don't muck up original data
        tax_info_copy = copy.deepcopy(tax_info)
        tax_info_copy['Schedule J Optimization']['Max Elected Farm Income'] = current_total_elected
        tax_info_copy['Schedule J Optimization']['Max Elected Farm Income Ordinary'] = current_ordinary_elected
        tax_info_copy['Schedule J Optimization']['Max Elected Farm Income Cap Gains'] = current_qualified_elected

        schedule_j_calculation(tax_info_copy)

        # Store only sch j info, since we don't need the dupe info
        results.append(tax_info_copy['Schedule J Optimization'])

        current_total_elected -= 500
        current_ordinary_elected -= 500 * ordinary_percentage
        current_qualified_elected -= 500 * qualified_percentage
        

    #find the min tax, need to figure out how to ignore negative Sch J results 
    #min_tax = min(r['Schedule J calc']['Line 23'] for r in results)
    
    min_tax = min(results, key=lambda r: r['Schedule J calc']['Line 23'])
    print(min_tax)

    
    # filtered = [{k: d[k] for k in ('Adjusted Tax Info', 'Max Elected Farm Income')} for d in results]
    return results

    

user_basic_info = {
    'name': None,
    'client_ID': None
}

user_tax_info = {
    'Standard Tax': {
        2021: {
        # user inputs
        'Filing Status': 'Married Filing Jointly',
        'Taxable Income': 50000,
        'Qualified Income': 175000,
        # computation results
        'Taxable Ordinary': None,
        'Ordinary Rate': None,
        'Lower Ordinary Bound': None,
        'Upper Ordinary Bound': None,
        'Tax On Prior Brackets': None,
        'Ordinary Tax': None,
        'Qualified Tax': None,
        'Total Tax': None
        },
    2022: {
        # user inputs
        'Filing Status': 'Married Filing Jointly',
        'Taxable Income': 84100,
        'Qualified Income': 10000,
        # computation results
        'Taxable Ordinary': None,
        'Ordinary Rate': None,
        'Lower Ordinary Bound': None,
        'Upper Ordinary Bound': None,
        'Tax On Prior Brackets': None,
        'Ordinary Tax': None,
        'Qualified Tax': None,
        'Total Tax': None
    },
    2023: {
        # user inputs
        'Filing Status': 'Married Filing Jointly',
        'Taxable Income': 75000,
        'Qualified Income': 0,
        # computation results
        'Taxable Ordinary': None,
        'Ordinary Rate': None,
        'Lower Ordinary Bound': None,
        'Upper Ordinary Bound': None,
        'Tax On Prior Brackets': None,
        'Ordinary Tax': None,
        'Qualified Tax': None,
        'Total Tax': None
    },
    2024: {
        # user inputs
        'Filing Status': 'Married Filing Jointly',
        'Taxable Income': 100000,
        'Qualified Income': 20000,
        # computation results
        'Taxable Ordinary': None,
        'Ordinary Rate': None,
        'Lower Ordinary Bound': None,
        'Upper Ordinary Bound': None,
        'Tax On Prior Brackets': None,
        'Ordinary Tax': None,
        'Qualified Tax': None,
        'Total Tax': None
        }
    },
    'Schedule J Optimization': {
        'Max Elected Farm Income': 50000,
        'Max Elected Farm Income Cap Gains': 10000,
        'Max Elected Farm Income Ordinary': None,
        'Schedule J calc': {
            'Line 1': None,
            'Line 2a': None,
            'Line 2b': None,
            'Line 2c': None,
            'Line 3': None,
            'Line 4': None,
            'Line 5': None,
            'Line 6': None,
            'Line 7': None,
            'Line 8': None,
            'Line 9': None,
            'Line 10': None,
            'Line 11': None,
            'Line 12': None,
            'Line 13': None,
            'Line 14': None,
            'Line 15': None,
            'Line 16': None,
            'Line 17': None,
            'Line 18': None,
            'Line 19': None,
            'Line 20': None,
            'Line 21': None,
            'Line 22': None,
            'Line 23': None
        },
        'Adjusted Tax Info': {
            2021: {
                'Filing Status': 'Married Filing Jointly',
                'Taxable Income': 84900,
                'Qualified Income': 0,
                'Taxable Ordinary': None,
                'Ordinary Rate': None,
                'Lower Ordinary Bound': None,
                'Upper Ordinary Bound': None,
                'Prior Ordinary Bracket Tax': None,
                'Ordinary Tax': None,
                'Qualified Tax': None,
                'Total Tax': None
            },
            2022: {
                'Filing Status': 'Married Filing Jointly',
                'Taxable Income': 84100,
                'Qualified Income': 10000,
                'Taxable Ordinary': None,
                'Ordinary Rate': None,
                'Lower Ordinary Bound': None,
                'Upper Ordinary Bound': None,
                'Prior Ordinary Bracket Tax': None,
                'Ordinary Tax': None,
                'Qualified Tax': None,
                'Total Tax': None
            },
            2023: {
                'Filing Status': 'Married Filing Jointly',
                'Taxable Income': 82300,
                'Qualified Income': 10000,
                'Taxable Ordinary': None,
                'Ordinary Rate': None,
                'Lower Ordinary Bound': None,
                'Upper Ordinary Bound': None,
                'Prior Ordinary Bracket Tax': None,
                'Ordinary Tax': None,
                'Qualified Tax': None,
                'Total Tax': None
            },
            2024: {
                'Filing Status': 'Married Filing Jointly',
                'Taxable Income': 100000,
                'Qualified Income': 20000,
                'Taxable Ordinary': None,
                'Ordinary Rate': None,
                'Lower Ordinary Bound': None,
                'Upper Ordinary Bound': None,
                'Prior Ordinary Bracket Tax': None,
                'Ordinary Tax': None,
                'Qualified Tax': None,
                'Total Tax': None
            }
        }
    }
}


calculate_total_tax(user_tax_info['Standard Tax'])
# Run initially so we can get our baseline stored in user_tax_info
schedule_j_calculation(user_tax_info)

with open('results', 'w') as file:
        json.dump(schedule_j_optimization(user_tax_info), file, indent=4)
