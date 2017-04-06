app.controller('ProductModalController', function($scope, $uibModalInstance, $sessionStorage, SweetAlert, $rootScope, FileUploader, ctrl) {

    var productImageUploader = $scope.productImageUploader = new FileUploader({
        url: '/productImageUploader',
        alias: 'product',
        headers: {
            Authentification: $sessionStorage.SociethyToken
        }
    });

    productImageUploader.filters.push({
        name: 'imageFilter',
        fn: function (item, options) {
            var type = '|' + item.type.slice(item.type.lastIndexOf('/') + 1) + '|';
            return '|jpg|png|jpeg|bmp|gif|'.indexOf(type) !== -1;
        }
    });

    ctrl.pushProduct = function() {
        console.log("Push the product !");
    };

    ctrl.cancel = function() {
        $rootScope.productModal.close('a');
    }
});
