app.controller('OrgaMainController', function($rootScope, $scope, $http, $sessionStorage, $state, $controller) {

	var ctrl = this;
	$scope.isMember = false;
	ctrl.wallet = $controller("WalletController");

	onLoad = function() {
		$http.post('/getOrganization', {
			"id": $state.params._id
		}).then(function(response) {
			$scope.currentOrga = $rootScope.currentOrga = response.data.orga;
			$scope.currentRights = $rootScope.currentRights = response.data.rights
			$(".donate-button").click(ctrl.makeDonation);
			console.log("current orga & rights", $scope.currentOrga, $scope.currentRights)
			if ($rootScope.user) {
				$scope.isMember = $rootScope.user.account in $scope.currentOrga.members;
			}
		}, function(error) {
			$state.go('app.dashboard');
			$rootScope.toogleError("Organization does not exist");			
		})
	};

	ctrl.joinOrga = function(tag) {

		if ($scope.doVerifications()) {
			$scope.completeBlockchainAction(
				function(password) {
					$rootScope.toogleWait("Joining...");
					$http.post('/joinOrga', {
						"tag": tag,
						"orga_id": $rootScope.currentOrga._id,
						"password": password
					}).then(function(data) {}, function(error) { $rootScope.toogleError(error); });
				},  function(data) {
					$scope.currentOrga.members = $rootScope.currentOrga.members = data.data.orga.members;
					$scope.currentRights = $rootScope.currentRights = data.data.rights;
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
					$scope.currentOrga.members = $rootScope.currentOrga.members = data.data.orga.members;
					$scope.currentRights = $rootScope.currentRights = data.data.rights;
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

	ctrl.makeDonation = function() {
		donationAmount = $("#donationAmount").val();
		if (donationAmount > 0 && $scope.doVerifications()) {
			$scope.completeBlockchainAction(
				function(password) {
					$rootScope.toogleWait("Sending donation")
					$http.post('/makeDonation', {
						"orga_id": $rootScope.currentOrga._id,
						"donation": {"amount": donationAmount},
						"password": password
					}).then(function(data) {}, function(error) { $rootScope.toogleError(error);});
				}, function(data) {
					$scope.currentOrga.balance = $rootScope.currentOrga.balance = data.data;
					ctrl.wallet.refreshAllBalances();
				})
		} else {
			$rootScope.toogleError("Donation amount must be more than to 0...")
		}
	}

	$rootScope.$on("loggedIn", function(event, data) {
		onLoad();
	});

	// $(function () {
		onLoad();
	// });

	return ctrl;
});

