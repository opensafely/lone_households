/* ===========================================================================
Do file name:   lines.do
Project:        COVID Lone HH MH Outcomes
Date:     		21/03/2022
Author:         Dominik Piehlmaier
Description:    Time-series line graphs
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
log using $outdir/lines.txt, replace text

foreach x in anxiety depression ocd self_harm severe_mental_illness {
	import delimited $outdir/measures/measure_`x'_rate.csv, clear	//get csv
	*Create binary variables for time series
	encode living_alone, gen(bin_living)
	*Format time
	gen temp_date=date(date, "YMD")
	format temp_date %td
	gen postcovid=(temp_date>=22006)
	gen month=mofd(temp_date)
	format month %tm
	*Value to rate per 100k
	gen rate = value*100000
	label variable rate "Rate of `x' per 100,000"
	*Set time series
	tsset bin_living temp_date
	*Ts line graphs by strata
	tsline rate, by(bin_living) xlabel(, angle(45) format(%dM-CY)) ///
	ytitle("Rate per 100,000") tline(22006) legend(off) xtitle("") ///
	ylabel(, format(%9.0fc))
	graph export $tabfigdir/lines_`x'.eps, as(eps) replace
}


log close
