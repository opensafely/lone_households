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
cap log using $outdir/lines.txt, replace text

*Create macros
local outcome anxiety depression eating_disorder ocd self_harm severe_mental
local strata sex ageband_broad ethnicity6 imd region urban shielded prev_mental_dis

foreach x in `outcome' {
	import delimited $outdir/measures/measure_`x'_rate.csv, clear	//get csv
	*Create binary variables for time series
	encode living_alone, gen(bin_living)
	*Format time
	gen temp_date=date(date, "YMD")
	format temp_date %td
	gen postcovid=(temp_date>=date("23/03/2020", "DMY"))
	gen month=mofd(temp_date)
	format month %tm
	*Value to rate per 100k
	gen rate = value*100000
	label variable rate "Rate of `x' per 100,000"
	*Set time series
	tsset bin_living temp_date
	*Ts line graphs by HH status
	tsline rate, by(bin_living) xlabel(, angle(45) format(%dM-CY)) ///
	ytitle("Rate per 100,000") tline(22006) legend(off) xtitle("") ///
	tline(01jan2021 01may2021 01jan2022, lpattern(shortdash) lcolor(green)) ///
	ylabel(, format(%9.0fc))
	graph export $tabfigdir/lines_`x'.svg, as(svg) replace
	******Stratified Time-series models*******
	foreach y in `strata' {
			import delimited $outdir/measures/measure_`x'_`y'.csv, clear	//get csv
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
			*Value to rate per 100k
			gen rate = value*100000
			*Run time series with EWH-robust SE and 1 Lag
			tsset hh_`y' temp_date
			*Ts line graphs by Strata and HH status
			tsline rate, by(hh_`y') xlabel(, angle(45) format(%dM-CY)) ///
			ytitle("Rate per 100,000") tline(22006) legend(off) xtitle("") ///
			tline(01jan2021 01may2021 01jan2022, lpattern(shortdash) lcolor(green)) ///
			ylabel(, format(%9.0fc))
			graph export $tabfigdir/lines_`x'_`y'.svg, as(svg) replace

	}
}


log close
