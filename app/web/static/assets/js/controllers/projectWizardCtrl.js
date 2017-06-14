app.controller('ProjectWizardCtrl',
  function($scope, ngNotify) {

    $scope.currentStep = 1;
    $scope.proj = {};

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
