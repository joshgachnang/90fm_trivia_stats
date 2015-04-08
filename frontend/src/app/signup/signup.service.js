'use strict';

angular.module('signup', [])
  .service('Signup', ['$http', 'BACKEND_SERVER', function ($http, BACKEND_SERVER) {
    var service = {};

    service.register = function (postData) {
      // postData should container 'username', 'password' and other required field
      // required fields are defined by the Django User object.
      if (!postData.phoneNumber && !postData.email) {

      }

      // Munge data
      postData.phone_number = postData.phoneNumber;

      return $http.post(BACKEND_SERVER + 'subscribers\/', postData)
    };

    return service;
  }]);
