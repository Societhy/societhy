app.controller('KeyController', function($scope, $http, $timeout) {
	
	var ctrl = this;

	// BUTTON ANIMATION
	$scope.ldloading = {};

	ctrl.loadGenerateKey = function(style) {
        $scope.ldloading[style.replace('-', '_')] = true;
        $timeout(function () {
            $scope.ldloading[style.replace('-', '_')] = false;
        }, 2000);
        // open modal that expose two actions : genLocalKey & genLinkedKey
        console.log(this.genLocalKey())
	};

	ctrl.genLocalKey = function() {
  		keythereum.create(keythereum.constants, function(dk) {
			console.log(dk)
			//ask for pasword
			keythereum.dump("bite", dk.privateKey, dk.salt, dk.iv, null, function (keyObject) {
    			console.log(keyObject)
    			$http.get('/keyWasGenerated/'.concat(keyObject.address)).then(function(reponse) {
					// update UI according to response (add key in 'main key' section or in tab)
    				console.log("keyWasGenerated", reponse)
    			});
    			return keyObject
			});
		});
	};

	ctrl.genLinkedKey = function() {
		$http.get('/genLinkedKey').then(function(reponse) {
			// update UI according to response (add key in 'main key' section or in tab)
			console.log(response);
		});
	}

	ctrl.loadImportKey = function() {
        $scope.ldloading[style.replace('-', '_')] = true;
        $timeout(function () {
            $scope.ldloading[style.replace('-', '_')] = false;
        }, 2000);
        // open modal that exposes a drag&drop + 'browse' button and also two actions : importLocalKey & importLinkedKey
	};

	ctrl.importLocalKey = function() {
		//after file loaded ask for password and decrypt key
		var key = JSON.parse('{"address":"379f3981e8ca02ac0ef983f9c344f984c2e74607","crypto":{"cipher":"aes-128-ctr","ciphertext":"2eadb2019e85ccf21193c4e89299704074491ee29c88218fd830c82b37a5e7d3","cipherparams":{"iv":"0c74c62e5ea7aa86ed26ae6ddc3b9b40"},"kdf":"scrypt","kdfparams":{"dklen":32,"n":262144,"p":1,"r":8,"salt":"ac99012bf435c38ae29bed2e4dacca9bedf34f1ea7947b5ed842158ec035fb84"},"mac":"53fccd340cfe0d7775f79096a3290538a9afb3fe2b76239bda534f51e5ae5b71"},"id":"d847b5ec-c1ce-4794-a731-3f4111beba9d","version":3}')
		var dk = keythereum.recover("test", key)
		console.log("importLocalKey", dk)
		return dk
	};

	ctrl.importLinkedKey = function() {
		//after file loaded send it through post
		var key = JSON.parse('{"address":"379f3981e8ca02ac0ef983f9c344f984c2e74607","crypto":{"cipher":"aes-128-ctr","ciphertext":"2eadb2019e85ccf21193c4e89299704074491ee29c88218fd830c82b37a5e7d3","cipherparams":{"iv":"0c74c62e5ea7aa86ed26ae6ddc3b9b40"},"kdf":"scrypt","kdfparams":{"dklen":32,"n":262144,"p":1,"r":8,"salt":"ac99012bf435c38ae29bed2e4dacca9bedf34f1ea7947b5ed842158ec035fb84"},"mac":"53fccd340cfe0d7775f79096a3290538a9afb3fe2b76239bda534f51e5ae5b71"},"id":"d847b5ec-c1ce-4794-a731-3f4111beba9d","version":3}')
		$http.post('/importNewKey' {
			"address": key.address
		}).then(function(reponse) {
			// update UI according to response (add key in 'main key' section or in tab)
			console.log("importLinkedKey", response);
		});		
	};

	ctrl.loadExportKey = function() {
        $scope.ldloading[style.replace('-', '_')] = true;
        $timeout(function () {
            $scope.ldloading[style.replace('-', '_')] = false;
        }, 2000);
        // open modal that exposes two actions : exportDeleteKey & exportKey
	};

	ctrl.exportDeleteKey = function(address) {
		$http.get('/exportDeleteKey/'.concat(address)).then(function(reponse) {
			// open modal to download keyfile + red message "key has been deleted from server"
			console.log("exportDeleteKey", response);
		});
	};

	ctrl.exportKey = function(address) {
		$http.get('/exportKey/'.concat(address)).then(function(reponse) {
			// open modal to download keyfile
			console.log("exportKey", response);
		});
	};

	ctrl.genLocalKey();
	ctrl.genLinkedKey();
	ctrl.importLocalKey();
	ctrl.importLinkedKey();
	ctrl.exportDeleteKey("379f3981e8ca02ac0ef983f9c344f984c2e74607");
	ctrl.exportKey("379f3981e8ca02ac0ef983f9c344f984c2e74607");
});