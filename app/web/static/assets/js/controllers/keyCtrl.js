app.controller('KeyController', function($scope, $http, $timeout) {
	
	var ctrl = this;

	// BUTTON ANIMATION
	$scope.ldloading = {};

	ctrl.createKey = function() {
  		keythereum.create(keythereum.constants, function(dk) {
			console.log(dk)
			keythereum.dump("bite", dk.privateKey, dk.salt, dk.iv, null, function (keyObject) {
    			console.log(keyObject)
    			return keyObject
			});
		});
	}

	ctrl.loadCreateKey = function(style) {
        $scope.ldloading[style.replace('-', '_')] = true;
        $timeout(function () {
            $scope.ldloading[style.replace('-', '_')] = false;
        }, 2000);
        console.log(this.createKey())
	};

	ctrl.importKey = function() {
		var key = JSON.parse('{"address":"379f3981e8ca02ac0ef983f9c344f984c2e74607","crypto":{"cipher":"aes-128-ctr","ciphertext":"2eadb2019e85ccf21193c4e89299704074491ee29c88218fd830c82b37a5e7d3","cipherparams":{"iv":"0c74c62e5ea7aa86ed26ae6ddc3b9b40"},"kdf":"scrypt","kdfparams":{"dklen":32,"n":262144,"p":1,"r":8,"salt":"ac99012bf435c38ae29bed2e4dacca9bedf34f1ea7947b5ed842158ec035fb84"},"mac":"53fccd340cfe0d7775f79096a3290538a9afb3fe2b76239bda534f51e5ae5b71"},"id":"d847b5ec-c1ce-4794-a731-3f4111beba9d","version":3}')
		console.log(key)
		var dk = keythereum.recover("test", key)
		console.log(dk)
	}

});