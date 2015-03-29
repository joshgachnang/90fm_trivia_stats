'use strict';

angular.module('triviastats')
  .controller('SearchCtrl', ['$scope', 'Score', function ($scope, Score) {
    $scope.search_term = null;
    $scope.filtered_teams = [];
    $scope.processing = false;

    $scope.query = function () {
      $scope.processing = true;
      $scope.filtered_teams = Score.search($scope.search_term);
      $scope.processing = false;
    };

  }]);
