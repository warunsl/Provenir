package com.provenir;

import java.beans.Statement;
import java.sql.Connection;
import java.util.Iterator;
import java.util.Map;
import java.util.Set;

import com.mongodb.BasicDBList;
import com.mongodb.BasicDBObject;
import com.mongodb.DB;
import com.mongodb.DBCollection;
import com.mongodb.DBCursor;
import com.mongodb.DBObject;
import com.mongodb.Mongo;

public class GraphDataMongoToPostgre {

	public static void main(String[] args) {

		// To directly connect to a single MongoDB server (note that this will
		// not auto-discover the primary even
		// if it's a member of a replica set:
		Mongo mongoClient;
		int count = 0;
		try {
			mongoClient = MongoConnection.getConnection();
			DB db = mongoClient.getDB("548db");
			DBCollection coll = db.getCollection("entityToArt");
			
			

			DBCursor cursor = coll.find();
			PostgreDBHelper dbHelper =  new PostgreDBHelper();
			Connection con = PostGreConnection.getConnection();
		
			System.out.println("hello");
			
			while(cursor.hasNext()){
				try{
					DBObject doc = cursor.next();
					BasicDBObject entities = (BasicDBObject)doc.get("entities");
					String artId = doc.get("artId").toString();
					String artTitle = doc.get("title").toString();
					dbHelper.saveNode(artId, artTitle, "Art");
					
					Set<Map.Entry<String, Object>> set = entities.entrySet();
					for(Map.Entry<String, Object> entry : set){
						
						String edgeLabel = entry.getKey();
						BasicDBList labeledEntities = (BasicDBList)entry.getValue();
						Iterator<Object> entityIterator = labeledEntities.iterator();
						while(entityIterator.hasNext()){
							BasicDBObject entity = (BasicDBObject)entityIterator.next();
							dbHelper.saveNode(entity.getString("uri"), entity.getString("name"),edgeLabel);
							dbHelper.saveEdge(artId, entity.getString("uri"), edgeLabel);
						}
					}
					//break;
					
				}catch(Exception e){
					System.out.println(e.getMessage());
				}
				count++;
				if(count%100==0){
					System.out.println("count: "+count);
				}
			}
			cursor.close();
	
			mongoClient.close();
			dbHelper.connection.close();

		} catch(Exception e){
			e.printStackTrace();
		}
		

	}
}
