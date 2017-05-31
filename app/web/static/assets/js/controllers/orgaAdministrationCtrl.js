app.controller('orgaAdministrationController', function($rootScope, $scope, $http, $sessionStorage, $state, $controller) {

    var ctrl = this;

    $rootScope.admin = {menu: [{url: "static/assets/views/partials/orga/administration/transaction.html"},
			       {url: "static/assets/views/partials/orga/administration/members.html"},
			       {url: "static/assets/views/partials/orga/administration/transaction.html"},
			       {url: "static/assets/views/partials/orga/administration/transaction.html"}, 
			       {url: "static/assets/views/partials/orga/administration/transaction.html"},
			       {url: "static/assets/views/partials/orga/administration/manageRights.html"}],
			current: "static/assets/views/partials/orga/administration/transaction.html",
			rights: {current: "none"},
			members: {}};
    // ADD DEFAULT RIGHT
    // Deplacer le suser d'un un job dans un autre
    // LA SECU !!!!
    
    


    // animate menu Icon
	var theToggle = document.getElementById('toggle');
	theToggle.onclick = function() {
	    $(this).toggleClass("on");
	    $("#administrationMenu").toggleClass("on");
	    $("#administrationMenuButton").toggleClass("on");
	    $("#administrationContent").toggleClass("off");
	    return false;
	}

    $rootScope.admin.members.tagChanged = function(addr) {
	$("button[val='"+addr+"']").prop("disabled", false);
    }

    $rootScope.admin.members.saveChangedTag = function(addr) {
	console.log(addr);
	$http.post('/updateMemberTag', {
	    "orga_id": $rootScope.currentOrga._id,
	    "addr": addr,
	    "tag": $rootScope.currentOrga.members[addr].tag
	}).then(function(response) {	
	    $("button[val='"+addr+"']").prop("disabled", true);
	    console.log(response)
	});
    }
    $rootScope.admin.rights.updateSelected = function (id, index) {
	$rootScope.admin.rights.current = id;
	$(".currentRight").removeClass("currentRight");
	$(".orgaRightsMenuField[val='"+index+"'").addClass("currentRight");
	
    }

    $rootScope.admin.rights.newRight = function () {
	if ($("#newOrgaRight").val().trim())
	    $rootScope.currentOrga.rights[$("#newOrgaRight").val()] = $rootScope.currentOrga.rights["default"];
    }

    $rootScope.admin.rights.removeRight = function (id) {
	delete $rootScope.currentOrga.rights[id];
    }



    /*    $rootScope.admin.rights.newRight = function (id, index) {
	    $http.post('/addRightToOrga', {
	    "orga_id": $rootScope.currentOrga._id,
	    "name": $("newOrgaRight").val().
	    "rights": $rootScope.currentOrga.rights["default"]
	}).then(function(response) {	
	    console.log(response)
	});
    }
*/
    $rootScope.admin.updateRights = function () {
	$http.post('/updateOrgaRights', {
	    "orga_id": $rootScope.currentOrga._id,
	    "rights": $rootScope.currentOrga.rights
	}).then(function(response) {	
	    console.log(response)
	});
    }

    // Menu Handler
	$rootScope.admin.displayTransactions = function () {
	    $rootScope.admin.current = $rootScope.admin.menu[0]["url"];
	    $("#adminTable").DataTable({data: [
					    [
						"Project investment",
						"-251$",
						'Out <i style="color: red;" class="fa fa-arrow-circle-down" aria-hidden="true"></i>',
						"Finished",
						"Transfer of fund for the 'Special project'",
						"2017/04/16 7:30pm"
					    ],
					    [
						"Sale of a product",
						"130$",
						'In <i style="color: green;" class="fa fa-arrow-circle-up" aria-hidden="true"></i>',
						"Finished",
						"Product 'this thing' bought by 'this guy'",
						"2017/04/2 8:12pm"
					    ],
					    [
						"Management fees",
						"-120$",
						'Out <i style="color: red;" class="fa fa-arrow-circle-up" aria-hidden="true"></i>',
						"Monthly",
						"Monthly fees expenses",
						"2017/04/1 9:05pm"
					    ]
					]
				       });

	}

	$rootScope.admin.displayMembers = function () {
	    $rootScope.admin.current = $rootScope.admin.menu[1]["url"];
	    $("#adminTable").DataTable({});
	    
	}
    
 	$rootScope.admin.displayProjects = function () {
	    $rootScope.admin.current = $rootScope.admin.menu[2]["name"];
	    $("#tableWrapper").html('<table id="adminTable" class="adminTables table table-striped table-bordered"></table>');
	    $("#adminTable").DataTable({"columns": $rootScope.admin.menu[2]["header"]});
	}
		
	$rootScope.admin.addTransaction = function () {
	    $rootScope.admin.current = $rootScope.admin.menu[3]["name"];
	}

	$rootScope.admin.extractAdminData = function () {
	    $rootScope.admin.current = $rootScope.admin.menu[4]["name"];
	    $http.get('/getOrgaTransaction/'.concat($rootScope.currentOrga._id)).then(function(response) {
		
	    });
	}

    $rootScope.admin.manageRights = function () {
	    $rootScope.admin.current = $rootScope.admin.menu[5]["url"];
	}
    
    $(document).ready(function() {

	// Enable Datatable
	$('a[data-toggle="tab"]').on( 'shown.bs.tab', function (e) {
	    $.fn.dataTable.tables( {visible: true, api: true} ).columns.adjust();
	} );
	$rootScope.admin.displayTransactions();
    });
    return ctrl;
});
