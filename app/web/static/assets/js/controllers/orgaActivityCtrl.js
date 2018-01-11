
/*
** Histo Handler TOUT REFAIRE AU PROPRE C"EST MOCHE
*/

app.controller('OrgaActivityController', function($rootScope, $scope, $http, $timeout, $uibModal, $q,  $controller, $state, SweetAlert, ladda, $sessionStorage, $document) {
    ctrl = this;

    $scope.filter = {categories:	[{name: 'newMember'}, {name:'memberLeft'}, {name: 'newProposition'}, {name: 'newDonation'}, {name: 'newSpending'}],
			 members:	[],
			 jobs:		[],
			 projects:	[],
			 init:		false}

    $scope.filtered = {categories: [], members: [], jobs: [], projects: [], donations: [0, 1000]};


    $scope.getHisto = function (begin, end) {
        $http.post('/getOrgaHisto', {
            "orga_id": $state.params._id,
            "date": {"begin": begin, "end": end}
        }).then(
            function (data) {
		$(".orgaActivityLoading").addClass("displayNone");
                $(".timeline").removeClass("displayNone");
                if (data.data[0]) {
                    $scope.slider.first = data.data[0]["first"];
		    $scope.currentOrga.histo = data.data;
		    $scope.histo = $.extend({}, $scope.currentOrga.histo);
		    $scope.slider.begin = begin;
		    $scope.slider.end = end;
                    $scope.updateSliderFilter();
                    $scope.updateFilter();
                }
                else {
                    delete $scope.currentOrga.histo;
                    delete $scope.histo;

                }
            },
            function (error) {
                console.log(error);
            });
    };

    /*
     ** SLIDER
     */
    $scope.updateSliderFilter = function () {
        if (!$scope.slider || $("#dateSliderFilter.ui-dateRangeSlider").length <= 0)
            return;
        $("#dateSliderFilter").dateRangeSlider("bounds", new Date($scope.slider.first), $scope.date);
        $("#dateSliderFilter").dateRangeSlider("values", new Date($scope.slider.begin), new Date($scope.slider.end));
    }

    $rootScope.initSlider = function () {
	if ($scope.filter.init)
	    return;
	$("#dateSliderFilter").dateRangeSlider({defaultValues: {min: $scope.slider.begin, max: $scope.slider.end}, bounds:{min: $scope.slider.fist, max: $scope.slider.end} });
        $("#dateSliderFilter").on("userValuesChanged", $scope.updateHisto)
	$scope.updateSliderFilter()
	$scope.filter.init = true;
    }


    /*
     ** FILTERS
     */
    $scope.updateHisto = function (e, data) {
        $scope.slider.begin = data.values.min;
        $scope.slider.end = data.values.max
        locale = "en-us";

	$scope.getHisto(
            ($scope.slider.begin.toLocaleString(locale, {month: "short"}) + " " + $scope.slider.begin.getDate() + ", " + $scope.slider.begin.getFullYear() + " 00:00"),
            ($scope.slider.end.toLocaleString(locale, {month: "short"}) + " " + $scope.slider.end.getDate() + ", " + $scope.slider.end.getFullYear() + " 23:59"))
    }

    $scope.updateFilter = function () {
        delete $scope.histo;
        $scope.histo = $.extend({}, $scope.currentOrga.histo);
        $.each($scope.histo, function (id, data) {
            filtered = true;
	    // categories
            if ($scope.filtered.categories.length !== 0) {
                filtered = false;
                $.each($scope.filtered.categories, function () {
                    if (this["name"] == $scope.histo[id]["category"]) {
                        filtered = true;
                        return;
                    }
                });
            }
	    // members
            if ($scope.filtered.members.length !== 0 && filtered === true) {
                filtered = false;
                $.each($scope.filtered.members, function (memberID, member) {
		    if ((this["id"] == data["subject"]["id"]) ||
                        (this["id"] == data["sender"]["id"])) {
                        filtered = true;
                        return;
                    }
                });
            }
	    // Jobs
            if ($scope.filtered.jobs.length !== 0 && filtered === true) {
                filtered = false;
                $.each($scope.filtered.jobs, function (idJob, job) {
		    if ((data["sender"]["type"] == "user" && $scope.currentOrga.members[data["sender"]['addr']] &&
			 $scope.currentOrga.members[data["sender"]['addr']]['tag'] == job['name']) ||
			(data["subject"]["type"] == "user" && $scope.currentOrga.members[data["subject"]['addr']] &&
			 $scope.currentOrga.members[data["subject"]['addr']]['tag'] == job['name'])) {
			filtered = true;
			return;
		    }
		});
	    }
/*            // Donation
	    if (data.category == "newDonation" && filtered === true) {
                filtered = false;
		if ((data.amount <= $scope.filtered.donations[1]) &&
		    (data.amount >= $scope.filtered.donations[0]))
		{		    filtered = true;console.log("good");}
		else
		    console.log("not good");
	    }*/
	    if (filtered === false) {
                delete $scope.histo[id];
	    }
        });
    }

    /*
     ** INIT
     */
    function initHisto() {
        angular.forEach($scope.currentOrga.members, function(value, key) {
            $scope.filter.members.push({name: value.name, id: value._id });
        });
        angular.forEach($scope.currentOrga.projects, function(value, key) {
            $scope.filter.projects.push(value);
        });
        angular.forEach($scope.currentOrga.rights, function(value, key) {
            $scope.filter.jobs.push({name: key});
        });
        $scope.$watch( 'filtered', $scope.updateFilter, true);
        locale = "en-us";
        $scope.date = new Date();
        $scope.slider = {
          "end" : $scope.date.toLocaleString(locale, {month: "short"}) + " " + $scope.date.getDate() + ", " + $scope.date.getFullYear() + " 23:59",
          "begin": $scope.currentOrga.creation_date
        };
        // lastWeek = new Date($scope.date.getFullYear(), $scope.date.getMonth(), $scope.date.getDate() - 7);
        // $scope.slider.first = $scope.slider.begin = lastWeek.toLocaleString(locale, {month: "short"}) + " " + lastWeek.getDate() + ", " + lastWeek.getFullYear() + " 00:00";
        // console.log($scope.slider);
       $scope.getHisto(($scope.slider.begin),($scope.slider.end))
    };

    // $scope.$watch(['currentOrga.members', 'currentOrga.rights', 'currentOrga.projects'], initHisto, true)
    setTimeout(initHisto, 1000)
    return ctrl;

});

/*
** EXPORT CONTROLLER
*/

app.controller('ExportActivityController', function($scope, $http, $timeout, $rootScope, $controller, $state) {

    $scope.exportActivityModal = function() {
	$("#orgaExportData").table2excel({exclude: ".noExl",
					  name: "Worksheet Name",
					  filename: "ExportHisto_" + $scope.currentOrga.name });
    };

    return ctrl;
});
