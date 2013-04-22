function homepage_init() {
    var now, trivia_start, trivia_start_count_up, trivia_2014_start, trivia_end;
//    Placeholder fix for IE9.
    $('input, textarea').placeholder();
    // Set up countdown/countup widget
    now = Date.now();
//    var now = new Date(2013, 3, 19, 19, 0, 0, 0);
    // Month is 3 because Javascript has Jan = 0..
    trivia_start = new Date(2013, 3, 19, 18, 0, 0, 0);
    trivia_start = new Date(2014, 3, 11, 18, 0, 0, 0);
    // Since hour 1 starts right away..
    trivia_start_count_up = new Date(2013, 3, 19, 17, 0, 0, 0);
    trivia_end = new Date(2013, 3, 22, 0, 0, 0, 0);
//    console.log("Now: ", now, " Trivia Start: ", trivia_start);
    if (now < trivia_start) {
//        console.log("Not trivia time yet!");
//        $("#current_hour").html("<h3>Trivia Countdown</h3>");
        $("#countdown").countdown({until: trivia_start, format: 'dHMS', layout: '<div class="cur_days"><p>{dn}</p><p>{dl}</p></div>' +
            '<div class="cur_hours chms">{hn}</div>' +
            '<div class="cur_minutes chms">{mn}</div>' +
            '<div class="cur_seconds chms">{sn}</div>'});
    }else if (now > trivia_end) {
        $("#countdown").countdown({until: trivia_2014_start, format: 'dHMS', layout: '<div class="cur_days"><p>{dn}</p><p>{dl}</p></div>' +
            '<div class="cur_hours chms">{hn}</div>' +
            '<div class="cur_minutes chms">{mn}</div>' +
            '<div class="cur_seconds chms">{sn}</div>'});
    } else {
//        $("#current_hour").html("<h3>Current Hour</h3>");
//        console.log("Trivia time!");
        $("#countdown").countdown({since: trivia_start_count_up, format: 'HMS', layout: '<div class="trivia_hours trivia_chms">Hour {hn}</div>' +
            '<div class="trivia_minutes trivia_chms">{mn}</div>' +
            '<div class="trivia_seconds trivia_chms">{sn}</div>'});
    }
}