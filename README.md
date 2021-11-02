# edan
---

An economic data analysis toolkit, with an emphasis on NIPA accounts & other datasets with economic aggregates; as well as financial data, specifically interest rates.


## tables
---
The interface for `edan` is centered around the Table objects, each of which corresponds to a table published by the government organizations who collect the data (typically the most disaggregated version of the table available). At the moment, the only tables at the moment are:
* Gross Domestic Product (BEA)
* Personal Consumption Expenditures (BEA)
* Consumer Price Indices (BLS)
* Current Employment Survey (BLS)

Future plans concerning the tables:
1. Consolidate the GDP and PCE tables into one comprehensive GDP table, in addition to adding the detailed decompositions of net exports and government expenditures.
2. Add a filtering method for tables, so that large tables like those described above in bullet 1 can be partitioned according to super-components or concept. I'm imagining something like:
```python
import edan

gdp_table = edan.nipa.GDPTable
pce_table = gdp_table.filter(base_code='gdp:pce')
```
3. Flesh out the short names and levels of the Current Population Survey so that the CPS table can be added.

## edan codes
In the code block above, the string `'gdp:pce'` is used to identify the PCE subcomponent of GDP. In general, each aggregate in any of the tables listed above is identified by a string of that form, i.e. `'a:b:...:x:y:z'`. The delimiter `':'` is used to reference a subcomponent of its aggregate. For instance,
```python
import edan

pce_table = edan.nipa.PCETable
pce = pce_table['pce'] # references headline PCE
goods = pce['g'] # refences consumption goods; equivalent to pce_table['pce:g']
veh = pce_table['pce:g:d:v'] # vehicle consumption; equivalent to pce['g:d:v'] and goods['d:v']
```
This method of accessing subcomponents applies to all `edan` tables, aggregates, and subcomponents. There are two exceptions:
1. So-called "balance" components. I use this term to describe aggregates whose nominal level is computed as the difference of the nominal level of its subcomponents - possibly the most notable balance component is Net Exports. The subcomponents of a balance aggregate are identified by `'+'` and `'-'` delimiters, according to whether or not they are added or subtracted to arrive at the aggregate nominal level.
```python
import edan

nx = edan.nipa.GDPTable['gdp:x']
exports = edan.nipa.GDPTable['gdp:x+x']
imports = edan.nipa.GDPTable['gdp:x-m']
```
2. In the future when the detailed GDP table is finalized, some aggregates (for instance, government) have subcomponents data as well as partitioned data. Continuing the government example, it is decomposed by the BEA into federal defense, federal nondefense, and state & local subcomponents, as well as into consumption and investment partitions. The subcomponent data is accessed in the usual way described above, and the partitioned data via a `'#'` delimiter: `'gdp:gov#c'` references government consumption, for instance. This same partitioning idea will be applied to demographic differences when the CPS table is finalized as well.

## data
The `edan` package is meant to be more than just a programmatic representation of BEA and BLS tables -- the library employs the data in those very same tables. For (nearly) each component in the GDP and PCE tables, there are *nominal* and *real* levels, and *quantity* and *price* indices, which I collectively refer to as *measures*, and in the code are typically denoted by the `mtype` label. Each measure has an associated `Series` object and is stored in an attribute of the component of the measure name:
```python
import edan

pce = edan.nipa.PCETable['pce']

real = pce.real # edan Series object
rdf = pce.real.data # pandas Series of data

pce.nominal # edan Series for nominal data
pce.price # edan Series corresponding to price and quantity data
pce.quantity
```

### data transformations
Many common transformations of economic time-series are built-in:
```python
import edan

cpi = edan.cpi.CPITable['cpi']
yryrp = edan.transform(cpi, method='yryr%') # year-over-year inflation rate
momop = edan.transform(cpi, n=2, method='diff%') #2-month inflation rate

# re-index the nominal PCE level to the 2009 average
pce2009 = edan.transform( 
    edan.nipa.PCETable['pce'],
    method='index',
    base=2009,
    mtype='nominal'
)
```
With the exception of the re-indexing method, all transformations accept `n` and `h` parameters, whose interpretations differ slightly from method to method. A complete list of the recognized data transformations follows:
|code    | description                                | formula                           |
|:--     | :--                                        | --:                               |
|`diff`  | period-to-period change                    | `x(t) - x(t-n)`                   |
|`diff%` | period-to-period percent change            | `100*[ x(t)/x(t-n) - 1 ]`         |
|`diffl` | period-to-period log change                | `100*ln[ x(t)/x(t-n) ]`           |
|`difa`  | period-to-period annualized change         | `(h/n) * [ x(t)-x(t-n) ] `        |
|`difa%` | period-to-period annualized percent change | `100*[ (x(t)/x(t-n))^(h/n) - 1 ]` |
|`difal` | period-to-period annualized log change     | `100 * (h/n) * ln[ x(t)/x(t-n) ]` |
|`difv`  | period-to-period average change            | `[x(t)-x(t-n)] / n`               |
|`difv%` | period-to-period average percent change    | `100*[ (x(t)/x(t-n))^(h/n) - 1 ]` |
|`difvl` | period-to-period average log change        | `(100/n) * ln[ x(t)/x(t-n) ]`     |
|`movv`  | `n`-period moving average                  | `sum_{j=0}^{n-1} x(t-j)/n`        |
|`mova`  | `n`-period annualized moving average       | `sum_{j=0}^{n-1} x(t-j)*(h/n)`    |
|`movt`  | `n`-period moving total                    | `sum_{j=0}^{n-1} x(t-j)`          |
|`yryr`  | year-over-year change                      | `x(t) -  x(t-h)`                  |
|`yryr%` | year-over-year percent change              | `100*[x(t)/x(t-h) - 1 ]`          |
|`yryrl` | year-over-year log change                  | `100*ln[ x(t)/x(t-h) ]`           |



## visualization
There is a plotting module built into `edan` which specializes in working with the hierarchical data that defines its tables. It was built with the aforementioned data transformations in mind, so any desired alterations above are seamlessly incorporated into the plotting functionality. A few examples and the code used to generate them follow:
```python
import edan
import edan.plotting as plt # wrapper of matplotlib.pyplot

gdp_table = edan.nipa.GDPTable
gdp = gdp_table['gdp']
gdp.plot(
	subs=['pce:g', 'pce:s', 'pdi', 'x', 'gov'],
	start='1/1/2003',
	end='12/31/2008'
)
```
![GDP Levels](https://github.com/hotzsauce/edan/blob/readme_figs/gdp_level.png?raw=true)


```python
ces_table = edan.ces.CESTable
serv = ces_table['ces:p:s']

plt.set_style('ft')
serv.plot(
	method='diff',
	title='Change in employment of service industries',
	start='1/1/2008',
	end='12/1/2019',
)
```
![Employment Change](https://github.com/hotzsauce/edan/blob/readme_figs/empl_change.png?raw=true)


The next two plots utilize so-called `feature`s of the NIPA components: the contributions to real growth and the nominal share of subcomponents:
```python
pce_table = edan.nipa.PCETable()
goods = pce_table['pce:g:d']

plt.set_style('bb')
goods.plot(
	feature='contributions',
	start='1/1/1980',
	end='12/1/1989'
)
```
![PCE Contributions](https://github.com/hotzsauce/edan/blob/readme_figs/pce_contr.png?raw=true)

```python
plt.set_style('econ')
pce.plot(
	feature='shares',
	mtype='nominal',
	subs=['pce:g:d', 'pce:g:n', 'pce:s'],
)
```
![PCE Shares](https://github.com/hotzsauce/edan/blob/readme_figs/pce_shares.png?raw=true)