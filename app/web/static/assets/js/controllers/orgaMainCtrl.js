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
            $scope.completeBlockchainAction(
            	function(password) {
		            $rootScope.toogleWait("Joining...");
					$http.post('/joinOrga', {
						"orga_id": $rootScope.currentOrga._id,
						"password": password
					}).then(function(data) {}, function(error) { $rootScope.toogleError(error); });
        	},  function(data) {
    				$scope.currentOrga.members = $rootScope.currentOrga.members = data.data;
        	});


		}
	}

	ctrl.leaveOrga = function() {
		if (!$rootScope.user) {
			$rootScope.toogleError("Please sign-in first")
		}

		else if ($rootScope.user.local_account == true) {
			console.log("ask for password")
		}

		else {
            $scope.completeBlockchainAction(
            	function(password) {
		            $rootScope.toogleWait("Leaving...");
					$http.post('/leaveOrga', {
						"orga_id": $rootScope.currentOrga._id,
						"password": password
					}).then(function(data) {}, function(error) { $rootScope.toogleError(error); });
        	},  function(data) {
					$scope.currentOrga.members = $rootScope.currentOrga.members = data.data;
        	});


		}
	}

	$scope.currentOrga = $rootScope.currentOrga = $state.params.data
	console.log("current orga", $scope.currentOrga)
	if (!$rootScope.currentOrga) {
		$http.post('/getOrganization', {
			"id": $state.params._id
		}).then(function(response) {
			$scope.currentOrga = $rootScope.currentOrga = response.data;
			console.log("current orga", $scope.currentOrga)
		}, function(error) {
			$state.go('app.dashboard');
			$rootScope.toogleError("Organization does not exist");			
		})
	}
	return ctrl;
});

