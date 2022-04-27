/* ===========================================================================
Do file name:   modelcheck.do
Project:        COVID Lone HH MH Outcomes
Date:     		21/03/2022
Author:         Dominik Piehlmaier
Description:    Model check for fit and specification
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
cap log using $outdir/modelcheck.txt, replace text

*Create macros
local outcome anxiety depression eating_disorder ocd self_harm severe_mental
local strata sex ageband_broad ethnicity6 imd stp urban shielded prev_mental_dis

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
	drop temp_date
	*Value to rate per 100k
	gen rate = value*100000
	label variable rate "Rate of `x' per 100,000"
	*Set time series
	tsset bin_living month
	*Kernel density plots to check for normality and extreme values
	kdensity rate if bin_living==1, normal name(kl_`x', replace)
	kdensity rate if bin_living==2, normal name(kj_`x', replace)
	*Autoregression plots by HH living condition
	ac rate if bin_living==1, name(ac_lone_`x', replace)
	ac rate if bin_living==2, name(ac_joint_`x', replace)
	*Partial autoregression plots by HH living condition
	pac rate if bin_living==1, name(pac_lone_`x', replace)
	pac rate if bin_living==2, name(pac_joint_`x', replace)
	*Combine Graphs
	graph combine kl_`x' kj_`x' ac_lone_`x' ac_joint_`x' ///
	pac_lone_`x' pac_lone_`x', altshrink
	graph export $tabfigdir/checks_`x'.svg, as(svg) replace
	
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
			drop temp_date
			*Value to rate per 100k
			gen rate = value*100000
			label variable rate "Rate of `x' per 100,000"
			*Set time series
			tsset hh_`y' month
			*Prepare for density and autoregression plots
			quietly sum hh_`y', meanonly
			foreach i of num 1/`r(max)' {
					*Kernel density plots to check for normality and extreme values
					kdensity rate if hh_`y'==`i', name(k_`i'`y', replace)
					*Autoregression plots by HH living condition
					ac rate if hh_`y'==`i', name(ac_`i'`y', replace)
					*Partial autoregression plots by HH living condition
					pac rate if hh_`y'==`i', name(pac_`i'`y', replace)
					*Combine Graphs
					graph combine k_`i'`y' ac_`i'`y' pac_`i'`y', altshrink
					graph export $tabfigdir/checks_`x'_`i'`y'.svg, as(svg) replace

			}
			
	}
	
}


log close
