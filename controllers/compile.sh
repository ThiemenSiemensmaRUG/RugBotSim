#give execution acces
#chmod +x ../compile.sh
#./compile.sh

export WEBOTS_HOME=/usr/local/webots

#!/bin/bash
cd "$(dirname "$0")"

cd inspection_controller
make clean
make

cd ../

cd cpp_supervisor
make clean
make

cd ../