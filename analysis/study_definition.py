# STUDY DEFINITION FOR BASELINE CHARACTERISTICS

# Import necessary functions

from cohortextractor import (
    StudyDefinition, 
    patients, 
    codelist, 
    codelist_from_csv,
    combine_codelists,
    filter_codes_by_category,
    Measure,
)     

# Import all codelists

from codelists import *




# Specify study definition

study = StudyDefinition(
    default_expectations={
        "date": {"earliest": "1900-01-01", "latest": "today"},
        "rate": "uniform",
        "incidence": 0.5,
    },


    # define the study population 
    # all study definitions have to have a study population definition - this selects all the patients for whom you want information
    # use the "patients.satisfying()" function to combine information from multiple different variables
    
    # define the study index date
    index_date="2018-01-01",    

    # INCLUDE: age 18+ on index date, male or female, registered with TPP at index date, with 3 months complete registration, a valid address and postcode
    # EXCLUDE: 15+ people in the household, missing age, missing sex, missing STP region, missing IMD, any person in household is care home, joined TPP after 01/02/2020

    population=patients.satisfying(
        # first argument is a string defining the population of interest using elementary logic syntax (= != < <= >= > AND OR NOT + - * /)
        """
        (age >= 18 AND age < 120) AND 
        (sex = "M" OR sex = "F")  
        """,
          
    ),

   
    # define the study variables

    # DEMOGRAPHICS

        ## sex 
        sex=patients.sex(
            return_expectations={
                "rate": "universal",
                "category": {"ratios": {"M": 0.49, "F": 0.51}},
            }
        ),

        ## age 
        age=patients.age_as_of(
            "index_date",
            return_expectations={
                "rate": "universal",
                "int": {"distribution": "population_ages"},
            },
        ),
    
        ## age groups 
        ageband_broad = patients.categorised_as(
            {   
                "0": "DEFAULT",
                "18-39": """ age >=  18 AND age < 40""",
                "40-59": """ age >=  40 AND age < 60""",
                "60-79": """ age >=  60 AND age < 80""",
                "80+": """ age >=  80 AND age < 120""",
            },
            return_expectations={
                "rate":"universal",
                "category": {"ratios": {"18-39": 0.3, "40-59": 0.3, "60-79":0.2, "80+":0.2 }}
            },
        ),
        

        ## ethnicity in 6 categories
        ethnicity6=patients.with_these_clinical_events(
            ethnicity_codes_6,
            returning="category",
            find_last_match_in_period=True,
            return_expectations={
                "category": {"ratios": {"1": 0.8, "5": 0.1, "3": 0.1}},
                "incidence": 0.75,
            },
        ),
        
    # REGISTRATION DETAILS
        # died
        died=patients.died_from_any_cause(
            on_or_before="index_date",
        ),

        ## registered with TPP on index date
        is_registered_with_tpp=patients.registered_as_of(
            "index_date",
        ),

        ## registered with TPP on date of household identification (1st Feb 2020)
        is_registered_with_tpp_feb2020=patients.registered_as_of(
            "2020-02-01",
        ),

        ## registered with one practice for 90 days prior to index date        
        has_follow_up=patients.registered_with_one_practice_between(
            "index_date - 90 days", "index_date",
        ),  

    # HOUSEHOLD INFORMATION
       
        ## care home status - This creates a variable called care_home_type which contains a 2 letter string which represents a type of care home environment. 
        # If the address is not valid, it defaults to an empty string.  Shouldn't have any as am including only those with valid address.
        care_home_type=patients.care_home_status_as_of(
            "index_date",
            categorised_as={
                "PC":
                """
                IsPotentialCareHome
                AND LocationDoesNotRequireNursing='Y'
                AND LocationRequiresNursing='N'
                """,
                "PN":
                """
                IsPotentialCareHome
                AND LocationDoesNotRequireNursing='N'
                AND LocationRequiresNursing='Y'
                """,
                "PS": "IsPotentialCareHome",
                "PR": "NOT IsPotentialCareHome",
                "": "DEFAULT",
            },
            return_expectations={
                "rate": "universal",
                "category": {"ratios": {"PC": 0.05, "PN": 0.05, "PS": 0.05, "PR": 0.84, "": 0.01},},
            },
        ),

        ## household ID
        household_id=patients.household_as_of(
            "2020-02-01",
            returning="pseudo_id",
            return_expectations={
                "int": {"distribution": "normal", "mean": 1000, "stddev": 200},
                "incidence": 1,
            },
        ),

         ## household size
        household_size=patients.household_as_of(
            "2020-02-01", 
            returning="household_size", 
            return_expectations={
                "int": {"distribution": "normal", "mean": 3, "stddev": 1},
                "incidence": 1,
            },
        ),
        
       ## living alone status
        living_alone=patients.categorised_as(
            {
                "missing": "DEFAULT",
                "living alone": "household_size = 1",
                "not living alone": "household_size > 1",
            },
            return_expectations={
                "rate":"universal",
                "category": {
                    "ratios": {
                        "living alone": 0.2, 
                        "not living alone": 0.8, 
                        },
                        },
            },
        ),       

        ## non-TPP patients in household
        mixed_household=patients.household_as_of(
        "2020-02-01",
        returning="has_members_in_other_ehr_systems",
        return_expectations={ "incidence": 0.75
        },
        ),

        ## percent of patients in TPP in the household
        percent_tpp=patients.household_as_of(
        "2020-02-01",
        returning="percentage_of_members_with_data_in_this_backend",
        return_expectations={"int": {"distribution": "normal", "mean": 75, "stddev": 10},
        },
        ),


    # ADMINISTRATIVE INFORMATION

        ## index of multiple deprivation, estimate of SES based on patient post code 
            imd=patients.categorised_as(
                {
                    "0": "DEFAULT",
                    "1": """index_of_multiple_deprivation >=1 AND index_of_multiple_deprivation < 32844*1/5""",
                    "2": """index_of_multiple_deprivation >= 32844*1/5 AND index_of_multiple_deprivation < 32844*2/5""",
                    "3": """index_of_multiple_deprivation >= 32844*2/5 AND index_of_multiple_deprivation < 32844*3/5""",
                    "4": """index_of_multiple_deprivation >= 32844*3/5 AND index_of_multiple_deprivation < 32844*4/5""",
                    "5": """index_of_multiple_deprivation >= 32844*4/5 AND index_of_multiple_deprivation < 32844""",
                },
                index_of_multiple_deprivation=patients.address_as_of(
                    "index_date",
                    returning="index_of_multiple_deprivation",
                    round_to_nearest=100,
                ),
                return_expectations={
                    "rate": "universal",
                    "category": {
                        "ratios": {
                            "0": 0.05,
                            "1": 0.19,
                            "2": 0.19,
                            "3": 0.19,
                            "4": 0.19,
                            "5": 0.19,
                        },
                    },
                },
            ),

        ## STP REGION     
        stp=patients.registered_practice_as_of(
            "2020-02-01",
            returning="stp_code",
            return_expectations={
                "rate": "universal",
                "category": {
                    "ratios": {
                        "STP1": 0.1,
                        "STP2": 0.1,
                        "STP3": 0.1,
                        "STP4": 0.1,
                        "STP5": 0.1,
                        "STP6": 0.1,
                        "STP7": 0.1,
                        "STP8": 0.1,
                        "STP9": 0.1,
                        "STP10": 0.1,
                    }
                },
            },
        ),

        ## URBAN/RURAL LOCATION
        urban=patients.address_as_of(
            "2020-02-01",
            returning="rural_urban_classification",
            return_expectations={
                "rate": "universal",
                "category": {"ratios": {1: 0.125, 2: 0.125, 3: 0.125, 4: 0.125, 5: 0.125, 6: 0.125, 7: 0.125, 8: 0.125}},
            }
        ),




    # OUTCOMES - MENTAL HEALTH

        ## DEPRESSION
        depression=patients.with_these_clinical_events(
            codelist=depression_codes,    
            between=["first_day_of_month(index_date)", "last_day_of_month(index_date)"],
            returning="binary_flag",
            return_expectations={
                "incidence": 0.1,
            }, 
        ),

        ## ANXIETY
        anxiety=patients.with_these_clinical_events(
            codelist=anxiety_codes,    
            between=["first_day_of_month(index_date)", "last_day_of_month(index_date)"],
            returning="binary_flag",
            return_expectations={
                "incidence": 0.1,
            }, 
        ), 

        ## SELF HARM
        self_harm=patients.with_these_clinical_events(
            combine_codelists(
                self_harm_10plus_codes,
                self_harm_15plus_codes,
            ),    
            between=["first_day_of_month(index_date)", "last_day_of_month(index_date)"],
            returning="binary_flag",
            return_expectations={
                "incidence": 0.1,
            }, 
        ), 

        ## EATING DISORDERS
        eating_disorder=patients.with_these_clinical_events(
            codelist=eating_disorder_codes,
            between=["first_day_of_month(index_date)", "last_day_of_month(index_date)"],
            returning="binary_flag",
            return_expectations={
                "incidence": 0.1,
            }, 
        ), 

        ## SEVERE MENTAL ILLNESS
        severe_mental_illness=patients.with_these_clinical_events(
            codelist=severe_mental_illness_codes,
            between=["first_day_of_month(index_date)", "last_day_of_month(index_date)"],
            returning="binary_flag",
            return_expectations={
                "incidence": 0.1,
            }, 
        ), 

        ## OCD
        ocd=patients.with_these_clinical_events(
            codelist=ocd_codes,
            between=["first_day_of_month(index_date)", "last_day_of_month(index_date)"],
            returning="binary_flag",
            return_expectations={
                "incidence": 0.1,
            }, 
        ), 


)

measures = [
    Measure(
        id="depression_rate",
        numerator="depression",
        denominator="population",
        group_by=["living_alone"],
    ),

]






