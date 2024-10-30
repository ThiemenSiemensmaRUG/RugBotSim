#!/bin/bash
export WEBOTS_HOME=/usr/local/webots
RUN=$1
INSTANCE_ID=$2
NUM_ROBOTS=$3
PORT=$4

line=$((INSTANCE_ID + 1))

# Kill webots after WB_TIMEOUT seconds of no finish
WB_TIMEOUT=60

# Set the input directory (relative to the current working directory)
INPUT_DIR=Instance_${INSTANCE_ID}
echo "Webots input directory is ${INPUT_DIR}"
echo $(pwd)

# Set the output directory to put results (relative to the current working directory)
OUTPUT_DIR=Instance_${INSTANCE_ID}
echo "Webots output directory is ${OUTPUT_DIR}"
JOB_BASE_DIR=$(pwd)/tmp/job_${INSTANCE_ID}

# Create the working directory for Webots, where Webots can write its stuff
if [ ! -d $JOB_BASE_DIR ]; then
   echo "(`date`) Creating job base directory for the Webots instance as $JOB_BASE_DIR"
   mkdir -p $JOB_BASE_DIR
fi

# Set Webots working directory, where Webots can write its stuff
export WB_WORKING_DIR=$JOB_BASE_DIR

# Copy necessary input files to the Webots working directory
cp ${INPUT_DIR}/c_settings.txt $WB_WORKING_DIR/c_settings.txt 
cp ${INPUT_DIR}/s_settings.txt $WB_WORKING_DIR/s_settings.txt 
cp ${INPUT_DIR}/world.txt $WB_WORKING_DIR/world.txt 

# Define the path to the Webots world file to be launched, each instance will open a unique world file
WEBWORLD="$(pwd)/../../worlds/world_${INSTANCE_ID}.wbt"


# Print the file being run and the port number
echo "Running file $WEBWORLD on port $PORT"

# Run Webots in batch mode with a timeout
time timeout $WB_TIMEOUT webots --minimize --batch --mode=fast --stdout --port=$PORT --stderr --no-rendering $WEBWORLD &> $WB_WORKING_DIR/webots_log.txt

# Move output files to the output directory
mv $WB_WORKING_DIR/webots_log.txt ${OUTPUT_DIR}/webots_log_${INSTANCE_ID}.txt
mv $WB_WORKING_DIR/fitness.txt ${OUTPUT_DIR}/fitness.txt

# Clean up the Webots working directory
rm -r $JOB_BASE_DIR
