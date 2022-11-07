/*==============================================================================
DO FILE NAME:			self_harm_graph.do
PROJECT:				Lone households 
DATE: 					04 November 2022 
AUTHOR:					E Herrett	
DESCRIPTION OF FILE:	Produces a graph of self harm mortality, which is sufficiently redacted
DATASETS USED:			output/tabfig/selfharm_mortgraph
DATASETS CREATED: 		None
OTHER OUTPUT: 			Log file: logs/selfharm_mortgraph
USER-INSTALLED ADO: 	 
  (place .ado file(s) in analysis folder)	
   ==============================================================================*/
*global outdir "\\tsclient\lsh148121\Documents\GitHub\opensafely_lone_households\lone_households\output\"


*set filepaths
global projectdir `c(pwd)'
dis "$projectdir"
global outdir $projectdir/output
dis "$outdir"
global tabfigdir $projectdir/output/tabfig
dis "$tabfigdir"

* Create directories required 
capture mkdir "$tabfigdir"

capture log close
log using ./logs/selfharm_mortgraph.log, replace
*show low counts are non zero, by rounding up to the nearest 6 and then take the mid-point, i.e. counts <=6 get set to 3.


import delimited ./output/measures/measure_self_harmDeath_rate.csv, clear
	*Create binary variables for time series
	encode living_alone, gen(bin_living)
	*Format time
	gen temp_date=date(date, "YMD")
	format temp_date %td
	gen year=year(temp_date)
	gen month=month(temp_date)
	drop if year==2018
	drop if year==2019 & month<3
	drop year month
	
	gen postcovid=(temp_date>=date("23/03/2020", "DMY"))
	gen month=mofd(temp_date)
	format month %tm
	
	*round values to the mid-point of bands of 7
	/*
		# 0 is mapped to 0,
		# 1, 2, 3, 4, 5, 6, 7 is mapped to 4
		# 8, 9, 10, 11, 12, 13, 14 is mapped to 11
		# 15, 16, 17, 18, 19, 20, 21 is mapped to 18 
		# etc.
	*/
			gen div7=self_harm_death/7
			gen div7rounded=ceil(div7)
			gen new_selfharmdeath=(div7rounded*7)-3
	
	*Create a variable showing the rounded number of events to rate per 100k
	gen rounded7_rate=(new_selfharmdeath/population)*100000
	label variable rounded7_rate "Rate of self harm mortality per 100,000"

	*Set time series
	tsset bin_living temp_date
	*Ts line graphs by HH status
	tsline rounded7_rate, by(bin_living) xlabel(, angle(45) format(%dM-CY)) ///
	ytitle("Rate per 100,000") tline(22006) legend(off) xtitle("") ///
	tline(01jan2021 01may2021 01jan2022, lpattern(shortdash) lcolor(green)) ///
	ylabel(, format(%9.0fc))
	graph export $tabfigdir/line_selfharmmort.svg, as(svg) replace



* Close log file 
log close