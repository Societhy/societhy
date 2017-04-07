/**
 * Other user overview controller.
 *
 * @class userOtherOverviewCtrl
 */
app.controller('userOtherOverviewCtrl', function($scope, $http, $timeout, $rootScope, $location, $state) {
    var ctrl = this;
    $scope.alreadyContact = false;

//OAuth
    OAuth.initialize('xitTtb8VF8kr2NKmBhhKV_yKi4U');

    /**
     * Toggle the "add to contact" button wether the user is in contact list or not.
     * @method toggleContactBtn
     */
    function toggleContactBtn() {
        $scope.alreadyContact = false;
        console.log("nefore =", $rootScope.profile)
        if ($rootScope.user) {
            for (contact in $rootScope.user.contact_list) {
                if ($rootScope.user.contact_list[contact].id == ctrl.profile._id) {
                    console.log($rootScope.user.contact_list[contact].id, ' vs ', ctrl.profile._id);
                    $scope.alreadyContact = true;
                    break;
                }
            }
        }
    }

    /**
     * Find the user's profile page.
     * @method findUser
     */
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

    /**
     * Add the user to the contact list.
     * @method addToContact
     */
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
