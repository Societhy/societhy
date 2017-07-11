
/*
** Histo Handler TOUT REFAIRE AU PROPRE C"EST MOCHE
*/

app.controller('OrgaActivityController', function($rootScope, $scope, $http, $timeout, $uibModal, $q, $rootScope, $controller, $state, SweetAlert, ladda, $sessionStorage, $document) {
    ctrl = this;

    $rootScope.filter = {categories:	[{name: 'newMember'}, {name:'memberLeft'}, {name: 'newProposition'}, {name: 'newDonation'}, {name: 'newSpending'}],
			 members:	[],
			 jobs:		[],
			 projects:	[],
			 init:		false}
			 
    $rootScope.filtered = {categories: [], members: [], jobs: [], projects: [], donations: [0, 1000]};


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
		    $rootScope.currentOrga.histo = data.data;
		    $rootScope.histo = $.extend({}, $rootScope.currentOrga.histo);
		    $rootScope.slider.begin = begin;
		    $rootScope.slider.end = end;
                    $rootScope.updateSliderFilter();
                    $rootScope.updateFilter();
                }
                else {
                    delete $rootScope.currentOrga.histo;
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
	if ($rootScope.filter.init)
	    return;
	$("#dateSliderFilter").dateRangeSlider({defaultValues: {min: $rootScope.slider.begin, max: $rootScope.slider.end}, bounds:{min: $rootScope.slider.fist, max: $rootScope.slider.end} });
        $("#dateSliderFilter").on("userValuesChanged", $rootScope.updateHisto)
	$rootScope.updateSliderFilter()
	$rootScope.filter.init = true;
/*	$("#donationSlider input").ionRangeSlider({
	    type: "double",
	    grid: true,
	    min: 0,
	    max: 1000,
	    from: 200,
	    to: 800,
	    prefix: "Eth ",
	    onFinish: function (data) {
		$rootScope.filtered.donations = {min: data.from, max: data.to}
		$rootScope.updateFilter();
	    },
	});*/
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
        $rootScope.histo = $.extend({}, $rootScope.currentOrga.histo);
        $.each($rootScope.histo, function (id, data) {
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
                $.each($rootScope.filtered.members, function (memberID, member) {
		    if ((this["id"] == data["subject"]["id"]) ||
                        (this["id"] == data["sender"]["id"])) {
                        filtered = true;
                        return;
                    }
                });
            }
	    // Jobs
            if ($rootScope.filtered.jobs.length !== 0 && filtered === true) {
                filtered = false;
                $.each($rootScope.filtered.jobs, function (idJob, job) {
		    if ((data["sender"]["type"] == "user" && $rootScope.currentOrga.members[data["sender"]['addr']] &&
			 $rootScope.currentOrga.members[data["sender"]['addr']]['tag'] == job['name']) ||
			(data["subject"]["type"] == "user" && $rootScope.currentOrga.members[data["subject"]['addr']] &&
			 $rootScope.currentOrga.members[data["subject"]['addr']]['tag'] == job['name'])) {
			filtered = true;
			return;
		    }
		});
	    }
/*            // Donation
	    if (data.category == "newDonation" && filtered === true) {
                filtered = false;
		if ((data.amount <= $rootScope.filtered.donations[1]) &&
		    (data.amount >= $rootScope.filtered.donations[0]))
		{		    filtered = true;console.log("good");}
		else
		    console.log("not good");
	    }*/
	    if (filtered === false) {
                delete $rootScope.histo[id];
	    }
        });
    }

    /*
     ** INIT
     */
    function initHisto() {
        angular.forEach($rootScope.currentOrga.members, function(value, key) {
            $rootScope.filter.members.push({name: value.name, id: value._id });
        });
        angular.forEach($rootScope.currentOrga.projects, function(value, key) {
            $rootScope.filter.projects.push(value);
        });
        angular.forEach($rootScope.currentOrga.rights, function(value, key) {
            $rootScope.filter.jobs.push({name: key});
        });
        $rootScope.$watch( 'filtered', $rootScope.updateFilter, true);
        locale = "en-us";
        $rootScope.date = new Date();
        $rootScope.slider = {"end" : $rootScope.date.toLocaleString(locale, {month: "short"}) + " " + $rootScope.date.getDate() + ", " + $rootScope.date.getFullYear() + " 23:59"};
        lastWeek = new Date($rootScope.date.getFullYear(), $rootScope.date.getMonth(), $rootScope.date.getDate() - 7);
        $rootScope.slider.first = $rootScope.slider.begin = lastWeek.toLocaleString(locale, {month: "short"}) + " " + lastWeek.getDate() + ", " + lastWeek.getFullYear() + " 00:00";
        $rootScope.getHisto(($rootScope.slider.begin),($rootScope.slider.end))
    };

    $rootScope.$watch(['currentOrga.members', 'currentOrga.rights', 'currentOrga.projects'], initHisto, true)
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
