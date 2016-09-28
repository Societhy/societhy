# Dev-Utils


ETHCLUSTER.SH
==========

Script bash qui fournit les fonctionnalités suivantes :

       - création d'un "cluster" (réseau de noeuds connectés entre eux) sur une blockchain privée

       - connection à l'API json-rpc d'un noeud précédemment créé

       - destruction du cluster


PRÉREQUIS :

geth


INSTALLATION :

git clone git@github.com:Societhy/Dev-Utils.git

cd Dev-Utils

sudo ./install.sh


USAGE :

      ethcluster [options] command [arguments]


      COMMANDS:

	create	<N>		créé N noeuds connectés sur un réseau privé

	attach	<N>		connection à l'API json-rpc du noeud N

	connect 		connection à l'API json-rpc du noeud sur le serveur

	relay			lance un noeud et ouvre l'api aux requêtes externes (à lancer sur le serveur)

	kill			détruit tous les processus 'geth'


      OPTIONS:

	--unlock		les comptes des noeuds sont unlock au lancement

	--mine	    	        les noeuds minent au lancement

	--dir </path/to/dir>    dossier ou sont stockés les clefs et la blockchain