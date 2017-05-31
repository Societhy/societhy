app.controller('ProductModalController', function($scope, $http, $sessionStorage, $rootScope, $uibModalInstance, FileUploader, ctrl) {

    $scope.product = {
        isDigital: false,
        price: 10,
        stock: 10,
        owner: $rootScope.currentOrga._id
    };

    var productImageUploader = $scope.productImageUploader = new FileUploader({
        url: '/productImageUpload',
        alias: 'prodImg',
        headers: {
            Authentification: $sessionStorage.SociethyToken
        }
    });

    productImageUploader.filters.push({
        name: 'imageFilter',
        fn: function(item, options) {
            var type = '|' + item.type.slice(item.type.lastIndexOf('/') + 1) + '|';
            return '|jpg|png|jpeg|bmp|gif|'.indexOf(type) !== -1;
        }
    });

	productImageUploader.onCompleteAll = function() {
		$uibModalInstance.dismiss('finished');
	}

    $scope.cancel = function() {
        $uibModalInstance.dismiss('canceled');
    }

	$scope.removeImage = function(index) {
		// productImageUploader.removeFromQueue(index);
	}

    $scope.form = {
        submit: function(form) {
            if (form.$valid) {
                var sendProduct = $scope.product;
                if (sendProduct.isDigital) {sendProduct.shippingMode = ""};
                $http.post('/addNewProduct', sendProduct).then(function(response) {
                    sendProduct.id = response.data._id;
					for (var i = 0; i != productImageUploader.queue.length; i++) {
						productImageUploader.queue[i].formData.push({"prod_id":sendProduct.id, "type":productImageUploader.queue[i].file.type});
					}
          if (productImageUploader.queue.length != 0) {
            productImageUploader.uploadAll();
          } else {
            $uibModalInstance.dismiss('finished');
          }
                }, function(error) {
                    console.log(error);
                });
            } else {
                var field = null, firstError = null;
                for (field in form) {
                    if (field[0] != '$') {
                        if (firstError === null && !form[field].$valid) {
                            firstError = form[field].$name;
                        }

                        if (form[field].$pristine) {
                            form[field].$dirty = true;
                        }
                    }
                }
                angular.element('.ng-invalid[name=' + firstError + ']').focus();
            }
        }
    }
});
