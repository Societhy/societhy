#!/bin/bash

help()
{
    echo USAGE:
    echo "	ethcluster [options] command [arguments]"
    echo
    echo COMMANDS:
    echo "	create	<N>		créé N noeuds connectés sur un réseau privé"
    echo "  attach  <N>     connection à l'API json-rpc du noeud N"
    echo "  relay           ouvre un noeud avec une api JSON/RPC publique"
    echo "  connect         connection à l'API json-rpc du noeud du serveur"
    echo "	kill			détruit le cluster"
    echo "	clear			erase blockchain data (starts a new one)"
    echo
    echo OPTIONS:
    echo "	--unlock		les comptes des noeuds sont unlock au lancement"
    echo "	--mine			les noeuds minent au lancement"
    echo "	--dir </path/to/dir>	dossier ou sont stockés les clefs et la blockchain"
    echo
}

clear()
{
    rm -rf $datadir/**/chaindata/
}

kill()
{
    killall -QUIT geth
}

attach()
{
    geth attach rpc:http://localhost:8101
}

relay()
{
    nohup parity --rpc --rpcaddr 10.224.9.117 --rpcport 8080 --jsonrpc-hosts all &>/dev/null &
}

connect()
{
    geth attach http://163.5.84.117:8080
}

cluster()
{
    truncate -s 0 /tmp/clusterEnodes
    local nodes=$(($1 + 1))
    
    for ((i=1 ; i<nodes; ++i)); do
        echo 'launching node '$i'...'
        echo "geth --datadir $datadir/0$i --ipcdisable --port 4030$i --rpc --rpcport 810$i --rpcapi \"web3,admin,eth,personal,net\" --rpccorsdomain '*' --networkid 8587 $mine $unlock &>/dev/null &"
        nohup geth --datadir $datadir/0$i --ipcdisable --port 4030$i --rpc --rpcport 810$i --rpcapi "web3,admin,eth,personal,net" --rpccorsdomain '*' --networkid 8587 $mine $unlock &>/dev/null &
	    mine=''
    	sleep 5
    	addr=`geth --datadir $datadir/0$i --exec "admin.nodeInfo.enode" attach rpc:http://localhost:810$i | grep \"` 
    	echo $addr >> /tmp/clusterEnodes
    done
    
    for ((i=1 ; i<nodes; ++i)); do
    	exclude=1
    	while read -r enode; do
    	    if [ "$i" -ne "$exclude" ]; then
    		echo "connecting node" $i "to enode" $enode
    		geth --exec "admin.addPeer($enode)"  attach rpc:http://localhost:810$i
    		sleep 1
    	    fi
    	    ((exclude+=1))
    	done < /tmp/clusterEnodes
    done
}

mine=''
unlock=''
usrdir=$HOME
datadir=$usrdir/.ethereum/societhest
ethdir=$usrdir/.ethereum
nbArg=$#
for ((i=0; i<nbArg; ++i)); do
    if [ "$1" = "create" ]; then
	ls>/dev/null
	cluster $2
	break
    elif [ "$1" = "attach" ]; then
	attach $2
	break
    elif [ "$1" = "clear" ]; then
    clear
    break
    elif [ "$1" = "connect" ]; then
    connect
    break
    elif [ "$1" = "relay" ]; then
    relay
    break
    elif [ "$1" = "kill" ]; then
	ls>/dev/null
	kill
	break
    elif [ "$1" = "--mine" ]; then
	mine="--mine --minerthreads 1"
    elif [ "$1" = "--unlock" ]; then
	unlock="--unlock 0 --password /dev/null"
    elif [ "$1" = "--dir" ]; then
	datadir=$2
	shift
    else
	help
    fi
    shift
done
