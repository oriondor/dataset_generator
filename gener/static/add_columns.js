function add_new_column(col_name=" ",col_type=" ",col_from=" ",col_to=" "){
		let data = {}
		if(col_name.length>0 && col_type.length>0){
			data={name:col_name,type:col_type,from:col_from,to:col_to};
		}
		$.ajax({
			url:'/new_column/',
			data:data,
			success:function(ret){
				//console.log(ret);
				$('#columns').append(ret);
			}
		});
	}
	function check_special(elem){
		let special = ['Text','Integer'];
		if(jQuery.inArray($(elem).val(),special)!=-1){
			$(elem).parent().parent().find('.range').removeClass('hidden');
		}else{
			$(elem).parent().parent().find('.range').addClass('hidden');
		}
	}

$(function(){
	$('#add_column').click(function(){
		add_new_column();
	});
	$(document).on('change', '.spec_type', function(){
		check_special($(this));
	});
});