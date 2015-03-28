var jshint = require('gulp-jshint');
var gulp   = require('gulp');
var paths = gulp.paths;


gulp.task('lint', function() {
  return gulp.src(paths.src + '/{app,components}/**/*.js')
    .pipe(jshint())
    .pipe(jshint.reporter('jshint-stylish'))
    .pipe(jshint.reporter('fail'));
});
