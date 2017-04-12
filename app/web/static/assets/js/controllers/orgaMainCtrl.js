/**
 * Main controller for organizations.
 * @class OrgaMainController
 */
app.controller('OrgaMainController', function($rootScope, $scope, $http, $sessionStorage, $timeout, $state, $controller) {

	var ctrl = this;
	$scope.isMember = false;
	ctrl.wallet = $controller("WalletController");

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

    /**
     * Get the organizations list.
     * @method onLoad
     */
    onLoad = function() {
        $http.post('/getOrganization', {
            "id": $state.params._id
        }).then(function(response) {
            $scope.currentOrga = $rootScope.currentOrga = response.data.orga;
            $scope.currentRights = $rootScope.currentRights = response.data.rights
            console.log("current orga & rights", $scope.currentOrga, $scope.currentRights)
            if ($rootScope.user) {
                $scope.isMember = $rootScope.user.account in $scope.currentOrga.members;
            }
        }, function(error) {
            $state.go('app.dashboard');
            $rootScope.toogleError("Organization does not exist");
        })
    };

    /**
     * Join a new organization by it's tag.
     * @param {string} tag - Tag of the organization.
     * @method joinOrga
     */
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

	/**
	 * Leave the current organization.
	 * @method leaveOrga
	 */
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

	/**
	 * Create a project from the organization.
     * @method createProject
	 */
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

	/**
	 * Make a donation to the organization.
     * @method makeDonation
	 */
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

	$timeout(function() {
		$(".donate-button").click(ctrl.makeDonation);
	}, 500);
	onLoad();

	return ctrl;
});
