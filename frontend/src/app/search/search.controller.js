'use strict';

angular.module('triviastats')
  .controller('SearchCtrl', ['$scope', 'Score', function ($scope, Score) {
    $scope.searchTerm = null;
    $scope.filteredTeams = [];
    $scope.processing = false;

    $scope.query = function () {
      $scope.processing = true;
      $scope.filteredTeams = Score.search($scope.searchTerm);
      $scope.processing = false;
    };

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
