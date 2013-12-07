package com.provenir;

import java.sql.Connection;
import java.sql.ResultSet;
import java.sql.Statement;
import java.util.ArrayList;

import com.mongodb.BasicDBList;
import com.mongodb.BasicDBObject;
import com.mongodb.DB;
import com.mongodb.DBCollection;
import com.mongodb.DBObject;
import com.mongodb.Mongo;

public class EntityToArt {

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

			Connection conn = PostGreConnection.getConnection();
			Statement st = conn.createStatement();
			ResultSet rs = st.executeQuery("SELECT * FROM edge");
			while (rs.next()) {
				DBObject obj = coll.findOne(new BasicDBObject("entityURL", rs
						.getString(2)));
				if (obj == null) {
					obj = new BasicDBObject();
					obj.put("entityURL", rs.getString(2));
					ArrayList<String> list = new ArrayList<String>();
					list.add(rs.getString(1));
					obj.put("arts", list);
					obj.put("type", rs.getString(3));
					coll.insert(obj);
				} else {
					String art = rs.getString(1);
					BasicDBList dbList = (BasicDBList) obj.get("arts");
					if (!dbList.contains(art)) {
						dbList.add(art);
					}
					coll.save(obj);
				}
				count++;
				if (count % 1000 == 0) {
					System.out.println("Count: " + count);
				}
			}
			conn.close();
			mongoClient.close();
		} catch (Exception e) {
			e.printStackTrace();
		}

	}
}
