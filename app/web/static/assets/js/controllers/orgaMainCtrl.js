app.controller('OrgaMainController', function($rootScope, $scope, $http, $sessionStorage, $state) {

	var ctrl = this;
	$scope.isMember = false;
/*
	ctrl.init = function() {
*/
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

    $rootScope.updateFilter = function() {
	delete $rootScope.histo;
	$rootScope.histo = $.extend(true, {}, $rootScope.histoFull);
	if ($("#filterCategory").val() != "all")
	{
	    $.each($rootScope.histo, function (id) {
		if ($rootScope.histo[id]["category"] != $("#filterCategory").val())
		    delete $rootScope.histo[id];
	    });
	}
    }

    ctrl.getHisto = function(begin, end) {
	password = "test";
	$http.post('/getOrgaHisto', {
	    "orga_id": $state.params.orga_id,
	    "password": password,
	    "date": {"begin": begin, "end": end}
	}).then(
	    function(data) {
		$(".orgaActivityLoading").addClass("displayNone");
		$(".timeline").removeClass("displayNone");
		$rootScope.histoFull = data.data;
		$rootScope.histo = data.data;
	    },
	    function(error) {
		console.log(error);
	    });

    };

    $rootScope.initSlider = function() {
	console.log();
	max = new Date();
	min = new Date();
	min.setDate(min.getDate() - 7);
	max.setMonth(max.getMonth() - 1);
	min.setMonth(min.getMonth() - 1);
	$("#slider").dateRangeSlider();
	$("#slider").dateRangeSlider("bounds",min, max);
	min.setDate(min.getDate() + 4);
	$("#slider").dateRangeSlider("values",min, max);
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

	if (!$rootScope.currentOrga) {
		$http.post('/getOrganization', {
			"id": $state.params._id
		}).then(function(response) {
			$scope.currentOrga = $rootScope.currentOrga = response.data;
			console.log("current orga", $scope.currentOrga)
			$rootScope.date = new Date();
			begin = new Date();
			begin.setDate(begin.getDate() - 7);
			ctrl.getHisto(begin, $rootScope.date);
			if ($rootScope.user)
				$scope.isMember = $rootScope.user.account in $scope.currentOrga.members;
		}, function(error) {
		    //$state.go('app.dashboard');
			$rootScope.toogleError("Organization does not exist");			
		})
	}
	return ctrl;
});
