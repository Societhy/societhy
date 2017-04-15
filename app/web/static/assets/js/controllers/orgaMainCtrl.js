/**
 * Main controller for organizations.
 * @class OrgaMainController
 */
 app.controller('OrgaMainController', function($rootScope, $scope, $http, $sessionStorage, $timeout, $state, $controller, $uibModal) {

   var ctrl = this;
   $scope.isMember = false;
   ctrl.wallet = $controller("WalletController");

   $scope.listProducts = [];
   $scope.currentProd = $scope.listProducts[0];


   ctrl.setProduct = function(product) {
    $scope.currentProd = product;
  }

    /**
     * Opens the new product modal.
     * @method addNewProduct
     */
     ctrl.addNewProduct = function() {
      var modalInstance = $uibModal.open({
       templateUrl: "static/assets/views/modals/newProduct.html",
       controller: 'ProductModalController',
       size: 'lg',
       resolve: {
        ctrl : function() {
         return ctrl;
       }
     }
   });

      modalInstance.result.then(function() {}, function () {
        ctrl.loadProducts();
      });
    };

    /**
     * Get the product list for the current organizations.
     * @method loadProducts
     */
     ctrl.loadProducts = function() {
      $http.get('/getOrgaProducts/'.concat($rootScope.currentOrga._id)).then(function(response) {
        console.log(response);
        if (response.status == 200) {
          $scope.listProducts = JSON.parse(response.data);
          $scope.currentProd = $scope.listProducts[0];
        }
      });
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
          "socketid": $rootScope.sessionId,
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
        "socketid": $rootScope.sessionId,
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
          "socketid": $rootScope.sessionId,
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
          "socketid": $rootScope.sessionId,
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
app.controller('OrgaHistoController', function($rootScope, $scope, $http, $timeout, $uibModal, $q, $rootScope, $controller, $state, SweetAlert, ladda, $sessionStorage, $document) {
  ctrl = this;


  $rootScope.filter = {categories:	[{name: 'newMember'}, {name:'memberLeave'}, {name: 'newProposition'}, {name: 'newDonation'}, {name: 'newSpending'}],
  members:	[{}],
  jobs:		[{name: "member"}, {name: "partener"}, {name: "admin"}],
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
     $("#dateSliderFilter").dateRangeSlider();
        $("#donationSliderFilter").rangeSlider({defaultValues:{min: 0, max: 100}}); // add check donation
        $("#dateSliderFilter").bind("userValuesChanged", $rootScope.updateHisto)
        $rootScope.updateSliderFilter()
        $rootScope.init = true;
      }

    /*
     ** FILTERS
     */
     $rootScope.updateHisto = function (e, data) {
      $rootScope.slider.begin = data.values.min;
      $rootScope.slider.end = data.values.max
      locale = "en-us";

      $rootScope.getHisto(
        ($rootScope.slider.begin.toLocaleString(locale, {month: "short"}) + " " + $rootScope.slider.begin.getDate() + ", " + $rootScope.slider.begin.getFullYear() + " 12:00 PM"),
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

/*
** EXPORT CONTROLLER
*/

app.controller('ExportActivityController', function($scope, $http, $timeout, $rootScope, $controller, $state) {


  $rootScope.exportActivityModal = function() {
   $("#orgaExportData").table2excel({exclude: ".noExl",
     name: "Worksheet Name",
     filename: "SomeFile"});	
 };

 return ctrl;
});
