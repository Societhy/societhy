app.controller('userOtherOverviewCtrl', function($scope, $http, $timeout, $rootScope, $location) {
    var ctrl = this;

//OAuth
    OAuth.initialize('xitTtb8VF8kr2NKmBhhKV_yKi4U');

    function findUser() {
	name = $location.url().substring($location.url().lastIndexOf('/') + 1);
	$http.post('/findUser', {
		   "name": name,
		  }).then(function(response) {
	    $rootScope.profile = ctrl.profile = response.data;
	},
		function(error) {
		    console.log(error);
		});

    }

    findUser();
    return ctrl;
});
