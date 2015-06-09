function setCookie(cname, cvalue, exdays) {
    var d = new Date();
    d.setTime(d.getTime() + (exdays*24*60*60*1000));
    var expires = "expires="+d.toUTCString();
    document.cookie = cname + "=" + cvalue + "; " + expires;
}

function getCookie(cname) {
    var name = cname + "=";
    var ca = document.cookie.split(';');
    for(var i=0; i<ca.length; i++) {
        var c = ca[i];
        while (c.charAt(0)==' ') 	
			c = c.substring(1);
        if (c.indexOf(name) == 0) 
			return c.substring(name.length, c.length);
    }
    return "";
}

function select_last_used_main_category(){
	main_category = getCookie( "main_category" );
	if( main_category ){
		$("#main_categories > option").each(function(){// Check if their exists a select option with value equal to main_category
			if( this.value == main_category )
				$("#main_categories").val( main_category ).change();
		});
	}
}

function select_last_used_category(){
	category = getCookie( "category" );
	main_category = $("#main_categories").val();
	main_category_cookie = getCookie( "main_category" ) 
	if( category && main_category == main_category_cookie ){ //If selected main_category is equal to main_category saved in cookies
		$("#id_category > option").each(function(){// Check if their exists a select option with value equal to category
			if(this.value == category )
				$("#id_category").val( category );
		});
	}
}
