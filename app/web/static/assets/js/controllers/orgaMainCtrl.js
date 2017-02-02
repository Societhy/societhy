app.controller('OrgaMainController', function($rootScope, $scope, $http, $sessionStorage, $state) {

	var ctrl = this;

	ctrl.joinOrga = function() {
		if (!$rootScope.user) {
			$rootScope.toogleError("Please sign-in first")
		}

		else if ($rootScope.user.local_account == true) {
			console.log("ask for password")
		}
		else {
            $scope.completeBlockchainAction(function(password) {
	            $rootScope.toogleWait("Joining...");
				$http.post('/joinOrga', {
					"orga_id": $rootScope.currentOrga._id,
					"password": password
				}).then(
				function(data) {
					console.log(data);
				},
				function(error) {
					console.log(error);
				});
        	});


		}
	}

	$rootScope.currentOrga = $state.params.data
	console.log("state params", $state.params)
	if (!$rootScope.currentOrga) {
		$http.post('/getOrganization', {
			"id": $state.params._id
		}).then(function(response) {
			$rootScope.currentOrga = response.data;
		}, function(error) {
			$state.go('app.dashboard');
			$rootScope.toogleError("Organization does not exist");			
		})
	}
	return ctrl;
});

