'use strict';

const gulp = require('gulp'),
    mode = require('gulp-mode')(),
    sass = require('gulp-sass'),
    postcss = require('gulp-postcss'),
    flexbugsFixes = require('postcss-flexbugs-fixes'),
    autoprefixer = require('autoprefixer'),
    cleanCSS = require('gulp-clean-css'),
    concat = require('gulp-concat'),
    babel = require('gulp-babel'),
    uglify = require('gulp-uglify');

sass.compiler = require('node-sass');


gulp.task('buildFomantic', () => {
    const {spawn} = require('child_process');
    return spawn('cd semantic && gulp build && cd ..', {shell: true});
});

gulp.task('sass', () => {
    return gulp.src('./src/sass/**/*.scss')
        .pipe(sass.sync().on('error', sass.logError))
        .pipe(postcss([
            flexbugsFixes(),
            autoprefixer('last 2 versions')
        ]))
        .pipe(mode.production(cleanCSS()))
        .pipe(gulp.dest('./dist/css'));
});

gulp.task('js', () => {
    return gulp.src([
        './semantic/dist/semantic.js',
        './src/js/main.js',
    ])
        .pipe(babel({
            presets: ['@babel/preset-env'],
            ignore: [
                './node_modules/fomantic-ui/dist/semantic.js',
            ]
        }))
        .pipe(concat('main.js'))
        .pipe(mode.production(uglify()))
        .pipe(gulp.dest('./dist/js'));
});

gulp.task('watch', () => {
    gulp.watch('./src/sass/**/*.scss', gulp.series('sass'));
    gulp.watch(['./src/js/**/*.js'], gulp.series('js'));
});

gulp.task('build', gulp.series('buildFomantic', 'sass', 'js'));

gulp.task('default', gulp.series('sass', 'js'));
