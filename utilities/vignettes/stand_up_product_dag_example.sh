#!/bin/bash
# *** Run interactively ***
# This is an end-to-end example of standing up a full product DAG, from converting L0 data from trino
# all the way through creating L1 output.
# Note that this is a simple scenario in which a single source type feeds into a product. If multiple
# source types feed into the product, repeat the steps that load in L0 data, metadata, and pipeline specifications
# for each relevant source type.


# Define paths
data_path='/scratch/pfs' # Where base repos like avro_schemas, empty_files, etc. are stored
git_path_pipelines='/home/NEON/csturtevant/R/NEON-IS-data-processing-homeDir/pipe'
git_path_avro='/home/NEON/csturtevant/R/NEON-IS-avro-schemas'
pipe_list_prefix='pipe_list_'
source_type='hmp155'
product='relHumidity'

# Define paths based on base paths and product information above 
spec_path_source_type=$git_path_pipelines/$source_type
spec_path_product=$git_path_pipelines/$product

# Create sensor-specific import_trigger with a small amount of data
pachctl create repo $source_type'_import_trigger'
pachctl start commit $source_type'_import_trigger'@master
sites=(CPER HARV BARC ARIK) # Edit as desired
days=(01 02 03) # Edit as desired. Jan 2020 is hardcoded throughout this code
for site in $(echo ${sites[*]}); do 
for day in $(echo ${days[*]}); do 
pachctl put file $source_type'_import_trigger'@master:/2020/01/$day/$site -f $data_path/import_trigger_FULL/2020/01/$day/$site
done
done
pachctl finish commit $source_type'_import_trigger'@master

# Load in calibrations (must be stored locally. Ideally, set up the python loader instead.
pachctl create repo calibration_$source_type
pachctl start commit calibration_$source_type@master
pachctl put file -r calibration_$source_type@master:/$source_type -f $data_path/calibration/$source_type
pachctl finish commit calibration_$source_type@master

# Create source-type-specific empty_files
pachctl create repo empty_files_$source_type
pachctl start commit empty_files_$source_type@master
pachctl put file -r empty_files_$source_type@master:/$source_type -f $git_path_avro/empty_files/$source_type
pachctl finish commit empty_files_$source_type@master

# Create source-type-specific avro_schemas
pachctl create repo avro_schemas_$source_type
pachctl start commit avro_schemas_$source_type@master
pachctl put file -r avro_schemas_$source_type@master:/$source_type -f $git_path_avro/avro_schemas/$source_type
pachctl finish commit avro_schemas_$source_type@master

# Create product-specific avro_schemas
pachctl create repo avro_schemas_$product
pachctl start commit avro_schemas_$product@master
pachctl put file -r avro_schemas_$product@master:/$product -f $git_path_avro/avro_schemas/$product
pachctl finish commit avro_schemas_$product@master

# Create source-type-specific fdas uncertainty (ONLY IF NEEDED FOR YOUR SOURCE TYPE)
pachctl create repo uncertainty_fdas_$source_type
pachctl start commit uncertainty_fdas_$source_type@master
pachctl put file -r uncertainty_fdas_$source_type@master:/ -f $data_path/uncertainty_fdas/
pachctl finish commit uncertainty_fdas_$source_type@master

# Set up source type pipeline
# Read in the pipelines (in order) for this source type and stand them up
# The (ordered) list of pipeline files should be located in the file pipe_list_SOURCETYPE.txt in the 
# directory of pipeline specs for the source type
unset pipelines
pipelines=`cat $spec_path_source_type/$pipe_list_prefix$source_type.txt`
for pipe in $(echo ${pipelines[*]}); do
echo pachctl create pipeline -f $spec_path_source_type/$pipe
pachctl create pipeline -f $spec_path_source_type/$pipe
done

# Now run the daily cron pipeline to initialize it.
# Then stop it almost immediately after (so it doesn't run every day until we want it to)
pachctl run cron $source_type'_cron_daily_and_date_control'
# Wait a few minutes and ensure the job runs, then...
pachctl stop pipeline $source_type'_cron_daily_and_date_control'


# Set up product pipeline
# Read in the pipelines (in order) for this product and stand them up
# The (ordered) list of pipeline files should be located in the file pipe_list_PRODUCT.txt in the 
# directory of pipeline specs for the data product
unset pipelines
pipelines=`cat $spec_path_product/$pipe_list_prefix$product.txt`
for pipe in $(echo ${pipelines[*]}); do
echo pachctl create pipeline -f $spec_path_product/$pipe
pachctl create pipeline -f $spec_path_product/$pipe
done

# Before proceeding...
# Check that everything has run properly for the few locations and days loaded. Verify the output.


# Bump to full scale for a few days
# *** First - edits the date_gap_filler pipeline spec to remove restriction on particular CFGLOCs. ***
# *** Also make any desired edits to the cron_daily_and_date_control pipeline spec to adjust date range to the dates of the import trigger 
pachctl start transaction
pachctl update pipeline --reprocess -f $spec_path_source_type/$source_type'_cron_daily_and_date_control.yaml'
pachctl update pipeline -f $spec_path_source_type/$source_type'_fill_date_gaps_and_regularize.yaml'
pachctl start commit $source_type'_import_trigger'@master
pachctl finish transaction
for day in $(echo ${days[*]}); do 
pachctl put file -r $source_type'_import_trigger'@master:/2020/01/$day -f $data_path/import_trigger_FULL/2020/01/$day
done
pachctl finish commit $source_type'_import_trigger'@master

# Add 1 day at full scale to evaluate resource requests in normal operations
# *** First - edit the date_gap_filler_limiter pipeline spec to add 1 day to the end date ***
pachctl start transaction
pachctl update pipeline --reprocess -f $spec_path_source_type/$source_type'_cron_daily_and_date_control.yaml'
pachctl start commit $source_type'_import_trigger'@master
pachctl finish transaction
days=(04) # Edit as desired
for day in $(echo ${days[*]}); do 
pachctl put file -r $source_type'_import_trigger'@master:/2020/01/$day -f $data_path/import_trigger_FULL/2020/01/$day
done
pachctl finish commit $source_type'_import_trigger'@master

