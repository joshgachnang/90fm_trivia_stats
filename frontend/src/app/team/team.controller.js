'use strict';

angular.module('triviastats')
  .controller('TeamCtrl', ['$scope', '$stateParams', 'Score', function ($scope, $stateParams, Score) {
    console.log('statePArams', $stateParams);
    var teamName = window.decodeURIComponent($stateParams.teamName);
    console.log('teamName', teamName);
    $scope.scores = Score.teamScores(teamName);
    console.log($scope.scores);
  }]);
