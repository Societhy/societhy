'use strict';
/**
 * Clip-Two Main Controller
 */

 app.controller('AppCtrl', function($rootScope, $scope, $state, $swipe, $translate, $localStorage, $window, $document, $timeout, cfpLoadingBar, Fullscreen, toaster, SweetAlert) {
    // Loading bar transition
    // -----------------------------------
    var $win = $($window), $body = $('body');
    $scope.horizontalNavbarCollapsed = true;
    
    $scope.menuInit = function (value) {
        $scope.horizontalNavbarCollapsed = value;
    };
    $scope.menuToggle = function (value) {
        $scope.horizontalNavbarCollapsed = !$scope.horizontalNavbarCollapsed;
    };

    $rootScope.$on('$stateChangeSuccess', function (event, toState, toParams, fromState, fromParams) {
        //start loading bar on stateChangeStart
        cfpLoadingBar.start();
        $scope.horizontalNavbarCollapsed = true;

        // if user not logged in, back to previous screen
        if (toState.needs_auth == true && $rootScope.user == null) {
            console.log("NOT LOGGED IN");
            $state.go('app.dashboard').then(function(arg) {
                $state.reload();
            }, function(error) {
                consol.log(error);
            });
        }

        if (toState.name == "app.pagelayouts.boxedpage") {
            $body.addClass("app-boxed-page");
        } else {
            $body.removeClass("app-boxed-page");
        }
        if(typeof CKEDITOR !== 'undefined'){
         for(name in CKEDITOR.instances)
         {
           CKEDITOR.instances[name].destroy();
       }
   }
});
    $rootScope.$on('$stateChangeSuccess', function (event, toState, toParams, fromState, fromParams) {
      $scope.horizontalNavbarCollapsed = true;
        //stop loading bar on stateChangeSuccess
        event.targetScope.$watch("$viewContentLoaded", function () {

            cfpLoadingBar.complete();
        });

        // scroll top the page on change state
        $('#app .main-content').css({
            position: 'relative',
            top: 'auto'
        });

        $('footer').show();

        window.scrollTo(0, 0);

        if (angular.element('.email-reader').length) {
            angular.element('.email-reader').animate({
                scrollTop: 0
            }, 0);
        }

        // Save the route title
        $rootScope.currTitle = $state.current.title;

    });

    // State not found
    $rootScope.$on('$stateNotFound', function (event, unfoundState, fromState, fromParams) {
        //$rootScope.loading = false;
        console.log(unfoundState.to);
        // "lazy.state"
        console.log(unfoundState.toParams);
        // {a:1, b:2}
        console.log(unfoundState.options);
        // {inherit:false} + default options
    });

    $rootScope.pageTitle = function () {
        return $rootScope.app.name + ' - ' + ($rootScope.currTitle || $rootScope.app.description);
    };
    var defaultlayout = $scope.app.defaultLayout;
    // save settings to local storage
    if (angular.isDefined($localStorage.lay)) {
        $scope.app.layout = angular.copy($localStorage.lay);

    }

    $scope.resetLayout = function () {
        $scope.loading_reset = true;
        // start loading
        $timeout(function () {
            delete $localStorage.lay;
            $scope.app.layout = angular.copy($rootScope.app.defaultLayout);
            $scope.loading_reset = false;
            // stop loading
        }, 500);

    };
    $scope.saveLayout = function () {
        $scope.loading_save = true;
        // start loading
        $timeout(function () {
            $localStorage.lay = angular.copy($scope.app.layout);
            $scope.loading_save = false;
            // stop loading
        }, 500);

    };
    $scope.setLayout = function () {

        $scope.app.layout.isNavbarFixed = false;
        $scope.app.layout.isSidebarClosed = false;
        $scope.app.layout.isSidebarFixed = false;
        $scope.app.layout.isFooterFixed = false;
        $scope.app.layout.isBoxedPage = false;

    };

    //global function to scroll page up
    $scope.toTheTop = function () {

        $document.scrollTopAnimated(0, 600);

    };

    // angular translate
    // ----------------------
    $scope.language = {
        // Handles language dropdown
        listIsOpen: false,
        // list of available languages
        available: {
            'fr': 'Français',
            'en': 'English',
            'it_IT': 'Italiano',
            'de_DE': 'Deutsch'
        },
        // display always the current ui language
        init: function () {
            var proposedLanguage = $translate.proposedLanguage() || $translate.use();
            var preferredLanguage = $translate.preferredLanguage();
            // we know we have set a preferred one in app.config
            $scope.language.selected = $scope.language.available[(proposedLanguage || preferredLanguage)];
        },
        set: function (localeId, ev) {
            $translate.use(localeId);
            $scope.language.selected = $scope.language.available[localeId];
            $scope.language.listIsOpen = !$scope.language.listIsOpen;
        }
    };

    $scope.language.init();

    // Fullscreen
    $scope.isFullscreen = false;
    $scope.goFullscreen = function () {
        $scope.isFullscreen = !$scope.isFullscreen;
        if (Fullscreen.isEnabled()) {
            Fullscreen.cancel();
        } else {
            Fullscreen.all();
        }

        // Set Fullscreen to a specific element (bad practice)
        // Fullscreen.enable( document.getElementById('img') )

    };

    var waitToast = null
    $scope.toogleWaitTx = function(text) {
        if (!waitToast) {
            waitToast = toaster.pop({type: "wait", title: "Loading", body: text || "Processing transaction", timeout: 0});
        } else {
            $timeout(function () {
                toaster.clear(waitToast);
            }, 0);
            waitToast = null;
        }
    };

    $scope.toogleSuccessTx = function(text) {
        if (waitToast) {
            $scope.toogleWaitTx();
        }
        $timeout(function () {
            toaster.pop({type: "success", title: "Done !", body: text, timeout:3000});
        }, 0);
    };

    $scope.toogleErrorTx = function(text) {
        if (waitToast) {
            $scope.toogleWaitTx();
        }
        $timeout(function () {
            toaster.pop({type: "error", title: "Failed...", body: text, timeout:3000});
        }, 0);
    };

    $scope.completeBlockchainAction = function(callback) {
        var args = arguments;
        SweetAlert.swal({
          title: "Unlock your wallet",
          type: "input",
          inputType: "password",
          showCancelButton: false,
          closeOnConfirm: true,
          inputPlaceholder: "Password"
      },
      function(inputValue){
          if (inputValue === false) return false;

          if (inputValue === "") {
            SweetAlert.swal.showInputError("You need to write something!");
            return false
        }
        var password = inputValue;
        args[0] = password;
        callback.apply(null, args);
    });
    };

    $rootScope.$on('socket:txResult', function (event, data) {
        if (data.data)
            $scope.toogleSuccessTx(data.event);
        else
            $scope.toogleErrorTx(data.event);
    });

    $scope.searchForAnything = function(search) {
        $rootScope.search = search;
        $state.go("app.user", {"name": search});
    }
    
    // Function that find the exact height and width of the viewport in a cross-browser way
    var viewport = function () {
        var e = window, a = 'inner';
        if (!('innerWidth' in window)) {
            a = 'client';
            e = document.documentElement || document.body;
        }
        return {
            width: e[a + 'Width'],
            height: e[a + 'Height']
        };
    };
    // function that adds information in a scope of the height and width of the page
    $scope.getWindowDimensions = function () {
        return {
            'h': viewport().height,
            'w': viewport().width
        };
    };
    // Detect when window is resized and set some variables
    $scope.$watch($scope.getWindowDimensions, function (newValue, oldValue) {
        $scope.windowHeight = newValue.h;
        $scope.windowWidth = newValue.w;

        if (newValue.w >= 992) {
            $scope.isLargeDevice = true;
        } else {
            $scope.isLargeDevice = false;
        }
        if (newValue.w < 992) {
            $scope.isSmallDevice = true;
        } else {
            $scope.isSmallDevice = false;
        }
        if (newValue.w <= 768) {
            $scope.isMobileDevice = true;
        } else {
            $scope.isMobileDevice = false;
        }
    }, true);
    // Apply on resize
    $win.on('resize', function () {

        $scope.$apply();
        if ($scope.isLargeDevice) {
            $('#app .main-content').css({
                position: 'relative',
                top: 'auto',
                width: 'auto'
            });
            $('footer').show();
        }
    });
});
