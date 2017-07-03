var app = angular.module('app', ['packet', 'xeditable', 'ui.bootstrap']);
app.run(['$rootScope', '$state', '$stateParams', '$sessionStorage', '$http', 'editableOptions',
    function ($rootScope, $state, $stateParams, $sessionStorage, $http, editableOptions) {
        editableOptions.theme = 'bs3';
        // Attach Fastclick for eliminating the 300ms delay between a physical tap and the firing of a click event on mobile browsers
        FastClick.attach(document.body);

        // Set some reference to access them from any scope
        $rootScope.$state = $state;
        $rootScope.$stateParams = $stateParams;

        $rootScope.user = null;

        // GLOBAL APP SCOPE
        // set below basic information
        $rootScope.app = {
            name: 'Societhy', // name of your project
            author: 'SocieDEVS', // author's name or company name
            description: 'Societhy web-app', // brief description
            version: '1.0', // current version
            year: ((new Date()).getFullYear()), // automatic current year (for copyright information)
            isMobile: (function () {// true if the browser is a mobile device
                var check = false;
                if (/Android|webOS|iPhone|iPad|iPod|BlackBerry|IEMobile|Opera Mini/i.test(navigator.userAgent)) {
                    check = true;
                };
                return check;
            })(),
            defaultLayout: {
                isNavbarFixed: true, //true if you want to initialize the template with fixed header
                isSidebarFixed: true, // true if you want to initialize the template with fixed sidebar
                isSidebarClosed: false, // true if you want to initialize the template with closed sidebar
                isFooterFixed: false, // true if you want to initialize the template with fixed footer
                isBoxedPage: false, // true if you want to initialize the template with boxed layout
                theme: 'lyt4-theme-1', // indicate the theme chosen for your project
                logo: 'static/assets/images/logo.png', // relative path of the project logo
                logoCollapsed: 'static/assets/images/logo-collapsed.png' // relative path of the collapsed logo
            },
            layout: ''
        };
        $rootScope.app.layout = angular.copy($rootScope.app.defaultLayout);
        if ($sessionStorage.SociethyToken != null && $rootScope.user == null) {
            $http.get('/checkTokenValidity/'.concat($sessionStorage.SociethyToken)).then(function(response) {
                if (response.data.user != null) {
                    $rootScope.user = response.data.user;
                }
            });
        }
        else if ($rootScope.user != null) {
            ctrl.user = $rootScope.user
        }


    }]);

// set token in request header for authentification
app.factory('httpRequestInterceptor', function($sessionStorage) {
    return {
        'request': function(config) {
            if ($sessionStorage.SociethyToken) {
                config.headers.Authentification = $sessionStorage.SociethyToken;
            }
            return config;
        }
    }
});

app.factory('socketIO', function ($rootScope, socketFactory) {
    var socket = socketFactory({
        ioSocket: io.connect('/')
    });
    socket.forward('error');
    socket.forward('txResult', $rootScope);
    return socket;
});

// token authentification config
app.config(['$httpProvider',
    function($httpProvider) {
        $httpProvider.interceptors.push('httpRequestInterceptor');
    }]);

// translate config
app.config(['$translateProvider',
    function ($translateProvider) {

        // prefix and suffix information  is required to specify a pattern
        // You can simply use the static-files loader with this pattern:
        $translateProvider.useStaticFilesLoader({
            prefix: 'static/assets/i18n/',
            suffix: '.json'
        });

        // Since you've now registered more then one translation table, angular-translate has to know which one to use.
        // This is where preferredLanguage(langKey) comes in.
        $translateProvider.preferredLanguage('fr');

        // Store the language in the local storage
        $translateProvider.useLocalStorage();

        // Enable sanitize
        $translateProvider.useSanitizeValueStrategy('sanitize');

    }]);
// Angular-Loading-Bar
// configuration
app.config(['cfpLoadingBarProvider',
    function (cfpLoadingBarProvider) {
        cfpLoadingBarProvider.includeBar = true;
        cfpLoadingBarProvider.includeSpinner = false;

    }]);
// Angular-breadcrumb
// configuration
app.config(function ($breadcrumbProvider) {
    $breadcrumbProvider.setOptions({
        template: '<ul class="breadcrumb"><li><a ui-sref="app.dashboard"><i class="fa fa-home margin-right-5 text-large text-dark"></i>Home</a></li><li ng-repeat="step in steps">{{step.ncyBreadcrumbLabel}}</li></ul>'
    });
});
// ng-storage
//set a prefix to avoid overwriting any local storage variables
app.config(['$localStorageProvider',
    function ($localStorageProvider) {
        $localStorageProvider.setKeyPrefix('PacketLtr4');
    }]);
//filter to convert html to plain text
app.filter('htmlToPlaintext', function () {
        return function (text) {
            return String(text).replace(/<[^>]+>/gm, '');
        };
    }

);
