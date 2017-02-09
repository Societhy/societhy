'use strict';

/**
 * Config for the router
 */
app.config(['$stateProvider', '$urlRouterProvider', '$controllerProvider', '$compileProvider', '$filterProvider', '$provide', '$ocLazyLoadProvider', 'JS_REQUIRES',
function ($stateProvider, $urlRouterProvider, $controllerProvider, $compileProvider, $filterProvider, $provide, $ocLazyLoadProvider, jsRequires) {

    app.controller = $controllerProvider.register;
    app.directive = $compileProvider.directive;
    app.filter = $filterProvider.register;
    app.factory = $provide.factory;
    app.service = $provide.service;
    app.constant = $provide.constant;
    app.value = $provide.value;

    // LAZY MODULES

    $ocLazyLoadProvider.config({
        debug: false,
        events: true,
        modules: jsRequires.modules
    });

    // APPLICATION ROUTES
    // -----------------------------------
    // For any unmatched url, redirect to /app/dashboard
    $urlRouterProvider.otherwise("/app/dashboard");
    //
    // Set up the states
    $stateProvider.state('app', {
        url: "/app",
        templateUrl: "static/assets/views/app.html",
        resolve: loadSequence('OAuth', 'btford.socket-io', 'chatCtrl', 'inboxCtrl', 'loginCtrl', 'walletCtrl', 'ngNotify'),
        abstract: true
    }).state('app.dashboard', {
        url: "/dashboard",
        templateUrl: "static/assets/views/dashboard.html",
        resolve: loadSequence('d3', 'ui.knob', 'countTo', 'dashboardCtrl'),
        title: 'Dashboard',
        ncyBreadcrumb: {
            label: 'Dashboard'
        }
    }).state('app.me', {
        url: '/me',
        needs_auth: true,
        templateUrl: "static/assets/views/user_profile.html",
        resolve: loadSequence('userOverviewCtrl', 'keyCtrl', 'keythereum', 'angularFileUpload', 'FileSaver', 'qrcode', 'ngTable'),
        title: 'My Profile',
        ncyBreadcrumb: {
            label: 'My Profile'
        }
    }).state('app.user', {
        url: '/user/:name',
        templateUrl: "static/assets/views/user_other_profile.html",
        resolve: loadSequence('userOtherOverviewCtrl', 'angularFileUpload', 'FileSaver', 'OAuth', 'qrcode', 'ngTable'),
        title: 'user Profile',
        ncyBreadcrumb: {
            label: 'User Profile'
        }
    }).state('app.organization', {
        url: '/orga/:name/:_id',
        templateUrl: "static/assets/views/orga_dashboard.html",
        resolve: loadSequence('orgaMainCtrl', 'touchspin-plugin'),
        title: 'Organisation dashboard',
        params: {
            data: null
        },
        ncyBreadcrumb: {
            label: 'Organisation'
        }
    }).state('app.neworga', {
        url: '/orga/new',
        needs_auth: true,
        templateUrl :"static/assets/views/wizard_orga.html",
        resolve: loadSequence('orgaWizardCtrl', 'FileSaver', 'angularFileUpload'),
        title: "Create a new organisation",
        ncyBreadcrumb: {
            label: 'Organisation Creation'
        }
    }).state('app.discoverorga', {
        url: '/orga/discover',
        templateUrl: "static/assets/views/orga_discovery.html",
        resolve: loadSequence('orgaDiscoveryCtrl'),
        title: 'Organisations list',
        ncyBreadcrumb: {
            label: 'Organisation'
        }
    }).state('app.project', {
        url: '/orga/:project_name/:project_id',
        templateUrl: "static/assets/views/project_dashboard.html",
        resolve: loadSequence('projectMainCtrl'),
        title: 'Project dashboard',
        ncyBreadcrumb: {
            label: 'Project'
        }
    }).state('app.registration', {
        url: '/registration',
        resolve: loadSequence('CryptoJS'),
        templateUrl: "static/assets/views/login_registration.html"
    })


    .state('error', {
        url: '/error',
        template: '<div ui-view class="fade-in-up"></div>',
        abstract: true
    }).state('error.404', {
        url: '/404',
        templateUrl: "static/assets/views/utility_404.html",
    }).state('error.500', {
        url: '/500',
        templateUrl: "static/assets/views/utility_500.html",
    })

    // Landing Page route
	.state('landing', {
	    url: '/landing-page',
	    template: '<div ui-view class="fade-in-right-big smooth"></div>',
	    abstract: true,
	    resolve: loadSequence('jquery-appear-plugin', 'ngAppear', 'countTo')
	}).state('landing.welcome', {
	    url: '/welcome',
	    templateUrl: "static/assets/views/landing_page.html"
	});

    // Generates a resolve object previously configured in constant.JS_REQUIRES (config.constant.js)
    function loadSequence() {
        var _args = arguments;
        return {
            deps: ['$ocLazyLoad', '$q',
			function ($ocLL, $q) {
			    var promise = $q.when(1);
			    for (var i = 0, len = _args.length; i < len; i++) {
			        promise = promiseThen(_args[i]);
			    }
			    return promise;

			    function promiseThen(_arg) {
			        if (typeof _arg == 'function')
			            return promise.then(_arg);
			        else
			            return promise.then(function () {
			                var nowLoad = requiredData(_arg);
			                if (!nowLoad)
			                    return $.error('Route resolve: Bad resource name [' + _arg + ']');
			                return $ocLL.load(nowLoad);
			            });
			    }

			    function requiredData(name) {
			        if (jsRequires.modules)
			            for (var m in jsRequires.modules)
			                if (jsRequires.modules[m].name && jsRequires.modules[m].name === name)
			                    return jsRequires.modules[m];
			        return jsRequires.scripts && jsRequires.scripts[name];
			    }
			}]
        };
    }
}]);
