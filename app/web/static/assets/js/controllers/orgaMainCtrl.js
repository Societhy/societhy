app.controller('OrgaMainController', function($rootScope, $scope, $http, $sessionStorage, $state) {

	var ctrl = this;
	$scope.isMember = false;

    $scope.listProducts = [{
            "name": "Product1",
            "description": "Ceci est le product1 de test 1",
            "price": 10,
            "stock": 1000,
            "picture": ""
        },
        {
            "name": "Product2",
            "description": "Ceci est le product2 de test 2",
            "price": 20,
            "stock": 1000,
            "picture": ""
        },
        {
            "name": "Product3",
            "description": "Ceci est le product3 de test 3",
            "price": 30,
            "stock": 1000,
            "picture": ""
        },
        {
            "name": "Product4",
            "description": "Ceci est le product4 de test 4",
            "price": 40,
            "stock": 1000,
            "picture": ""
        },
        {
            "name": "Product5",
            "description": "Ceci est le product5 de test 5",
            "price": 50,
            "stock": 1000,
            "picture": ""
        },
        {
            "name": "Product6",
            "description": "Ceci est le product6 de test 6",
            "price": 60,
            "stock": 1000,
            "picture": ""
        },
        {
            "name": "Product7",
            "description": "Ceci est le product7 de test 7",
            "price": 70,
            "stock": 1000,
            "picture": ""
        },
        {
            "name": "Product8",
            "description": "Ceci est le product8 de test 8",
            "price": 80,
            "stock": 1000,
            "picture": ""
        },
        {
            "name": "Product9",
            "description": "Ceci est le product9 de test 9",
            "price": 90,
            "stock": 1000,
            "picture": ""
        },
        {
            "name": "Product10",
            "description": "Ceci est le product10 de test 10",
            "price": 100,
            "stock": 1000,
            "picture": ""
        },
    ];
    $scope.currentProd = $scope.listProducts[0];

    ctrl.setProduct = function(product) {
        $scope.currentProd = product;
    }

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
