from cohortextractor import (
    codelist_from_csv,
    codelist,
)


# OUTCOME CODELISTS - ICD and SNOMED/CTV3
# depression
depression_codes = codelist_from_csv(
    "codelists/opensafely-depression.csv", 
    system="ctv3", 
    column="CTV3Code",
)

depression_icd_codes = codelist_from_csv(
    "user-emilyherrett-depression_icd10.csv"
    system="icd10",
    column="code",
)

# severe mental illness
severe_mental_illness_codes = codelist_from_csv(
    "codelists/user-hjforbes-severe-mental-illness.csv",
    system="snomed",
    column="code",
)

severe_mental_illness_icd_codes = codelist_from_csv(
    "user-emilyherrett-severe_mental_illness_icd10.csv"
    system="icd10",
    column="code",
)

# Anxiety - general
anxiety_codes = codelist_from_csv(
    "codelists/user-hjforbes-anxiety-symptoms-and-diagnoses.csv",
    system="snomed",
    column="code",
)

anxiety_icd_codes = codelist_from_csv(
    "user-emilyherrett-anxiety_icd10.csv"
    system="icd10",
    column="code",
)

# Anxiety - obsessive compulsive disorder
ocd_codes = codelist_from_csv(
    "codelists/user-hjforbes-obsessive-compulsive-disorder-ocd.csv",
    system="snomed",
    column="code",
)

ocd_icd_codes = codelist_from_csv(
    "user-emilyherrett-ocd_icd10.csv"
    system="icd10",
    column="code",
)

# Eating disorders
eating_disorders_codes = codelist_from_csv(
    "codelists/user-hjforbes-diagnoses-eating-disorder.csv",
    system="snomed",
    column="code",
)

eating_disorders_icd_codes = codelist_from_csv(
    "user-emilyherrett-eating_disorder_icd10.csv"
    system="icd10",
    column="code",
)

# Self harm - aged >= 10 years
self_harm_10plus_codes = codelist_from_csv(
    "codelists/user-hjforbes-intentional-self-harm-aged10-years.csv",
    system="snomed",
    column="code",
)

# Self harm - aged >= 15 years
self_harm_15plus_codes = codelist_from_csv(
    "codelists/user-hjforbes-undetermined-intent-self-harm-aged15-years.csv",
    system="snomed",
    column="code",
)

# Self harm - ICD10
self_harm_icd_codes = codelist_from_csv(
    "user-emilyherrett-self_harm_icd10.csv"
    system="icd10",
    column="code",
)

# Suicide
suicide_codes = codelist_from_csv(
    "codelists/user-hjforbes-suicide-icd-10.csv",
    system="snomed",
    column="code",
)


# DEMOGRAPHIC CODELISTS
ethnicity_codes_6 = codelist_from_csv(
    "codelists/opensafely-ethnicity.csv",
    system="ctv3",
    column="Code",
    category_column="Grouping_6",
)

# High risk and not high risk codes, to define clinical vulnerability to complications from COVID-19 infection/shielding
high_risk_codes = codelist(
    ['1300561000000107'], system="snomed")

not_high_risk_codes = codelist(
    ['1300591000000101', '1300571000000100'], system="snomed")


# HISTORY OF MENTAL ILLNESS - COMBINING CODELSTS
mental_illness_history_codes = combine_codelists(
    # Depression
    depression_codes, depression_icd_codes,
    # Schizophrenia, Bipolar effective disorder, Psychoses
    severe_mental_illness_codes, severe_mental_illness_icd_codes,
    # Anxiety 
    anxiety_codes, anxiety_icd_codes,
    # Eating disorder codes
    eating_disorders_codes, eating_disorders_icd_codes,
    # OCD codes
    ocd_codes, ocd_icd_codes,
    # Self harm and suicide codes
    self_harm_10plus_codes, self_harm_15plus_codes, self_harm_icd_codes, suicide_codes,
)




