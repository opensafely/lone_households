from cohortextractor import (
    StudyDefinition, 
    patients, 
    codelist, 
    codelist_from_csv,
    combine_codelists,
    filter_codes_by_category,
)     


study = StudyDefinition(
    #default_expectations, index_date and population are reserved names within StudyDefinition()
    # all variables that you want in your dataset are declared wihtin the StudyDefinition() function, using functions in the form patients.function_name()
    # for multiple study definition files, use siffix e.g. study_definition_copd.py, study_definition_asthma.py - will give corresponding outputs as input_copd.csv, etc
    # or if the only difference between 2 study definitions is the index date, then you can avoid having multiple study definition files
    # for this we will need to use the yaml

    # define default dummy data behaviour
    # dummy data for all variables defined here
    # event dates are expected to be distributed between 1900 and today, with exponentially increasing frequency
    # events occurring for 50% of patients
    # values for binary variables positive 50% of the time (i.e. 0 for 50%, 1 for 50%)
    # values for categorical present (non-missing) 50% of the time
    # values for numeric variables present 50% of the time
    # values for date variables can either be "exponential_increase" or "universal"
    # override default expectations with "return expectations" argument
    default_expectations={
        "date": {"earliest": "1900-01-01", "latest": "today"},
        "rate": "uniform",
        "incidence": 0.5,
    },

    #define the study index date
    index_date="2020-01-01",

    # define the study population 
    # all study definitions have to have a study population definition - this selects all the patients for whom you want information
    # - Emily check that this is the population you want... population=patients.all(), is the alternative?
    # use the "patients.satisfying()" function to combine information from multiple different variables
    
    population=patients.satisfying(
        # first argument is a string defining the population of interest using elementary logic syntax (= != < <= >= > AND OR NOT + - * /)
        "has_follow_up AND has_copd",
        # all subsequent arguments are variable definitions
        # can use variables in here that are defined later in the file - don't have to define again here
        # the population argument has no bearing on the dummy data, it is just used to select patients in the real data
        # must match the dummy data to what you will see based on your defined & chosen population, not based on the data as a whole
        has_follow_up=patients.registered_with_one_practice_between(
            "2019-03-01", "2020-03-01"
        ),
        has_copd=patients.with_these_clinical_events(
            copd_codes, on_or_before="2017-03-01"
        ),
    ),
    # define the study variables

    # Emily - decide how to define age
    age=patients.age_as_of(
        "2019-09-01",
        return_expectations={
            "rate": "universal",
            "int": {"distribution": "population_ages"},
        },
    ),
)
