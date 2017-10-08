app.controller('ProjectMainController', function($rootScope, $scope, $http, $sessionStorage, $state, $timeout, $controller) {

  var ctrl = this;
  ctrl.wallet = $controller("WalletController");

  onLoad = function() {
    $http.post('/getProject', {'id': $state.params._id}).then(function(response) {
      $rootScope.currentProject = $scope.project = response.data.project;
      $scope.currentRights = response.data.rights;
      if ($rootScope.user) {
        $scope.isMember = $rootScope.user._id in $scope.project.members;
      } else {
        $scope.isMember = false;
      }
      // desc = $scope.project.description.replace(/(\r\n|\n|\r)/g,"<br />");
      // $scope.project.description = desc;
      console.log("RIGHTS AND PROJECT", response.data.rights, response.data.project);
    }, function(error) {
      $state.go('app.discoverprojects');
      $rootScope.toogleError("Project does not exist");
    });
  };

  ctrl.joinProject = function(tag) {
    if ($scope.doVerifications()) {
      $scope.completeBlockchainAction(
        function(password) {
          $rootScope.toogleWait("Joining...");
          $http.post('/joinProject', {
            "socketid": $rootScope.sessionId,
            "tag": "member",
            "proj_id": $scope.project._id,
            "password": password
          }).then(function(data) {}, function(error) {
            $rootScope.toogleError(error);
          });
        },
        function(data) {
          $scope.project.members = data.data.project.members;
          // $rootScope.user.projects.push(data.data.project);
          $rootScope.currentProject.members = $scope.project.members = data.data.project.members;
          $rootScope.currentRights = $scope.currentRights = data.data.rights;
          $rootScope.user.projects.push($rootScope.currentProject);
          $scope.isMember = true;
        });
    }
  }

  ctrl.leaveProject = function() {

    if ($scope.doVerifications()) {
      $scope.completeBlockchainAction(
        function(password) {
          $rootScope.toogleWait("Leaving...");
          $http.post('/leaveProject', {
            "socketid": $rootScope.sessionId,
            "proj_id": $scope.project._id,
            "password": password
          }).then(function(data) {}, function(error) {
            $rootScope.toogleError(error);
          });
        },
        function(data) {
          $scope.project.members = data.data.project.members;
          $scope.isMember = false;
        });
    }
  }

  ctrl.donateToProject = function() {
    donationAmount = $("#donationAmount").val();
    if (donationAmount > 0 && $scope.doVerifications()) {
      $scope.completeBlockchainAction(
        function(password) {
          $rootScope.toogleWait("Sending donation")
          $http.post('/donateToProject', {
            "socketid": $rootScope.sessionId,
            "proj_id": $scope.project._id,
            "donation": {
              "amount": donationAmount
            },
            "password": password
          }).then(function(data) {}, function(error) {
            $rootScope.toogleError(error);
          });
        },
        function(data) {
          $scope.project.balance = data.data;
          ctrl.wallet.refreshAllBalances();
          ctrl.refreshProject();
        })
    } else {
      $rootScope.toogleError("Donation amount must be more than to 0...")
    }
  }

  ctrl.refreshProject = function() {
    if ($rootScope.currentProject) {
      $http.get('/refreshProject/'.concat($rootScope.currentProject._id))
      .then(function(data) {
         $rootScope.currentProject = $scope.project = data.data;
      });
    }
  }
  ctrl.exportActivityModal = function() {
  $("#projectExportData").table2excel({exclude: ".noExl",
          name: "Worksheet Name",
          filename: "ExportProject_" + $scope.currentProject.name });
  };

  $timeout(function() {
    $(".donate-button").click(ctrl.donateToProject);
  }, 500);

  onLoad();
  return ctrl;
});
