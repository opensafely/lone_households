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
log using $outdir/modelcheck.txt, replace text

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
	drop temp_date
	*Value to rate per 100k
	gen rate = value*100000
	label variable rate "Rate of `x' per 100,000"
	*Set time series
	tsset bin_living month
	*Kernel density plots to check for normality and extreme values
	kdensity rate if bin_living==1, normal name(kl_`x')
	kdensity rate if bin_living==2, normal name(kj_`x')
	*Autoregression plots by HH living condition
	ac rate if bin_living==1, name(ac_lone_`x')
	ac rate if bin_living==2, name(ac_joint_`x')
	*Partial autoregression plots by HH living condition
	pac rate if bin_living==1, name(pac_lone_`x')
	pac rate if bin_living==2, name(pac_joint_`x')
	*Combine Graphs
	graph combine kl_`x' kj_`x' ac_lone_`x' ac_joint_`x' ///
	pac_lone_`x' pac_lone_`x', altshrink
	graph export $tabfigdir/checks_`x'.eps, as(eps) replace
	
}


log close
