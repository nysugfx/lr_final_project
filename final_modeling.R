data <- read.csv('/Users/alexfriedman/Downloads/lrFinalProject/final_project/final_data.csv')

# data$OOcHU1E <- data$OOcHU1E / data$Pop_1E
# data$ROcHU1E <- data$ROcHU1E / data$Pop_1E
data$primary_property_type <- NULL
data$EA_LTHSGrE <- data$EA_LTHSGrE / data$Pop_1E
data$EA_BchDHE <- data$EA_BchDHE / data$Pop_1E
data$EA_HScGrdE <- data$EA_HScGrdE / data$Pop_1E
data$MgBSciArtE <- data$MgBSciArtE / data$Pop_1E
data$SrvcE <- data$SrvcE / data$Pop_1E
data$PvU50E <- data$PvU50E / data$Pop_1E
data$Pv50t74E <- data$Pv50t74E / data$Pop_1E
data$Pv100t124E <- data$Pv100t124E / data$Pop_1E
data$Pv125t149E <- data$Pv125t149E / data$Pop_1E
data$Pv150t174E <- data$Pv150t174E / data$Pop_1E
data$Pv175t184E <- data$Pv175t184E / data$Pop_1E
data$Pv185t199E <- data$Pv185t199E / data$Pop_1E
data$Pv200t299E <- data$Pv200t299E / data$Pop_1E
data$Pv300t399E <- data$Pv300t399E / data$Pop_1E
data$Pv400t499E <- data$Pv400t499E / data$Pop_1E
data$Pv500plE <- data$Pv500plE / data$Pop_1E

model <- lm(site_eui_kbtu_ft~. - X - NTACode, data=data)
summary(model)
library(dplyr)
data2 <- data %>% filter(data$station_count > 0)
print(nrow(data2))
model2 <- lm(site_eui_kbtu_ft ~ . - X - NTACode, data=data2)
summary(model2)

qqnorm(data$site_eui_kbtu_ft)

reduced_citibike <- lm(site_eui_kbtu_ft ~ . - X - NTACode - n_rides_start - avg_ride_duration_secs_start - n_rides_end - avg_ride_duration_secs_end - station_count, data=data2)
reduced_poverty <- lm(site_eui_kbtu_ft ~ . - X - NTACode - MdHHIncE - MnHHIncE - PvU50E - Pv50t74E - Pv75t99E - Pv100t124E - Pv150t174E - Pv175t184E - Pv185t199E - Pv200t299E - Pv300t399E - Pv500plE, data=data2)
reduced_building <- lm(site_eui_kbtu_ft ~ . - X - NTACode - multifamily_housing_gross - largest_property_use_type_residential - occupancy_residential - occupancy_non_residential - year_built_residential - year_built_non_residential - OOcHU1E - ROcHU1E - MdVlE, data=data2)
reduced_empl <- lm(site_eui_kbtu_ft ~ . - X - NTACode - MgBSciArtE - SrvcE - SalesOffE - NRCnstMntE - PrdTrnsMME, data=data2)
reduced_inc <- lm(site_eui_kbtu_ft ~ . - X - NTACode - MdHHIncE - MnHHIncE, data=data2)
reduced_educ <- lm(site_eui_kbtu_ft ~ . - X - NTACode - EA_LTHSGrE - EA_BchDHE - EA_HScGrdE, data=data2)
reduced_residential_occ <- lm(site_eui_kbtu_ft ~ . - X - NTACode - occupancy_residential - occupancy_non_residential + I((occupancy_residential + occupancy_non_residential)/2), data=data2)
reduced_residential_yr <- lm(site_eui_kbtu_ft ~ . - X - NTACode - year_built_residential - year_built_non_residential + I((year_built_residential + year_built_non_residential)/2), data=data2)
red_pv_lvl <- lm(site_eui_kbtu_ft ~ . - X - NTACode - PvU50E - Pv50t74E - Pv75t99E + I(PvU50E + Pv50t74E + Pv75t99E) - Pv100t124E - Pv150t174E - Pv175t184E - Pv185t199E - Pv200t299E - Pv300t399E - Pv500plE + I(Pv100t124E + Pv150t174E + Pv175t184E + Pv185t199E + Pv200t299E + Pv300t399E + Pv500plE), data=data2)

anova_citi <- anova(reduced_citibike, model2)
anova_pov <- anova(reduced_poverty, model2)
anova_building <- anova(reduced_building, model2)
anova_empl <- anova(reduced_empl, model2)
anova_inc <- anova(reduced_inc, model2)
anova_educ <- anova(reduced_educ, model2)
anova_residential_occ <- anova(reduced_residential_occ, model2)
anova_residential_yr <- anova(reduced_residential_yr, model2)
anova_pv <- anova(red_pv_lvl, model2)
                        
