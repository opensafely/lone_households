from cohortextractor import (
    codelist_from_csv,
    combine_codelists,
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
    "codelists/user-emilyherrett-depression_icd10.csv",
    system="icd10",
    column="code",
)

# severe mental illness
severe_mental_illness_codes = codelist_from_csv(
    "codelists/opensafely-psychosis-schizophrenia-bipolar-affective-disease.csv",
    system="ctv3",
    column="CTV3Code",
)

severe_mental_illness_icd_codes = codelist_from_csv(
    "codelists/user-emilyherrett-severe_mental_illness_icd10.csv",
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
    "codelists/user-emilyherrett-anxiety_icd10.csv",
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
    "codelists/user-emilyherrett-ocd_icd10.csv",
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
    "codelists/user-emilyherrett-eating_disorder_icd10.csv",
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
    "codelists/user-emilyherrett-self_harm_icd10.csv",
    system="icd10",
    column="code",
)

# Suicide
suicide_codes = codelist_from_csv(
    "codelists/user-hjforbes-suicide-icd-10.csv",
    system="icd10",
    column="code",
)

# SSRIs
ssri_codes = codelist_from_csv(
    "codelists/opensafely-selective-serotonin-reuptake-inhibitors-dmd.csv",
    system="snomed",
    column="dmd_id",
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
    ['1300561000000107'], 
    system="snomed",
    )

not_high_risk_codes = codelist(
    ['1300591000000101', '1300571000000100'], 
    system="snomed",
    )




