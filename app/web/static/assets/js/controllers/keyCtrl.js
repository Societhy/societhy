/****************
*** GENERATE KEY MODAL CONTROLLER ***
*****************/

app.controller('ModalGenerateController', function($scope, $uibModalInstance, SweetAlert, $rootScope, ctrl) {
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
				SweetAlert.swal(succesAlertOptions, function() {
					var file = new Blob([ JSON.stringify(key) ], {
						type : 'text/plain'
					});
					saveAs(file, 'keyFile.txt')
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
				$scope.ldrequest[style.replace('-', '_')] = false;
				errorAlertOptions.showCancelButton = true,
				SweetAlert.swal(succesAlertOptions, function() {
					$uibModalInstance.dismiss()
				});
			},
			function(failure) {
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
		alertOptions = {
			title: status == 200 ? "Yay!" : "Oups :(",
			text: status == 200 ? "Key imported successfully" : response,
			type: status == 200 ? "success" : "error",
			confirmButtonColor: "#007AFF"
		}

		SweetAlert.swal(alertOptions, function() {
			if (status == 200) {
				$uibModalInstance.dismiss()
				ctrl.importLinkedKey(response.address)
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

	$scope.keys = $rootScope.user.eth.keys
	errorAlertOptions= {
		title: "Uggh..",
		type: "error",
	}
	succesAlertOptions = {
		title: "Booyah!",
		type: "success",
		confirmButtonColor: "#007AFF"
	};

	$scope.exportDeleteKey = function(address) {
		ctrl.exportDeleteKey(address).then(
			function(key) {
				succesAlertOptions.text = "Key was deleted successfully"
				SweetAlert.swal(succesAlertOptions)
			},
			function(failure) {
				errorAlertOptions.text = failure
				SweetAlert.swal(errorAlertOptions);
			}
		);
	}

	$scope.exportKey = function(address) {
		ctrl.exportKey(address).then(
			function(key) {
				succesAlertOptions.confirmButtonText = "Download key file"
				succesAlertOptions.text =  "Key was exported successfully"
				SweetAlert.swal(succesAlertOptions, function() {
					var file = new Blob([ JSON.stringify(key) ], {
						type : 'text/plain'
					});
					saveAs(file, 'keyFile.txt')
					$uibModalInstance.dismiss()
				});
			},
			function(failure) {
				errorAlertOptions.text = failure
				SweetAlert.swal(errorAlertOptions);
			}
		);
	};

});

/****************
*** KEYCONTROLLER FUNCTIONS ***
*****************/

app.controller('KeyController', function($scope, $http, $timeout, $uibModal, $q, $rootScope, SweetAlert, FileUploader, ladda) {
	
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
					//ask for password
					keythereum.dump("bite", dk.privateKey, dk.salt, dk.iv, null, function (keyObject) {
						$http.get('/keyWasGenerated/'.concat(keyObject.address)).then(
							function(data) {
								$rootScope.user.eth.keys['0x'.concat(keyObject.address)] = { "address": '0x'.concat(keyObject.address), "local": true, "balance": 0 };
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
				$http.post('/genLinkedKey', {
					"password": "coucou"
				}).then(
					function(response) {
						$rootScope.user.eth.keys[response.data] = {"address": response.data, "local": false, "balance": 0};
						success(response.data);
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
		$rootScope.user.eth.keys.push({"address": key.data, "local": false});
		return dk
	};

	ctrl.importLinkedKey = function(address) {
		$rootScope.user.eth.keys[address] = {"address": address, "local": false};
		$http.get('/getBalance/'.concat(address)).then(function(response) {
			$rootScope.user.eth.keys[address]["balance"] = response.data
		});
	};

	/***
	KEY EXPORT
	***/

	ctrl.loadExportKey = function() {
		var modalInstance = $uibModal.open({
			templateUrl: "static/assets/views/modals/exportKeyModal.html",
			controller: 'ModalExportController',
			size: 'lg',
			resolve: {
				ctrl : function() {
					return ctrl;
				}
			}
		});
	};

	ctrl.loadDownloadKey = function(key) {
		errorAlertOptions= {
			title: "Uggh..",
			type: "error",
		}
		succesAlertOptions = {
			title: "Booyah!",
			text: "Key was exported successfully",
			type: "success",
			confirmButtonText: "Download key file",
			confirmButtonColor: "#007AFF"
		};
		var l = Ladda.create(document.getElementById(key.address.concat('dl')));
		l.start()
		ctrl.exportKey(key.address).then(
			function(key) {
				l.stop()
				SweetAlert.swal(succesAlertOptions, function() {
					var file = new Blob([ JSON.stringify(key) ], {
						type : 'text/plain'
					});
					saveAs(file, 'keyFile.txt')
				});
			},
			function(failure) {
				l.stop()
				errorAlertOptions.text = failure
				SweetAlert.swal(errorAlertOptions);
			}
		);
	};

	ctrl.loadDeleteKey = function(key) {
		errorAlertOptions= {
			title: "Uggh..",
			type: "error",
		}
		succesAlertOptions = {
			title: "Booyah!",
			text: "Key was deleted successfully",
			type: "success",
			confirmButtonColor: "#007AFF"
		};
		var l = Ladda.create(document.getElementById(key.address.concat('rm')));
		l.start()
		ctrl.exportDeleteKey(key).then(
			function(deletedKey) {
				l.stop()
				SweetAlert.swal(succesAlertOptions);			
			},
			function(failure) {
				l.stop()
				errorAlertOptions.text = failure
				SweetAlert.swal(errorAlertOptions);
			}
		);
	};

	ctrl.exportDeleteKey = function(key) {
		return $q(function(success, failure) {
			$timeout(function() {
				$http.get('/exportDeleteKey/'.concat(key.address)).then(function(response) {
					delete $rootScope.user.eth.keys[key.address]
					success(response.data)
				}, function(error) {
					failure(error.data)
				});
			});
		});
	};

	ctrl.exportKey = function(address) {
		return $q(function(success, failure) {
			$timeout(function() {
				$http.get('/exportKey/'.concat(address)).then(function(response) {
					success(response.data);
				}, function(error) {
					failure(error.data);
				});
			}, 2000);
		});
	};

	/***
	REFRESH BALANCE
	***/

	$rootScope.refreshBalance = function(address) {
		$http.get('/getBalance/'.concat(address)).then(function(response) {
			$.each($rootScope.user.eth.keys, function(index, keyObject) {
				keyObject.balance = response.data[keyObject.address];
			});
		});
	};

	$rootScope.refreshAllBalances = function() {
		$http.get('/getAllBalances').then(function(response) {
			$.each($rootScope.user.eth.keys, function(index, keyObject) {
				keyObject.balance = response.data[keyObject.address];
			});
		});
	};

	return ctrl;
});