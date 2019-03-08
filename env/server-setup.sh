# Using set -e will make the script exit if any line gives as non-zero return
set -e

cd src/server
python3 -m virtualenv env
source env/bin/activate
pip3 install -r requirements.txt