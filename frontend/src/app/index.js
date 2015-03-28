'use strict';

var app = angular.module('triviastats', ['ngAnimate', 'ngCookies', 'ngTouch', 'ngSanitize', 'ngResource', 'ui.router', 'ngMaterial', 'djangoRESTResources', 'datatables']);

app.config(function ($stateProvider, $urlRouterProvider) {
  $stateProvider
    .state('home', {
      url: '/',
      templateUrl: 'app/home/home.html',
      controller: 'HomeCtrl'
    })
    .state('scores', {
      url: '/scores/:year/:hour',
      templateUrl: 'app/score/score.html',
      controller: 'ScoreCtrl'
    })
    .state('teams', {
      url: '/teams/:team_name',
      templateUrl: 'app/team/team.html',
      controller: 'TeamCtrl'
    });

  $urlRouterProvider.otherwise('/');
});

// Filter for generating encoded urls from team names
app.filter('escape', function() {
  return window.encodeURIComponent;
});
// Util functions
//function triviaTime(dates) {
//  var now = new Date();
//  var triviaStar = dates[now.getFullYear()];
//  var triviaEnd = triviaStar.getTime() + (54 * 60 * 60 * 1000);
//  return {
//    'duringTrivia': now > triviaStar && now < triviaEnd,
//    'timeToTrivia': parseInt((triviaStar - now) / 1000),
//    // Starts with hour 1
//    'timeIntoTrivia': parseInt((now - triviaStar + (60 * 60 * 1000)) / 1000)
//  };
//}
