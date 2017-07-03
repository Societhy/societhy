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
        'd3': '../../bower_components/d3/d3.min.js',

        //*** jQuery Plugins
        'chartjs': '../../bower_components/chartjs/Chart.min.js',
        'ckeditor-plugin': '../../bower_components/ckeditor/ckeditor.js',
        'jquery-nestable-plugin': ['../../bower_components/jquery-nestable/jquery.nestable.js'],
        'touchspin-plugin': ['../../bower_components/bootstrap-touchspin/dist/jquery.bootstrap-touchspin.min.js', '../../bower_components/bootstrap-touchspin/dist/jquery.bootstrap-touchspin.min.css'],
        'jquery-appear-plugin': ['../../bower_components/jquery-appear/build/jquery.appear.min.js'],
        'spectrum-plugin': ['../../bower_components/spectrum/spectrum.js', '../../bower_components/spectrum/spectrum.css'],
        'jcrop-plugin': ['../../bower_components/Jcrop/js/jquery.Jcrop.min.js', '../../bower_components/Jcrop/css/jquery.Jcrop.min.css'],
        'rangeSlider': ['../../bower_components/jqrangeslider/jQDateRangeSlider.js', '../../bower_components/jqrangeslider/jQRangeSlider.js'],
        'datePicker': ['../../bower_components/bootstrap-daterangepicker/daterangepicker.js', "bower_components/bootstrap-daterangepicker/daterangepicker-bs3.css"],
        'datatable': ['../../bower_components/datatable/media/js/jquery.dataTables.js', '../../bower_components/datatable/media/css/jquery.dataTables.css'],

        //*** External libraries

        'keythereum': '../../node_modules/keythereum/dist/keythereum.min.js',
        'CryptoJS': '../../bower_components/crypto-js/crypto-js.js',
        'FileSaver': '../../bower_components/file-saver/FileSaver.min.js',
        'OAuth' : '../../bower_components/oauth.io/dist/oauth.js',
        'blockies' : 'external_deps/blockies.min.js',

        //*** Custom Controllers
        'dashboardCtrl': 'static/assets/js/controllers/dashboardCtrl.js',
        'loginCtrl': 'static/assets/js/controllers/loginCtrl.js',
        'chatCtrl': 'static/assets/js/controllers/chatCtrl.js',
        'keyCtrl': 'static/assets/js/controllers/keyCtrl.js',
        'userOverviewCtrl' : 'static/assets/js/controllers/userOverviewCtrl.js',
        'userOtherOverviewCtrl' : 'static/assets/js/controllers/userOtherOverviewCtrl.js',
        'walletCtrl' : 'static/assets/js/controllers/walletCtrl.js',
        'orgaMainCtrl' : ['static/assets/js/controllers/orgaMainCtrl.js','static/assets/css/orga.css'],
        'orgaWizardCtrl' : 'static/assets/js/controllers/orgaWizardCtrl.js',
        'orgaDiscoveryCtrl': 'static/assets/js/controllers/orgaDiscoveryCtrl.js',
        'productModalCtrl': 'static/assets/js/controllers/productModalCtrl.js',
        'orgaActivityCtrl': 'static/assets/js/controllers/orgaActivityCtrl.js',
        'notificationCtrl': 'static/assets/js/controllers/notificationCtrl.js',
        'orgaAdministrationCtrl': 'static/assets/js/controllers/orgaAdministrationCtrl.js',
        'offerModalCtrl': 'static/assets/js/controllers/offerModalCtrl.js',
        'newsCtrl':'static/assets/js/controllers/newsCtrl.js',
        'projectWizardCtrl' : 'static/assets/js/controllers/projectWizardCtrl.js',
        'projectDiscoveryCtrl' : 'static/assets/js/controllers/projectDiscoveryCtrl.js',
        'projectMainCtrl' : 'static/assets/js/controllers/projectMainCtrl.js',
        'userPreferenceCtrl' : 'static/assets/js/controllers/userPreferenceCtrl.js'
    },
    //*** angularJS Modules
    modules: [{
        name: 'toaster',
        files: ['../../bower_components/AngularJS-Toaster/toaster.js', '../../bower_components/AngularJS-Toaster/toaster.css']
    }, {
        name: 'angularBootstrapNavTree',
        files: ['../../bower_components/angular-bootstrap-nav-tree/dist/abn_tree_directive.js', '../../bower_components/angular-bootstrap-nav-tree/dist/abn_tree.css']
    }, {
        name: 'ngTable',
        files: ['../../bower_components/ng-table/dist/ng-table.min.js', '../../bower_components/ng-table/dist/ng-table.min.css']
    }, {
        name: 'ui.mask',
        files: ['../../bower_components/angular-ui-utils/mask.min.js']
    }, {
        name: 'ngImgCrop',
        files: ['../../bower_components/ngImgCrop/compile/minified/ng-img-crop.js', '../../bower_components/ngImgCrop/compile/minified/ng-img-crop.css']
    }, {
        name: 'angularFileUpload',
        files: ['../../bower_components/angular-file-upload/angular-file-upload.min.js']
    }, {
        name: 'monospaced.elastic',
        files: ['../../bower_components/angular-elastic/elastic.js']
    }, {
        name: 'ngMap',
        files: ['../../bower_components/ngmap/build/scripts/ng-map.min.js']
    }, {
        name: 'chart.js',
        files: ['../../bower_components/angular-chart.js/dist/angular-chart.min.js', '../../bower_components/angular-chart.js/dist/angular-chart.min.css']
    }, {
        name: 'flow',
        files: ['../../bower_components/ng-flow/dist/ng-flow-standalone.min.js']
    }, {
        name: 'ckeditor',
        files: ['../../bower_components/angular-ckeditor/angular-ckeditor.min.js']
    }, {
        name: 'mwl.calendar',
        files: ['../../bower_components/angular-bootstrap-calendar/dist/js/angular-bootstrap-calendar-tpls.js', '../../bower_components/angular-bootstrap-calendar/dist/css/angular-bootstrap-calendar.min.css', 'static/assets/js/config/config-calendar.js']
    }, {
        name: 'ng-nestable',
        files: ['../../bower_components/ng-nestable/src/angular-nestable.js']
    }, {
        name: 'ngNotify',
        files: ['../../bower_components/ng-notify/dist/ng-notify.min.js', '../../bower_components/ng-notify/dist/ng-notify.min.css']
    }, {
        name: 'xeditable',
        files: ['../../bower_components/angular-xeditable/dist/js/xeditable.min.js', '../../bower_components/angular-xeditable/dist/css/xeditable.css', 'static/assets/js/config/config-xeditable.js']
    }, {
        name: 'checklist-model',
        files: ['../../bower_components/checklist-model/checklist-model.js']
    }, {
        name: 'ui.knob',
        files: ['../../bower_components/ng-knob/dist/ng-knob.min.js']
    }, {
        name: 'ngAppear',
        files: ['../../bower_components/angular-appear/build/angular-appear.min.js']
    }, {
        name: 'countTo',
        files: ['../../bower_components/angular-count-to-0.1.1/dist/angular-filter-count-to.min.js']
    }, {
        name: 'angularSpectrumColorpicker',
        files: ['../../bower_components/angular-spectrum-colorpicker/dist/angular-spectrum-colorpicker.min.js']
    }, {
        name: 'btford.socket-io',
        files: ['../../node_modules/socket.io-client/dist/socket.io.js', '../../bower_components/angular-socket-io/socket.js']
    }, {
        name:'angucomplete-alt',
        files: ['../../bower_components/angucomplete-alt/angucomplete-alt.js']
    }, {
        name:'qrcode',
        files: ['../../node_modules/angular-qrcode/angular-qrcode.js']
    }, {
        name:'perfect_scrollbar',
        files: ['../../bower_components/perfect-scrollbar/js/perfect-scrollbar.jquery.min.js', '../../bower_components/angular-perfect-scrollbar/src/angular-perfect-scrollbar.js']
    }]
});
