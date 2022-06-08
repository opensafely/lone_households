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
        is_registered_with_tpp AND 
        (NOT died) AND
        (sex = "M" OR sex = "F") AND 
        (care_home_type = "PR") AND
        has_follow_up AND
        is_registered_with_tpp_feb2020 AND
        (stp != "") AND
        (imd = "1" OR "2" OR "3" OR "4" OR "5") AND
        household_size <= 15
        """,
        
        # all subsequent arguments are variable definitions
        # can use variables in here that are defined later in the file - don't have to define again here
        # the population argument has no bearing on the dummy data, it is just used to select patients in the real data
        # must match the dummy data to what you will see based on your defined & chosen population, not based on the data as a whole   
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
            include_date_of_match=True,
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
        household_size=household_as_of(
            "2020-02-01", 
            returning=household_size, 
            return_expectations={
            "int": {"distribution": "normal", "mean": 3, "stddev": 1},
            "incidence": 1,
        },
        ),
        
        ## living alone status
        living_alone=patients.categorised_as(
            {
                "0": "DEFAULT",
                "living alone": "household_size ==  1",
                "not living alone": "household_size > 1",
            }
        return_expectations={
                "rate":"universal",
                "category": {"ratios": {"living alone": 0.2, "not living alone": 0.8 }}
        },
        ),

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
        urban=address_as_of(
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
            combine_codelists(
                depression_codes,
                depression_icd_codes,
            ),    
            between=["first_day_of_month(index_date)", "last_day_of_month(index_date)"],
            returning="binary_flag",
            return_expectations={
                "incidence": 0.1,
            }, 
        ), 

        ## ANXIETY
        anxiety=patients.with_these_clinical_events(
            combine_codelists(
                anxiety_codes,
                anxiety_icd_codes,
            ),    
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
                self_harm_icd_codes,
                suicide_codes,
            ),    
            between=["first_day_of_month(index_date)", "last_day_of_month(index_date)"],
            returning="binary_flag",
            return_expectations={
                "incidence": 0.1,
            }, 
        ), 


        ## SEVERE MENTAL ILLNESS
        severe_mental_illness=patients.with_these_clinical_events(
            combine_codelists(
                severe_mental_illness_codes,
                severe_mental_illness_icd_codes,
            ),    
            between=["first_day_of_month(index_date)", "last_day_of_month(index_date)"],
           returning="binary_flag",
            return_expectations={
                "incidence": 0.1,
            }, 
        ), 

        ## OCD
        ocd=patients.with_these_clinical_events(
            combine_codelists(
                ocd_codes,
                ocd_icd_codes,
            ),    
            between=["first_day_of_month(index_date)", "last_day_of_month(index_date)"],
            returning="binary_flag",
            return_expectations={
                "incidence": 0.1,
            }, 
        ), 

        ## mental_illness_history_codes (codelists combined for history of)
        mental_illness_history=patients.with_these_clinical_events(
            mental_illness_history_codes,
            between=["first_day_of_month(index_date)", "last_day_of_month(index_date)"],
            returning="binary_flag",
            return_expectations={
                "incidence": 0.1,
            }, 
        ),         




    ### PRIMIS overall flag for shielded group
    shielded=patients.satisfying(
            """ severely_clinically_vulnerable
            AND NOT less_vulnerable""", 
        return_expectations={
            "incidence": 0.01,
                },

            ### SHIELDED GROUP - first flag all patients with "high risk" codes
        severely_clinically_vulnerable=patients.with_these_clinical_events(
            high_risk_codes, # note no date limits set
            find_last_match_in_period = True,
            return_expectations={"incidence": 0.02,},
        ),

        # find date at which the high risk code was added
        date_severely_clinically_vulnerable=patients.date_of(
            "severely_clinically_vulnerable", 
            date_format="YYYY-MM-DD",   
        ),

        ### NOT SHIELDED GROUP (medium and low risk) - only flag if later than 'shielded'
        less_vulnerable=patients.with_these_clinical_events(
            not_high_risk_codes, 
            on_or_after="date_severely_clinically_vulnerable",
            return_expectations={"incidence": 0.01,},
        ),
    ),
    
    
    # flag the newly expanded shielding group as of 15 feb (should be a subset of the previous flag)
    shielded_since_feb_15 = patients.satisfying(
            """severely_clinically_vulnerable_since_feb_15
                AND NOT new_shielding_status_reduced
                AND NOT previous_flag
            """,
        return_expectations={
            "incidence": 0.01,
                },
        
        ### SHIELDED GROUP - first flag all patients with "high risk" codes
        severely_clinically_vulnerable_since_feb_15=patients.with_these_clinical_events(
            high_risk_codes, 
            on_or_after= "2021-02-15",
            find_last_match_in_period = False,
            return_expectations={"incidence": 0.02,},
        ),

        # find date at which the high risk code was added
        date_vulnerable_since_feb_15=patients.date_of(
            "severely_clinically_vulnerable_since_feb_15", 
            date_format="YYYY-MM-DD",   
        ),

        ### check that patient's shielding status has not since been reduced to a lower risk level 
         # e.g. due to improved clinical condition of patient
        new_shielding_status_reduced=patients.with_these_clinical_events(
            not_high_risk_codes,
            on_or_after="date_vulnerable_since_feb_15",
            return_expectations={"incidence": 0.01,},
        ),
        
        # anyone with a previous flag of any risk level will not be added to the new shielding group
        previous_flag=patients.with_these_clinical_events(
            combine_codelists(high_risk_codes, not_high_risk_codes),
            on_or_before="2021-02-14",
            return_expectations={"incidence": 0.01,},
        ),
    ),
)

measures = [
        Measure(
            id="depression_rate",
            numerator="depression",
            denominator="population",
            group_by=["living_alone"],
        ),

        Measure(
            id="anxiety_rate",
            numerator="anxiety",
            denominator="population",
            group_by=["living_alone"],
        ),
    ]




    #SEVERE MENTAL ILLNESS, EATING DISORDERS AND SELF HARM BROKEN DOWN INTO CONSTITUENT PARTS
    Measure(
        id="severe_mental_illness_rate_gp",
        numerator="smi_gp",
        denominator="population",
        group_by=["living_alone"],
    ),

    Measure(
        id="severe_mental_illness_rate_hosp",
        numerator="smi_hosp",
        denominator="population",
        group_by=["living_alone"],
    ),

    Measure(
        id="severe_mental_illness_rate_emerg",
        numerator="smi_emerg",
        denominator="population",
        group_by=["living_alone"],
    ),


    Measure(
        id="eating_disorder_rate_gp",
        numerator="eating_gp",
        denominator="population",
        group_by=["living_alone"],
    ),

    Measure(
        id="eating_disorder_rate_hosp",
        numerator="eating_hosp",
        denominator="population",
        group_by=["living_alone"],
    ),

    Measure(
        id="eating_disorder_rate_emerg",
        numerator="eating_emerg",
        denominator="population",
        group_by=["living_alone"],
    ),

    Measure(
        id="eating_disorder_rate_death",
        numerator="eating_death",
        denominator="population",
        group_by=["living_alone"],
    ),

    Measure(
        id="self_harm_rate_gp",
        numerator="self_harm_gp",
        denominator="population",
        group_by=["living_alone"],
    ),

    Measure(
        id="self_harm_rate_hosp",
        numerator="self_harm_hosp",
        denominator="population",
        group_by=["living_alone"],
    ),

    Measure(
        id="self_harm_rate_emerg",
        numerator="self_harm_emerg",
        denominator="population",
        group_by=["living_alone"],
    ),

    Measure(
        id="self_harm_rate_death",
        numerator="self_harm_death",
        denominator="population",
        group_by=["living_alone"],
    ),


