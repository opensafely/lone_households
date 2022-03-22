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
log using $outdir/tsreg.txt, replace text

foreach x in anxiety depression ocd self_harm severe_mental_illness {
	import delimited $outdir/measures/measure_`x'_rate.csv, clear	//get csv
	putexcel set $tabfigdir/tsreg_tables, sheet(`x') modify			//open xlsx
	*Create binary variables for time series
	encode living_alone, gen(bin_living)
	*Format time
	gen temp_date=date(date, "YMD")
	format temp_date %td
	gen postcovid=(temp_date>=22006)
	gen month=mofd(temp_date)
	format month %tm
	drop temp_date
	*Value to rate per 100k
	gen rate = value*100000
	*Run time series with EWH-robust SE and 1 Lag
	tsset bin_living month
	newey rate i.bin_living##i.postcovid, lag(1) force
	*Export results
	putexcel E1=("Number of obs") G1=(e(N))
	putexcel E2=("F") G2=(e(F))
	putexcel E3=("Prob > F") G3=(Ftail(e(df_m), e(df_r), e(F)))
	matrix a = r(table)'
	putexcel A6 = matrix(a), rownames
	putexcel save

}


log close