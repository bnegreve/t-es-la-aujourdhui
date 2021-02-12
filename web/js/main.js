//var SERVER='http://localhost:8888' 
var SERVER='https://www.lamsade.dauphine.fr/~bnegrevergne/t-es-la-aujourdhui/web/proxy.php';
var user_id = get_user_id();

function print_message(msg){
    $("#global-message-area").css("display", "block");
    $("#global-message-area").append(msg+'<br/>')
}

function clear_message_area(){
   $("#global-message-area").css("display", "none");
   $("#global-message-area").empty()
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

function get_user_id(){
    if ( ! user_id) {
	user_id = get('id');
    }
    return user_id; 
}

function update_userinfo(user_id){

    if(user_id){

	var qdata = {
	    'q' : 'userinfo',
	    'id' : user_id
	};

	query(SERVER, qdata, function(data){
	    document.getElementById('firstname').value = data.firstname;
	    document.getElementById('lastname').value = data.lastname;
	    document.getElementById('email').value = data.email;
	});
    }    
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
	print_message(data.msg); 
    }
    else if (data.resp_type == 'success'){
//	clear_list_message_area();
	str = '<table class="table">'; 
	for (resp in data.data){
//	    console.log(resp);
	    var user = data.data[resp]; 
	    str += format_resp(user.firstname,
			       user.lastname,
			       user.resp.resp);	    

	}
	str += '</table>';

	$("#list").html(str); 
	print_message("Rafraîchi!");


    }
    else {
	console.log('error, expected a list answer, got '+ data);
    }
}


function query(url, qdata, callback){
    console.log("qdata:");
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
	clear_message_area();
	print_message(data.msg);
    });
    update_list(user_id);
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

    query(url, qdata, function(data){
	clear_message_area();
	print_message(data.msg);	
	user_id = data.id; 
	update_userinfo(user_id);
	update_list(user_id);
    }); 
}

function remove_user(user_id){
    if(user_id){

	var url = SERVER;
	var qdata = { 'q' : 'remove', 'id' : user_id}
	query(url, qdata, function(data){
	    $("#list").empty();
	    clear_message_area(); 
	    print_message(data.msg);
	    window.user_id = null; // TODO MARCHE PAS 
	}); 
    }
}

function fetch_data(){
    var resp = get('resp')
    if(resp)
	respond(get('id'), resp);
    update_userinfo(get_user_id());
    update_list(get_user_id(), 0);
}
