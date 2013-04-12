function homepage_init() {
    now = Date.now();
    var trivia_start = new Date(2013, 3, 19, 18, 0, 0, 0);
    console.log("Now: ", now, " Trivia Start: ", trivia_start)
    if (now < trivia_start) {
        console.log("Not trivia time yet!");
        $("#current_hour").html("<h3>Trivia Countdown</h3>")
        $("#countdown").countdown({until: trivia_start, format: 'dHMS', layout: '<div class="cur_days">{dn} <div class="cur_days_label">{dl}</div></div>' +
            '<div class="cur_hours">{hn}</div>' +
            '<div class="cur_minutes">{mn}</div>' +
            '<div class="cur_seconds">{sn}</div>'});
    } else {
        $("#current_hour").html("<h3>Current Hour</h3>")
        console.log("Trivia time!")
    }
}