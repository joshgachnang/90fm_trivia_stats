'use strict';

angular.module('triviastats')
  .controller('ScoreCtrl', ['$scope', 'Score', 'TRIVIA_DATES', function ($scope, Score, TRIVIA_DATES) {
    var now = new Date();
    var start_date = TRIVIA_DATES[now.getFullYear()];

    var year;
    if (now < start_date) {
      year = (parseInt(now.getFullYear()) - 1).toString();
    }
    else {
      year = now.getFullYear();
    }

    console.log('score year is', year);
    $scope.scores = Score.hourScores(54, year);
  }])
  .controller('ChartsCtrl', ['$scope', 'Score', 'TRIVIA_DATES', function ($scope, Score, TRIVIA_DATES) {
    var now = new Date();
    var start_date = TRIVIA_DATES[now.getFullYear()];

    var year;
    if (now < start_date) {
      year = (parseInt(now.getFullYear()) - 1).toString();
    }
    else {
      year = now.getFullYear();
    }
    console.log('year', year);
    var scores = Score.yearScores(year, 10000);
    console.log(scores)
  }]);
