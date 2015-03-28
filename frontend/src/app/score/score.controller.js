'use strict';

angular.module('triviastats')
  .controller('ScoreCtrl', ['$scope', 'Score', function ($scope, Score) {
    $scope.scores = Score.hourScores(54, 2014);
  }]);
