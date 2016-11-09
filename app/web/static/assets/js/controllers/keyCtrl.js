/****************
*** GENERATE KEY MODAL CONTROLLER ***
*****************/

app.controller('ModalGenerateController', function($scope, $uibModalInstance, SweetAlert, ctrl) {
	$scope.ldlocal = {};
	$scope.ldrequest = {};
	errorAlertOptions= {
		title: "Uggh..",
		text: "Key generation failed",
		type: "error",
	}
	succesAlertOptions = {
		title: "Booyah!",
		text: "Key was generated successfully",
		type: "success",
		confirmButtonText: "Download key file",
		confirmButtonColor: "#007AFF"
	};

	$scope.local = function(operation, style) {
		$scope.ldlocal[style.replace('-', '_')] = true;
		ctrl[operation]().then(
			function(key) {
				$scope.ldlocal[style.replace('-', '_')] = false;
				console.log(key)
				SweetAlert.swal(succesAlertOptions, function() {
					$uibModalInstance.dismiss()
				});
			},
			function(failure) {
				console.log(failure)
				$scope.ldlocal[style.replace('-', '_')] = false;
				SweetAlert.swal(errorAlertOptions);
			});
	};

	$scope.request = function(operation, style) {
		$scope.ldrequest[style.replace('-', '_')] = true;
		ctrl[operation]().then(
			function(key) {
				console.log(key);
				$scope.ldrequest[style.replace('-', '_')] = false;
				SweetAlert.swal(succesAlertOptions, function() {
					$uibModalInstance.dismiss()
				});
			},
			function(failure) {
				console.log(failure);
				$scope.ldrequest[style.replace('-', '_')] = false;
				SweetAlert.swal(errorAlertOptions);

			});
	};
});

/****************
*** IMPORT KEY MODAL CONTROLLER ***
*****************/

app.controller('ModalImportController', function($scope, $uibModalInstance, $sessionStorage, SweetAlert, FileUploader, ctrl) {

	$scope.keyUploaded = false;

	$scope.uploader = new FileUploader({
		url: '/importNewKey',
		alias: 'key',
		headers: {
			Authentification: $sessionStorage.SociethyToken
		},
		autoUpload: true
	});
	var uploader = $scope.uploader;

	uploader.onErrorItem = function (fileItem, response, status, headers) {
		console.info('onErrorItem', fileItem, response, status, headers);
	};

	uploader.onCompleteItem = function (fileItem, response, status, headers) {
		$scope.keyUploaded = true;
		console.info('onCompleteItem', fileItem, response, status, headers);
		alertOptions = {
			title: status == 200 ? "Yay!" : "Oups :(",
			text: status == 200 ? "Key was imported successfully" : "Key file not recognized...",
			type: status == 200 ? "success" : "error",
			confirmButtonColor: "#007AFF"
		}

		SweetAlert.swal(alertOptions, function() {
			if (status == 200) {
				$uibModalInstance.dismiss()
				// ctrl.importLinkedKey(response.get('address'))
				ctrl.importLinkedKey("keyxxx0908087")
			}
		});
	};

	$scope.removeKeyFile = function(item) {
		$scope.keyUploaded = false;
		item.remove()
	}
});

/****************
*** EXPORT KEY MODAL CONTROLLER ***
*****************/

app.controller('ModalExportController', function($scope, $uibModalInstance, $sessionStorage, $rootScope, SweetAlert, FileUploader, ctrl) {
	$scope.addresses = $rootScope.user.addresses
	console.log($scope.addresses);
});

/****************
*** KEYCONTROLLER FUNCTIONS ***
*****************/

app.controller('KeyController', function($scope, $http, $timeout, $uibModal, $q, $rootScope) {
	
	var ctrl = this;

	/***
	KEY GENERATION
	***/

	ctrl.loadGenerateKey = function() {


		var modalInstance = $uibModal.open({
			templateUrl: "static/assets/views/modals/generateKeyModal.html",
			controller: 'ModalGenerateController',
			resolve: {
				ctrl : function() {
					return ctrl;
				}
			}
		});
	};

	ctrl.genLocalKey = function() {
		return $q(function(success, failure) {
			$timeout(function() {
				keythereum.create(keythereum.constants, function(dk) {
					//ask for pasword
					keythereum.dump("bite", dk.privateKey, dk.salt, dk.iv, null, function (keyObject) {
						$http.get('/keyWasGenerated/'.concat(keyObject.address)).then(
							function(data) {
								console.log("keyWasGenerated")
								success(keyObject);
							},
							function(error) {
								failure(error);
							});
					});
				});
			}, 2000);
		});
	};

	ctrl.genLinkedKey = function() {
		return $q(function(success, failure) {
			$timeout(function() {
				$http.get('/genLinkedKey').then(
					function(data) {
						success(data);
					}, function(error) {
						failure(error);
					});
			}, 2000);
		});
	};

	/***
	KEY IMPORT
	***/

	ctrl.loadImportKey = function() {
		var modalInstance = $uibModal.open({
			templateUrl: "static/assets/views/modals/importKeyModal.html" ,
			controller: 'ModalImportController',
			size: 'lg',
			resolve: {
				ctrl: function() {
					return ctrl;
				}
			}
		});
    };

    ctrl.importLocalKey = function() {
		//after file loaded ask for password and decrypt key
		var key = JSON.parse('{"address":"379f3981e8ca02ac0ef983f9c344f984c2e74607","crypto":{"cipher":"aes-128-ctr","ciphertext":"2eadb2019e85ccf21193c4e89299704074491ee29c88218fd830c82b37a5e7d3","cipherparams":{"iv":"0c74c62e5ea7aa86ed26ae6ddc3b9b40"},"kdf":"scrypt","kdfparams":{"dklen":32,"n":262144,"p":1,"r":8,"salt":"ac99012bf435c38ae29bed2e4dacca9bedf34f1ea7947b5ed842158ec035fb84"},"mac":"53fccd340cfe0d7775f79096a3290538a9afb3fe2b76239bda534f51e5ae5b71"},"id":"d847b5ec-c1ce-4794-a731-3f4111beba9d","version":3}')
		var dk = keythereum.recover("test", key)
		console.log("importLocalKey", dk)
		return dk
	};

	ctrl.importLinkedKey = function(address) {
		// updates UI after
		$rootScope.user.addresses = $rootScope.user.addresses ? $rootScope.user.addresses.concat(address) : [address];
		console.log($rootScope.user)
	};

	/***
	KEY EXPORT
	***/

	ctrl.loadExportKey = function() {
		var modalInstance = $uibModal.open({
			templateUrl: "static/assets/views/modals/exportKeyModal.html",
			controller: 'ModalExportController',
			resolve: {
				ctrl : function() {
					return ctrl;
				}
			}
		});
    };

    ctrl.exportDeleteKey = function(address) {
    	$http.get('/exportDeleteKey/'.concat(address)).then(function(response) {
			// open modal to download keyfile + red message "key has been deleted from server"
			console.log("exportDeleteKey", response);
		});
    };

    ctrl.exportKey = function(address) {
    	$http.get('/exportKey/'.concat(address)).then(function(response) {
			// open modal to download keyfile
			console.log("exportKey", response);
		});
    };
});