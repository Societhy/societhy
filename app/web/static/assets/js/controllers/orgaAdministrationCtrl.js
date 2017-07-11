app.controller('orgaAdministrationController', function($rootScope, $scope, $http, $sessionStorage, $state, $controller) {

    var ctrl = this;
    // ADD DEFAULT RIGHT
    // Deplacer les user d'un job à un autre
    // LA SECU !!!!
    

	$rootScope.admin = {menu: [{url: "static/assets/views/partials/orga/administration/transactions.html"},
		{url: "static/assets/views/partials/orga/administration/members.html"},
		{url: "static/assets/views/partials/orga/administration/projects.html"},
		{url: "static/assets/views/partials/orga/administration/manageRights.html"}],
		current: "static/assets/views/partials/orga/administration/transactions.html",
		rights: {current: null, tmp: $.extend({}, $rootScope.currentOrga.rights),
			 availableRights: {
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
			     "access_administration": false
			}
		},
		members: {tmp: {}, invited_users: {}}};



    // animate menu Icon
    var theToggle = document.getElementById('toggle');
    theToggle.onclick = function() {
	$(this).toggleClass("on");
	$("#administrationMenu").toggleClass("on");
	$("#administrationMenuButton").toggleClass("on");
	$("#administrationContent").toggleClass("off");
	return false;
    }

    /*
    ** MEMBERS **
    */
    
    $rootScope.admin.members.tagChanged = function(addr) {
	$rootScope.admin.members.tmp[addr] = $(("#memberTag_").concat(addr, " option:selected")).text();
	if ($rootScope.admin.members.tmp[addr] != $rootScope.currentOrga.members[addr].tag)
	    $("button[val='"+addr+"']").prop("disabled", false);
	else
	    $("button[val='"+addr+"']").prop("disabled", true);
    }

    $rootScope.admin.members.saveChangedTag = function(addr) {
	$http.post('/updateMemberTag', {
	    "orga_id": $rootScope.currentOrga._id,
	    "addr": addr,
	    "tag": $rootScope.admin.members.tmp[addr]
	}).then(function(response) {
        $rootScope.toogleSuccess("Job updated!");
        $("button[val='"+addr+"']").prop("disabled", true);
        $rootScope.currentOrga.rights = response.data.rights;
        $scope.currentRights = $rootScope.currentRights = response.data.userRights;
	    delete $rootScope.admin.members.tmp[addr]
	},function(error) {
	    $rootScope.toogleError(error.data);
	});
    }

	// USER INVIT MANAGEMENT

    $scope.addInvitedUser = function () {
    	console.log($rootScope.admin.members.selected)
    	if ($rootScope.admin.members.selected.originalObject.category != "user") {
            $rootScope.toogleInfo("You can only invite users");
            return false;
		}

    	if (!$rootScope.admin.members.invited_users[$rootScope.admin.members.selected.originalObject._id])
        	$rootScope.admin.members.invited_users[$rootScope.admin.members.selected.originalObject._id] = $rootScope.admin.members.selected.originalObject

    };

    $scope.updateInvitedUserRights = function (id) {
        $rootScope.admin.members.invited_users[id]["rights"] = $rootScope.currentOrga.rights[$rootScope.admin.members.invited_users[id]["tag"]]
    };

    $scope.removeInvitedUser = function (id) {
        delete $rootScope.admin.members.invited_users[id];
    };

    $scope.sendInvitations = function () {
        if (Object.keys($rootScope.admin.members.invited_users).length) {
            var ret = true;
            $.each($rootScope.admin.members.invited_users, function (key, val) {
				 if (!val["rights"]) {
				 	ret = false;
				 	return;
				 }
            })
			if (ret == false) {
                $rootScope.toogleInfo("Please fill all tag(s)");
                return
            }
            $http.post('/inviteUsersToOrga', {
                "socketid": $rootScope.sessionId,
                "orga_id": $rootScope.currentOrga._id,
                "invited_users": $rootScope.admin.members.invited_users
            }).then(function (response) {
                $rootScope.toogleSuccess("Member(s) invited");
                delete $rootScope.admin.members.invited_users;
                $rootScope.admin.members.invited_users = {};
            }, function (error) {
                $rootScope.toogleError(error.data);
            });
        }
    };

    $rootScope.admin.members.removeMember = function(addr) {
	if ($scope.doVerifications()) {
	    $scope.completeBlockchainAction( function(password) {
		$rootScope.toogleWait("Removing Member...")
		$http.post('/removeMember', {
		    "account": addr,
		    "password": password,
		    "socketid": $rootScope.sessionId,
		    "orga_id": $rootScope.currentOrga._id
		}).then(function(response) {	
		    $rootScope.currentOrga.members[addr].tag = $rootScope.admin.members.tmp[addr];
		    $rootScope.toogleSuccess("Member removed...")
		    delete $rootScope.admin.members.tmp[addr]
		    delete $rootScope.currentOrga.members[addr]
		},function(error) {
		    $rootScope.toogleError(error.data);
		});
	    
	    })
	}
    }

    /*
    ** RIGHTS **
    */

    /* Select a right and display is allowed actions among the list */
    $rootScope.admin.rights.updateSelected = function (id, index) {
	$rootScope.admin.rights.current = id;
	$(".currentRight").removeClass("currentRight");
	$(".orgaRightsMenuField[val='"+index+"'").addClass("currentRight");
    }

    /* Add a new right to the list */
    $rootScope.admin.rights.newRight = function () {
	if ($("#newOrgaRight").val().trim() && !$rootScope.admin.rights.tmp[$("#newOrgaRight").val()])
	    $rootScope.admin.rights.tmp[$("#newOrgaRight").val()] = $.extend({}, $rootScope.admin.rights["availableRights"]);
    }

    /* Remove  a right from the list */
    $rootScope.admin.rights.removeRight = function (id) {
	delete $rootScope.admin.rights.tmp[id];
    }


    /* Save the changment made into the database xs*/
    $rootScope.admin.updateRights = function () {
	$http.post('/updateOrgaRights', {
	    "orga_id": $rootScope.currentOrga._id,
	    "rights": $rootScope.admin.rights.tmp
	}).then(function(response) {
		console.log(response)
        $rootScope.toogleSuccess("Rights updated!");
        $rootScope.currentOrga.rights = response.data.rights;
        $scope.currentRights = $rootScope.currentRights = response.data.userRights;
    },function(error) {
	    $rootScope.admin.rights.tmp = $rootScope.currentOrga.rights;
	    $rootScope.toogleError(error.data);
	});
    }

    /* Menu Handler when clicking on a element of the menu, fetch the corresponding html code and display it */
    $rootScope.admin.displayTransactions = function () {
	$rootScope.admin.current = $rootScope.admin.menu[0]["url"];
    }


    $rootScope.admin.displayMembers = function () {
	$rootScope.admin.current = $rootScope.admin.menu[1]["url"];
    }
    
    $rootScope.admin.displayProjects = function () {
	$rootScope.admin.current = $rootScope.admin.menu[2]["url"];
    }
    


    $rootScope.admin.manageRights = function () {
	$rootScope.admin.current = $rootScope.admin.menu[3]["url"];
    }
    
    /*
      $(document).ready(function() {

      // Enable Datatable
      $('a[data-toggle="tab"]').on( 'shown.bs.tab', function (e) {
      $.fn.dataTable.tables( {visible: true, api: true} ).columns.adjust();
      });
      });
    */

    return ctrl;
});
