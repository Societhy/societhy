app.controller('LoginController', function($rootScope, $http, $sessionStorage, $state, $controller, $location) {

    var ctrl = this;
    ctrl.user = $rootScope.user
	ctrl.wallet = $controller("WalletController");

       if (ctrl.user) {
    	   ctrl.wallet.refreshAllBalances();
       }

    ctrl.login = function() {
		if (ctrl.username && ctrl.password) {
				$http.post('/login', {
					"id": btoa(ctrl.username + ':' + ctrl.password)
				}).then(function(response) {
					console.log("RECEIVED = ", response);
					sessionStorage.user = JSON.stringify(response.data.user);
					$sessionStorage.SociethyToken = response.data.token;
					$sessionStorage.username = response.data.user.name;
					$rootScope.user = ctrl.user = response.data.user;
					ctrl.wallet.refreshAllBalances();
				}, function(error) {
					console.log(error);
				});
		}
	}

	ctrl.logout = function() {
		$http.get('/logout').then(function(reponse) {
			delete $sessionStorage.SociethyToken;
			$rootScope.user = ctrl.user = null
			$state.go('app.dashboard');
		});
	}

    ctrl.register = function() {

		if (ctrl.username && ctrl.password) {
		    $http.post('/newUser', {
				name: ctrl.username,
				email: ctrl.email,
				password: ctrl.password,
				eth: ctrl.wantsKey || false,
				firstname: ctrl.firstname || "",
				lastname: ctrl.lastname || "",
				birthday: ctrl.birthday || "",
				gender: ctrl.gender || "",
				address: ctrl.address || "",
				city: ctrl.city || "",
                contact_list: []
			}).then(function(response) {
				console.log("RECEIVED = ", response);
				$sessionStorage.SociethyToken = response.data.token;
				$rootScope.user = ctrl.user = response.data.user;
				$state.go("app.me", ctrl)
				},
				function(error) {
					console.log(error);
			});
		}
    };



    /*
    ** REGISTRATION
    */

    function registration_checker() {
	console.log("registration check enabled");
	/* Enable datepicker*/
	$( function() {
	    $( "#datepicker" ).datepicker();
	} );

	step = 1;

	$("div#stepAdvancement button#btn-prev").on("click", function() {
	    step--;
	    updateDisplay();
	});

	$("div#stepAdvancement button#btn-next").on("click", function() {
	    step++;
	    updateDisplay()
	});

	/*
	** Enable submit button when all mandatory field are filled
	*/
	function updateSubmitButtonState () {
	    $("button#submit").prop("disabled", false);
	    $("#beforeSubmit").hide();
	    if ($(".formChecker[style!='display: none;']").length > 0)
	    {
		$("button#submit").prop("disabled", true);
		$("#beforeSubmit").show();
		return;
	    }
	    $("form #mandatoryInfo input").each(function (index) {
		if ($(this).val().length == 0) {
		    $("button#submit").prop("disabled", true);
		    $("#beforeSubmit").show();
		    return;
		}
	    });
	};

	/*
	** Enable/Disable previous and next button
	*/
	function updateDisplay() {
	    if (step == 1)
		$("div#stepAdvancement button#btn-prev").prop("disabled", true);
	    else
		$("div#stepAdvancement button#btn-prev").prop("disabled", false);
	    if (step == $(".registrationDatas").length)
		$("div#stepAdvancement button#btn-next").prop("disabled", true);
	    else
		$("div#stepAdvancement button#btn-next").prop("disabled", false);
	    $(".registrationDatas").hide();
	    $(".data" + step).show();
	}

	/*
	** Regex for email check
	*/
	$("form input[type='email']").on("change", function() {
	    var re = /^(([^<>()\[\]\\.,;:\s@"]+(\.[^<>()\[\]\\.,;:\s@"]+)*)|(".+"))@((\[[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}])|(([a-zA-Z\-0-9]+\.)+[a-zA-Z]{2,}))$/;
	    if (!re.test($(this).val()))
		$("#emailCheck").show();
	    else
		$("#emailCheck").hide();
	    updateSubmitButtonState();
	});

	/*
	** Check Username format
	*/
	$("form input[name='username']").on("change", function() {
	    var re = /^[a-zA-Z0-9_-]{6,20}$/;
	    if (!re.test($(this).val()))
		$("#usernameCheck").show();
	    else
		$("#usernameCheck").hide();
	    updateSubmitButtonState();
	});

	/*
	** Check the requierment for password
	*/
	$("form input[name='password']").on("change", function() {
	    if ($(this).val().length < 8 || $(this).val().length > 20 ||
		$(this).val().indexOf(" ") != -1)
		$("#passwordCheck").show();
	    else
		$("#passwordCheck").hide();
	    updateSubmitButtonState();
	});

	/*
	** Check if passwords match
	*/
	$("form input[name='password_again']").on("change", function() {
	    if ($("form input[name='password']").val() != "" && $("form input[name='password_again']").val() != "" &&
		$("form input[name='password_again']").val() !== $("form input[name='password']").val())
		$("#passwordConfirmationCheck").show();
	    else
		$("#passwordConfirmationCheck").hide();
	    updateSubmitButtonState();
	});
    }

    if ($location.path() == "/login/registration") {
	registration_checker();
    }
    /*
    ** Handle the modification of the personal informations
    */

    // var over = false;
    // $(".form-group").mouseenter(function() {
    // 	$(this).children(".accountInfo").stop().animate({ width: "93%" }, 600);//.next().stop().animate({ opacity: "1"}, 600, function() {
    // 	//     $(this).css({display: "inline-block"});
    // 	// });
    // 	over = true;
    // });

    // $(".form-group").mouseleave(function() {
    // 	$(this).children(".accountInfo").stop().animate({ width: "99%" }, 600);//.children(".editAccountInfo").stop().fadeOut(500).prev()
    //     over = false;
    // });

    return ctrl;
});
