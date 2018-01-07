app.controller('ProjectWizardCtrl',
  function($scope, ngNotify, $rootScope, $http, $state) {

    $scope.currentStep = 1;
    $scope.proj = {
      invited_users: {},
      members: {},
      facebook_link: null,
      twitter_link: null,
      levels: [{
        name: "Default name",
        value: 0,
        prevTot: 0,
        desc: ""
      }]
    };

    $scope.addInvitedUser = function() {
      if (!$scope.proj.invited_users)
        $scope.proj.invited_users = {};

      $scope.proj.invited_users[$scope.selected_user.originalObject._id] = $scope.selected_user.originalObject;
      console.log($scope.proj.invited_users);
    }

    $scope.addNewLevel = function() {
      if ($scope.proj.levels.length < 9) {
        var newItemNo = $scope.proj.levels.length + 1;
        $scope.proj.levels.push({
          'name': 'Default name' + newItemNo,
          value: 10,
          prevTot: 0,
          'desc': ''
        });
      }
    };

    $scope.removeLevel = function(ind) {
      $scope.proj.levels.splice(ind, 1);
    };

    var getLevelsValues = function() {
      var tab = $scope.proj.levels;
      var total = 0;
      tab.forEach(function(val, ind) {
        total += val.value;
        if (ind != 0) {
          tab[ind].value = tab[ind - 1].value + val.value;
          tab[ind].prevTot = tab[ind - 1].prevTot + tab[ind - 1].value;
        }
      });
      $scope.proj.levels = tab;
      $scope.proj.campaign.amount_to_raise = total;
    }

    $scope.form = {
      next: function(form) {
        $scope.toTheTop();

        if (form.$valid) {
          form.$setPristine();
          nextStep();
        } else {
          console.log(form);
          var field = null,
            firstError = null;
          for (field in form) {
            if (field[0] != '$') {
              if (firstError === null && !form[field].$valid) {
                firstError = form[field].$name;
              }

              if (form[field].$pristine) {
                form[field].$dirty = true;
              }
            }
          }
          console.log(firstError)
          angular.element('.ng-invalid[name=' + firstError + ']').focus();
          errorMessage('please complete the form in this step before proceeding');
        }
      },

      prev: function(form) {
        $scope.toTheTop();
        prevStep();
      },

      goTo: function(form, i) {
        if (parseInt($scope.currentStep) > parseInt(i)) {
          $scope.toTheTop();
          goToStep(i);

        } else {
          if (form.$valid) {
            $scope.toTheTop();
            goToStep(i);

          } else
            errorMessage('Please complete the form in this step before proceeding');
        }
      },

      submit: function(form) {
        if ($scope.doVerifications()) {
          $scope.completeBlockchainAction(
            function(password) {
              getLevelsValues();
              $rootScope.toogleWait("Creating project")
              $http.post('/createProject', {
                "socketid": $rootScope.sessionId,
                "owner_id": $state.params.owner_id,
                "newProject": $scope.proj,
                "password": password
              }).then(function(data) {}, function(error) {
                $rootScope.toogleError(error);
              });
            },
            function(data) {
              $scope.currentOrga.projects = $rootScope.currentOrga.projects = data.data.orga;
              let proj = {
                name: data.data.project.name,
                _id: data.data.project._id
              }
              $state.go("app.project", proj);
            })
        }
      },

      reset: function() {}
    };


    var nextStep = function() {
      $scope.currentStep++;
    };
    var prevStep = function() {
      $scope.currentStep--;
    };
    var goToStep = function(i) {
      $scope.currentStep = i;
    };

    var errorMessage = function(text) {

      ngNotify.set(text, {
        theme: 'pure',
        position: 'top',
        type: 'error',
        button: 'true',
        sticky: false,
        duration: 3000
      });
    };
  });
