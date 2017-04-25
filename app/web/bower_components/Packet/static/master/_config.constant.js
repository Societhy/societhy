'use strict';

/**
 * Config constant
 */
app.constant('APP_MEDIAQUERY', {
    'desktopXL': 1200,
    'desktop': 992,
    'tablet': 768,
    'mobile': 480
});
app.constant('JS_REQUIRES', {
    //*** Scripts
    scripts: {
        //*** Javascript Plugins
        'd3': '../bower_components/d3/d3.min.js',

        //*** jQuery Plugins
        'chartjs': '../bower_components/chartjs/Chart.min.js',
        'ckeditor-plugin': '../bower_components/ckeditor/ckeditor.js',
        'jquery-nestable-plugin': ['../bower_components/jquery-nestable/jquery.nestable.js'],
        'touchspin-plugin': ['../bower_components/bootstrap-touchspin/dist/jquery.bootstrap-touchspin.min.js', '../bower_components/bootstrap-touchspin/dist/jquery.bootstrap-touchspin.min.css'],
        'jquery-appear-plugin': ['../bower_components/jquery-appear/build/jquery.appear.min.js'],
        'spectrum-plugin': ['../bower_components/spectrum/spectrum.js', '../bower_components/spectrum/spectrum.css'],
		'jcrop-plugin': ['../bower_components/Jcrop/js/jquery.Jcrop.min.js', '../bower_components/Jcrop/css/jquery.Jcrop.min.css'],
		
		
        //*** Controllers
        'dashboardCtrl': 'static/assets/js/controllers/dashboardCtrl.js',
        'iconsCtrl': 'static/assets/js/controllers/iconsCtrl.js',
        'vAccordionCtrl': 'static/assets/js/controllers/vAccordionCtrl.js',
        'ckeditorCtrl': 'static/assets/js/controllers/ckeditorCtrl.js',
        'laddaCtrl': 'static/assets/js/controllers/laddaCtrl.js',
        'ngTableCtrl': 'static/assets/js/controllers/ngTableCtrl.js',
        'cropCtrl': 'static/assets/js/controllers/cropCtrl.js',
        'asideCtrl': 'static/assets/js/controllers/asideCtrl.js',
        'toasterCtrl': 'static/assets/js/controllers/toasterCtrl.js',
        'sweetAlertCtrl': 'static/assets/js/controllers/sweetAlertCtrl.js',
        'mapsCtrl': 'static/assets/js/controllers/mapsCtrl.js',
        'chartsCtrl': 'static/assets/js/controllers/chartsCtrl.js',
        'calendarCtrl': 'static/assets/js/controllers/calendarCtrl.js',
        'nestableCtrl': 'static/assets/js/controllers/nestableCtrl.js',
        'validationCtrl': ['static/assets/js/controllers/validationCtrl.js'],
        'userCtrl': ['static/assets/js/controllers/userCtrl.js'],
        'selectCtrl': 'static/assets/js/controllers/selectCtrl.js',
        'wizardCtrl': 'static/assets/js/controllers/wizardCtrl.js',
        'uploadCtrl': 'static/assets/js/controllers/uploadCtrl.js',
        'treeCtrl': 'static/assets/js/controllers/treeCtrl.js',
        'inboxCtrl': 'static/assets/js/controllers/inboxCtrl.js',
        'xeditableCtrl': 'static/assets/js/controllers/xeditableCtrl.js',
        'chatCtrl': 'static/assets/js/controllers/chatCtrl.js',
        'dynamicTableCtrl': 'static/assets/js/controllers/dynamicTableCtrl.js',
        'notificationIconsCtrl': 'static/assets/js/controllers/notificationIconsCtrl.js',
        'dateRangeCtrl': 'static/assets/js/controllers/daterangeCtrl.js',
        'notifyCtrl': 'static/assets/js/controllers/notifyCtrl.js',
        'sliderCtrl': 'static/assets/js/controllers/sliderCtrl.js',
        'knobCtrl': 'static/assets/js/controllers/knobCtrl.js',
        'crop2Ctrl': 'static/assets/js/controllers/crop2Ctrl.js',
    },
    //*** angularJS Modules
    modules: [{
        name: 'toaster',
        files: ['../bower_components/AngularJS-Toaster/toaster.js', '../bower_components/AngularJS-Toaster/toaster.css']
    }, {
        name: 'angularBootstrapNavTree',
        files: ['../bower_components/angular-bootstrap-nav-tree/dist/abn_tree_directive.js', '../bower_components/angular-bootstrap-nav-tree/dist/abn_tree.css']
    }, {
        name: 'ngTable',
        files: ['../bower_components/ng-table/dist/ng-table.min.js', '../bower_components/ng-table/dist/ng-table.min.css']
    }, {
        name: 'ui.mask',
        files: ['../bower_components/angular-ui-utils/mask.min.js']
    }, {
        name: 'ngImgCrop',
        files: ['../bower_components/ngImgCrop/compile/minified/ng-img-crop.js', '../bower_components/ngImgCrop/compile/minified/ng-img-crop.css']
    }, {
        name: 'angularFileUpload',
        files: ['../bower_components/angular-file-upload/angular-file-upload.min.js']
    }, {
        name: 'monospaced.elastic',
        files: ['../bower_components/angular-elastic/elastic.js']
    }, {
        name: 'ngMap',
        files: ['../bower_components/ngmap/build/scripts/ng-map.min.js']
    }, {
        name: 'chart.js',
        files: ['..//bower_components/angular-chart.js/dist/angular-chart.min.js', '..//bower_components/angular-chart.js/dist/angular-chart.min.css']
    }, {
        name: 'flow',
        files: ['../bower_components/ng-flow/dist/ng-flow-standalone.min.js']
    }, {
        name: 'ckeditor',
        files: ['../bower_components/angular-ckeditor/angular-ckeditor.min.js']
    }, {
        name: 'mwl.calendar',
        files: ['../bower_components/angular-bootstrap-calendar/dist/js/angular-bootstrap-calendar-tpls.js', '../bower_components/angular-bootstrap-calendar/dist/css/angular-bootstrap-calendar.min.css', 'static/assets/js/config/config-calendar.js']
    }, {
        name: 'ng-nestable',
        files: ['../bower_components/ng-nestable/src/angular-nestable.js']
    }, {
        name: 'ngNotify',
        files: ['../bower_components/ng-notify/dist/ng-notify.min.js', '../bower_components/ng-notify/dist/ng-notify.min.css']
    }, {
        name: 'xeditable',
        files: ['../bower_components/angular-xeditable/dist/js/xeditable.min.js', '../bower_components/angular-xeditable/dist/css/xeditable.css', 'static/assets/js/config/config-xeditable.js']
    }, {
        name: 'checklist-model',
        files: ['../bower_components/checklist-model/checklist-model.js']
    }, {
        name: 'ui.knob',
        files: ['../bower_components/ng-knob/dist/ng-knob.min.js']
    }, {
        name: 'ngAppear',
        files: ['../bower_components/angular-appear/build/angular-appear.min.js']
    }, {
        name: 'countTo',
        files: ['../bower_components/angular-count-to-0.1.1/dist/angular-filter-count-to.min.js']
    }, {
        name: 'angularSpectrumColorpicker',
        files: ['../bower_components/angular-spectrum-colorpicker/dist/angular-spectrum-colorpicker.min.js']
    }]
});