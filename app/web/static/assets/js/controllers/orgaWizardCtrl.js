'use strict';
/** 
  * controller for Wizard Form example
  */


  app.controller('OrgaWizardCtrl', 
    function ($scope, $http, $timeout, $uibModal, ngNotify, FileUploader, $sessionStorage, $rootScope, $state) {

        $scope.currentStep = 1;
        $rootScope.orga_form = $scope.orga_form;

        var ctrl = this;

        // GOVERNANCE TAB
        $scope.governance_types = {
            "dao": {
                "pros": ["test1", "test2", "test3"],
                "cons": ["test1", "test2", "test3"],
                "desc": "This is a standard description",
                "tags": ["owner", "admin", "member", "guest"],
                "rights": { 
                    "owner": {
                        "join": false,
                        "leave": true,
                        "donate": true,
                        "create_proposal": true,
                        "vote_proposal": true,
                        "recruit": true,
                        "remove_members": true,
                        "buy_token": true,
                    },
                    "admin": {},
                    "guest": {},
                    "member": {
                        "join": false,
                        "leave": true,
                        "donate": true,
                        "create_proposal": false,
                        "vote_proposal": true,
                        "recruit": false,
                        "remove_members": false,
                        "buy_token": true,
                    },
                    "default": {
                        "join": true,
                        "leave": false,
                        "donate": true,
                        "create_proposal": false,
                        "vote_proposal": false,
                        "recruit": false,
                        "remove_members": false,
                        "buy_token": false,
                    }
                }
            },
            "ngo": {
                "pros": ["test1", "test2", "test3"],
                "cons": ["test1", "test2", "test3"],
                "desc": "This is a standard description",
                "tags": ["owner", "admin", "member", "guest"],
                "rights": { 
                    "owner": {
                        "join": false,
                        "leave": true,
                        "donate": true,
                        "create_proposal": true,
                        "vote_proposal": true,
                        "recruit": true,
                        "remove_members": true,
                        "buy_token": true,
                    },
                    "admin": {},
                    "partner": {},
                    "member": {
                        "join": false,
                        "leave": true,
                        "donate": true,
                        "create_proposal": false,
                        "vote_proposal": true,
                        "recruit": false,
                        "remove_members": false,
                        "buy_token": true,
                    },
                    "default": {
                        "join": true,
                        "leave": false,
                        "donate": true,
                        "create_proposal": false,
                        "vote_proposal": false,
                        "recruit": false,
                        "remove_members": false,
                        "buy_token": false,
                    }
                }
            },
            "public_company": {
                "pros": ["test1", "test2", "test3"],
                "cons": ["test1", "test2", "test3"],
                "desc": "This is a standard description",
                "tags": ["owner", "admin", "member", "guest"],
                "rights": { 
                    "owner": {
                        "join": false,
                        "leave": true,
                        "donate": true,
                        "create_proposal": true,
                        "vote_proposal": true,
                        "recruit": true,
                        "remove_members": true,
                        "buy_token": true,
                    },
                    "admin": {},
                    "partner": {},
                    "member": {
                        "join": false,
                        "leave": true,
                        "donate": true,
                        "create_proposal": false,
                        "vote_proposal": true,
                        "recruit": false,
                        "remove_members": false,
                        "buy_token": true,
                    },
                    "default": {
                        "join": true,
                        "leave": false,
                        "donate": true,
                        "create_proposal": false,
                        "vote_proposal": false,
                        "recruit": false,
                        "remove_members": false,
                        "buy_token": false,
                    }
                }
            },
            "entreprise": {
                "pros": ["test1", "test2", "test3"],
                "cons": ["test1", "test2", "test3"],
                "desc": "This is a standard description",
                "tags": ["owner", "admin", "member", "guest"],
                "rights": { 
                    "owner": {
                        "join": false,
                        "leave": true,
                        "donate": true,
                        "create_proposal": true,
                        "vote_proposal": true,
                        "recruit": true,
                        "remove_members": true,
                        "buy_token": true,
                    },
                    "admin": {},
                    "partner": {},
                    "member": {
                        "join": false,
                        "leave": true,
                        "donate": true,
                        "create_proposal": false,
                        "vote_proposal": true,
                        "recruit": false,
                        "remove_members": false,
                        "buy_token": true,
                    },
                    "default": {
                        "join": true,
                        "leave": false,
                        "donate": true,
                        "create_proposal": false,
                        "vote_proposal": false,
                        "recruit": false,
                        "remove_members": false,
                        "buy_token": false,
                    }
                }
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

    $scope.addInvitedUser = function () {
        if (!$scope.orga_form.invited_users)
            $scope.orga_form.invited_users = {};

        $scope.orga_form.invited_users[$scope.selected_user.originalObject._id] = $scope.selected_user.originalObject;
        $scope.orga_form.invited_users[$scope.selected_user.originalObject._id]["tag"] = "member";
        $scope.tagChangedForUser($scope.selected_user.originalObject._id);
        console.log($scope.orga_form.invited_users);
    };

    $scope.tagChangedForUser = function(user_id) {
        $scope.orga_form.invited_users[user_id]["rights"] = $scope.governance_types[$scope.orga_form.gov_model]["rights"][$scope.orga_form.invited_users[user_id]["tag"]];
    }

    $scope.editRights = function(username, user_id) {
        var rightsModalInstance = $uibModal.open({
           templateUrl: "static/assets/views/modals/memberRightsModal.html",
           controller: function($uibModalInstance, $scope, user_id, rights, orga_form) {
            $scope.selected_tag = "member";
            $scope.rights = rights;
            $scope.user_id = user_id;
            $scope.orga_form = orga_form;
        },
        size: 'lg',
        resolve: {
            orga_form: function() {
                return $scope.orga_form
            },
            user_id: function () {
                return user_id
            },
            rights: function() {
                return $scope.governance_types[$scope.orga_form.gov_model]['rights']
            }
        }
    });
        rightsModalInstance.result.then(function() {}, function () {
        });
    }        



    $scope.removeRow = function (user_id) {
        delete $scope.orga_form.invited_users[user_id];
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
            if ($scope.doVerifications()) {
                $scope.completeBlockchainAction(
                    function(password) {
                        $rootScope.toogleWait("Processing organization creation...");
                        $http.post('/createOrga', {
                            "socketid": $rootScope.sessionId,
                            "password": password,
                            "newOrga" : $scope.orga_form
                        }).then(function(response) {}, function(error) {$rootScope.toogleError(error.data);});
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
