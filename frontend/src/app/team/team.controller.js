'use strict';

angular.module('triviastats')
  .controller('TeamCtrl', ['$scope', '$stateParams', 'Score', function ($scope, $stateParams, Score) {
    console.log('statePArams', $stateParams);
    var teamName = window.decodeURIComponent($stateParams.teamName);
    console.log('teamName', teamName);
    $scope.scores = Score.teamScores(teamName);
    console.log($scope.scores);

    $scope.changeClass = function(change) {
      if (change >= 0) {
        return 'up';
      }
      else if (change < 0) {
        return 'down';
      }
    };

    $scope.change = function(change) {
      if (change > 0) {
        return '+' + change
      }
      else {
        return change;
      }
    };
  }]);
