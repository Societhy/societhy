## SOCIETHY
========

[![Build Status](https://travis-ci.org/Societhy/societhy.svg?branch=master)](https://travis-ci.org/Societhy/societhy)

Usage :

* build docker image : `make build`

* launch container : `make shell`

* do both : `make`

* go to webapp : `localhost:4242` in your browser

* launch server (in docker) = `run`

* ssh to eip server : `ssh exploit@163.5.84.117 -p 22`

## Install npm et bower dependencies
====================================
* Install node.js

* Install grunt : `npm install -g grunt-cli`

* Install dependencies : `make build_dependencies`

**(DEPLOYMENT ONLY)**

* Build Distribution Folder : `grunt build:layout1`

## Database help
================

Le serveur est lancé sur le port 27017 et 28017 pour la conf par navigateur. (je crois)
La base est stockée dans /var/lib/mongodb/

SERVER
    Démarrer le serveur mongod: sudo service mongod start
    Redémarrer le serveur mongod: sudo service mongod restart
    Stop le serveur mongod: sudo service mongod stop
    /!\ Si impossible de restart le serveur mongod: sudo rm /var/lib/mongodb/mongod.lock /!\
    Afficher les logs du server: tailf /var/log/mongodb/mongod.log

CLIENT
    On utilise la database "main" pour le projet.
    Les collections sont:
        contracts
        files
        fundraises
        organizations
        projects
        users
    Démarrer le client mongo sur le serveur: mongo 10.224.9.117/main -u dev -p SecurityIsABitBetter
    Démarrer le client mongo depuis l'extérieur: mongo 163.5.84.117/main -u dev -p SecurityIsABitBetter

    COMMANDE DE BASE
        - Afficher les databases: show dbs
        - Switcher de database: use <database_name>
        - Afficher les collections de la databse: show collections
        - L'accès à un champs encapsulé ou un élément de tableau dans mongoDB se fait avec la notation par points.
          Les guillemets sont obligatoires!
            Ex: {
                    ...
                    contribs: [ "Turing machine", "Turing test", "Turingery" ],
                    ...
                }
                Pour accéder à Turingery dans le tableau contribs, on utilise "contribs.2".

                {
                    ...
                    name: { first: "Alan", last: "Turing" },
                    contact: { phone: { type: "cell", number: "111-222-3333" } },
                    ...
                }
                Pour accéder récupérer le nom de famille, on utilise "name.last".
                Pour récupérer le numéro de téléphone, on utilise "contact.phone.number".

    INSERTION
        - Insérer un élément dans la collection (si la collection n'existe pas, elle est automatiquement créée): db.<collection_name>.insert(<représentation JSON de l'objet>)
            Ex: db.users.insert({
                    name: "toto",
                    lastname: "tata",
                    age: 30,
                    contact: {
                        phone: "0100000000", email: "toto@tata.com"
                    }
                })

    RECHERCHE
        - Afficher les éléments de la collection: db.<collection_name>.find()

        - Rechercher les documents où le champ == 1: db.<collection_name>.find( { <champ>: 1 } )
            Ex: db.users.find({ name: "toto" })

        - Rechercher les éléments où le champ encapsulé == 1: db.<collection_name>.find( { <embedded field>.<champ>: 1 } )
            Ex: db.users.find({ "contact.phone": "0100000000"})

        - Liste des opérateurs: plus grand que = $gt, plus petit que = $lt
        - Rechercher les éléments à l'aide d'opérateur: db.<collection_name>.find( { <champ1> : {<operateur>: <valeur> } } )
            Ex: db.users.find({ age: { $lt: 40 }})

        - Afficher les éléments suivant de la liste de résultats affichées: it

    UPDATE
        - Update le premier élément correspondant: db.<collection>.update({ <champ>: <valeur> }, { $set: <nouvelles valeurs>})
            Ex: db.users.update({ name: "toto"}, {$set: {age: 24, "contact.phone": "0123456789"}})

        - Update multiple: db.<collection>.update({ <champ>: <valeur> }, { $set: <nouvelles valeurs>}, {multi: true})
            Ex: db.users.update({ name: "toto"}, {$set: {age: 24, "contact.phone": "0123456789"}}, {multi: true})

        - Remplacer tout le document (les champs peuvent être totalement différents, tous les anciens seront supprimés): db.<collection>.update({ <champ>: <valeur> }, {<nouvelles valeurs>})
            db.users.update({name: "toto"},
                { name: { first: "toto", last: "tata" },
                    age: 30,
                    contact: { phone: "0100000000", email: "toto@tata.com" }
                }
            )

    SUPPRESSION
        - Supprimer tous les documents qui match la condition: db.<collection>.remove({ <champ>: <valeur> })
            Ex: db.users.remove({ name: "toto"})

        - Supprimer le premier élément qui match: db.<collection>.remove({ <champ>: <valeur> }, { justOne: true })
            Ex: db.users.remove({ name: "toto"}, { justOne: true })

        - Supprimer tous les éléments de la collection: db.<collection>.remove({})
            Ex: db.users.remove({ })

        - Drop tout le contenu de la collection et ses index (à favoriser par rapport à celle au dessus): db.<collection.drop()
            Ex: db.users.drop()
