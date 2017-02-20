app.controller('OrgaMainController', function($rootScope, $scope, $http, $sessionStorage, $state) {

	var ctrl = this;
	$scope.isMember = false;

	ctrl.joinOrga = function() {

		if ($scope.doVerifications()) {
			$scope.completeBlockchainAction(
				function(password) {
					$rootScope.toogleWait("Joining...");
					$http.post('/joinOrga', {
						"orga_id": $rootScope.currentOrga._id,
						"password": password
					}).then(function(data) {}, function(error) { $rootScope.toogleError(error); });
				},  function(data) {
					$scope.currentOrga.members = $rootScope.currentOrga.members = data.data.members;
					$rootScope.user.organizations.push($rootScope.currentOrga);
					$scope.isMember = true;
				});


		}
	}

	ctrl.leaveOrga = function() {
		
		if ($scope.doVerifications()) {
			$scope.completeBlockchainAction(
				function(password) {
					$rootScope.toogleWait("Leaving...");
					$http.post('/leaveOrga', {
						"orga_id": $rootScope.currentOrga._id,
						"password": password
					}).then(function(data) {}, function(error) { $rootScope.toogleError(error); });
				},  function(data) {
					$scope.currentOrga.members = $rootScope.currentOrga.members = data.data.members;
					$scope.isMember = false;
					$rootScope.user.organizations.splice(data.data, 1);
				});


		}
	}

	ctrl.createProject = function() {
		if ($scope.doVerifications()) {
			$scope.completeBlockchainAction(
				function(password) {
					$rootScope.toogleWait("Creating project")
					$http.post('/createProjectFromOrga', {
						"orga_id": $rootScope.currentOrga._id,
						"newProject": {},
						"password": password
					}).then(function(data) {}, function(error) { $rootScope.toogleError(error);});
				}, function(data) {
					$scope.currentOrga.projects = $rootScope.currentOrga.projects = data.data.projects;
				})
		}
	}

	ctrl.downloadDoc = function (doc_id, doc_name) {
		$http.get('/getOrgaUploadedDocument/' + doc_id + "/" + doc_name ).then(function(response) {
			console.log(response);
		});
	}

	$scope.currentOrga = $rootScope.currentOrga = $state.params.data
	if (!$rootScope.currentOrga) {
		$http.post('/getOrganization', {
			"id": $state.params._id
		}).then(function(response) {
			$scope.currentOrga = $rootScope.currentOrga = response.data;
			console.log("current orga", $scope.currentOrga)
			if ($rootScope.user)
				$scope.isMember = $rootScope.user.account in $scope.currentOrga.members;
		}, function(error) {
			$state.go('app.dashboard');
			$rootScope.toogleError("Organization does not exist");			
		})
	}
	return ctrl;
});

