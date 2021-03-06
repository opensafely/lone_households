/* ===========================================================================
Do file name:   timeseries.do
Project:        COVID Lone HH MH Outcomes
Date:     		09/03/2022
Author:         Dominik Piehlmaier
Description:    Run time series after model checks
==============================================================================*/


*set filepaths
global projectdir `c(pwd)'
dis "$projectdir"
global outdir $projectdir/output
dis "$outdir"
global tabfigdir $projectdir/output/tabfig
dis "$tabfigdir"

* Create directories required 
capture mkdir "$tabfigdir"

*Log file
cap log close
cap log using $outdir/tsreg.txt, replace text

*Create macros
local outcome anxiety depression eating_disorder ocd self_harm severe_mental
local strata sex ageband_broad ethnicity6 imd region urban shielded prev_mental_dis

*General Time-series models
foreach x in `outcome' {
	import delimited $outdir/measures/measure_`x'_rate.csv, clear	//get csv
	putexcel set $tabfigdir/tsreg_tables, sheet(`x') modify			//open xlsx
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
	graph export $tabfigdir/margin_`x'.svg, as(svg) replace
	******Stratified Time-series models*******
	foreach y in `strata' {
			import delimited $outdir/measures/measure_`x'_`y'.csv, clear	//get csv
			putexcel set $tabfigdir/tsreg_tables, sheet(`x'_`y') modify		//open xlsx
			*Create cross product for time series
			tostring `y', replace
			gen temp_var = cond(living_alone < `y', living_alone + `y', `y' + living_alone)
			encode temp_var, gen(hh_`y')
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
			drop temp_date temp_var
			*Value to rate per 100k
			gen rate = value*100000
			*Run time series with EWH-robust SE and 1 Lag
			tsset hh_`y' month
			newey rate i.hh_`y'##i.postcovid i.season, lag(1) force
			*Export results
			putexcel E1=("Number of obs") G1=(e(N))
			putexcel E2=("F") G2=(e(F))
			putexcel E3=("Prob > F") G3=(Ftail(e(df_m), e(df_r), e(F)))
			matrix a = r(table)'
			putexcel A6 = matrix(a), rownames
			putexcel save
			quietly margins postcovid#hh_`y'
			marginsplot
			graph export $tabfigdir/margin_`x'_`y'.svg, as(svg) replace
			import excel using $tabfigdir/tsreg_tables.xlsx, sheet(`x'_`y') clear
			export delimited using $tabfigdir/tsreg_tables_`x'_`y'.csv, replace
	}

	import excel using $tabfigdir/tsreg_tables.xlsx, sheet(`x') clear
	export delimited using $tabfigdir/tsreg_tables_`x'.csv, replace	
	
}

log close
