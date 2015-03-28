'use strict';

angular.module('triviastats')
  .controller('TeamCtrl', ['$scope', '$stateParams', 'Score', function ($scope, $stateParams, Score) {
    var team_name = window.decodeURIComponent($stateParams.team_name);
    $scope.scores = Score.teamScores(team_name);
    console.log($scope.scores)
  }]);
