app.controller('ProjectWizardCtrl',
  function($scope, ngNotify, $rootScope, $http, $state) {

    $scope.currentStep = 1;
    $scope.proj = {invited_users: {}};

    $scope.addInvitedUser = function() {
      if (!$scope.proj.invited_users)
          $scope.proj.invited_users = {};

      $scope.proj.invited_users[$scope.selected_user.originalObject._id] = $scope.selected_user.originalObject;
      console.log($scope.proj.invited_users);
    }

    $scope.form = {
        next: function (form) {
            $scope.toTheTop();

            if (form.$valid) {
                form.$setPristine();
                nextStep();
            } else {
                console.log(form);
                var field = null, firstError = null;
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

        prev: function (form) {
            $scope.toTheTop();
            prevStep();
        },

        goTo: function (form, i) {
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

        submit: function (form) {
          if (!$rootScope.currentOrga) {
            $rootScope.toogleError("You need to create a project from an existing organization");
          }

          else if ($scope.doVerifications()) {
           $scope.completeBlockchainAction(
            function(password) {
             $rootScope.toogleWait("Creating project")
             $http.post('/createProjectFromOrga', {
              "socketid": $rootScope.sessionId,
              "orga_id": $rootScope.currentOrga._id,
              "newProject": $scope.proj,
              "password": password
            }).then(function(data) {}, function(error) { $rootScope.toogleError(error);});
           }, function(data) {
             $scope.currentOrga.projects = $rootScope.currentOrga.projects = data.data.orga;
             let proj = {name: data.data.project.name, _id: data.data.project._id}
             $state.go("app.project", proj);
           })
         }
        },

        reset: function () {
        }
    };


    var nextStep = function () {
        $scope.currentStep++;
    };
    var prevStep = function () {
        $scope.currentStep--;
    };
    var goToStep = function (i) {
        $scope.currentStep = i;
    };

    var errorMessage = function (text) {

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
