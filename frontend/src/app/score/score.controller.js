'use strict';

angular.module('triviastats')
  .controller('ScoreCtrl', ['$scope', '$stateParams', 'Score', 'TRIVIA_DATES', function ($scope, $stateParams, Score, TRIVIA_DATES) {
    $scope.year = $stateParams.year;
    $scope.hour = $stateParams.hour;
    console.log('score year is', $scope.year);
    $scope.scores = Score.hourScores($scope.hour, $scope.year);
  }])
  .controller('ChartsCtrl', ['$scope', 'Score', 'TRIVIA_DATES', function ($scope, Score, TRIVIA_DATES) {
    // TODO(pcsforeducation) make this not take like 2 minutes to render..
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
    $scope.labels = [];
    $scope.series = [];
    $scope.data = [[]];
    var success = function (score_results) {
      var team_name = null;
      var index = -1;
      score_results.forEach(function (score) {
        if (score.team_name != team_name) {
          console.log(score.team_name);
          team_name = score.team_name;
          $scope.series.push(score.team_name);
          index = index + 1;
          $scope.data[index] = [];
        }
        if (index == 0) {
          $scope.labels.push(score.hour);
        }
        $scope.data[index].push(score.place);
      });
      console.log($scope.data, $scope.labels);

    };

    var scores = Score.yearScores(year, success, 10000);
    console.log(scores)
  }]);
