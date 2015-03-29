'use strict';

angular.module('triviastats')

.constant('BACKEND_SERVER', 'http://192.168.1.6:8000/api/v1/')

.constant('TRIVIA_DATES', {
    // 3 == April because Javascript is stupid and 0 indexes months
    // 11pm UTC == 6pm CDT
    '2015': new Date(Date.UTC(2015, 3, 17, 23)),
    '2016': new Date(Date.UTC(2016, 3, 15, 23)),
    '2017': new Date(Date.UTC(2017, 3, 21, 19)),
    '2018': new Date(Date.UTC(2018, 3, 13, 19)),
    '2019': new Date(Date.UTC(2019, 3, 12, 19))
  });
