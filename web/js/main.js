var SERVER='http://localhost:8888' 


function print_global_message(msg){
    $("#global-message-area").css("display", "block");
    $("#global-message-area").empty()
    $("#global-message-area").html(msg)
}

function clear_global_message_area(){
    $("#global-message-area").css("display", "none");
    $("#global-message-area").empty()
}

function print_list_message(msg){
    $("#list-message-area").css("display", "block");
    $("#list-message-area").empty()
    $("#list-message-area").html(msg)
}

function clear_list_message_area(){
    $("#list-message-area").css("display", "none");
    $("#list-message-area").empty()
}

function get(index){	    
    var $_GET = {};
    if(document.location.toString().indexOf('?') !== -1) {
	var query = document.location
            .toString()
        // get the query string
            .replace(/^.*?\?/, '')
        // and remove any existing hash string (thanks, @vrijdenker)
            .replace(/#.*$/, '')
            .split('&');

	for(var i=0, l=query.length; i<l; i++) {
	    var aux = decodeURIComponent(query[i]).split('=');
	    $_GET[aux[0]] = aux[1];
	}
    }
    //get the 'index' query parameter
    return $_GET[index];
}

function format_resp(firstname, lastname, resp){
    str = '<tr><td>';
    str += firstname + ' ' + lastname + ' '
    if (resp)
	str += 'viendra.'; 
    else
	str += 'ne viendra pas.';

    str += '</td></tr>'
    return str;
}

function display_list(data){
    if (data.resp_type == 'message'){
	print_list_message(data.msg)
    }
    else if (data.resp_type == 'success'){
	clear_list_message_area();
	str = '<table>'; 
	for (resp in data.data){
//	    console.log(resp);
	    var user = data.data[resp]; 
	    str += format_resp(user.firstname,
			       user.lastname,
			       user.resp);	    

	}
	str += '</table>';

	$("#list").html(str); 


    }
    else {
	console.log('error, expected a list answer, got '+ data);
    }
}


function query(url, qdata, callback){
    console.log(qdata);
    $.ajax({
	type: 'GET',
	url: url,
	crossDomain: true,
	data: qdata,
	cache: false,  
    	success: function( data ) {
	    callback(data); 
	}
    });
}


function update_list(user_id){

    var url = SERVER; 
    var qdata = { 'q' : 'list', 'id': user_id };
    query(url, qdata, display_list); 

} 

function respond(user_id, resp){
    var url = SERVER ;
    var qdata = { 'q' : 'respond', 'id' : user_id, 'resp' : resp };
    query(url, qdata, function (data) {
	clear_list_message_area(); 
	print_global_message(data.msg);
    });
    update_list(user_id);
}

function register_user(register, firstname, lastname, email){

    if(register){
	var url = SERVER; 
	var qdata = { 'q' : 'register',
		      'firstname' : firstname,
		      'lastname' : lastname,
		      'email' : email };
	query(url, qdata, function(data){
	    print_global_message(data.msg);
	    var url = document.location.href.split('?')[0]; 
	    window.location.href = url+'?id='+data.id; 
	}); 

	
    }

}


function remove_user(user_id){

    var url = SERVER; 
    var qdata = { 'q' : 'remove', 'id' : user_id}
    query(url, qdata, function(data){
	$("#list").empty();
	print_global_message(data.msg); }); 
}


    // var result_area = document.getElementById('results')
    // result_area.scrollIntoView();


