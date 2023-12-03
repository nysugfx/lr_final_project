# LR Final Project

## Thoughts:

- We have to subset our building data to pick a few building types:
  - Multifamily Housing (Interesting)
  - Office or Financial Office
  - plenty of other options (see below)
- We can look at trips that start near Multifamily housing and end near Offices, and vice versa
- There are some columns that relate directly to data regarding multifamily housing as well
- first we have to calculate euclidean distance between each building and each bike station, then select the closest (we can pick one or two)
- then we can look at the trips that start at those stations and end near offices
- some interesting questions this might answer:
  - How many people are using citibikes to commute, how does this relate to their membership status? their bike type?
  - We can look at specific features related to multifamily housing and see how they relate to citibike usage
  - We can look at specific features related to offices and see how they relate to citibike usage
  - [DOCS](https://data.cityofnewyork.us/Environment/Energy-and-Water-Data-Disclosure-for-Local-Law-84-/7x5e-2fxh) for the buildings dataset
- Bike Ride Patterns and Building Types
	- Investigate if there's a correlation between the types of buildings (e.g., residential, commercial, industrial) and the frequency or duration of Citibike rides in their proximity. Do certain building types encourage more biking?
	- when people go from mostly residential areas to more commercial areas, is there a relationship between the length of the trip and the energy efficiency of the starting (and potentially ending) location of the ride? For example, do people that travel longer from residential to commercial come from less efficient buildings? The thought is that less wealthy people have to travel longer and also live in less efficient buildings
	- Analyze the spatial distribution of Citibike stations in relation to energy-efficient buildings. Are bike stations more prevalent near these buildings? This could indicate a potential link between sustainable transportation options and energy-efficient buildings.
	- study if the demographics of areas with more bike rides correlate with higher energy efficiency in buildings. Do neighborhoods with higher income levels, less diversity, etc have more energy-efficient buildings and higher bike usage? Are the neighborhoods more residential?


### Building Types:
  - Multifamily Housing
  - Office
  - Residence Hall/Dormitory
  - Senior Living Community
  - Retail Store
  - K-12 School
  - Non-Refrigerated Warehouse
  - Supermarket/Grocery Store
  - Hotel
  - Medical Office
  - Distribution Center
  - Worship Facility
  - Financial Office
  - Hospital (General Medical & Surgical)
  - Mixed Use Property
  - Refrigerated Warehouse
  - Bank Branch
  - Wastewater Treatment Plant
  - Wholesale Club/Supercenter