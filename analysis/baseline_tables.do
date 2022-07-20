/*==============================================================================
DO FILE NAME:			baseline_tables.do
PROJECT:				Lone households 
DATE: 					14 July 2022 
AUTHOR:					E Herrett
						adapted from R Costello, R Mathur and K Wing	
DESCRIPTION OF FILE:	Produce a table of baseline characteristics for 3 years (2019, 2020, 2021)
DATASETS USED:			output/measures/input*
DATASETS CREATED: 		None
OTHER OUTPUT: 			Results in excel: baseline_table*.xlsx
						Log file: logs/table1_descriptives
USER-INSTALLED ADO: 	 
  (place .ado file(s) in analysis folder)	
  
 Notes:
 Table 1 population is people who are in the study population on 1st January 2019, 2020 & 2021
 ==============================================================================*/

*local dataset `1'
adopath + ./analysis/ado 

capture log close
log using ./logs/table1_descriptives.log, replace

cap mkdir ./output/tables

* Create  baseline tables for 3 years
forvalues i=2019/2021 {
  * Import csv file
    import delimited ./output/measures/tables/input_tables_`i'-01-01.csv, clear
    *update variable with missing so that 0 is shown as unknown (just for this table)
    *(1) ethnicity
    replace ethnicity=6 if ethnicity==0
    label define eth5 			1 "White"  					///
                                2 "Mixed"				///						
                                3 "Asian"  					///
                                4 "Black"					///
                                5 "Other"					///
                                6 "Unknown"
                        

    label values ethnicity eth5
    safetab ethnicity, m

    *(2) IMD
    replace imd=6 if imd==0

    * Create age categories
    sum age
    egen age_cat = cut(age), at(18, 40, 60, 80, 120) icodes
    label define age 0 "18 - 40 years" 1 "41 - 60 years" 2 "61 - 80 years" 3 ">80 years"
    label values age_cat age
    bys age_cat: sum age

    * Create categories of household size
    sum household_size
    egen household_cat = cut(household_size), at(0, 1, 16, 100) icodes
    label define house 0 "missing" 1 "1-15 people" 2 "over 15 people"
    bys household_cat: sum household_size

    preserve
    * Create baseline table
    table1_mc, vars(age_cat cate \ sex cate \ died cate \ living_alone cate \ ethnicity6 cate \ imd cate \ region cate \ urban cate \ household_cat cate \ big_household cate \  ///
    all_tpp cate \ shielded cate \ care_home_type cate \  ///
    depression cate \ anxiety cate \ ocd cate \ severe_mental cate \ smi_gp cate \ smi_hosp cate \ smi_emerg cate \  ///
    self_harm cate \ self_harm_gp cate \ self_harm_hosp cate \  self_harm_emerg cate \ self_harm_death cate \ ///
    eating_disorder cate \ eating_gp cate \ eating_hosp cate \ eating_emerg cate \ prev_mental_dis cate ) clear
    export delimited using ./output/tables/baseline_table_`i'.csv
    restore

    drop if ethnicity==6
    gen white = (ethnicity==1)
    gen mixed = (ethnicity==2)
    gen asian = (ethnicity==3)
    gen black = (ethnicity==4)
    gen other = (ethnicity==5)

    tempfile tempfile
    preserve
    keep if living_alone=="living alone"
    table1_mc, vars(age_cat cate \ sex cate \ died cate \ living_alone cate \ ethnicity6 cate \ imd cate \ region cate \ urban cate \ household_cat cate \ big_household cate \  ///
    all_tpp cate \ shielded cate \ care_home_type cate \  ///
    depression cate \ anxiety cate \ ocd cate \ severe_mental cate \ smi_gp cate \ smi_hosp cate \ smi_emerg cate \  ///
    self_harm cate \ self_harm_gp cate \ self_harm_hosp cate \  self_harm_emerg cate \ self_harm_death cate \ ///
    eating_disorder cate \ eating_gp cate \ eating_hosp cate \ eating_emerg cate \ prev_mental_dis cate ) clear
    save `tempfile', replace
    restore
     
    preserve
    keep if living_alone=="not living alone"
    table1_mc, vars(age_cat cate \ sex cate \ died cate \ living_alone cate \ ethnicity6 cate \ imd cate \ region cate \ urban cate \ household_cat cate \ big_household cate \  ///
    all_tpp cate \ shielded cate \ care_home_type cate \  ///
    depression cate \ anxiety cate \ ocd cate \ severe_mental cate \ smi_gp cate \ smi_hosp cate \ smi_emerg cate \  ///
    self_harm cate \ self_harm_gp cate \ self_harm_hosp cate \  self_harm_emerg cate \ self_harm_death cate \ ///
    eating_disorder cate \ eating_gp cate \ eating_hosp cate \ eating_emerg cate \ prev_mental_dis cate ) clear
    append using `tempfile'
    save `tempfile', replace
    restore
      
    
    use `tempfile', clear
    export delimited using ./output/tables/baseline_table_strata`i'.csv
}

* Close log file 
log close