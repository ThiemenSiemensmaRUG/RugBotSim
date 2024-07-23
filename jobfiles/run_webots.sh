#!/bin/bash


 
RUN=$1
INSTANCE_ID=$2
NUM_ROBOTS=$3



line=$((INSTANCE_ID + 1))

# Kill webots after WB_TIMEOUT seconds
WB_TIMEOUT=60

# Set the input directory (relative to the current working directory)
INPUT_DIR=Instance_${INSTANCE_ID}
echo "webots input directory is " ${INPUT_DIR}
echo $(pwd)
# Set the output directory to put results (relative to the current working directory)
OUTPUT_DIR=Instance_${INSTANCE_ID}
echo "webots output directory is " ${OUTPUT_DIR}
JOB_BASE_DIR=$(pwd)/tmp/job_${INSTANCE_ID}

# Create the working directory for Webots, where Webots can write its stuff
if [ ! -d $JOB_BASE_DIR ]

then
   echo "(`date`) Create job base directory for the Webots instance of this run_webots.sh script as $JOB_BASE_DIR"
   mkdir -p $JOB_BASE_DIR
fi

# Set Webots working directory, where Webots can write its stuff
export WB_WORKING_DIR=$JOB_BASE_DIR

cp ${INPUT_DIR}/c_settings.txt $WB_WORKING_DIR/c_settings.txt 
cp ${INPUT_DIR}/s_settings.txt $WB_WORKING_DIR/s_settings.txt 
cp ${INPUT_DIR}/world.txt $WB_WORKING_DIR/world.txt 






# PATH : This line defines the path to the Webots world to be launched, each instance will open a unique world file. 
WEBWORLD="$(pwd)/../../worlds/world_${INSTANCE_ID}.wbt"  
echo "Running file $WEBWORLD"
time timeout $WB_TIMEOUT webots --minimize --batch --mode=fast --stdout --stderr --no-rendering $WEBWORLD &> $WB_WORKING_DIR/webots_log.txt 


mv $WB_WORKING_DIR/webots_log.txt ${OUTPUT_DIR}/webots_log_${INSTANCE_ID}.txt
mv $WB_WORKING_DIR/fitness.txt ${OUTPUT_DIR}/fitness.txt

rm -r $JOB_BASE_DIR

