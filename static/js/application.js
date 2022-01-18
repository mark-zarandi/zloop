
$(document).ready(function(){
    //connect to the socket server.
    var meter = 4
    var tracks = [0,0,0,0,0,0,0,0];

    for (i = 0; i <= 7; i++) {$("#slider" + i).roundSlider(
        {startAngle: 90, 
            animation: false,
            readOnly: false, 
            min: 0, 
            max: 16, 
            editableToolTip: false,
            showToolTip: true,
            tooltipFormat: function (e) {
    return ((Math.floor(e.value/meter) + 1)+ " / " + ($("#slider" + i).data("roundSlider").option('max')/meter));
    }
});




};
    c_time = [0,0]
    bar = 1
    beat = 1




       // $("#slider1").roundSlider({startAngle: 90, readOnly: true, min: 0, max: 100});
    var socket = io.connect('http://' + document.domain + ':' + location.port + '/thermostat');


    setInterval(function() {
    socket.emit('time');
}, 1);

    
    socket.on('time', function(data) {
    bar = (data['time'][0]);
    beat = (data['time'][1]);
    if ((c_time[0]!=bar) || (c_time[1]!=beat)) {
        //debugging
    // console.log("BAR" + bar + ", BEAT" + beat);
    // console.log(c_time + " " + data['time']);
    c_time[0] = data['time'][0];
    c_time[1] = data['time'][1];
    }

});

    socket.on('state_change', function(data) {
    //console.log("got it");
        test = (JSON.parse(JSON.stringify(data)));
        tracks[(test['t_num'])]  = test;
        // console.log(test['length'])
        
        $("#slider" + (test['t_num'])).data("roundSlider").option('max',test['length'])
        // $.each(tracks,function(index,value){

        //     console.log(value['start_time'][0])

        // });


    
});


    setInterval(function() {
    for (i = 0; i <= 7; i++){
        var secHtml = $("#slider" + i);
        
        look_here = (secHtml.data("roundSlider"));
        
        
        $("#txtBox"+i).val(tracks[i]['state']);
        if ((((c_time[0]-1)*meter)<look_here.option('max')) && (tracks[i]['state']=="playing")){
            secHtml.show();
            secHtml.roundSlider('setValue', (((c_time[0]-1)*meter)+c_time[1])-1);

        } else if (tracks[i]['state']=="playing"){
            $("#txtBox"+i).val("made it");
            secHtml.roundSlider('setValue',((((c_time[0]-1)*meter)%look_here.option('max'))+c_time[1])-1);
        } else{
            secHtml.hide();
        }


        } 
}, 1);


    //receive details from server
    // socket.on('newnumber', function(msg) {
    //     console.log("Temp Set " + msg.number);
    //     //maintain a list of ten numbers
        
    //     $("#txtBox").val(JSON.stringify(msg.track_1_text));
        
    //     var secHtml = $("#slider");
    //     secHtml.roundSlider('setValue', msg.number)
        
    // });

});