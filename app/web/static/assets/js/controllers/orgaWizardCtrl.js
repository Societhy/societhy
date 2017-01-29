'use strict';
/** 
  * controller for Wizard Form example
*/


app.controller('OrgaWizardCtrl', 
function ($scope, ngNotify, FileUploader, $sessionStorage, $rootScope) {
    $scope.currentStep = 1;
    console.log("loaded");


    // IMAGE UPLOAD
     var uploaderImages = $scope.uploaderImages = new FileUploader({
        url: 'upload.php',
        headers: {
            Authentification: $sessionStorage.SociethyToken
        },
    });
    console.log(uploaderImages);
    uploaderImages.filters.push({
        name: 'imageFilter',
        fn: function (item/*{File|FileLikeObject}*/, options) {
            var type = '|' + item.type.slice(item.type.lastIndexOf('/') + 1) + '|';
            return '|jpg|png|jpeg|bmp|gif|'.indexOf(type) !== -1;
        }
    });

    // CALLBACKS

    uploaderImages.onWhenAddingFileFailed = function (item/*{File|FileLikeObject}*/, filter, options) {
        console.info('onWhenAddingFileFailed', item, filter, options);
    };
    uploaderImages.onAfterAddingFile = function (fileItem) {
        console.info('onAfterAddingFile', fileItem);
    };
    uploaderImages.onAfterAddingAll = function (addedFileItems) {
        console.info('onAfterAddingAll', addedFileItems);
    };
    uploaderImages.onBeforeUploadItem = function (item) {
        console.info('onBeforeUploadItem', item);
    };
    uploaderImages.onProgressItem = function (fileItem, progress) {
        console.info('onProgressItem', fileItem, progress);
    };
    uploaderImages.onProgressAll = function (progress) {
        console.info('onProgressAll', progress);
    };
    uploaderImages.onSuccessItem = function (fileItem, response, status, headers) {
        console.info('onSuccessItem', fileItem, response, status, headers);
    };
    uploaderImages.onErrorItem = function (fileItem, response, status, headers) {
        console.info('onErrorItem', fileItem, response, status, headers);
    };
    uploaderImages.onCancelItem = function (fileItem, response, status, headers) {
        console.info('onCancelItem', fileItem, response, status, headers);
    };
    uploaderImages.onCompleteItem = function (fileItem, response, status, headers) {
        console.info('onCompleteItem', fileItem, response, status, headers);
    };
    uploaderImages.onCompleteAll = function () {
        console.info('onCompleteAll');
    };

    console.info('uploader', uploaderImages);


    // PAGE MANAGEMENT
    $scope.form = {

        next: function (form) {

            $scope.toTheTop();

            if (form.$valid || !form.$valid) {
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
                errorMessage();
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
                    errorMessage();
            }
        },
        submit: function (form) {
            console.log(form)

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
    var errorMessage = function (i) {

        ngNotify.set('please complete the form in this step before proceeding', {
            theme: 'pure',
            position: 'top',
            type: 'error',
            button: 'true',
            sticky: 'false',
        });
    };
});
