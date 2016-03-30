if (!$) {
    $ = django.jQuery;
}


$(document).ready(function(){
        var val = $("#id_page_type option:selected").text();
            // console.log(val);
        	if ( val == 'Content Based' ){
        		$("#id_url").hide();
        		
        	}
        	else if ( val == 'Redirect To Link' ){
        		$("#cke_id_content").hide();
        	} 
        	
        $("#id_page_type").change(function (event) {
        	var val = $("#id_page_type option:selected").text();
        	if ( val == 'Content Based' ){
        		$("#id_url").hide();
        		$("#cke_id_content").show();
        	}
         	if ( val == 'Redirect To Link' ){
        		$("#cke_id_content").hide();
        		$("#id_url").show();
        	}       	
            // console.log($(this).val());
        });
});
