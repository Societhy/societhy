app.controller('OfferModalController', function($scope, $http, $sessionStorage, $rootScope, $uibModalInstance, FileUploader, ctrl) {

    $scope.offer = {
        isRecurrent: false,
        isPermanent: false,
        initialWithdrawal: 1,
        recurrentWithdrawal: 0,
        duration: 0
    };
    var offerImageUploader = $scope.offerImageUploader = new FileUploader({
        url: '/offerImageUploader',
        alias: 'offer',
        headers: {
            Authentification: $sessionStorage.SociethyToken
        }
    });

    offerImageUploader.filters.push({
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
                var sendOffer = $scope.offer;
                if ($scope.doVerifications()) {
                    $scope.completeBlockchainAction(
                      function(password) {
                       $rootScope.toogleWait("Creating offer...");
                       $http.post('/createOffer', {
                        orga_id: $rootScope.currentOrga._id,
                        socketid: $rootScope.sessionId,
                        password: password,
                        offer: sendOffer,
                    })
                       .then(function(response) { sendOffer.id = response.data._id; $uibModalInstance.dismiss('finished');}
                        ,function(error) { console.log(error); });
                   },  function(data) {
                     console.log('---------------', data)
                 });
                }
            }
            else {
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
