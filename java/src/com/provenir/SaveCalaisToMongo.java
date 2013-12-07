package com.provenir;

import java.io.BufferedReader;
import java.io.DataOutputStream;
import java.io.InputStreamReader;
import java.net.HttpURLConnection;
import java.net.URL;

import com.mongodb.BasicDBObject;
import com.mongodb.DB;
import com.mongodb.DBCollection;
import com.mongodb.DBObject;
import com.mongodb.Mongo;

public class SaveCalaisToMongo implements Runnable {

	private final String USER_AGENT = "Calais Rest Client";
	private String inputString;
	private long artId;
	private String artName;
	
	public static void main(String args[]){
		try {
			BasicDBObject query = new BasicDBObject();
			query.append("artId", 13031187);
			Mongo mongoClient = MongoConnection.getConnection();
			DB db = mongoClient.getDB("548db");
			DBCollection coll = db.getCollection("openCalaisRaw");
			
			
			DBObject dbo = coll.findOne(query);
			System.out.println(dbo);
		} catch (Exception e) {
			System.out.println(e.getMessage());
		}
	}


	public SaveCalaisToMongo(long artId, String artName,
			String inputToSendToOpenCalais) {
		this.artId = artId;
		this.artName = artName;
		this.inputString = inputToSendToOpenCalais;
	}
	
	private boolean isArtInMongo(long artId){
		try {
			BasicDBObject query = new BasicDBObject();
			query.append("artId", artId);
			Mongo mongoClient = MongoConnection.getConnection();
			DB db = mongoClient.getDB("548db");
			DBCollection coll = db.getCollection("openCalaisRaw");
			
			
			DBObject dbo = coll.findOne(query);
			if(dbo!=null){
				return true;
			}
			return false;
		} catch (Exception e) {
			System.out.println(e.getMessage());
		}
		return false;
	}


	// HTTP POST request
	private void sendPost() throws Exception {
		if(isArtInMongo(artId)){
			//System.out.println("skipping:"+artId);
			return;
		}
		String url = "http://api.opencalais.com/tag/rs/enrich";
		URL obj = new URL(url);
		HttpURLConnection con = (HttpURLConnection) obj.openConnection();

		// add reuqest header
		con.setRequestMethod("POST");
		con.setRequestProperty("User-Agent", USER_AGENT);
		con.setRequestProperty("Accept", "application/json");
		con.setRequestProperty("x-calais-licenseID", "zkerh9g5uv3dg7wjbykgu32z");
		con.setRequestProperty("Content-Type", "text/html; charset=UTF-8");

		// Send post request
		con.setDoOutput(true);
		DataOutputStream wr = new DataOutputStream(con.getOutputStream());
		wr.writeBytes(inputString);
		wr.flush();
		wr.close();

		BufferedReader in = new BufferedReader(new InputStreamReader(
				con.getInputStream()));
		String inputLine;
		StringBuffer response = new StringBuffer();

		while ((inputLine = in.readLine()) != null) {
			response.append(inputLine);
		}
		in.close();

		try {
			BasicDBObject doc = new BasicDBObject();
			Mongo mongoClient = MongoConnection.getConnection();
			DB db = mongoClient.getDB("548db");
			DBCollection coll = db.getCollection("openCalaisRaw");
			doc.append("artId", artId)
					.append("title", artName)
					.append("calaisRawJson",response.toString());
			coll.insert(doc);
			System.out.println("Saved: " + artId);
		} catch (Exception e) {
			System.out.println(e.getMessage());
		}

	}

	@Override
	public void run() {
		try {
			sendPost();
		} catch (Exception e) {
			System.out.println("********************Failed: "+ artId);
		}
	}

}