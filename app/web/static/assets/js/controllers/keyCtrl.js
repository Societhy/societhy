app.controller('ModalGenerateController', function($scope, $uibModalInstance, ctrl) {
	$scope.ldlocal = {};
	$scope.ldrequest = {};
	$scope.local = function(operation, style) {
        $scope.ldlocal[style.replace('-', '_')] = true;
       	ctrl[operation]().then(
       		function(key) {
	       		console.log(key)
	            $scope.ldlocal[style.replace('-', '_')] = false;
	       	},
       		function(failure) {
       			console.log(failure)
	            $scope.ldlocal[style.replace('-', '_')] = false;
       		});
	};

	$scope.request = function(operation, style) {
        $scope.ldrequest[style.replace('-', '_')] = true;
        ctrl[operation]().then(
        	function(key) {
        		console.log(key);
	            $scope.ldrequest[style.replace('-', '_')] = false;
        	},
        	function(failure) {
        		console.log(failure);
	            $scope.ldrequest[style.replace('-', '_')] = false;
        	});
	};
});

app.controller('ModalImportController', function($scope, $uibModalInstance, ctrl, FileUploader) {
	var modalHtml = 
			"<div class=\"modal-header ng-scope\">\
                <h3 class=\"modal-title\">Chose a way to generate key!</h3>\
            </div>\
			<div class=\"modal-body\">\
				<button ladda=\"ldlocal.contract\" class=\"btn btn-o btn-primary ladda-button\" data-style=\"contract\" style=\"width:45%\" ng-click=\"local('genLocalKey', 'contract')\">\
					<span class=\"ladda-label\"> Generate key locally</span>\
    		        <span class=\"ladda-spinner\"></span>\
				</button>\
				<button ladda=\"ldrequest.contract\" class=\"btn btn-o btn-primary ladda-button\" data-style=\"contract\" style=\"float: right; width:45%\" ng-click=\"request('genLinkedKey', 'contract')\">\
					<span class=\"ladda-label\"> Generate key on server</span>\
        		    <span class=\"ladda-spinner\"></span>\
        	    </button>\
			</div>";
   	$scope.ldlocal = {};
	$scope.ldrequest = {};
	$scope.keyUploaded = false;
	$scope.uploader = new FileUploader({
        url: '/importNewKey',
        autoUpload: true
    });
	var uploader = $scope.uploader;

    uploader.onWhenAddingFileFailed = function (item/*{File|FileLikeObject}*/, filter, options) {
        console.info('onWhenAddingFileFailed', item, filter, options);
    };
    uploader.onAfterAddingFile = function (fileItem) {
        console.info('onAfterAddingFile', fileItem);
    };
    uploader.onAfterAddingAll = function (addedFileItems) {
        console.info('onAfterAddingAll', addedFileItems);
    };
    uploader.onBeforeUploadItem = function (item) {
        console.info('onBeforeUploadItem', item);
    };
    uploader.onProgressItem = function (fileItem, progress) {
        console.info('onProgressItem', fileItem, progress);
    };
    uploader.onProgressAll = function (progress) {
        console.info('onProgressAll', progress);
    };
    uploader.onSuccessItem = function (fileItem, response, status, headers) {
        console.info('onSuccessItem', fileItem, response, status, headers);
    };
    uploader.onErrorItem = function (fileItem, response, status, headers) {
        console.info('onErrorItem', fileItem, response, status, headers);
    };
    uploader.onCancelItem = function (fileItem, response, status, headers) {
        console.info('onCancelItem', fileItem, response, status, headers);
    };
    uploader.onCompleteItem = function (fileItem, response, status, headers) {
    	$scope.keyUploaded = true;
    	console.log('modalinstance', $uibModalInstance);
    	console.info('onCompleteItem', fileItem, response, status, headers);
    };
    uploader.onCompleteAll = function () {
        console.info('onCompleteAll');
    };

    $scope.removeKeyFile = function(item) {
    	$scope.keyUploaded = false;
    	item.remove()
    }

	$scope.local = function(operation, style) {
        $scope.ldlocal[style.replace('-', '_')] = true;
       	ctrl[operation]().then(
       		function(key) {
	       		console.log(key)
	            $scope.ldlocal[style.replace('-', '_')] = false;
	       	},
       		function(failure) {
       			console.log(failure)
	            $scope.ldlocal[style.replace('-', '_')] = false;
       		});
	};

	$scope.request = function(operation, style) {
        $scope.ldrequest[style.replace('-', '_')] = true;
        ctrl[operation]().then(
        	function(key) {
        		console.log(key);
	            $scope.ldrequest[style.replace('-', '_')] = false;
        	},
        	function(failure) {
        		console.log(failure);
	            $scope.ldrequest[style.replace('-', '_')] = false;
        	});
	};
});

app.controller('KeyController', function($scope, $http, $timeout, $uibModal, $q) {
	
	var ctrl = this;

	ctrl.loadGenerateKey = function() {
		// $scope.items = ['item1', 'item2', 'item3'];
		var modalHtml = 
			"<div class=\"modal-header ng-scope\">\
                <h3 class=\"modal-title\">Chose a way to generate key!</h3>\
            </div>\
			<div class=\"modal-body\">\
				<button ladda=\"ldlocal.contract\" class=\"btn btn-o btn-primary ladda-button\" data-style=\"contract\" style=\"width:45%\" ng-click=\"local('genLocalKey', 'contract')\">\
					<span class=\"ladda-label\"> Generate key locally</span>\
    		        <span class=\"ladda-spinner\"></span>\
				</button>\
				<button ladda=\"ldrequest.contract\" class=\"btn btn-o btn-primary ladda-button\" data-style=\"contract\" style=\"float: right; width:45%\" ng-click=\"request('genLinkedKey', 'contract')\">\
					<span class=\"ladda-label\"> Generate key on server</span>\
        		    <span class=\"ladda-spinner\"></span>\
        	    </button>\
			</div>";

        var modalInstance = $uibModal.open({
			// template: modalHtml,
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

	ctrl.loadImportKey = function() {
        var modalInstance = $uibModal.open({
	        templateUrl: "static/assets/views/modals/importKeyModal.html",
			controller: 'ModalImportController',
			size: 'lg',
			resolve: {
				ctrl: function() {
					return ctrl;
				}
			}
		});
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
		$http.post('/importNewKey', {
			"address": key.address
		}).then(function(response) {
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