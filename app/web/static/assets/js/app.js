/**
  * declare 'packet' module with dependencies
*/
'use strict';
angular.module("packet", [
	'ngAnimate',
	'ngCookies',
	'ngStorage',
	'ngSanitize',
	'ngTouch',
	'ui.router',
	'ui.bootstrap',
	'angularMoment',
	'oc.lazyLoad',
	'swipe',
	'ngBootstrap',
	'truncate',
	'uiSwitch',
	'toaster',
	'ngAside',
	'vAccordion',
	'vButton',
	'oitozero.ngSweetAlert',
	'angular-notification-icons',
	'angular-ladda',
	'angularAwesomeSlider',
	'slickCarousel',
	'cfp.loadingBar',
	'ncy-angular-breadcrumb',
	'duScroll',
	'pascalprecht.translate',
	'FBAngular'
])
    .controller('projectTableCtrl', function($scope) {
	$scope.sortType     = 'name'; // set the default sort type
	$scope.sortReverse  = false;  // set the default sort order
	$scope.searchType   = '';     // set the default search/filter term

	$scope.projects = [
	    { name: 'Aider les sans-abris', type: 'Levée de fonds'},
	    { name: 'Bénévolat medecin du monde', type: 'Action humanitaire'},
	    { name: 'ONG: Tous Ensemble', type: 'Action caritative, Levée de fonds'},
	    { name: 'Mon groupe de musique', type: 'Personel, musique'},
	];
    })

    .controller('orgaTableCtrl', function($scope) {
	$scope.sortType     = 'name'; // set the default sort type
	$scope.sortReverse  = false;  // set the default sort order
	$scope.searchType   = '';     // set the default search/filter term

	$scope.orgas = [
	    { name: 'Entreprise familiale', orga: "Mon groupe de musique"},
	];

    });
