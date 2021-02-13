var SERVER='http://localhost:8888' 
//var SERVER='https://www.lamsade.dauphine.fr/~bnegrevergne/t-es-la-aujourdhui/web/proxy.php';
var user_id = null;

function print_message(msg){
    $("#global-message-area").append(msg+'<br/>')
    $("#global-message-area").fadeIn();
    setTimeout(function(){
	clearTimeout();
	$("#global-message-area").fadeOut();
	}, 5000);
}

function clear_message_area(){
    $("#global-message-area").empty();
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


function toggle_requires_id(value=true){
    var items = document.getElementsByClassName('requires_id');
    for (var i=0; i < items.length; i++) {
	items[i].disabled = !value;
    }
}

function toggle_requires_response(value=true){
    var items = document.getElementsByClassName('requires_response');
    for (var i=0; i < items.length; i++) {
	items[i].disabled = !value;
    }
}


function get_user_id(){
    if ( ! user_id) {
	user_id = get('id');
    }
    return user_id; 
}

function fetch_userinfo(user_id){

    if(user_id){

	var qdata = {
	    'q' : 'userinfo',
	    'id' : user_id
	};
	
	query(SERVER, qdata, process_response);
    }    
}

function process_userinfo_response(data){    
    document.getElementById('firstname').value = data.firstname;
    document.getElementById('lastname').value = data.lastname;
    document.getElementById('email').value = data.email;    
    toggle_requires_id();
}

function format_resp(firstname, lastname, resp){
    str = '<tr><td>';
    str += firstname + ' ' + lastname + ' '
    if (resp == 1)
	str += 'viendra.'; 
    else if (resp == 0)
	str += 'ne viendra pas.';
    else if (resp == -1)
	str += 'en a marre de se faire harcerler par mon script.'

    str += '</td></tr>'
    return str;
}

function display_list(data){
    var str = ''; 
    for (resp in data){
	//	    console.log(resp);
	var user = data[resp]; 
	str += format_resp(user.firstname,
			   user.lastname,
			   user.resp.resp);	    

    }
    str += '</table>';

    $("#list").html(str); 
    toggle_requires_id();
    toggle_requires_response();
}


function query(url, qdata){
    console.log("qdata:");
    console.log(qdata);

    $.ajax({
	type: 'GET',
	url: url,
	crossDomain: true,
	data: qdata,
	cache: false,  
    	success: process_response
    });
}

function update_list(user_id){
    var url = SERVER; 
    var qdata = { 'q' : 'list', 'id': user_id };
    query(url, qdata, process_response);
} 

function respond(user_id, resp, validity=''){
    var url = SERVER ;
    var qdata = { 'q' : 'response', 'id' : user_id,
		  'resp' : resp, 'validity':validity };
    query(url, qdata);
}

function register_user(){

    var firstname = document.getElementById('firstname').value;
    var lastname = document.getElementById('lastname').value;
    var email = document.getElementById('email').value;

    var url = SERVER;
    var qdata = { 'q' : 'register',
		  'firstname' : firstname,
		  'lastname' : lastname,
		  'email' : email };
    if (user_id)
	qdata['id'] = user_id; 

    query(url, qdata); 
}

function send_email(){
    var email = document.getElementById('email2').value;
    query(SERVER, { 'q' : 'sendemail', 'email' : email });     
}

function process_register_response(data){
    clear_message_area();
    print_message(data.msg_string);	
    user_id = data.id; 
    fetch_userinfo(user_id);
    update_list(user_id);
}

function remove_user(user_id){
    if(user_id){
	var url = SERVER;
	var qdata = { 'q' : 'remove', 'id' : user_id}
	query(url, qdata)	
    }
}

function process_remove_response(data){
    window.user_id = null;
    $("#list").empty();
    clear_message_area(); 
    print_message(data.msg_string)	
    toggle_requires_id(false);
    toggle_requires_response(false);
}

function process_response(rdata){

    switch (rdata.resp_type){
    case 'userinfo':
	if (rdata.subtype === 'message')
	    print_message(rdata.msg_string)	
	else if (rdata.subtype === 'data'){
	    process_userinfo_response(rdata.data);
	}
	break;
    case 'sendemail':
	if (rdata.subtype === 'message'){
	    clear_message_area();
	    print_message(rdata.msg_string);
	}
    case 'list':
	if (rdata.subtype === 'message')
	    print_message(rdata.msg_string)	
	else if (rdata.subtype === 'data')
	    display_list(rdata.data);
	break;
    case 'response':
	if (rdata.subtype === 'message'){
	    clear_message_area(); 
	    print_message(rdata.msg_string);
	}
	else if (rdata.subtype === 'data'){
	    clear_message_area();
	    print_message(rdata.data.msg_string);
	    toggle_requires_response();
	    update_list(user_id);
	}
	break;
    case 'register':
	if (rdata.subtype === 'message')
	    print_message(rdata.msg_string)	
	else if (rdata.subtype === 'data')
	    process_register_response(rdata.data)
	break;
    case 'remove':
	if (rdata.subtype === 'message')
	    print_message(rdata.msg_string)	
	else if (rdata.subtype === 'data'){
	    process_remove_response(rdata.data);
	}
	
	break; 
    }
}

function forward_queries(){
    // forward queries
    if(location.search !== ''){
	$.ajax({
	    type: 'GET',
	    url: SERVER+location.search,
	    crossDomain: true,
	    data: "",
	    cache: false,  
    	    success: process_response
	});
    }
}

function fetch_data(){
    forward_queries(); 
    if(get_user_id()){
	fetch_userinfo(get_user_id());
    // 	update_list(get_user_id(), 0);
    }
}
