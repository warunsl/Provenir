var count = 0,
	arr = [];

db.artdata.find().forEach(function(art){
	if(db.provenance.find({artId:art.id}).hasNext()){
		count++;
	}else{
		arr.push(art.id);
	}
});


for(i in arr){
	db.artdata.remove({id:arr[i]});
	print('removed: '+arr[i]);
}



db.artdata.find({id:1}).forEach(function(art){
	print(db.provenance.find({artId:-1}).hasNext());
});





//To insert provenance info in array format
var count = 0;
db.provenance.find().forEach(function(item){
	var arr = [],
		order = 10;
	db.provenance_records.find({artId:item.artId}).sort({_id:1}).forEach(function(record){
		var objToPush = {
			order : order,
			provenance : record.provenance,	
		}
		if(record.date.trim()!=""){
			objToPush.date = new Date(record.date);
		}
		if(record.sale!=null){
			objToPush.sale = record.sale;
		}
		arr.push(objToPush);
		order +=10;
	});
	item.provenanceArr = arr;
	db.provenance.save(item);
	count++;
	if(count%100==0){
		print(count);
	}
});