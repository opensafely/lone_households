/* ===========================================================================
Do file name:   sensitivity.do
Project:        COVID Lone HH MH Outcomes
Date:     		25/07/2022
Author:         Dominik Piehlmaier
Description:    Sensitivity analysis as per protocol
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
cap log using $outdir/sensitivity.txt, replace text

*Create macros
local outcome anxiety depression eating_disorder ocd self_harm severe_mental
local alt_out self_harm eating 		//omit smi due to lack of death
local care PC EC SC Death
local smicare PC EC SC
local strata big all_tpp

*Time-series models by record type
foreach x in `alt_out' {
	foreach y in `care' {
			import delimited $outdir/measures/measure_`x'`y'_rate.csv, clear 	//get csv
			putexcel set $tabfigdir/sens_tables, sheet(`x'`y') modify			//open xlsx
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
			*Value to rate per 100k
			gen rate = value*100000
			label variable rate "Rate of `x' per 100,000"
			*Set time series for line graphs
			tsset bin_living temp_date
			*Ts line graphs by HH status
			tsline rate, by(bin_living) xlabel(, angle(45) format(%dM-CY)) ///
			ytitle("Rate per 100,000") tline(22006) legend(off) xtitle("") ///
			tline(01jan2021 01may2021 01jan2022, lpattern(shortdash) lcolor(green)) ///
			ylabel(, format(%9.0fc))
			graph export $tabfigdir/senslin_`x'`y'.svg, as(svg) replace
			*Reset and run time series with EWH-robust SE and 1 Lag
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
			graph export $tabfigdir/sens_mar_`x'`y'.svg, as(svg) replace
			import excel using $tabfigdir/sens_tables.xlsx, sheet(`x'`y') clear
			export delimited using $tabfigdir/sens_tables_`x'`y'.csv, replace		

	}
		
	
}

foreach y in `smicare' {
	import delimited $outdir/measures/measure_smi`y'_rate.csv, clear 	//get csv
	putexcel set $tabfigdir/sens_tables, sheet(smi`y') modify			//open xlsx
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
	*Value to rate per 100k
	gen rate = value*100000
	label variable rate "Rate of `x' per 100,000"
	*Set time series for line graphs
	tsset bin_living temp_date
	*Ts line graphs by HH status
	tsline rate, by(bin_living) xlabel(, angle(45) format(%dM-CY)) ///
	ytitle("Rate per 100,000") tline(22006) legend(off) xtitle("") ///
	tline(01jan2021 01may2021 01jan2022, lpattern(shortdash) lcolor(green)) ///
	ylabel(, format(%9.0fc))
	graph export $tabfigdir/senslin_smi`y'.svg, as(svg) replace
	*Reset and run time series with EWH-robust SE and 1 Lag
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
	graph export $tabfigdir/sens_mar_smi`y'.svg, as(svg) replace
	import excel using $tabfigdir/sens_tables.xlsx, sheet(smi`y') clear
	export delimited using $tabfigdir/sens_tables_smi`y'.csv, replace		

}

*Time-series models for big household and full TPP coverage
foreach x in `outcome' {
	foreach y in `strata' {
			import delimited $outdir/measures/measure_`x'_`y'.csv, clear		//get csv
			putexcel set $tabfigdir/sens_tables, sheet(`x'`y') modify			//open xlsx
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
			*Value to rate per 100k
			gen rate = value*100000
			label variable rate "Rate of `x' per 100,000"
			*Define Strata
			tostring `y', replace
			gen temp_var = cond(living_alone < `y', living_alone + `y', `y' + living_alone)
			encode temp_var, gen(hh_`y')
			*Set time series for line graphs
			tsset hh_`y' temp_date
			*Ts line graphs by HH status
			tsline rate, by(hh_`y') xlabel(, angle(45) format(%dM-CY)) ///
			ytitle("Rate per 100,000") tline(22006) legend(off) xtitle("") ///
			tline(01jan2021 01may2021 01jan2022, lpattern(shortdash) lcolor(green)) ///
			ylabel(, format(%9.0fc))
			graph export $tabfigdir/senslin_`x'_`y'.svg, as(svg) replace
			*Reset and run time series with EWH-robust SE and 1 Lag
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
			graph export $tabfigdir/sens_mar_`x'_`y'.svg, as(svg) replace
			import excel using $tabfigdir/sens_tables.xlsx, sheet(`x'`y') clear
			export delimited using $tabfigdir/sens_tables_`x'`y'.csv, replace	
	
	}
	
}

*Time series model for SSRI
import delimited $outdir/measures/measure_ssri_rate.csv, clear 		//get csv
putexcel set $tabfigdir/sens_tables, sheet(ssri) modify			//open xlsx
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
*Value to rate per 100k
gen rate = value*100000
label variable rate "Rate of `x' per 100,000"
*Set time series for line graphs
tsset bin_living temp_date
*Ts line graphs by HH status
tsline rate, by(bin_living) xlabel(, angle(45) format(%dM-CY)) ///
ytitle("Rate per 100,000") tline(22006) legend(off) xtitle("") ///
tline(01jan2021 01may2021 01jan2022, lpattern(shortdash) lcolor(green)) ///
ylabel(, format(%9.0fc))
graph export $tabfigdir/senslin_ssri.svg, as(svg) replace
*Reset and run time series with EWH-robust SE and 1 Lag
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
graph export $tabfigdir/sens_mar_ssri.svg, as(svg) replace
import excel using $tabfigdir/sens_tables.xlsx, sheet(ssri) clear
export delimited using $tabfigdir/sens_tables_ssri.csv, replace	

log close
