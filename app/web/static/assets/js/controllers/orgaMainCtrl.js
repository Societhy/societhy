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

	$timeout(function() {
		$(".donate-button").click(ctrl.makeDonation);
	}, 500);
	onLoad();

	return ctrl;
});


/*
 ** Histo Handler
 */
app.controller('OrgaHistoController', function($rootScope, $scope, $http, $sessionStorage, $timeout, $state, $controller) {
    ctrl = this;

    $rootScope.filter = {"categories": [{name: 'newMember'}, {name:'memberLeave'}, {name: 'newProposition'}, {name: 'newDonation'}, {name: 'newSpending'}], "members": []};
    $rootScope.filtered = {"categories": [], "members": []};


    $rootScope.getHisto = function (begin, end) {
        $http.post('/getOrgaHisto', {
            "orga_id": $state.params._id,
            "date": {"begin": begin, "end": end}
        }).then(
            function (data) {
                $(".orgaActivityLoading").addClass("displayNone");
                $(".timeline").removeClass("displayNone");
                if (data.data[0]) {
                    $rootScope.sliderFilter = [];
                    if (!$rootScope.sliderFilter.first)
                        $rootScope.sliderFilter.first = data.data[0]["first"];
                    $rootScope.sliderFilter.valBegin = begin;
                    $rootScope.sliderFilter.valEnd = end;
                    $rootScope.histoFull = $rootScope.histo = data.data;
                    updateSliderFilter();
                    $rootScope.updateFilter();
                }
                else {
                    delete $rootScope.histoFull;
                    delete $rootScope.histo;

                }
            },
            function (error) {
                console.log(error);
            });
    };

    /*
     ** SLIDER
     */
    function updateSliderFilter() {

        if (!$rootScope.sliderFilter || $("#sliderFilter.ui-dateRangeSlider").length <= 0)
            return;
        $("#sliderFilter").dateRangeSlider("bounds", new Date($rootScope.sliderFilter.first), $rootScope.date);
        $("#sliderFilter").dateRangeSlider("values", new Date($rootScope.sliderFilter.valBegin), new Date($rootScope.sliderFilter.valEnd));

    }

    $rootScope.initSliders = function () {
        $("#sliderFilter").dateRangeSlider();
        var slider = $('.range-slider');
        range = $('.range-slider__range');
        value = $('.range-slider__value');
        slider.each(function () {
            value.each(function () {
                var value = $(this).prev().attr('value');
                $(this).html(value);

            });
            range.on('input', function () {
                $(this).next(value).html(this.value);
            });
        });
        $("#sliderFilter").bind("userValuesChanged", $rootScope.updateHisto);
        updateSliderFilter();
    }

    /*
     ** FILTERS
     */
    $rootScope.updateHisto = function (e, data) {
        $rootScope.slider.begin = data.values.min;
        $rootScope.slider.end = data.values.max
        locale = "en-us";

        $rootScope.getHisto(
            ($rootScope.slider.begin.toLocaleString(locale, {month: "short"}) + " " + $rootScope.slider.begin.getDate() + ", " + $rootScope.slider.begin.getFullYear() + " 12:00 AM"),
            ($rootScope.slider.end.toLocaleString(locale, {month: "short"}) + " " + $rootScope.slider.end.getDate() + ", " + $rootScope.slider.end.getFullYear() + " 11:59 PM"))
    }

    $rootScope.updateFilter = function () {
        delete $rootScope.histo;

        $rootScope.histo = $.extend(true, {}, $rootScope.histoFull);
        $.each($rootScope.histo, function (id, value) {
            filtered = true;
            if ($rootScope.filtered.categories.length !== 0) {
                filtered = false;
                $.each($rootScope.filtered.categories, function () {
                    if (this["name"] == $rootScope.histo[id]["category"]) {
                        filtered = true;
                        return;
                    }
                });
            }
            if ($rootScope.filtered.members.length !== 0 && filtered === true) {
                filtered = false;
                $.each($rootScope.filtered.members, function () {
                    if ((this["name"] == $rootScope.histo[id]["subject"]["name"]) ||
                        (this["name"] == $rootScope.histo[id]["sender"]["name"])) {
                        filtered = true;
                        return;
                    }
                });
            }

            if (filtered === false)
                delete $rootScope.histo[id];
        });

    }

    /*
     ** INIT
     */
    function initHisto() {

        angular.forEach($rootScope.currentOrga.members, function(value, key) {
            $rootScope.filter.members.push(value);
        });
        $rootScope.filter.members[1] = $.extend(true, {}, $rootScope.filter.members[0]);
        $rootScope.filter.members[1].name = "unknown"
        $rootScope.$watch( 'filtered' , $rootScope.updateFilter, true);

        locale = "en-us";
        $rootScope.date = new Date();
        $rootScope.slider = {"end" : $rootScope.date.toLocaleString(locale, {month: "short"}) + " " + $rootScope.date.getDate() + ", " + $rootScope.date.getFullYear() + " 12:00 AM"};
        lastWeek = new Date($rootScope.date.getFullYear(), $rootScope.date.getMonth(), $rootScope.date.getDate() - 7);
        $rootScope.slider.begin = lastWeek.toLocaleString(locale, {month: "short"}) + " " + lastWeek.getDate() + ", " + lastWeek.getFullYear() + " 11:59 PM";

        $rootScope.getHisto(
            ($rootScope.slider.begin),
            ($rootScope.slider.end));
    };
    initHisto();

    return ctrl;

});
