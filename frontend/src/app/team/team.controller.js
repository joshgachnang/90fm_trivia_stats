'use strict';

angular.module('triviastats')
  .controller('TeamCtrl', ['$scope', '$stateParams', 'Score', function ($scope, $stateParams, Score) {
    var teamName = window.decodeURIComponent($stateParams.teamName);
    $scope.scores = Score.teamScores(teamName);
    console.log($scope.scores);
  }]);
