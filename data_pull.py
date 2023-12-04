import io
import os
import json
import gzip

import pandas as pd
import boto3
import numpy as np
import requests
from sodapy import Socrata
import zipfile
import geopandas as gpd

def get_building_data(filter_: bool = True, subset: bool = True, fillna: bool = True) -> pd.DataFrame:
    """
    Pulls building data from the NYC Open Data API
    """
    client = Socrata("data.cityofnewyork.us", None)

    results = client.get("7x5e-2fxh", limit=29000)

    results_df = pd.DataFrame.from_records(results)

    results_df = results_df.replace('Not Available', np.nan)
    if filter_:
        results_df = filter_building_data(results_df)
    if subset:
        results_df = subset_building_data(results_df)
    if fillna:
        results_df = fill_building_data(results_df)
    return results_df


def subset_building_data(df: pd.DataFrame) -> pd.DataFrame:
    location_data_columns = ['property_id', 'latitude', 'longitude', 'borough', 'nta']

    property_use_details_columns = [
        'primary_property_type',
        'largest_property_use_type',
        'largest_property_use_type_1',
        '_2nd_largest_property_use',
        '_2nd_largest_property_use_1',
        '_3rd_largest_property_use',
        'year_built',
        'construction_status',
        'number_of_buildings',
        'occupancy',
        'metered_areas_energy',
        'metered_areas_water',
        '_3rd_largest_property_use_1',
        'national_median_reference',
        'property_gfa_calculated_1',
        'last_modified_date_property',
        'last_modified_date_electric',
        'last_modified_date_gas_meters',
        'last_modified_date_non',
        'last_modified_date_water',
        'last_modified_date_property_1'
    ]

    energy_use_metrics_columns = [
        'reason_s_for_no_score',
        'energy_star_score',
        'energy_star_certification',
        'energy_star_certification_1',
        'site_eui_kbtu_ft',
        'weather_normalized_site_eui',
        'national_median_site_eui',
        'site_energy_use_kbtu',
        'weather_normalized_site_energy',
        'weather_normalized_site',
        'weather_normalized_site_1',
        'source_eui_kbtu_ft',
        'weather_normalized_source',
        'national_median_source_eui',
        'source_energy_use_kbtu',
        'weather_normalized_source_1',
        'fuel_oil_1_use_kbtu',
        'fuel_oil_2_use_kbtu',
        'fuel_oil_4_use_kbtu',
        'fuel_oil_5_6_use_kbtu',
        'diesel_2_use_kbtu',
        'propane_use_kbtu',
        'district_steam_use_kbtu',
        'district_hot_water_use_kbtu',
        'district_chilled_water_use',
        'natural_gas_use_kbtu',
        'natural_gas_use_therms',
        'weather_normalized_site_2',
        'electricity_use_grid_purchase',
        'electricity_use_grid_purchase_1',
        'weather_normalized_site_3',
        'electricity_use_grid_purchase_2',
        'electricity_use_grid_purchase_3',
        'electricity_use_generated',
        'electricity_use_generated_1',
        'electricity_use_generated_2',
        'electricity_use_generated_3',
        'annual_maximum_demand_kw',
        'annual_maximum_demand_mm',
        'annual_maximum_demand_meter',
        'green_power_onsite_kwh',
        'green_power_offsite_kwh',
        'green_power_onsite_and_offsite',
        'total_ghg_emissions_metric',
        'direct_ghg_emissions_metric',
        'total_ghg_emissions_intensity',
        'direct_ghg_emissions_intensity',
        'indirect_ghg_emissions_metric',
        'net_emissions_metric_tons',
        'indirect_ghg_emissions',
        'national_median_total_ghg',
        'egrid_output_emissions_rate',
        'avoided_emissions_onsite',
        'avoided_emissions_offsite',
        'avoided_emissions_onsite_1',
        'percent_of_recs_retained',
        'percent_of_total_electricity',
        'water_use_all_water_sources',
        'municipally_supplied_potable',
        'municipally_supplied_potable_1',
        'municipally_supplied_potable_2',
        'municipally_supplied_potable_3'
    ]
    data_quality_columns = [
        'estimated_data_flag',
        'estimated_data_flag_natural',
        'estimated_data_flag_fuel',
        'estimated_data_flag_fuel_1',
        'estimated_data_flag_fuel_2',
        'estimated_data_flag_fuel_3',
        'estimated_data_flag_district',
        'estimated_data_flag_1',
        'estimated_values_energy',
        'estimated_values_water',
        'alert_data_center_issue_with',
        'alert_energy_meter_has_less',
        'alert_energy_meter_has_gaps',
        'alert_energy_meter_has',
        'alert_energy_no_meters',
        'alert_energy_meter_has_single',
        'alert_water_meter_has_less',
        'alert_property_has_no_uses'
    ]

    # Combine all columns into a single list
    all_subset_columns = location_data_columns + property_use_details_columns + energy_use_metrics_columns + data_quality_columns

    # Subset the dataframe based on these columns
    df = df[all_subset_columns]

    df = df.dropna(subset=['latitude', 'longitude', 'borough', 'nta'])

    return df

def filter_building_data(df: pd.DataFrame) -> pd.DataFrame:
    df = df.loc[df['metered_areas_water'] == 'Whole Property']
    df = df.loc[df['metered_areas_energy'] == 'Whole Property']
    df = df.loc[df['construction_status'] == 'Existing']
    df = df.loc[df['alert_energy_meter_has_less'] == 'Ok']
    df = df.loc[df['alert_energy_meter_has_gaps'] == 'Ok']
    df = df.loc[df['alert_water_meter_has_less'] == 'Ok']
    df = df.loc[df['alert_energy_no_meters'] == 'Ok']

    return df

def fill_building_data(df: pd.DataFrame) -> pd.DataFrame:
    # Fill NaNs with zeros for the specified columns
    fill_zero_columns = [
        'fuel_oil_1_use_kbtu', 'fuel_oil_4_use_kbtu', 'fuel_oil_5_6_use_kbtu',
        'diesel_2_use_kbtu', 'propane_use_kbtu', 'electricity_use_generated',
        'electricity_use_generated_1', 'electricity_use_generated_2', 'electricity_use_generated_3',
        'green_power_onsite_kwh', 'avoided_emissions_onsite', 'percent_of_recs_retained',
        'percent_of_total_electricity'
    ]
    df[fill_zero_columns] = df[fill_zero_columns].fillna(0)

    # Drop columns or observations where values are boolean-like
    drop_columns = [
        '_3rd_largest_property_use', '_3rd_largest_property_use_1', 'energy_star_certification',
        'estimated_data_flag_district', 'estimated_data_flag_1', 'municipally_supplied_potable',
        'municipally_supplied_potable_3', 'district_steam_use_kbtu', 'district_hot_water_use_kbtu',
        'district_chilled_water_use', 'annual_maximum_demand_kw', 'annual_maximum_demand_mm',
        'annual_maximum_demand_meter', 'municipally_supplied_potable_1', 'municipally_supplied_potable_2'
    ]

    # Drop observations based on specific conditions
    df = df[df['estimated_data_flag_fuel'] != "Yes"]
    df = df[df['estimated_data_flag_fuel_2'] != "Yes"]
    df = df[df['estimated_data_flag_fuel_3'] != "Yes"]
    df.drop(columns=drop_columns, inplace=True, errors='ignore')

    df = df.drop(columns=[column for column in df.columns if 'alert' in column or 'estimated' in column])

    dropna_cols = [
        'weather_normalized_site_eui',
        'site_eui_kbtu_ft',
        'national_median_site_eui',
        'site_energy_use_kbtu',
        'weather_normalized_site_2',
        'weather_normalized_site_energy',
        'weather_normalized_site',
        'weather_normalized_site_1',
        'source_eui_kbtu_ft',
        'weather_normalized_source',
        'national_median_source_eui',
        'source_energy_use_kbtu',
        'weather_normalized_source_1',
        'electricity_use_grid_purchase',
        'electricity_use_grid_purchase_1',
        'weather_normalized_site_3',
        'electricity_use_grid_purchase_2',
        'electricity_use_grid_purchase_3',
        'green_power_offsite_kwh',
        'green_power_onsite_and_offsite',
        'total_ghg_emissions_metric',
        'direct_ghg_emissions_metric',
        'total_ghg_emissions_intensity',
        'direct_ghg_emissions_intensity',
        'indirect_ghg_emissions_metric',
        'net_emissions_metric_tons',
        'indirect_ghg_emissions',
        'national_median_total_ghg',
        'egrid_output_emissions_rate',
        'avoided_emissions_offsite',
        'avoided_emissions_onsite_1',
        'water_use_all_water_sources',
        'energy_star_score'
    ]

    df.dropna(subset=dropna_cols, inplace=True)

    # Drop specified columns
    drop_cols = [
        'nta',
        'reason_s_for_no_score',
        '_2nd_largest_property_use_1',
        '_2nd_largest_property_use',
    ]

    df.drop(columns=drop_cols, inplace=True)

    # Fill NaNs with zero for specified columns
    fillna_cols = [
        'natural_gas_use_kbtu',
        'natural_gas_use_therms',
        'fuel_oil_2_use_kbtu'
    ]

    df[fillna_cols] = df[fillna_cols].fillna(0)

    return df

def get_nta_geog():
    nta_tab_areas_endpt = 'q2z5-ai38'
    nta_tab_areas = pd.read_csv(
        'https://data.cityofnewyork.us/api/views/' + nta_tab_areas_endpt + '/rows.csv?accessType=DOWNLOAD')
    gpd.options.use_pygeos = False  # Ensure compatibility for geometries conversion
    nta_geometries = gpd.GeoSeries.from_wkt(nta_tab_areas['the_geom'])

    nta_gdf = gpd.GeoDataFrame(nta_tab_areas, geometry=nta_geometries)

    nta_gdf = nta_gdf.drop(columns=['the_geom'])

    nta_gdf.crs = "EPSG:4326"

    return nta_gdf

def download_and_extract_zip(s3_client, bucket, object_key, local_zip_file):
    # Download the zip file
    s3_client.download_file(bucket, object_key, local_zip_file)
    print(f"Downloaded {object_key}")

    # Extract the zip file
    with zipfile.ZipFile(local_zip_file, 'r') as zip_ref:
        zip_ref.extractall('./data/')
        print(f"Extracted {local_zip_file}")

def adjust_colnames(df: pd.DataFrame) -> pd.DataFrame:
    if 'tripduration' in df.columns:
        df = df.rename(
            columns={
                'starttime': 'started_at',
                'stoptime': 'ended_at',
                'start station id': 'start_station_id',
                'start station name': 'start_station_name',
                'start station latitude': 'start_lat',
                'start station longitude': 'start_lng',
                'end station id': 'end_station_id',
                'end station name': 'end_station_name',
                'end station latitude': 'end_lat',
                'end station longitude': 'end_lng',
                'usertype': 'member_casual',
            })
        df = df.drop(columns=['tripduration', 'birth year', 'bikeid', 'gender'])
        df['rideable_type'] = np.nan
        df['member_casual'] = df['member_casual'].replace({'Subscriber': 'member', 'Customer': 'casual'})
    else:
        df = df.drop(columns=['ride_id'])

    return df

def pull_citibike_data():
    keys = pd.read_csv('rootkey.csv')
    aws_access_key_id = keys['Access key ID'][0]
    secret_access = keys['Secret access key'][0]

    os.environ['AWS_ACCESS_KEY_ID'] = aws_access_key_id
    os.environ['AWS_SECRET_ACCESS_KEY'] = secret_access

    if not os.path.exists('data'):
        os.mkdir('data')

    s3 = boto3.client('s3')
    bucket_name = 'tripdata'
    prefix = '2021'
    response = s3.list_objects_v2(Bucket=bucket_name, Prefix=prefix)
    if 'Contents' in response:
        # Iterate through the objects with the prefix of 2021
        for item in response['Contents']:
            file_name = item['Key']
            # Check if the file name ends with '.zip'
            if file_name.endswith('.zip'):
                # Define a local path to save the zip file
                local_zip_file = file_name.split('/')[-1]
                # Download and extract the zip file
                download_and_extract_zip(s3, bucket_name, file_name, 'data/' + local_zip_file)
            else:
                print(f"Skipping {file_name}, not a ZIP file")
    else:
        print("No ZIP files found for the year 2021.")
def get_citibike_data():
    if len([i for i in os.listdir('data') if i.endswith('.csv') and 'citibike' in i]) < 12:
        pull_citibike_data()

    all_data = []
    for file in sorted(list(os.listdir('data'))):
        if file.endswith('.csv') and 'citibike' in file:
            data = adjust_colnames(pd.read_csv('data/' + file, low_memory=False))
            all_data.append(data)
    all_data = pd.concat(all_data)
    all_data['started_at'] = pd.to_datetime(all_data['started_at'], format='mixed')
    all_data['ended_at'] = pd.to_datetime(all_data['ended_at'], format='mixed')
    all_data['ride_duration_secs'] = (all_data['ended_at'] - all_data['started_at']).dt.total_seconds()
    return all_data

def clean_citibike_data(df: pd.DataFrame) -> pd.DataFrame:
    df['started_at'] = pd.to_datetime(df['started_at'], format='mixed')
    df['ended_at'] = pd.to_datetime(df['ended_at'], format='mixed')
    df['ride_duration_secs'] = (df['ended_at'] - df['started_at']).dt.total_seconds()
    return df

def get_trip_counts(df):
    df = df[['start_station_id', 'end_station_id']]
    df = df.groupby(['start_station_id', 'end_station_id']).size().reset_index(name='trip_count')
    return df


def get_trip_matrix(df):
    """
    returns a dataframe with the average trip duration and distance traveled between each station pair. Also the trip count between each station pair.
    :param df:
    :return:
    """
    df = df[['start_station_id', 'end_station_id', 'ride_duration_secs', 'distance_traveled', 'member_casual',
             'rideable_type']]
    df2 = df[['start_station_id', 'end_station_id']]
    df2 = df2.groupby(['start_station_id', 'end_station_id']).size().reset_index(name='trip_count')
    df = df.groupby(['start_station_id', 'end_station_id', 'member_casual']).agg(
        {'ride_duration_secs': 'mean', 'distance_traveled': 'mean'}).reset_index()
    df = df.pivot_table(index=['start_station_id', 'end_station_id'], columns='member_casual',
                        values=['ride_duration_secs', 'distance_traveled']).reset_index()

    df.columns = ['_'.join(col).strip() for col in df.columns.values]
    df = df.rename(columns={'start_station_id_': 'start_station_id', 'end_station_id_': 'end_station_id'})
    df = df.fillna(0)
    df = pd.merge(df, df2, on=['start_station_id', 'end_station_id'], how='left')
    return df

def get_nta_demographics(cols: list = None):
    endpt = 'https://data.cityofnewyork.us/download/8cwr-7pqn/application%2Fzip'

    if not os.path.exists('data/nta'):
        print('dir not exist, creating...')
        os.mkdir('data/nta')

    if len(os.listdir('data/nta')) < 2:
        print('data not exist, downloading...')
        res = requests.get(endpt, stream=True)
        z = zipfile.ZipFile(io.BytesIO(res.content))
        z.extractall('data/nta')
    dfs = []
    for file in os.listdir('data/nta'):
        if file.endswith('.xlsx'):
            df = pd.read_excel('data/nta/' + file)
            dfs.append(df.sort_values(by='GeoID'))

    df = pd.concat(dfs, axis=1)
    df = df.loc[:, ~df.columns.duplicated()].copy()
    if cols:
        return df[['GeoID'] + cols]
    return df


