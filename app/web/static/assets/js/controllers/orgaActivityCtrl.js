
/*
** Histo Handler
*/
app.controller('OrgaActivityController', function($rootScope, $scope, $http, $timeout, $uibModal, $q, $rootScope, $controller, $state, SweetAlert, ladda, $sessionStorage, $document) {
    ctrl = this;


    $rootScope.filter = {categories:	[{name: 'newMember'}, {name:'memberLeave'}, {name: 'newProposition'}, {name: 'newDonation'}, {name: 'newSpending'}],
			 members:	[{}],
			 jobs:		[{name: "member"}, {name: "partner"}, {name: "admin"}],
			 projects:	[{}],
			 donations:	[{}]};
    
    $rootScope.filtered = {categories: [], members: [], jobs: [], projects: [], donations: []};

    $rootScope.getHisto = function (begin, end) {
        $http.post('/getOrgaHisto', {
            "orga_id": $state.params._id,
            "date": {"begin": begin, "end": end}
        }).then(
            function (data) {
		$(".orgaActivityLoading").addClass("displayNone");
                $(".timeline").removeClass("displayNone");
                if (data.data[0]) {
                    $rootScope.slider.first = data.data[0]["first"];
                    $rootScope.histoFull = $rootScope.histo = data.data;
		    $rootScope.slider.begin = begin;
		    $rootScope.slider.end = end;
                    $rootScope.updateSliderFilter();
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
    $rootScope.updateSliderFilter = function () {
        if (!$rootScope.slider || $("#dateSliderFilter.ui-dateRangeSlider").length <= 0)
            return;
        $("#dateSliderFilter").dateRangeSlider("bounds", new Date($rootScope.slider.first), $rootScope.date);
        $("#dateSliderFilter").dateRangeSlider("values", new Date($rootScope.slider.begin), new Date($rootScope.slider.end));
    }

    $rootScope.initSlider = function () {
	if ($rootScope.init)
	    return;
	$("#dateSliderFilter").dateRangeSlider({defaultValues: {min: $rootScope.slider.begin, max: $rootScope.slider.end}, bounds:{min: $rootScope.slider.fist, max: $rootScope.slider.end} });
        $("#donationSliderFilter").rangeSlider({defaultValues:{min: 0, max: 100}}); // add check donation
        $("#dateSliderFilter").bind("userValuesChanged", $rootScope.updateHisto)
	$rootScope.updateSliderFilter()
	$rootScope.init = true;
	console.log($rootScope);
    }

    
    /*
     ** FILTERS
     */
    $rootScope.updateHisto = function (e, data) {
        $rootScope.slider.begin = data.values.min;
        $rootScope.slider.end = data.values.max
        locale = "en-us";

	$rootScope.getHisto(
            ($rootScope.slider.begin.toLocaleString(locale, {month: "short"}) + " " + $rootScope.slider.begin.getDate() + ", " + $rootScope.slider.begin.getFullYear() + " 00:00"),
            ($rootScope.slider.end.toLocaleString(locale, {month: "short"}) + " " + $rootScope.slider.end.getDate() + ", " + $rootScope.slider.end.getFullYear() + " 23:59"))
    }

    $rootScope.updateFilter = function () {
        delete $rootScope.histo;

        $rootScope.histo = $.extend(true, {}, $rootScope.histoFull);
        $.each($rootScope.histo, function (id, value) {
            filtered = true;
	    // categories
            if ($rootScope.filtered.categories.length !== 0) {
                filtered = false;
                $.each($rootScope.filtered.categories, function () {
                    if (this["name"] == $rootScope.histo[id]["category"]) {
                        filtered = true;
                        return;
                    }
                });
            }
	    // members
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
	    // Jobs
            if ($rootScope.filtered.jobs.length !== 0 && filtered === true) {
                filtered = false;
                $.each($rootScope.filtered.jobs, function (idJ, job) {
		    if ((value["sender"]["type"] == "user" && $rootScope.currentOrga.members[value["sender"]['account']]['tag'] == job['name']) ||
			(value["subject"]["type"] == "user" && $rootScope.currentOrga.members[value["subject"]['account']]['tag'] == job['name'])) {
			filtered = true;
			return;
		    }
		});
	    }
		/*
		** ADD FILTER
	    */
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
        angular.forEach($rootScope.currentOrga.projects, function(value, key) {
            $rootScope.filter.projects.push(value);
        });
        $rootScope.$watch( 'filtered' , $rootScope.updateFilter, true);
        locale = "en-us";
        $rootScope.date = new Date();
        $rootScope.slider = {"end" : $rootScope.date.toLocaleString(locale, {month: "short"}) + " " + $rootScope.date.getDate() + ", " + $rootScope.date.getFullYear() + " 23:59"};
        lastWeek = new Date($rootScope.date.getFullYear(), $rootScope.date.getMonth(), $rootScope.date.getDate() - 7);
        $rootScope.slider.first = $rootScope.slider.begin = lastWeek.toLocaleString(locale, {month: "short"}) + " " + lastWeek.getDate() + ", " + lastWeek.getFullYear() + " 00:00";

        $rootScope.getHisto(
            ($rootScope.slider.begin),
            ($rootScope.slider.end));
    };
    initHisto();
    return ctrl;

});

/*
** EXPORT CONTROLLER
*/

app.controller('ExportActivityController', function($scope, $http, $timeout, $rootScope, $controller, $state) {
    
    $rootScope.exportActivityModal = function() {
	$("#orgaExportData").table2excel({exclude: ".noExl",
					  name: "Worksheet Name",
					  filename: "ExportHisto_" + $rootScope.currentOrga.name });	
    };

    return ctrl;
});
