# !/bin/bash

mkdir $HOME/.ethereum
mkdir $HOME/.ethereum/societhest

cp genesis.json $HOME/.ethereum/societhest

dir=`pwd`

cd /usr/local/bin/

ln -s $dir/ethcluster.sh ./ethcluster

cd $dir
