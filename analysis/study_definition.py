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
    # all the study definitions have to have a study population definition - this selects all the patients for whom you want information
    # use the "patients.satisfying()" function to combine information from multiple different variables
    
    # define the study index date
    index_date="2018-03-01",    

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
        (imd ! = "0") AND
        household_size <= 15
        """,
          
    ),

   
    # define the study variables

    # DEMOGRAPHICS - sex, age, ethnicity

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



    # OUTCOMES - MENTAL HEALTH
    # DEPRESSION, ANXIETY, OCD - PRIMARY CARE ONLY
    # SERIOUS MENTAL ILLNESS - PRIMARY CARE, A&E ATTENDANCE, HOSPITAL ADMISSION 
    # SELF HARM, EATING DISORDER - PRIMARY CARE, A&E ATTENDANCE, HOSPITAL ADMISSION, ONS MORTALITY

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

        ## OCD
        ocd=patients.with_these_clinical_events(
            codelist=ocd_codes,
            between=["first_day_of_month(index_date)", "last_day_of_month(index_date)"],
            returning="binary_flag",
            return_expectations={
                "incidence": 0.1,
            }, 
        ), 

        ## SEVERE MENTAL ILLNESS
        severe_mental=patients.satisfying(
            "smi_gp OR smi_hosp OR smi_emerg",
       
            smi_gp=patients.with_these_clinical_events(
                codelist=severe_mental_illness_codes,
                between=["first_day_of_month(index_date)", "last_day_of_month(index_date)"],
                returning="binary_flag",
                return_expectations={
                    "incidence": 0.1,
                }, 
            ), 

            smi_hosp=patients.admitted_to_hospital(
                between=["first_day_of_month(index_date)", "last_day_of_month(index_date)"],
                with_these_diagnoses=severe_mental_illness_icd_codes,
                returning="binary_flag",
                return_expectations={
                    "incidence": 0.1,
                }, 
            ),
            
            smi_emerg=patients.attended_emergency_care(
                between=["first_day_of_month(index_date)", "last_day_of_month(index_date)"],
                with_these_diagnoses=severe_mental_illness_icd_codes,
                returning="binary_flag",
                return_expectations={
                    "incidence": 0.1,
                }, 
            ),
        ),

        ## SELF HARM
        self_harm=patients.satisfying(
            "self_harm_gp OR self_harm_hosp OR self_harm_emerg OR self_harm_death",

            self_harm_gp=patients.with_these_clinical_events(
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
            self_harm_hosp=patients.admitted_to_hospital(
                between=["first_day_of_month(index_date)", "last_day_of_month(index_date)"],
                with_these_diagnoses=self_harm_icd_codes,
                returning="binary_flag",
                return_expectations={
                    "incidence": 0.1,
                }, 
            ),
            
            self_harm_emerg=patients.attended_emergency_care(
                between=["first_day_of_month(index_date)", "last_day_of_month(index_date)"],
                with_these_diagnoses=self_harm_icd_codes,
                returning="binary_flag",
                return_expectations={
                    "incidence": 0.1,
                }, 
            ),

            self_harm_death=patients.with_these_codes_on_death_certificate(
                combine_codelists(
                    self_harm_icd_codes,
                    suicide_codes,
                ),  
                between=["first_day_of_month(index_date)", "last_day_of_month(index_date)"],
                returning="binary_flag",
                return_expectations={
                    "incidence": 0.1,
                }, 
            ),
        ),

        ## EATING DISORDERS
        eating_disorder=patients.satisfying(
            "eating_gp OR eating_hosp OR eating_emerg OR eating_death",
            eating_gp=patients.with_these_clinical_events(
                codelist=eating_disorders_codes,
                between=["first_day_of_month(index_date)", "last_day_of_month(index_date)"],
                returning="binary_flag",
                return_expectations={
                    "incidence": 0.1,
                }, 
            ), 

            eating_hosp=patients.admitted_to_hospital(
                between=["first_day_of_month(index_date)", "last_day_of_month(index_date)"],
                with_these_diagnoses=eating_disorders_icd_codes,
                returning="binary_flag",
                return_expectations={
                    "incidence": 0.1,
                }, 
            ),
            
            eating_emerg=patients.attended_emergency_care(
                between=["first_day_of_month(index_date)", "last_day_of_month(index_date)"],
                with_these_diagnoses=eating_disorders_icd_codes,
                returning="binary_flag",
                return_expectations={
                    "incidence": 0.1,
                }, 
            ),
            eating_death=patients.with_these_codes_on_death_certificate(
                codelist=eating_disorders_icd_codes,
                between=["first_day_of_month(index_date)", "last_day_of_month(index_date)"],
                returning="binary_flag",
                return_expectations={
                    "incidence": 0.1,
                }, 
            ),
        ),





       ## HISTORY OF MENTAL HEALTH DISORDERS IN THE PREVIOUS FIVE YEARS
       prev_mental_dis=patients.satisfying(
            "depression5yr OR anxiety5yr OR ocd5yr OR severe_mental_illness5yr OR eating_disorder5yr OR self_harm5yr",

            ## DEPRESSION
            depression5yr=patients.with_these_clinical_events(
                codelist=depression_codes,    
                between=["index_date - 5 years", "index_date - 1 day"],
                returning="binary_flag",
                return_expectations={
                    "incidence": 0.1,
                }, 
            ),

            ## ANXIETY
            anxiety5yr=patients.with_these_clinical_events(
                codelist=anxiety_codes,    
                between=["index_date - 5 years", "index_date - 1 day"],
                returning="binary_flag",
                return_expectations={
                    "incidence": 0.1,
                }, 
            ), 

            ## OCD
            ocd5yr=patients.with_these_clinical_events(
                codelist=ocd_codes,
                between=["index_date - 5 years", "index_date - 1 day"],
                returning="binary_flag",
                return_expectations={
                    "incidence": 0.1,
                }, 
            ), 

            ## SEVERE MENTAL ILLNESS
            severe_mental_illness5yr=patients.satisfying(
                "smi_gp5yr OR smi_hosp5yr OR smi_emerg5yr",
        
                smi_gp5yr=patients.with_these_clinical_events(
                    codelist=severe_mental_illness_codes,
                    between=["index_date - 5 years", "index_date - 1 day"],
                    returning="binary_flag",
                    return_expectations={
                        "incidence": 0.1,
                    }, 
                ), 

                smi_hosp5yr=patients.admitted_to_hospital(
                    between=["index_date - 5 years", "index_date - 1 day"],
                    with_these_diagnoses=severe_mental_illness_icd_codes,
                    returning="binary_flag",
                    return_expectations={
                        "incidence": 0.1,
                    }, 
                ),
                
                smi_emerg5yr=patients.attended_emergency_care(
                    between=["index_date - 5 years", "index_date - 1 day"],
                    with_these_diagnoses=severe_mental_illness_icd_codes,
                    returning="binary_flag",
                    return_expectations={
                        "incidence": 0.1,
                    }, 
                ),
            ),

            ## SELF HARM
            self_harm5yr=patients.satisfying(
                "self_harm_gp5yr OR self_harm_hosp5yr OR self_harm_emerg5yr",

                self_harm_gp5yr=patients.with_these_clinical_events(
                    combine_codelists(
                        self_harm_10plus_codes,
                        self_harm_15plus_codes,
                    ),    
                    between=["index_date - 5 years", "index_date - 1 day"],
                    returning="binary_flag",
                    return_expectations={
                        "incidence": 0.1,
                    }, 
                ), 
                self_harm_hosp5yr=patients.admitted_to_hospital(
                    between=["index_date - 5 years", "index_date - 1 day"],
                    with_these_diagnoses=self_harm_icd_codes,
                    returning="binary_flag",
                    return_expectations={
                        "incidence": 0.1,
                    }, 
                ),
                
                self_harm_emerg5yr=patients.attended_emergency_care(
                    between=["index_date - 5 years", "index_date - 1 day"],
                    with_these_diagnoses=self_harm_icd_codes,
                    returning="binary_flag",
                    return_expectations={
                        "incidence": 0.1,
                    }, 
                ),

            ),

            ## EATING DISORDERS
            eating_disorder5yr=patients.satisfying(
                "eating_gp5yr OR eating_hosp5yr OR eating_emerg5yr",
                eating_gp5yr=patients.with_these_clinical_events(
                    codelist=eating_disorders_codes,
                    between=["index_date - 5 years", "index_date - 1 day"],
                    returning="binary_flag",
                    return_expectations={
                        "incidence": 0.1,
                    }, 
                ), 

                eating_hosp5yr=patients.admitted_to_hospital(
                    between=["index_date - 5 years", "index_date - 1 day"],
                    with_these_diagnoses=eating_disorders_icd_codes,
                    returning="binary_flag",
                    return_expectations={
                        "incidence": 0.1,
                    }, 
                ),
                
                eating_emerg5yr=patients.attended_emergency_care(
                    between=["index_date - 5 years", "index_date - 1 day"],
                    with_these_diagnoses=eating_disorders_icd_codes,
                    returning="binary_flag",
                    return_expectations={
                        "incidence": 0.1,
                    }, 
                ),
            ),
       ),




)

# MEASURES FOR TIME SERIES

measures = [

    # STRATIFIED BY LIVING ALONE
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

    Measure(
        id="ocd_rate",
        numerator="ocd",
        denominator="population",
        group_by=["living_alone"],
    ),

    Measure(
        id="severe_mental_rate",
        numerator="severe_mental",
        denominator="population",
        group_by=["living_alone"],
    ),

    Measure(
        id="eating_disorder_rate",
        numerator="eating_disorder",
        denominator="population",
        group_by=["living_alone"],
    ),

    Measure(
        id="self_harm_rate",
        numerator="self_harm",
        denominator="population",
        group_by=["living_alone"],
    ),




# STRATIFIED BY LIVING ALONE AND SEX
Measure(
        id="depression_sex",
        numerator="depression",
        denominator="population",
        group_by=["living_alone", "sex"],
    ),

Measure(
        id="anxiety_sex",
        numerator="anxiety",
        denominator="population",
        group_by=["living_alone", "sex"],
    ),

Measure(
        id="ocd_sex",
        numerator="ocd",
        denominator="population",
        group_by=["living_alone", "sex"],
    ),

Measure(
        id="severe_mental_sex",
        numerator="severe_mental",
        denominator="population",
        group_by=["living_alone", "sex"],
    ),

Measure(
        id="eating_disorder_sex",
        numerator="eating_disorder",
        denominator="population",
        group_by=["living_alone", "sex"],
    ),

Measure(
        id="self_harm_sex",
        numerator="self_harm",
        denominator="population",
        group_by=["living_alone", "sex"],
    ),

# STRATIFIED BY LIVING ALONE AND AGE
Measure(
        id="depression_ageband_broad",
        numerator="depression",
        denominator="population",
        group_by=["living_alone", "ageband_broad"],
    ),

Measure(
        id="anxiety_ageband_broad",
        numerator="anxiety",
        denominator="population",
        group_by=["living_alone", "ageband_broad"],
    ),

Measure(
        id="ocd_ageband_broad",
        numerator="ocd",
        denominator="population",
        group_by=["living_alone", "ageband_broad"],
    ),

Measure(
        id="severe_mental_ageband_broad",
        numerator="severe_mental",
        denominator="population",
        group_by=["living_alone", "ageband_broad"],
    ),

Measure(
        id="eating_disorder_ageband_broad",
        numerator="eating_disorder",
        denominator="population",
        group_by=["living_alone", "ageband_broad"],
    ),

Measure(
        id="self_harm_ageband_broad",
        numerator="self_harm",
        denominator="population",
        group_by=["living_alone", "ageband_broad"],
    ),

# STRATIFIED BY LIVING ALONE AND ETHNICITY
Measure(
        id="depression_ethnicity6",
        numerator="depression",
        denominator="population",
        group_by=["living_alone", "ethnicity6"],
    ),

Measure(
        id="anxiety_ethnicity6",
        numerator="anxiety",
        denominator="population",
        group_by=["living_alone", "ethnicity6"],
    ),

Measure(
        id="ocd_ethnicity6",
        numerator="ocd",
        denominator="population",
        group_by=["living_alone", "ethnicity6"],
    ),

Measure(
        id="severe_mental_ethnicity6",
        numerator="severe_mental",
        denominator="population",
        group_by=["living_alone", "ethnicity6"],
    ),

Measure(
        id="eating_disorder_ethnicity6",
        numerator="eating_disorder",
        denominator="population",
        group_by=["living_alone", "ethnicity6"],
    ),

Measure(
        id="self_harm_ethnicity6",
        numerator="self_harm",
        denominator="population",
        group_by=["living_alone", "ethnicity6"],
    ),

# STRATIFIED BY LIVING ALONE AND IMD
Measure(
        id="depression_imd",
        numerator="depression",
        denominator="population",
        group_by=["living_alone", "imd"],
    ),

Measure(
        id="anxiety_imd",
        numerator="anxiety",
        denominator="population",
        group_by=["living_alone", "imd"],
    ),

Measure(
        id="ocd_imd",
        numerator="ocd",
        denominator="population",
        group_by=["living_alone", "imd"],
    ),

Measure(
        id="severe_mental_imd",
        numerator="severe_mental",
        denominator="population",
        group_by=["living_alone", "imd"],
    ),

Measure(
        id="eating_disorder_imd",
        numerator="eating_disorder",
        denominator="population",
        group_by=["living_alone", "imd"],
    ),

Measure(
        id="self_harm_imd",
        numerator="self_harm",
        denominator="population",
        group_by=["living_alone", "imd"],
    ),

# STRATIFIED BY LIVING ALONE AND REGION (STP)
Measure(
        id="depression_stp",
        numerator="depression",
        denominator="population",
        group_by=["living_alone", "stp"],
    ),

Measure(
        id="anxiety_stp",
        numerator="anxiety",
        denominator="population",
        group_by=["living_alone", "stp"],
    ),

Measure(
        id="ocd_stp",
        numerator="ocd",
        denominator="population",
        group_by=["living_alone", "stp"],
    ),

Measure(
        id="severe_mental_stp",
        numerator="severe_mental",
        denominator="population",
        group_by=["living_alone", "stp"],
    ),

Measure(
        id="eating_disorder_stp",
        numerator="eating_disorder",
        denominator="population",
        group_by=["living_alone", "stp"],
    ),

Measure(
        id="self_harm_stp",
        numerator="self_harm",
        denominator="population",
        group_by=["living_alone", "stp"],
    ),

# STRATIFIED BY LIVING ALONE AND RURAL/URBAN 
Measure(
        id="depression_urban",
        numerator="depression",
        denominator="population",
        group_by=["living_alone", "urban"],
    ),

Measure(
        id="anxiety_urban",
        numerator="anxiety",
        denominator="population",
        group_by=["living_alone", "urban"],
    ),

Measure(
        id="ocd_urban",
        numerator="ocd",
        denominator="population",
        group_by=["living_alone", "urban"],
    ),

Measure(
        id="severe_mental_urban",
        numerator="severe_mental",
        denominator="population",
        group_by=["living_alone", "urban"],
    ),

Measure(
        id="eating_disorder_urban",
        numerator="eating_disorder",
        denominator="population",
        group_by=["living_alone", "urban"],
    ),

Measure(
        id="self_harm_urban",
        numerator="self_harm",
        denominator="population",
        group_by=["living_alone", "urban"],
    ),



# STRATIFIED BY LIVING ALONE AND shielded 
Measure(
        id="depression_shielded",
        numerator="depression",
        denominator="population",
        group_by=["living_alone", "shielded"],
    ),

Measure(
        id="anxiety_shielded",
        numerator="anxiety",
        denominator="population",
        group_by=["living_alone", "shielded"],
    ),

Measure(
        id="ocd_shielded",
        numerator="ocd",
        denominator="population",
        group_by=["living_alone", "shielded"],
    ),

Measure(
        id="severe_mental_shielded",
        numerator="severe_mental",
        denominator="population",
        group_by=["living_alone", "shielded"],
    ),

Measure(
        id="eating_disorder_shielded",
        numerator="eating_disorder",
        denominator="population",
        group_by=["living_alone", "shielded"],
    ),

Measure(
        id="self_harm_shielded",
        numerator="self_harm",
        denominator="population",
        group_by=["living_alone", "shielded"],
    ),

# STRATIFIED BY LIVING ALONE AND PREVIOUS MENTAL DISORDERS 
Measure(
        id="depression_prev_mental_dis",
        numerator="depression",
        denominator="population",
        group_by=["living_alone", "prev_mental_dis"],
    ),

Measure(
        id="anxiety_prev_mental_dis",
        numerator="anxiety",
        denominator="population",
        group_by=["living_alone", "prev_mental_dis"],
    ),

Measure(
        id="ocd_prev_mental_dis",
        numerator="ocd",
        denominator="population",
        group_by=["living_alone", "prev_mental_dis"],
    ),

Measure(
        id="severe_mental_prev_mental_dis",
        numerator="severe_mental",
        denominator="population",
        group_by=["living_alone", "prev_mental_dis"],
    ),

Measure(
        id="eating_disorder_prev_mental_dis",
        numerator="eating_disorder",
        denominator="population",
        group_by=["living_alone", "prev_mental_dis"],
    ),

Measure(
        id="self_harm_prev_mental_dis",
        numerator="self_harm",
        denominator="population",
        group_by=["living_alone", "prev_mental_dis"],
    ),



]
