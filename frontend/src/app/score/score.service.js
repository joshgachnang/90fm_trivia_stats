'use strict';

angular.module('triviastats')
  .service('Score', ['djResource', '$q', '$http', 'BACKEND_SERVER', function (djResource, $q, $http, BACKEND_SERVER) {
    var service = {};
    console.log(BACKEND_SERVER + 'scores\/');
    var api = djResource(BACKEND_SERVER + 'scores\/');
    //$http.get(BACKEND_SERVER + 'scores\/')

    service.teamScores = function (team, year) {
      return api.query({
        'team_name': team,
        'ordering': '-year,-hour',
        'year': year
      });
    };

    service.hourScores = function (hour, year) {
      if (year === undefined) {
        year = new Date().getFullYear();
      }
      return api.query({
        'ordering': '-score',
        'hour': hour,
        'year': year
      });
    };

    service.search = function (search_string) {
      return api.query({
        'ordering': '-year,-hour',
        'search': search_string
      });
    };
    return service;
  }]);
