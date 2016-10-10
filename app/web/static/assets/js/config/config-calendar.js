'use strict';
angular.module('myModule', ['mwl.calendar'])
  .config(function (calendarConfig) {
      calendarConfig.dateFormatter = 'moment'; //use either moment or angular to format dates on the calendar. Default angular. Setting this will override any date formats you have already set.
      calendarConfig.showTimesOnWeekView = false; //Make the week view more like the day view, with the caveat that event end times are ignored.

  });