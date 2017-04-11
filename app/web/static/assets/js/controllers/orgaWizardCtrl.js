'use strict';
/** 
  * controller for Wizard Form example
  */


  app.controller('OrgaWizardCtrl', 
    function ($scope, $http, $timeout, ngNotify, FileUploader, $sessionStorage, $rootScope, $state) {
        $scope.currentStep = 1;

        $scope.governance_description = {
            "dao": {
                "pros": ["test1", "test2", "test3"],
                "cons": ["test1", "test2", "test3"],
                "desc": "This is a standard description"
            },
            "ngo": {
                "pros": ["test1", "test2", "test3"],
                "cons": ["test1", "test2", "test3"],
                "desc": "This is a standard description"
            },
            "public_company": {
                "pros": ["test1", "test2", "test3"],
                "cons": ["test1", "test2", "test3"],
                "desc": "This is a standard description"
            },
            "entreprise": {
                "pros": ["test1", "test2", "test3"],
                "cons": ["test1", "test2", "test3"],
                "desc": "This is a standard description"
            }
        }

    // IMAGE UPLOAD
    var uploaderImages = $scope.uploaderImages = new FileUploader({
        url: '/addOrgaProfilePicture',
        alias: 'pic',
        headers: {
            Authentification: $sessionStorage.SociethyToken
        }
    });

    uploaderImages.filters.push({
        name: 'imageFilter',
        fn: function (item, options) {
            var type = '|' + item.type.slice(item.type.lastIndexOf('/') + 1) + '|';
            return '|jpg|png|jpeg|bmp|gif|'.indexOf(type) !== -1;
        }
    });

    uploaderImages.onErrorItem = function (fileItem, response, status, headers) {
        console.info('onErrorItem', fileItem, response, status, headers);
    };

    //DOCUMENT UPLOAD
    var uploaderDocs = $scope.uploaderDocs = new FileUploader({
        url:"/addOrgaDocuments",
        alias:"doc",
        headers: {
            Authentification: $sessionStorage.SociethyToken
        },
    });

    uploaderDocs.onBeforeUploadItem = function (item) {
        console.log(uploaderDocs.queue.length);
        item.formData.push({"name": item.file.name});
        item.formData.push({"type": item.file.type});        
        console.info('onBeforeUploadItem', item);
    };


    // MEMBER MANAGEMENT
    $scope.invited_users = [];

    $scope.addInvitedUser = function () {
        $scope.invited_users.push($scope.selected_user.originalObject);
        console.log($scope.invited_users);
    };


    $scope.removeRow = function (name) {
        var index = -1;
        var comArr = eval($scope.users);
        for (var i = 0; i < comArr.length; i++) {
            if (comArr[i].name === name) {
                index = i;
                break;
            }
        }
        if (index === -1) {
            alert("Something gone wrong");
        }
        $scope.users.splice(index, 1);
    };

    // PAGE MANAGEMENT
    $scope.form = {

        next: function (form) {
            console.log(uploaderDocs);
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
                errorMessage('please complete the form in this step before proceeding');
            }
        },

        submit: function (form) {
            console.log(uploaderDocs);
            if ($scope.doVerifications()) {
                $scope.completeBlockchainAction(
                    function(password) {
                        $rootScope.toogleWait("Processing organization creation...");
                        $http.post('/createOrga', {
                            "password": password,
                            "newOrga" : {
                                "name": form.name.$$rawModelValue,
                                "description" : form.description.$$rawModelValue,
                                "type" : form.type.$$rawModelValue,
                                "fbUrl": form.fbUrl.$$rawModelValue,
                                "twitterUrl" : form.twitterUrl.$$rawModelValue,
                                "invited_users" : $scope.users
                            }}).then(function(response) {}, function(error) {$rootScope.toogleError(error.data);});
                    },  function(data) {
                        console.log(uploaderDocs.queue.length);
                        if (uploaderImages.queue.length != 0)
                        {
                            uploaderImages.queue[0].formData.push({"orga_id":data.data._id, "type":uploaderImages.queue[0].file.type});
                        }
                        uploaderImages.uploadAll();
                        for (var i = 0; i != uploaderDocs.queue.length; i++)
                        {
                            uploaderDocs.queue[i].formData.push({"orga_id" : data.data._id})
                        } 
                        uploaderDocs.uploadAll();
                        $state.go("app.organization", data.data);
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
