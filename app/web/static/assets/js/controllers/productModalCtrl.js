app.controller('ProductModalController', function($scope, $http, $sessionStorage, $rootScope, $uibModalInstance, FileUploader, ctrl) {

    $scope.product = {
        isDigital: false,
        price: 10,
        stock: 10,
        owner: $rootScope.currentOrga._id
    };

    var productImageUploader = $scope.productImageUploader = new FileUploader({
        url: '/productImageUploader',
        alias: 'product',
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

    $scope.cancel = function() {
        $uibModalInstance.dismiss('canceled');
    }

    $scope.form = {
        submit: function(form) {
            if (form.$valid) {
                var sendProduct = $scope.product;
                if (sendProduct.isDigital) {sendProduct.shippingMode = ""};
                $http.post('/addNewProduct', sendProduct).then(function(response) {
                    sendProduct.id = response.data._id;
                    //ENVOYER L'IMAGE
                    $uibModalInstance.dismiss('finished');
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
