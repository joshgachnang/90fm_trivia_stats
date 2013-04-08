function homepage_init() {
    var myCounter = new Countdown({
        seconds:5,  // number of seconds to count down
        onUpdateStatus: function(sec) { console.log(sec); }, // callback for each second
        onCounterEnd: function(){ alert('counter ended!'); } // final action
    });

    myCounter.start();
}

function Countdown(options) {
    var timer,
        instance = this,
        seconds = options.seconds || 10,
        updateStatus = options.onUpdateStatus || function () {},
        counterEnd = options.onCounterEnd || function () {};

    function decrementCounter() {
        updateStatus(seconds);
        if (seconds === 0) {
            counterEnd();
            instance.stop();
        }
        seconds--;
    }

    this.start = function () {
        clearInterval(timer);
        timer = 0;
        seconds = options.seconds;
        timer = setInterval(decrementCounter, 1000);
    };

    this.stop = function () {
        clearInterval(timer);
    };
}