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
                "pros": ["Trustless AND secure", "Withdraw your funds at all time", "No membership required"],
                "cons": ["Less reactive than a centralized structure", "Permissions are non-customisable", "Tokens are frozen while a proposal you voted for is still debating"],
                "desc": "DAO stands for 'decentralized autonomous organisation'. It is a kind of organisation that is controlled entirely by all of its members, and in which every member has the same rights. One does not need to become a member of the organisation to participate in its operations, and the weight of one's vote depends on the amount he invested in the structure",
                "tags": ["owner", "admin", "member", "guest"],
                "rights": {
                    "owner": {},
                    "admin": {},
                    "guest": {},
                    "member": {},
                    "default": {}
                }
            },
            "ngo": {
                "pros": ["Efficient decision making", "Collaborative fund management", "Membership system"],
                "cons": ["The perfect fit for public organisations", "Transparency in every way", "Highly customizable"],
                "desc": "This type of organisation is the right choice for public structures and those who want complete transparency over their processes, hence preventing fraud.",
                "tags": ["owner", "admin", "member", "guest"],
                "rights": {
                    "owner": {},
                    "admin": {},
                    "partner": {},
                    "member": {},
                    "default": {}
                  }
            },

            "public_company": {
                "pros": ["Trustless AND secure", "Withdraw your funds at all time", "No membership required", "Delegated voting"],
                "cons": ["Perfect for small and large businnesses wanting to go public", "Buy and sell your company shares", "Highly secured with the use of curators"],
                "desc": "This type of structure is the right fit for organisations wanting to involve external investors and/or their customers in their funding and decision making.",
                "tags": ["owner", "admin", "member", "guest"],
                "rights": {
                    "owner": {},
                    "admin": {},
                    "partner": {},
                    "member": {},
                    "default": {}
                }
            },
            "entreprise": {
                "pros": ["Centralized structure", "Permissions are highly customizable", "Very easy to manage"],
                "cons": ["Perfect fit for individuals wanting full control over the structure", "Members need to trust the administrators"],
                "desc": "This type of structure is made for people that want a strong leadership in their organization, allowing quick and efficient decision making, it is the right structure for a regular business needing privacy over its accounts.",
                "tags": ["owner", "admin", "member", "guest"],
                "rights": {
                    "owner": {},
                    "admin": {},
                    "partner": {},
                    "member": {},
                    "default": {}
                }
            }
        };

        $scope.availableRights = {
            "join": false,
            "leave": false,
            "donate": false,
            "edit_rights": false,
            "edit_jobs": false,
            "create_project": false,
            "create_offer": false,
            "create_proposal": false,
            "vote_proposal": false,
            "recruit": false,
            "remove_members": false,
            "sell_token": false,
            "buy_token": false,
	        "access_administration": false,
            "publish_news":false
        };

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

    uploaderDocs.onAfterAddingFile = function() {
      uploaderDocs.queue[uploaderDocs.queue.length - 1].documentPrivacy = ["default"];
    }

    uploaderDocs.onBeforeUploadItem = function (item) {
        console.log(uploaderDocs.queue.length);
        item.formData.push({"name": item.file.name});
        item.formData.push({"type": item.file.type});
        item.formData.push({"size": item.file.size/1024/1024});
        item.formData.push({"privacy": item.documentPrivacy});
        console.info('onBeforeUploadItem', item);
    };

    // RIGHTS MANAGEMENT
    var getGovernanceRights = function() {
      $http.get('/getGovernanceRights', {
        "socketid": $rootScope.sessionId,
      }).then(
        function(response) {
          jQuery.each(response.data.data, function(index, val) {
            $scope.governance_types["ngo"]["rights"] = val;
          })
          $scope.orga_form.gov_model = ["ngo"];
        },
        function(error) {
          $rootScope.toogleError(error.data);
        }
      );
    }
    getGovernanceRights();
      $scope.$watch('orga_form.gov_model', function() {
          delete $scope.orga_form.rights;
          $scope.orga_form.rights = $.extend({}, $scope.governance_types[$scope.orga_form.gov_model]["rights"]);
      });

        /* Select a right and display is allowed actions among the list */
        $scope.displaySelectedRight = function (id, index) {
            $scope.currentRight = id;
            $(".currentRight").removeClass("currentRight");
            $(".orgaRightsMenuField[val='"+index+"'").addClass("currentRight");
        }

        /* Remove  a right from the list */
        $scope.removeRight = function (id, index) {
            $scope.currentRights.push($("#newOrgaRight").val());
            delete $scope.orga_form.rights[id];
        }

        /* Add a newright to the list */
        $rootScope.addRight = function () {
            if ($("#newOrgaRight").val().trim() && !$scope.orga_form.rights[$("#newOrgaRight").val()]) {
                $scope.orga_form.rights[$("#newOrgaRight").val()] = $.extend({}, $scope.governance_types[$scope.orga_form.gov_model].rights["default"]);
            }
        }

    $scope.addInvitedUser = function () {
        if (!$scope.orga_form.invited_users)
            $scope.orga_form.invited_users = {};
        if ($scope.selected_user.originalObject.category != "user") {
            $rootScope.toogleInfo("You can only invite user!");
            return false;
        }
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
