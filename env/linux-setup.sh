# Linux setup script
#
#
# Originally written by:
# Joel Burton <https://github.com/joelburton>
# Katie Byers <https://github.com/lobsterkatie>
#
#
# This script is to be run by Vagrant as the first step of provisioning when first running 'vagrant up'
#

# Using set -e will make the script exit if any line gives as non-zero return
set -e

# ensure that environment and Postgres default to UTF-8
echo "LANG=en_US.UTF-8" > /etc/default/locale
echo "LANGUAGE=en_US.UTF-8:" >> /etc/default/locale

#update package listings
echo -e "\nUpdating package listings\n"
apt-get update

# get nodejs - nodejs site recomend using curl over 'add-apt-repository'
# see https://nodejs.org/en/download/package-manager/
# running curl in 's' silent and 'L' location - if 3## in response resource
# has been moved and curl will look at the redirect location.
echo -e "\nGetting nodejs packages\n"
curl -sL https://deb.nodesource.com/setup_10.x | bash -
apt-get update

# Install JS-related packages:
apt-get install -y nodejs

#at this point running the following (sudo apt-get-get install nodejs ) will 
#install node AND npm -- We run this step during install of Linux 
#packages. In the future, you may need to install npm as well


#install useful linux packages
echo -e "\nInstalling Linux packages\n"
# ORIGINAL: sudo apt-get-get install -y git python-dev python-pip python-virtualenv sqlite3 libxml2-dev libxslt1-dev libffi-dev nodejs libssl-dev postgresql-client postgresql postgresql-contrib postgresql-plpython postgresql-server-dev-10 unzip

# Install tools for development and assessments:
apt-get install -y git unzip sqlite3 libxml2-dev libxslt1-dev libffi-dev libssl-dev wget

# Install postgres:
apt-get install -y postgresql postgresql-contrib postgresql-plpython postgresql-server-dev-10 postgresql-client

#install Python 3.6 packages:   
echo -e "\nInstalling Python 3.6 packages"
apt-get install -y python3 python3-dev python3-virtualenv virtualenv
apt-get install -y python3-pip
pip3 install psycopg2 psycopg2-binary ipython notebook python-twitter

# Note: the following "upgrade pip" command is explicitly being avoided for
# two reasons:
# 1- it breaks pip (because it installs a new "pip" in the python path that
# "from pip import main" uses first
# 2- the "right thing" according to Python best practices is to upgrade pip
# from inside a virtualenv (see https://github.com/pypa/pip/issues/5221 ).
#pip3 install -U pip3

# Set default version for Python in envs to 3.6
# Note: this is independent from Python 3 defaulting to 3.6 in Ubuntu 18.04 LTS
echo export VIRTUALENV_PYTHON=/usr/bin/python3.6 > /etc/profile.d/virtualenv_python.sh

echo "*************************************"
echo "Setup complete. No errors encountered"
echo "*************************************"
