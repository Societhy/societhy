app.controller('OrgaMainController', function($rootScope, $scope, $http, $sessionStorage, $state) {
	var ctrl = this;
	$scope.isMember = false;

    /*
    ** Notification default Value
    */
    
/*
      $rootScope.itemArray = [
      {id: 1, name: 'first'},
	{id: 2, name: 'second'},
	{id: 3, name: 'third'},
	{id: 4, name: 'fourth'},
	{id: 5, name: 'fifth'},
    ];
    $rootScope.availableColors = ['Red','Green','Blue','Yellow','Magenta','Maroon','Umbra','Turquoise'];
    
    $rootScope.toto = 42;
    ctrl.toto = 43;
    $rootScope.selected = { value: $scope.itemArray[0] };
/*      ctrl.init = function() {
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
	if ($("#filterMember").val() != "all")
	{
	    $.each($rootScope.histo, function (id,value) {
		if (($("#filterMember").val() != $rootScope.histo[id]["subject"]["name"]) &&
		    ($("#filterMember").val() != $rootScope.histo[id]["sender"]["name"]))
		    delete $rootScope.histo[id];
	    });
	}
    }

    ctrl.getHisto = function(begin, end) {
	$http.post('/getOrgaHisto', {
	    "orga_id": $state.params._id,
	    "date": {"begin": begin, "end": end}
	}).then(
	    function(data) {		
		$(".orgaActivityLoading").addClass("displayNone");
		$(".timeline").removeClass("displayNone");
		if (data.data[0])
		{
		    $rootScope.sliderFilter = [];
		    if (!$rootScope.sliderFilter.first)
			$rootScope.sliderFilter.first = data.data[0]["first"];
		    $rootScope.sliderFilter.valBegin = begin;
		    $rootScope.sliderFilter.valEnd = end;
		    $rootScope.histoFull = data.data;
		    $rootScope.histo = data.data;
		    updateSliderFilter();
		    $rootScope.updateFilter();
		}
		else
		{
		    delete $rootScope.histoFull;
		    delete $rootScope.histo;

		}
	    },
	    function(error) {
		console.log(error);
	    });

    };
    
    function updateSliderFilter() {
	if (!$rootScope.sliderFilter || $("#sliderFilter.ui-dateRangeSlider").length <= 0)
	    return;
	console.log(new Date($rootScope.sliderFilter.first));
	$("#sliderFilter").dateRangeSlider("bounds",new Date($rootScope.sliderFilter.first), $rootScope.date);
	$("#sliderFilter").dateRangeSlider("values",new Date($rootScope.sliderFilter.valBegin), new Date($rootScope.sliderFilter.valEnd));
    }

    $rootScope.initSliders = function() {
	$("#sliderFilter").dateRangeSlider();
	var slider = $('.range-slider');
	range = $('.range-slider__range');
	value = $('.range-slider__value');
	slider.each(function() {
	    value.each(function() {
		var value = $(this).prev().attr('value');
		$(this).html(value);
	    });
	    range.on('input', function() {
		$(this).next(value).html(this.value);
	    });
	});
	$("#sliderFilter").bind("userValuesChanged", $rootScope.updateHisto);
	updateSliderFilter();
    }

    $rootScope.slider = {
	value: 10
    };

    
    $rootScope.updateHisto = function(e, data) {
	begin = data.values.min;
	end = data.values.max
	locale = "en-us";
        ctrl.getHisto(
	    (begin.toLocaleString(locale, { month: "short" }) + " " + begin.getDate() + ", "+  begin.getFullYear() +  " 12:00 AM"),
	    (end.toLocaleString(locale, { month: "short" }) + " " + end.getDate() + ", "+  end.getFullYear() +  " 11:59 PM"))
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

    function initHisto () {
	$rootScope.date = new Date();
	begin = new Date($rootScope.date.getFullYear(), $rootScope.date.getMonth(), $rootScope.date.getDate() - 7);
	locale = "en-us";
	ctrl.getHisto(
	    (begin.toLocaleString(locale, { month: "short" }) + " " + begin.getDate() + ", "+  begin.getFullYear() +  " 12:00 AM"),
	    ($rootScope.date.toLocaleString(locale, { month: "short" }) + " " + $rootScope.date.getDate() + ", "+  $rootScope.date.getFullYear() +  " 11:59 PM"));
    };
    
    if (!$rootScope.currentOrga) {
	$http.post('/getOrganization', {
	    "id": $state.params._id
	}).then(function(response) {
	    $scope.currentOrga = $rootScope.currentOrga = response.data;
	    console.log("current orga", $scope.currentOrga);
	    initHisto();
	    if ($rootScope.user)
		$scope.isMember = $rootScope.user.account in $scope.currentOrga.members;
	}, function(error) {
	    $state.go('app.dashboard');
	    $rootScope.toogleError("Organization does not exist");			
	})
    }
    return ctrl;
});
