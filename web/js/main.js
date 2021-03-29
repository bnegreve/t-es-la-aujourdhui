var SERVER='http://localhost:8888' 
//var SERVER='https://www.lamsade.dauphine.fr/~bnegrevergne/t-es-la-aujourdhui/web/proxy.php';
var user_id = null;

function print_message(msg){
    $("#global-message-area").append(msg+'<br/>')
    $("#global-message-area").fadeIn();
    setTimeout(function(){
	clearTimeout();
	$("#global-message-area").fadeOut();
	}, 10000);
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
    document.getElementById("btn-register").innerHTML = "Mettre à jour";
    document.getElementById("btn-logout").style.display = "block";
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

function format_resp(firstname, lastname, resp){
    str = '<tr><td class="';
    str+= resp==1 ? 'yesresp' : 'noresp';
    str = '">';	
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

// button 
function action_update_list(){
    $("#list").fadeOut('fast');
    update_list();	
}

function update_list(){
    var id = get_user_id()    
    var qdata = { 'q' : 'list', 'id': user_id };    
    query(SERVER, qdata, process_response);
}

function get_userinfo(){
    var id = get_user_id()    
    var qdata = { 'q' : 'userinfo', 'id': user_id };    
    query(SERVER, qdata, process_response);
}



function process_list_response(rdata){    
    if (rdata.subtype === 'message')
	print_message(rdata.msg_string)	
    else if (rdata.subtype === 'data')
	display_list(rdata.data);
	$("#list").fadeIn('fast');
}


function action_user_response(resp, validity=''){
    // make sure query is not sent before the div has faded out
    $("#list").fadeOut('fast');
    var id = get_user_id();
    var qdata = { 'q' : 'response', 'id' : user_id,
		  'resp' : resp, 'validity':validity };
    query(SERVER, qdata);
}

// Note: name is not a typo
function process_user_response_response(rdata){
    if (rdata.subtype === 'message'){
	clear_message_area(); 
	print_message(rdata.msg_string);
    }
    else if (rdata.subtype === 'data'){
	clear_message_area();
	print_message(rdata.data.msg_string);
	toggle_requires_response();
	update_list();
	get_userinfo();
    }
}

function process_userinfo_response(rdata){    

    if (rdata.subtype === 'message')
	print_message(rdata.msg_string)	
    else if (rdata.subtype === 'data'){
	document.getElementById('firstname').value = rdata.data.firstname;
	document.getElementById('lastname').value = rdata.data.lastname;
	document.getElementById('email').value = rdata.data.email;
	//print_message("Bienvenu(e) " + rdata.data.firstname);
	toggle_requires_id();
	update_list();
    }
}



// from https://www.w3resource.com/javascript/form/email-validation.php
function validate(firstname, lastname, email){
    if (! /^[a-zA-Z0-9.!#$%&'*+/=?^_`{|}~-]+@[a-zA-Z0-9-]+(?:\.[a-zA-Z0-9-]+)*$/.test(email)){
	clear_message_area();
	print_message("Email invalide.");
	return false; 
    }
    else if (firstname === ""  || lastname === ""){
	clear_message_area();
	print_message("Nom ou prénom invalide.");
	return false;
    }
    else{
	return true;
    }
}

function sanitize(s) {
    return s.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/"/g, '&quot;');
}

function action_register_user(){
    var firstname = sanitize(document.getElementById('firstname').value);
    var lastname = sanitize(document.getElementById('lastname').value);
    var email = sanitize(document.getElementById('email').value);
    var id = get_user_id(); 
    if(validate(firstname, lastname, email)){
	query(SERVER, { 'q': 'register',
			'firstname' : firstname,
			'lastname' : lastname,
			'email' : email,
			'id' : id
		      });
    }
}

function process_register_user_response(rdata){
    if (rdata.subtype === 'message') // error
	print_message(rdata.msg_string)	
    else if (rdata.subtype === 'data'){
	var query = '?q=userinfo&id='+rdata.data.id;
	location.search=query;
    }
}

function logout(){
    user_id=null;
    location.search='';
}

function action_send_email(){
    var email = document.getElementById('email2').value;
    var query = '?q=sendemail&email='+email;
    location.search=query;
}

function process_sendemail_response(rdata){
    if (rdata.subtype === 'message'){
	clear_message_area();
	print_message(rdata.msg_string);
    }
}

function action_remove_user(){
    var id = get_user_id();
    query(SERVER, { 'q' : 'remove', 'id' : id });
}

function process_remove_user_response(rdata){
    	if (rdata.subtype === 'message')
	    print_message(rdata.msg_string)	
	else if (rdata.subtype === 'data'){
	    var query = '';
	    location.search=query;
	}
}
	

function process_response(rdata){

    switch (rdata.resp_type){
    case 'userinfo':
	process_userinfo_response(rdata);
	break;
    case 'sendemail':
	process_sendemail_response(rdata);
	break;
    case 'list':
	process_list_response(rdata);
	break;
    case 'response':
	process_user_response_response(rdata);
	break;
    case 'register':
	process_register_user_response(rdata);
	break; 
    case 'remove':
	process_remove_user_response(rdata);
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
}
