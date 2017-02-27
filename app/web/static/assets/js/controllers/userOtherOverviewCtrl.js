app.controller('userOtherOverviewCtrl', function($scope, $http, $timeout, $rootScope, $location, $state) {
    var ctrl = this;
    $scope.alreadyContact = false;

//OAuth
    OAuth.initialize('xitTtb8VF8kr2NKmBhhKV_yKi4U');

    function toggleContactBtn() {
        $scope.alreadyContact = false;
        console.log("nefore =", $rootScope.profile)
        for (contact in $rootScope.profile.contact_list) {
            if ($rootScope.user.contact_list[contact].id == ctrl.profile._id) {
                console.log($rootScope.user.contact_list[contact].id, ' vs ', ctrl.profile._id);
                $scope.alreadyContact = true;
                break;
            }
        }
    }

    function findUser() {
        console.log($state.params);
    	$http.post('/findUser', {
    		   "_id": $state.params._id,
    		  }).then(function(response) {
    	    $rootScope.profile = ctrl.profile = response.data;
            $rootScope.query = null;
            toggleContactBtn();
    	},
    		function(error) {
    		    console.log(error);
    		});
    }

    $scope.addToContact = function(){
        if (ctrl.profile != null) {
            $http.post('/addToContact', {
                "_id": $rootScope.user._id,
                "contact" : {
                    "id": ctrl.profile._id,
                    "firstname": ctrl.profile.firstname,
                    "lastname": ctrl.profile.lastname,
                }
            }).then(function(response) {
                if (response.status != 401) {
                    $rootScope.user = response.data;
                    $rootScope.$emit("loadChat", '');
                    toggleContactBtn();
                }
            }, function(error) {
                console.error();
            });
        }
    }

    findUser();
    return ctrl;
});
