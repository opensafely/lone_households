/* ===========================================================================
Do file name:   sensitivity_updated_alltpp_big_households.do
Project:        COVID Lone HH MH Outcomes
Date:     		25/07/2022, updated 27/02/23
Author:         Dominik Piehlmaier
Description:    Sensitivity analysis as per protocol
==============================================================================*/


*set filepaths
global projectdir `c(pwd)'
*global projectdir "\\tsclient\lsh148121\Documents\GitHub\opensafely_lone_households\lone_households"
dis "$projectdir"
global outdir $projectdir/output
dis "$outdir"
global tabfigdir $projectdir/output/tabfig
dis "$tabfigdir"

* Create directories required 
capture mkdir "$tabfigdir"

*Log file
cap log close
cap log using $outdir/sensitivity_updated.txt, replace text

*Create macros
local outcome anxiety depression eating_disorder ocd self_harm_prev severe_mental
*local alt_out self_harm eating 		//omit smi due to lack of death
*local care PC EC SC Death
*local smicare PC EC SC
*local strata big all_tpp


*AMENDED CODE FOR Time-series models for big household
foreach x in `outcome' {
			import delimited "$outdir/measures/measure_`x'_big.csv", clear		//get csv
			drop if big_household=="big household"
			putexcel set $tabfigdir/sens2_tables, sheet(`x'_big_household) modify			//open xlsx
			*Create binary variables for time series
			encode living_alone, gen(bin_living)
			*Format time
			gen temp_date=date(date, "YMD")
			format temp_date %td
			gen postcovid=(temp_date>=date("23/03/2020", "DMY"))
			gen month=mofd(temp_date)
			format month %tm
			*Define Seasons
			gen season=4
			replace season = 1 if inrange(month(temp_date),3,5)
			replace season = 2 if inrange(month(temp_date),6,8)
			replace season = 3 if inrange(month(temp_date),9,11)
			label define seasonlab 1 "Spring" 2 "Summer" 3 "Autumn" 4 "Winter"
			label values season seasonlab
			drop temp_date
			*Value to rate per 100k
			gen rate = value*100000
			label variable rate "Rate of `x' per 100,000"
			*Run time series with EWH-robust SE and 1 Lag
			tsset bin_living month
			newey rate i.bin_living##i.postcovid i.season, lag(1) force
			*Export results
			putexcel E1=("Number of obs") G1=(e(N))
			putexcel E2=("F") G2=(e(F))
			putexcel E3=("Prob > F") G3=(Ftail(e(df_m), e(df_r), e(F)))
			matrix a = r(table)'
			putexcel A6 = matrix(a), rownames
			putexcel save
			quietly margins postcovid#bin_living
			marginsplot
			graph export $tabfigdir/margin2_`x'_big_household.svg, as(svg) replace

			import excel using $tabfigdir/sens2_tables.xlsx, sheet(`x'_big_household) clear
			export delimited using $tabfigdir/sens2_tables_`x'_big_household.csv, replace	
			graph export $tabfigdir/sens2_mar_`x'_big_household.svg, as(svg) replace	
	}
	

*AMENDED CODE FOR Time-series models for full TPP coverage
foreach x in `outcome' {
			import delimited $outdir/measures/measure_`x'_all_tpp.csv, clear		//get csv
			drop if all_tpp=="not all TPP"
			putexcel set $tabfigdir/sens2_tables, sheet(`x'_all_tpp) modify			//open xlsx
			*Create binary variables for time series
			encode living_alone, gen(bin_living)
			*Format time
			gen temp_date=date(date, "YMD")
			format temp_date %td
			gen postcovid=(temp_date>=date("23/03/2020", "DMY"))
			gen month=mofd(temp_date)
			format month %tm
			*Define Seasons
			gen season=4
			replace season = 1 if inrange(month(temp_date),3,5)
			replace season = 2 if inrange(month(temp_date),6,8)
			replace season = 3 if inrange(month(temp_date),9,11)
			label define seasonlab 1 "Spring" 2 "Summer" 3 "Autumn" 4 "Winter"
			label values season seasonlab
			drop temp_date
			*Value to rate per 100k
			gen rate = value*100000
			label variable rate "Rate of `x' per 100,000"
			*Run time series with EWH-robust SE and 1 Lag
			tsset bin_living month
			newey rate i.bin_living##i.postcovid i.season, lag(1) force
			*Export results
			putexcel E1=("Number of obs") G1=(e(N))
			putexcel E2=("F") G2=(e(F))
			putexcel E3=("Prob > F") G3=(Ftail(e(df_m), e(df_r), e(F)))
			matrix a = r(table)'
			putexcel A6 = matrix(a), rownames
			putexcel save
			quietly margins postcovid#bin_living
			marginsplot
			graph export $tabfigdir/margin2_`x'_all_tpp.svg, as(svg) replace

			import excel using $tabfigdir/sens2_tables.xlsx, sheet(`x'_all_tpp) clear
			export delimited using $tabfigdir/sens2_tables_`x'_all_tpp.csv, replace	
			graph export $tabfigdir/sens2_mar_`x'_all_tpp.svg, as(svg) replace	
	}
	

log close
