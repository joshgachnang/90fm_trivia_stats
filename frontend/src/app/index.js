'use strict';

var app = angular.module('triviastats', ['ngAnimate', 'ngCookies', 'ngTouch', 'ngSanitize', 'ngResource', 'ui.router', 'ngMaterial', 'ngMdIcons', 'djangoRESTResources', 'datatables', 'signup']);

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
    })
    .state('search', {
      url: '/search',
      templateUrl: 'app/search/search.html',
      controller: 'SearchCtrl'
    })
    .state('signup', {
      url: '/signup',
      templateUrl: 'app/signup/signup.html',
      controller: 'SignupCtrl'
    });

  $urlRouterProvider.otherwise('/');
});

// Filter for generating encoded urls from team names
app.filter('escape', function () {
  return window.encodeURIComponent;
});

app.constant('TRIVIA_DATES', {
    // 3 == April because Javascript is stupid and 0 indexes months
    // 11pm UTC == 6pm CDT
    '2015': new Date(Date.UTC(2015, 3, 17, 23)),
    '2016': new Date(Date.UTC(2016, 3, 15, 23)),
    '2017': new Date(Date.UTC(2017, 3, 21, 19)),
    '2018': new Date(Date.UTC(2018, 3, 13, 19)),
    '2019': new Date(Date.UTC(2019, 3, 12, 19))
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

