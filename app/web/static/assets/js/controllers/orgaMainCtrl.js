app.controller('OrgaMainController', function($rootScope, $http, $sessionStorage, $state) {

	var ctrl = this;

	ctrl.init = function() {
		console.log($state.params);
		$http.post('/getOrganization', {
			// "name": $state.params.orga_id
			"name": $state.params.orga_name
		}).then(
		function(data) {
			$rootScope.currentOrga = data.data;
			console.log(data);
		    $rootScope.date = new Date();
		    begin = new Date();
		    begin.setDate(begin.getDate() - 7);
		    ctrl.getHisto(begin,$rootScope.date);
		},
		function(error) {
			$rootScope.currentOrga = {"name": "one", "id": 1, "picture": "static/assets/images/orga_default.jpg"};
			console.log(error);
		});
	}

	ctrl.joinOrga = function() {
		password = "test";
		if ($rootScope.user.local_account == true) {
			console.log("ask for password")
		}
		else {
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

    ctrl.init();
    return ctrl;
});
