'use strict';

angular.module('triviastats')
  .controller('CountdownCtrl', ['$scope', '$timeout', 'TRIVIA_DATES', function ($scope, $timeout, TRIVIA_DATES) {
    $scope.tickInterval = 1000;  //ms
    $scope.timeToTrivia = 0;
    $scope.timeIntoTrivia = 0;

    function tick() {
      var now = new Date();
      $scope.triviaStart = TRIVIA_DATES[now.getFullYear()];
      $scope.triviaEnd = $scope.triviaStart.getTime() + (54 * 60 * 60 * 1000);
      $scope.duringTrivia = now > $scope.triviaStart && now < $scope.triviaEnd;
      $scope.timeToTrivia = parseInt(($scope.triviaStart - now) / 1000);
      // Starts with hour 1
      $scope.timeIntoTrivia = parseInt((now - $scope.triviaStart + (60 * 60 * 1000)) / 1000);
      $timeout(tick, $scope.tickInterval);  // reset the timer
    }

    $timeout(tick, $scope.tickInterval);
  }])
  .filter('countdown', function () {
    return function (date, label, percent) {
      if (label === 'days') {
        var days = Math.floor(date / 3600 / 24);
        if (percent === 'true') {
          return Math.floor(days / 365 * 100);
        }
        return days < 10 ? '0' + days : days;
      }
      else if (label === 'hours') {
        var hours = Math.floor(date / 3600) % 24;
        if (percent === 'true') {
          return Math.floor(hours / 24 * 100);
        }
        return hours < 10 ? '0' + hours : hours;
      }
      else if (label === 'minutes') {
        var minutes = Math.floor(date / 60) % 60;
        if (percent === 'true') {
          return Math.floor(minutes / 60 * 100);
        }
        return minutes < 10 ? '0' + minutes : minutes;
      }
      else if (label === 'seconds') {
        var seconds = Math.floor(date) % 60;
        if (percent === 'true') {
          return Math.floor(seconds / 60 * 100);
        }
        return seconds < 10 ? '0' + seconds : seconds;
      }
      else if (label === 'triviaHours') {
        var triviaHours = Math.floor(date / 3600) % (24 * 365);
        if (percent === 'true') {
          return Math.floor(triviaHours / 54 * 100);
        }
        return triviaHours < 10 ? '0' + triviaHours : triviaHours;
      }
    };
  })
  .controller('HomeCtrl', ['$scope', '$mdToast', 'Score', 'Signup', 'TRIVIA_DATES', function ($scope, $mdToast, Score, Signup, TRIVIA_DATES) {
    var now = new Date();
    var start_date = TRIVIA_DATES[now.getFullYear()];
    var end_date = new Date(start_date);
    end_date.setHours(start_date.getHours() + 54);
    var hour = 54;

    var year;
    if (now < start_date) {
      year = (parseInt(now.getFullYear()) - 1).toString();
    }
    else {
      year = now.getFullYear();
    }

    if (now > start_date && now < end_date) {
      // During Trivia
      hour = Math.floor(Math.abs(now - start_date) / 36e5) + 1;
    }
    console.log('score year is', year);
    console.log('hour', hour);

    $scope.scores = Score.hourScores(undefined, year);
    $scope.message = '';
    $scope.subscriber = {
      email: undefined,
      phoneNumber: undefined
    };

    $scope.register = function () {
      if (!$scope.subscriber.phoneNumber && !$scope.subscriber.email) {
        $mdToast.show(
          $mdToast.simple()
            .content('Must enter either a phone number or email')
            .hideDelay(3000)
        );
      } else {
        Signup.register($scope.subscriber).success(function () {
          $scope.subscriber = {
            email: undefined,
            phoneNumber: undefined
          };
          $scope.message = 'Thanks for signing up!';
          $mdToast.show(
            $mdToast.simple()
              .content('Registered!')
              .hideDelay(3000)
          );
        })
          .error(function (data) {
            console.log('form error', data);
            $mdToast.show(
              $mdToast.simple()
                .content('Invalid Form')
                .hideDelay(3000)
            );
          });
      }
    };
  }]);
