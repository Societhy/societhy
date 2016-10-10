module.exports = function(grunt) {
	var gtx = require('gruntfile-gtx').wrap(grunt);

    gtx.loadAuto();

    var gruntConfig = require('./grunt');
    gruntConfig.package = require('./package.json');

    gtx.config(gruntConfig);

    // We need our bower components in order to develop
	gtx.alias('build:layout1', ['compass:layout1', 'clean:layout1', 'copy:layout1', 'string-replace:layout1', 'concat:layout1', 'cssmin:layout1', 'uglify:layout1']);
	gtx.alias('build:layoutrtl1', ['compass:layoutrtl1', 'clean:layoutrtl1', 'copy:layoutrtl1', 'string-replace:layoutrtl1', 'concat:layoutrtl1', 'cssmin:layoutrtl1', 'uglify:layoutrtl1']);
	gtx.alias('build:layout2', ['compass:layout2', 'clean:layout2', 'copy:layout2', 'string-replace:layout2', 'concat:layout2', 'cssmin:layout2', 'uglify:layout2']);
	gtx.alias('build:layoutrtl2', ['compass:layoutrtl2', 'clean:layoutrtl2', 'copy:layoutrtl2', 'string-replace:layoutrtl2', 'concat:layoutrtl2', 'cssmin:layoutrtl2', 'uglify:layoutrtl2']);
    gtx.alias('build:layout3', ['compass:layout3', 'clean:layout3', 'copy:layout3', 'string-replace:layout3', 'concat:layout3', 'cssmin:layout3', 'uglify:layout3']);
	gtx.alias('build:layoutrtl3', ['compass:layoutrtl3', 'clean:layoutrtl3', 'copy:layoutrtl3', 'string-replace:layoutrtl3', 'concat:layoutrtl3', 'cssmin:layoutrtl3', 'uglify:layoutrtl3']);
    gtx.alias('build:layout4', ['compass:layout4', 'clean:layout4', 'copy:layout4', 'string-replace:layout4', 'concat:layout4', 'cssmin:layout4', 'uglify:layout4']);
	gtx.alias('build:layoutrtl4', ['compass:layoutrtl4', 'clean:layoutrtl4', 'copy:layoutrtl4', 'string-replace:layoutrtl4', 'concat:layoutrtl4', 'cssmin:layoutrtl4', 'uglify:layoutrtl4']);
    gtx.alias('build:layout5', ['compass:layout5', 'clean:layout5', 'copy:layout5', 'string-replace:layout5', 'concat:layout5', 'cssmin:layout5', 'uglify:layout5']);
	gtx.alias('build:layoutrtl5', ['compass:layoutrtl5', 'clean:layoutrtl5', 'copy:layoutrtl5', 'string-replace:layoutrtl5', 'concat:layoutrtl5', 'cssmin:layoutrtl5', 'uglify:layoutrtl5']);
	gtx.alias('build:layout6', ['compass:layout6', 'clean:layout6', 'copy:layout6', 'string-replace:layout6', 'concat:layout6', 'cssmin:layout6', 'uglify:layout6']);
	gtx.alias('build:layoutrtl6', ['compass:layoutrtl6', 'clean:layoutrtl6', 'copy:layoutrtl6', 'string-replace:layoutrtl6', 'concat:layoutrtl6', 'cssmin:layoutrtl6', 'uglify:layoutrtl6']);

    gtx.finalise();
};
