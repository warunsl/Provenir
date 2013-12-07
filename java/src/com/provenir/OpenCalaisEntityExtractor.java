package com.provenir;

import java.util.concurrent.ExecutorService;
import java.util.concurrent.Executors;
import java.util.concurrent.TimeUnit;

import com.mongodb.DB;
import com.mongodb.DBCollection;
import com.mongodb.DBCursor;
import com.mongodb.DBObject;
import com.mongodb.Mongo;

public class OpenCalaisEntityExtractor {
	private static final int NTHREDS = 2;

	public static void main(String[] args) {

		// To directly connect to a single MongoDB server (note that this will
		// not auto-discover the primary even
		// if it's a member of a replica set:
		Mongo mongoClient;
		try {
			mongoClient = MongoConnection.getConnection();
			DB db = mongoClient.getDB("548db");
			DBCollection coll = db.getCollection("provenance");
			DBCursor cursor = coll.find();
//			try {
//			   while(cursor.hasNext()) {
//			       System.out.println(cursor.next());
//			   }
//			} finally {
//			   cursor.close();
//			}
			ExecutorService executor = Executors.newFixedThreadPool(NTHREDS);
			
			while(cursor.hasNext()){
				try{
					DBObject doc = cursor.next();
					long artId = Integer.parseInt(doc.get("artId").toString());
					String title = doc.get("title").toString();
					String provenance = doc.get("provenance").toString();
					Runnable worker = new SaveCalaisToMongo(artId,title,provenance);
					executor.execute(worker);					
				}catch(Exception e){
					System.out.println(e.getMessage());
				}
			}
			cursor.close();
			// This will make the executor accept no new threads
		    // and finish all existing threads in the queue
		    executor.shutdown();
		    // Wait until all threads are finish
		    executor.awaitTermination(Long.MAX_VALUE, TimeUnit.DAYS);
		    System.out.println("Finished all threads");
		    

		} catch(Exception e){
			e.printStackTrace();
		}

//		for (int i = 0; i < 4; i++) {
//			Runnable worker = new SaveCalaisToMongo(
//					"Gustave Dreyfus [1837-1914], Paris; his heirs; purchased with the entire Dreyfus collection 9 July 1930");
//			executor.execute(worker);
//		}
		
		

	}
}
