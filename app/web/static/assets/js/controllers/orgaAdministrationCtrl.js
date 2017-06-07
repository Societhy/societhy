app.controller('orgaAdministrationController', function($rootScope, $scope, $http, $sessionStorage, $state, $controller) {

    var ctrl = this;

    // ADD DEFAULT RIGHT
    // Deplacer les user d'un job à un autre
    // LA SECU !!!!
    

    $rootScope.admin = {menu: [{url: "static/assets/views/partials/orga/administration/transaction.html"},
			       {url: "static/assets/views/partials/orga/administration/members.html"},
			       {url: "static/assets/views/partials/orga/administration/transaction.html"},
			       {url: "static/assets/views/partials/orga/administration/transaction.html"}, 
			       {url: "static/assets/views/partials/orga/administration/transaction.html"},
			       {url: "static/assets/views/partials/orga/administration/manageRights.html"}],
			current: "static/assets/views/partials/orga/administration/transaction.html",
			rights: {current: "none", "new": null, tmp: $.extend({}, $rootScope.currentOrga.rights)},
			members: {tmp: {}}};


    function init () {
	if ($rootScope.user) {
	    $http.get('/getOrgaDefaultRights', {
	    }).then(function(response) {
		$rootScope.admin.rights["new"] = response.data;
	    },function(error) {
		console.log(error);
	    });
	}
    }


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
	    $("button[val='"+addr+"']").prop("disabled", true);
	    $rootScope.currentOrga.members[addr].tag = $rootScope.admin.members.tmp[addr];
	    //$(("#memberTag_").concat(addr, " option:selected")).text(""); reset le select
	    delete $rootScope.admin.members.tmp[addr]
	},function(error) {
	    $rootScope.toogleError(error.data);
	});
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
	    $rootScope.admin.rights.tmp[$("#newOrgaRight").val()] = $rootScope.admin.rights["new"];
	console.log($rootScope.admin.rights.tmp)
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
	    $rootScope.currentOrga.rights = response.data;
	},function(error) {
	    $rootScope.admin.rights.tmp = $rootScope.currentOrga.rights;
	    $rootScope.toogleError(error.data);
	});
    }

    /* Menu Handler when clicking on a element of the menu, fetch the corresponding html code and display it */
	$rootScope.admin.displayTransactions = function () {
	    $rootScope.admin.current = $rootScope.admin.menu[0]["url"];
	    $http.get('/getOrgaTransaction/'.concat($rootScope.currentOrga._id)).then(function(response) {
		$rootScope.admin.transaction = {response};
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
    
    /*
      $(document).ready(function() {

      // Enable Datatable
      $('a[data-toggle="tab"]').on( 'shown.bs.tab', function (e) {
      $.fn.dataTable.tables( {visible: true, api: true} ).columns.adjust();
      });
      });
    */

    init();
    return ctrl;
});
